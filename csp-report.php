<?php
// CSP report receiver. POST = store, GET ?token=... = read (token-gated).
// Data lives OUTSIDE the web root: <parent of web root>/csp-data/
// Read token: put one long random string in <parent of web root>/csp-data/read_token.txt (never in git).
declare(strict_types=1);
$dir = dirname($_SERVER['DOCUMENT_ROOT']) . '/csp-data';
$file = $dir . '/reports.jsonl';
$max_body = 10240;
$max_file = 5 * 1024 * 1024;   // stop storing at 5 MB; rotate by hand

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    header('Cache-Control: no-store');
    $raw = file_get_contents('php://input', false, null, 0, $max_body + 1);
    if ($raw === false || strlen($raw) > $max_body) { http_response_code(413); exit; }
    $j = json_decode($raw, true);
    if (!is_array($j)) { http_response_code(400); exit; }
    $items = isset($j[0]) ? $j : [$j];
    if (!is_dir($dir)) { @mkdir($dir, 0700, true); }
    if (is_file($file) && filesize($file) > $max_file) { http_response_code(204); exit; }
    $cut = fn($v) => mb_substr((string)$v, 0, 300);
    $lines = '';
    foreach (array_slice($items, 0, 10) as $it) {
        if (!is_array($it)) continue;
        $r = $it['csp-report'] ?? ($it['body'] ?? $it);
        if (!is_array($r)) continue;
        $doc = (string)($r['document-uri'] ?? $r['documentURL'] ?? '');
        $p = parse_url($doc);
        if ($p && isset($p['host'])) $doc = ($p['scheme'] ?? 'https') . '://' . $p['host'] . ($p['path'] ?? '');
        $directive = $r['effective-directive'] ?? $r['effectiveDirective'] ?? $r['violated-directive'] ?? $r['violatedDirective'] ?? '';
        if ($directive === '') continue;
        $lines .= json_encode([
            'ts' => gmdate('c'),
            'directive' => $cut($directive),
            'blocked' => $cut($r['blocked-uri'] ?? $r['blockedURL'] ?? ''),
            'document' => $cut($doc),
            'source' => $cut($r['source-file'] ?? $r['sourceFile'] ?? ''),
            'disposition' => $cut($r['disposition'] ?? ''),
        ], JSON_UNESCAPED_SLASHES) . "\n";
    }
    if ($lines !== '') file_put_contents($file, $lines, FILE_APPEND | LOCK_EX);
    http_response_code(204);
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'GET') {
    header('Cache-Control: no-store');
    header('X-Robots-Tag: noindex');
    $tok = @trim((string)file_get_contents($dir . '/read_token.txt'));
    $given = $_SERVER['HTTP_AUTHORIZATION'] ?? ($_GET['token'] ?? '');
    $given = preg_replace('/^Bearer\s+/i', '', (string)$given);
    if ($tok === '' || !hash_equals($tok, (string)$given)) { http_response_code(403); exit('forbidden'); }
    $groups = [];
    $total = 0;
    foreach (is_file($file) ? file($file, FILE_IGNORE_NEW_LINES) : [] as $l) {
        $r = json_decode($l, true);
        if (!$r) continue;
        $total++;
        $k = $r['directive'] . '|' . $r['blocked'] . '|' . $r['document'];
        if (!isset($groups[$k])) $groups[$k] = $r + ['count' => 0, 'first_seen' => $r['ts']];
        $groups[$k]['count']++;
        $groups[$k]['last_seen'] = $r['ts'];
        unset($groups[$k]['ts']);
    }
    usort($groups, fn($a, $b) => $b['count'] <=> $a['count']);
    header('Content-Type: application/json');
    echo json_encode(['total_reports' => $total, 'groups' => array_slice($groups, 0, 500)], JSON_UNESCAPED_SLASHES);
    exit;
}
http_response_code(405);
