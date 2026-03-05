<?php
declare(strict_types=1);

header('Content-Type: application/json; charset=utf-8');
header('Cache-Control: no-store, no-cache, must-revalidate, max-age=0');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
  http_response_code(405);
  echo json_encode(['success' => false, 'error' => 'method_not_allowed']);
  exit;
}

$raw = file_get_contents('php://input');
$payload = json_decode($raw ?: '{}', true);
$token = trim((string)($payload['token'] ?? ''));

if ($token === '') {
  http_response_code(400);
  echo json_encode(['success' => false, 'error' => 'missing_token']);
  exit;
}

$secret = getenv('TURNSTILE_SECRET_KEY') ?: '';
if ($secret === '' && file_exists(__DIR__ . '/turnstile-secret.php')) {
  require_once __DIR__ . '/turnstile-secret.php';
  if (defined('TURNSTILE_SECRET_KEY')) {
    $secret = (string)TURNSTILE_SECRET_KEY;
  }
}

if ($secret === '' || str_contains($secret, 'YOUR_TURNSTILE_SECRET_KEY')) {
  http_response_code(500);
  echo json_encode(['success' => false, 'error' => 'missing_secret']);
  exit;
}

$postFields = http_build_query([
  'secret' => $secret,
  'response' => $token,
  'remoteip' => $_SERVER['REMOTE_ADDR'] ?? ''
]);

$ch = curl_init('https://challenges.cloudflare.com/turnstile/v0/siteverify');
curl_setopt_array($ch, [
  CURLOPT_POST => true,
  CURLOPT_POSTFIELDS => $postFields,
  CURLOPT_RETURNTRANSFER => true,
  CURLOPT_TIMEOUT => 15,
  CURLOPT_HTTPHEADER => ['Content-Type: application/x-www-form-urlencoded']
]);

$response = curl_exec($ch);
$curlError = curl_error($ch);
$httpCode = (int)curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($response === false || $httpCode >= 500) {
  http_response_code(502);
  echo json_encode(['success' => false, 'error' => 'upstream_error', 'detail' => $curlError]);
  exit;
}

$result = json_decode($response, true);
if (!is_array($result)) {
  http_response_code(502);
  echo json_encode(['success' => false, 'error' => 'invalid_upstream_response']);
  exit;
}

$ok = !empty($result['success']);
echo json_encode([
  'success' => $ok,
  'challenge_ts' => $result['challenge_ts'] ?? null,
  'hostname' => $result['hostname'] ?? null,
  'error-codes' => $result['error-codes'] ?? []
]);
