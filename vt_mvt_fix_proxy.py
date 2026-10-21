#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vt_mvt_fix_proxy.py

MapServer-en aurrean jartzen den proxy txikia. Tesela bat eskatzen zaionean:
  1. MapServer-i eskatzen dio (WMS GetMap, FORMAT=application/vnd.mapbox-vector-tile),
  2. poligonoen kanpo-eraztun alderantzikatuak zuzentzen ditu
     (vt_fix_mvt_orientation.py-ko fix_tile funtzioa),
  3. tesela bezeroari itzultzen dio.

Bi erabilera:

  a) XYZ helbidea (MapLibre-rentzat):
       http://lidar1:8020/<map-izena>/{z}/{x}/{y}.pbf
     Proxy-ak BBOX-a (EPSG:3857) kalkulatzen du, eta MapServer-i hau eskatzen dio:
       <upstream>?map=<mapdir>/<map-izena>.map&...&layers=<map-izena>
     Bezeroak TMS (Y alderantzikatua) erabiltzen badu: --tms.

  b) Pass-through: beste edozein helbide (adibidez WMS eskaera osoa, "?map=...")
     MapServer-i bere horretan bidaltzen zaio, eta erantzuna MVT bada, zuzendu egiten da.

     MAP fitxategia helbidean badoa (Apache bidez), erabili --map-in-path eta, behar bada, --format:
       python3 vt_mvt_fix_proxy.py --upstream http://lidar1/ogc/api/tiles/vt/ --map-in-path \\
           --format application/x-protobuf --port 8020
     Orduan MapServer-i hau eskatzen zaio:
       http://lidar1/ogc/api/tiles/vt/map-dev3?VERSION=1.1.1&REQUEST=GetMap&SERVICE=WMS&STYLES=&
       BBOX=...&WIDTH=256&HEIGHT=256&FORMAT=application%2Fx-protobuf&SRS=EPSG%3A3857&layers=map-dev3

Python 3.6+ (kanpoko libururik gabe). vt_fix_mvt_orientation.py fitxategia karpeta berean
egon behar da.

Adibidea:
  python3 vt_mvt_fix_proxy.py --upstream http://lidar1/ogc/api/tiles/vt/ --map-in-path --format application/x-protobuf --port 8020

PROBETARAKO da: hari bakarreko zerbitzaria (hari anitz), cacherik gabe (lehenetsia).
"""

import argparse
import gzip
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, HTTPServer
from socketserver import ThreadingMixIn

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from vt_fix_mvt_orientation import fix_tile  # noqa: E402

ORIGIN = 20037508.342789244          # web-mercator ardatzaren muga (m)
XYZ_RE = re.compile(r'^/([A-Za-z0-9_.\-]+)/(\d+)/(\d+)/(\d+)\.(?:pbf|mvt)$')
MVT_MIME = 'application/vnd.mapbox-vector-tile'


def log(msg):
    sys.stderr.write('[%s] %s\n' % (time.strftime('%H:%M:%S'), msg))
    sys.stderr.flush()


def tile_bbox(z, x, y, tms=False):
    n = 2 ** z
    if x < 0 or x >= n or y < 0 or y >= n:
        raise ValueError('tesela tartetik kanpo')
    if tms:
        y = n - 1 - y
    size = 2 * ORIGIN / n
    minx = -ORIGIN + x * size
    maxy = ORIGIN - y * size
    return minx, maxy - size, minx + size, maxy


class Handler(BaseHTTPRequestHandler):
    server_version = 'mvt-fix-proxy/1.0'

    def log_message(self, fmt, *args):   # lehenetsitako log-a isildu
        pass

    # ------------------------------------------------------------- helpers
    def _send(self, status, body, ctype, extra=None):
        accept = self.headers.get('Accept-Encoding', '')
        encoded = False
        if body and 'gzip' in accept and ctype.startswith('application/x-protobuf'):
            body = gzip.compress(body, 5)
            encoded = True
        self.send_response(status)
        self.send_header('Content-Type', ctype)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Vary', 'Accept-Encoding')
        if encoded:
            self.send_header('Content-Encoding', 'gzip')
        cache = self.server.cache
        self.send_header('Cache-Control', 'public, max-age=%d' % cache if cache else 'no-store')
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        self.wfile.write(body)

    def _upstream_url(self, path_and_query):
        m = XYZ_RE.match(urllib.parse.urlsplit(path_and_query).path)
        up = self.server.upstream
        if not m:
            return up.rstrip('/') + path_and_query, None
        name, z, x, y = m.group(1), int(m.group(2)), int(m.group(3)), int(m.group(4))
        bbox = tile_bbox(z, x, y, self.server.tms)
        params = []
        if not self.server.map_in_path:
            params.append(('map', '%s/%s.map' % (self.server.mapdir.rstrip('/'), name)))
        params += [
            ('VERSION', '1.1.1'), ('REQUEST', 'GetMap'), ('SERVICE', 'WMS'),
            ('STYLES', ''),
            ('BBOX', '%.6f,%.6f,%.6f,%.6f' % bbox),
            ('WIDTH', '256'), ('HEIGHT', '256'),
            ('FORMAT', self.server.fmt), ('SRS', 'EPSG:3857'), ('layers', name),
        ]
        base = up + name if self.server.map_in_path else up
        return base + '?' + urllib.parse.urlencode(params), '%d/%d/%d' % (z, x, y)

    # ------------------------------------------------------------- methods
    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', '*')
        self.send_header('Content-Length', '0')
        self.end_headers()

    def do_GET(self):
        t0 = time.time()
        try:
            url, label = self._upstream_url(self.path)
        except ValueError as exc:
            self._send(404, str(exc).encode('utf-8'), 'text/plain; charset=utf-8')
            log('GET %s -> 404 (%s)' % (self.path, exc))
            return
        body = ctype = None
        for attempt in (1, 2):
            try:
                req = urllib.request.Request(url, headers={'User-Agent': self.server_version})
                with self.server.opener.open(req, timeout=self.server.timeout) as resp:
                    body = resp.read()
                    ctype = resp.headers.get('Content-Type', '')
                break
            except urllib.error.HTTPError as exc:
                try:
                    detail = exc.read(600).decode('utf-8', 'replace').strip()
                except Exception:   # noqa
                    detail = ''
                if exc.code == 503 and attempt == 1:
                    log('MapServer-ek 503 itzuli du; berriro saiatzen (1 s)...')
                    time.sleep(1)
                    continue
                msg = 'MapServer-ek %d itzuli du' % exc.code
                if detail:
                    msg += ': ' + detail
                self._send(502, msg.encode('utf-8'), 'text/plain; charset=utf-8')
                log('GET %s -> 502 (upstream %d): %s' % (self.path, exc.code, detail[:200].replace('\n', ' ')))
                log('  upstream URL: %s' % url)
                return
            except Exception as exc:   # noqa
                self._send(502, ('Ezin da MapServer-ekin konektatu: %s' % exc).encode('utf-8'),
                           'text/plain; charset=utf-8')
                log('GET %s -> 502 (%s)' % (self.path, exc))
                log('  upstream URL: %s' % url)
                return

        ms = int((time.time() - t0) * 1000)
        is_mvt = 'vector-tile' in ctype or 'protobuf' in ctype
        if not is_mvt:
            # MVT ez den edukia (MapServer-en errorea: HTML/XML testua...).
            # XYZ moduan 502 itzultzen da, eta errorearen testua logean ikusten da.
            snippet = body[:300].decode('utf-8', 'replace').strip().replace('\n', ' ')
            status = 502 if label else 200
            self._send(status, body, ctype or 'application/octet-stream')
            log('GET %s -> %d, MVT ez (%s), %d ms' % (self.path, status, ctype, ms))
            log('  MapServer-en erantzuna: %s' % snippet)
            return
        try:
            fixed, npoly, nfixed = fix_tile(body)
        except Exception as exc:   # noqa
            log('GET %s -> ezin izan da zuzendu (%s); jatorrizkoa bidali da' % (self.path, exc))
            fixed, nfixed = body, 0
        self._send(200, fixed, 'application/x-protobuf')
        log('GET %s -> OK, %d KB, %d eraztun zuzendu, upstream %d ms' % (
            label or self.path[:80], len(fixed) // 1024, nfixed, ms))


class Server(ThreadingMixIn, HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main():
    ap = argparse.ArgumentParser(description='MapServer MVT teselen orientazioa zuzentzen duen proxya.')
    ap.add_argument('--upstream', default='http://lidar1:8010/',
                    help='MapServer-en helbidea (lehenetsia: http://lidar1:8010/)')
    ap.add_argument('--mapdir', default='/home/lidar/apache/htdocs/ogc/api/tiles/vt',
                    help='MAP fitxategien karpeta, MapServer-ek ikusten duen bidea (docker barruan)')
    ap.add_argument('--map-in-path', action='store_true',
                    help='MAP fitxategia helbidean doa: <upstream><map-izena>?VERSION=... '
                         '(bestela: <upstream>?map=<mapdir>/<map-izena>.map&...)')
    ap.add_argument('--format', default=MVT_MIME,
                    help='MapServer-i eskatuko zaion FORMAT (MAP-eko outputformat-aren mimetype-arekin '
                         'bat etorri behar du). Lehenetsia: %s' % MVT_MIME)
    ap.add_argument('--host', default='0.0.0.0')
    ap.add_argument('--port', type=int, default=8020)
    ap.add_argument('--tms', action='store_true', help='bezeroak TMS (Y alderantzikatua) erabiltzen du')
    ap.add_argument('--timeout', type=int, default=120, help='MapServer-i itxaroteko segundoak')
    ap.add_argument('--use-env-proxy', action='store_true',
                    help='http_proxy/no_proxy ingurune-aldagaiak erabili (lehenetsia: ezikusi, MapServer-era zuzenean konektatu)')
    ap.add_argument('--cache', type=int, default=0,
                    help='Cache-Control max-age segundotan (lehenetsia: 0 = no-store)')
    args = ap.parse_args()

    srv = Server((args.host, args.port), Handler)
    srv.upstream = args.upstream if args.upstream.endswith('/') else args.upstream + '/'
    srv.mapdir = args.mapdir
    srv.map_in_path = args.map_in_path
    srv.fmt = args.format
    srv.tms = args.tms
    srv.timeout = args.timeout
    srv.cache = args.cache
    srv.opener = (urllib.request.build_opener() if args.use_env_proxy
                  else urllib.request.build_opener(urllib.request.ProxyHandler({})))
    log('Proxy martxan: http://%s:%d/  ->  %s  (tms=%s, map-in-path=%s, format=%s, ingurune-proxya: %s)' % (
        args.host, args.port, srv.upstream, args.tms, args.map_in_path, args.format,
        'bai' if args.use_env_proxy else 'ez'))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        log('Gelditzen...')


if __name__ == '__main__':
    main()
