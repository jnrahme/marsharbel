#!/usr/bin/env node
import { createServer } from 'node:http';
import { readFile, stat } from 'node:fs/promises';
import { join, extname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { gzipSync } from 'node:zlib';

const ROOT = join(fileURLToPath(import.meta.url), '..', '..');
const PORT = Number(process.argv.find(a => a.startsWith('--port='))?.split('=')[1] || process.env.PORT || 4173);
// Match Hostinger's text compression when measuring production-like transfers.
const COMPRESS = process.argv.includes('--compress');

const MIME = {
  '.html': 'text/html',
  '.css': 'text/css',
  '.js': 'text/javascript',
  '.mjs': 'text/javascript',
  '.json': 'application/json',
  '.webmanifest': 'application/manifest+json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.jpeg': 'image/jpeg',
  '.gif': 'image/gif',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
  '.webp': 'image/webp',
  '.avif': 'image/avif',
  '.mp3': 'audio/mpeg',
  '.mp4': 'video/mp4',
  '.woff2': 'font/woff2',
  '.woff': 'font/woff',
  '.ttf': 'font/ttf',
  '.txt': 'text/plain',
  '.xml': 'application/xml',
  '.pdf': 'application/pdf',
};

const exists = async path => {
  try { await stat(path); return true; } catch { return false; }
};

const isFile = async path => {
  try { return (await stat(path)).isFile(); } catch { return false; }
};

const serve = async (req, res, filePath) => {
  try {
    const data = await readFile(filePath);
    const ext = extname(filePath).toLowerCase();
    const type = MIME[ext] || 'application/octet-stream';
    const headers = { 'Content-Type': type };
    let body = data;
    if (COMPRESS && /^(text\/|application\/(json|xml|manifest\+json))/.test(type)) {
      headers.Vary = 'Accept-Encoding';
      const acceptsGzip = (req.headers['accept-encoding'] || '').split(',').some(value => {
        const [encoding, ...parameters] = value.trim().split(';');
        return encoding === 'gzip' && !parameters.some(p => /^\s*q=0(?:\.0*)?\s*$/.test(p));
      });
      if (acceptsGzip) {
        body = gzipSync(data);
        headers['Content-Encoding'] = 'gzip';
      }
    }
    headers['Content-Length'] = body.length;
    res.writeHead(200, headers);
    res.end(req.method === 'HEAD' ? undefined : body);
  } catch {
    res.writeHead(500);
    res.end('Internal Server Error');
  }
};

createServer(async (req, res) => {
  const url = new URL(req.url, `http://localhost:${PORT}`);
  let pathname = decodeURIComponent(url.pathname);

  if (pathname.endsWith('/') && pathname !== '/') {
    pathname = pathname.slice(0, -1);
  }

  const filePath = join(ROOT, pathname);

  if (await isFile(filePath)) {
    return serve(req, res, filePath);
  }

  if (pathname === '/') {
    return serve(req, res, join(ROOT, 'index.html'));
  }

  if (pathname === '/gallery' && await isFile(join(ROOT, 'gallery.html'))) {
    return serve(req, res, join(ROOT, 'gallery.html'));
  }

  const htmlPath = filePath + '.html';
  if (!extname(pathname) && await isFile(htmlPath)) {
    return serve(req, res, htmlPath);
  }

  const indexPath = join(filePath, 'index.html');
  if (await exists(indexPath) && await isFile(indexPath)) {
    return serve(req, res, indexPath);
  }

  res.writeHead(404);
  res.end('File not found');
}).listen(PORT, '127.0.0.1', () => {
  console.log(`Dev server listening on http://127.0.0.1:${PORT}`);
});
