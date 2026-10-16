#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
map2vrt.py

MapServer-en MAP fitxategi batetik zoom-maila bakoitzerako OGR VRT fitxategi
bat sortzen du (lehenetsia: 9-23), eta ogr2ogr -f MVT erabiliz teselak
sortzeko shell script bat (make_tiles.sh).

Zer egiten du MAP fitxategiarekin:
  * Zoom bakoitzean aktibo dauden geruzak hautatzen ditu
    (minscaledenom / maxscaledenom, geruza eta klase mailan).
  * SCALETOKEN erabiltzen duten geruzetan (landcover, altimetry...) zoom
    horri dagokion taula hautatzen du.
  * Klaseen EXPRESSION-ak WHERE baldintza bihurtzen ditu (hydrography-lines,
    batimetry...).
  * gml_include_items eta gml_<atributua>_alias metadatuak SELECT ... AS ...
    bihurtzen ditu.
  * shapepath, bide absolutuak eta OGR konexioak (GPKG) kudeatzen ditu.

Python 3.6+ (ez du kanpoko libururik behar).

Erabilera:
  python3 map2vrt.py map-dev2.map -o vrt/
  python3 map2vrt.py map-dev2.map -o vrt/ --zmin 9 --zmax 23 --tms
"""

import argparse
import io
import math
import os
import re
import sys
from xml.sax.saxutils import escape

# Zoom 0-ko eskala-izendatzailea (256 px-ko tesela, 0.28 mm/pixel, OGC estandarra).
# z13 -> 68249, z15 -> 17062, z16 -> 8531... MAP fitxategiko iruzkinekin bat dator.
SCALE_Z0 = 559082264.0287178

BLOCKS = {
    'map', 'layer', 'class', 'scaletoken', 'values', 'metadata', 'projection',
    'outputformat', 'web', 'style', 'label', 'validation', 'leader', 'join',
    'composite', 'cluster', 'feature', 'points', 'grid', 'symbol', 'querymap',
    'legend', 'scalebar', 'reference',
}
# Bloke hauen barruan lerro guztiak datuak dira (ez dira azpibloke berriak).
DATA_BLOCKS = {'metadata', 'values', 'projection', 'points'}

WARNINGS = []


def warn(msg):
    if msg not in WARNINGS:
        WARNINGS.append(msg)
        sys.stderr.write('AVISO: %s\n' % msg)


class Unsupported(Exception):
    pass


# ---------------------------------------------------------------- MAP parser

class Node(object):
    def __init__(self, name):
        self.name = name
        self.props = []      # (gakoa, balioa) zerrenda, jatorrizko ordenean
        self.children = []

    def get(self, key, default=None):
        result = default
        for k, v in self.props:
            if k.lower() == key:
                result = v   # azkena nagusitzen da
        return result

    def kids(self, name):
        return [c for c in self.children if c.name == name]


def strip_comment(line):
    quote = None
    for i, c in enumerate(line):
        if quote:
            if c == quote:
                quote = None
        elif c in '"\'':
            quote = c
        elif c == '#':
            return line[:i]
    return line


def split_kv(line):
    m = re.match(r'''^(?:"([^"]*)"|'([^']*)'|(\S+))\s*(.*)$''', line)
    if not m:
        return line, ''
    for g in (1, 2, 3):
        if m.group(g) is not None:
            return m.group(g), m.group(4).strip()
    return line, ''


def unq(v):
    if v is None:
        return None
    v = v.strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in '"\'':
        return v[1:-1]
    return v


def parse_map(path):
    root = Node('root')
    stack = [root]
    with io.open(path, encoding='utf-8', errors='replace') as fh:
        for raw in fh:
            s = strip_comment(raw).strip()
            if not s:
                continue
            key, rest = split_kv(s)
            kl = key.lower()
            cur = stack[-1]
            if kl == 'end' and rest == '':
                if len(stack) > 1:
                    stack.pop()
            elif rest == '' and kl in BLOCKS and cur.name not in DATA_BLOCKS:
                node = Node(kl)
                cur.children.append(node)
                stack.append(node)
            else:
                cur.props.append((key, rest))
    maps = root.kids('map')
    if not maps:
        sys.exit('Errorea: ez da MAP blokerik aurkitu.')
    return maps[0]


# ---------------------------------------------------- expression -> SQL (OGR)

TOKEN_RE = re.compile(
    r'''\s*(?:(?P<str>'[^']*'|"[^"]*")|(?P<fld>\[\w+\])|'''
    r'''(?P<op>~\*?|!=|<>|<=|>=|==|=|<|>)|(?P<par>[()])|(?P<word>[\w.]+))''')

WORD_OPS = {'eq': '=', 'ne': '<>', 'lt': '<', 'gt': '>', 'le': '<=', 'ge': '>='}


def regex_to_like(pattern):
    """Adierazpen erregular sinple bat (testua, ^ eta $ ainguraketak) LIKE
    patroi bihurtzen du. Konplexuagoa bada, Unsupported altxatzen du."""
    start = pattern.startswith('^')
    end = pattern.endswith('$') and len(pattern) > (1 if start else 0)
    core = pattern[(1 if start else 0):len(pattern) - (1 if end else 0)]
    if re.search(r'[\\.*+?()|{}\[\]^$%_]', core):
        raise Unsupported('adierazpen erregularra: %s' % pattern)
    return ('' if start else '%') + core + ('' if end else '%')


def tokenize(expr):
    pos = 0
    tokens = []
    expr = expr.strip()
    while pos < len(expr):
        m = TOKEN_RE.match(expr, pos)
        if not m or m.end() == pos:
            raise Unsupported('token ezezaguna: %r' % expr[pos:pos + 10])
        pos = m.end()
        kind = m.lastgroup
        tokens.append((kind, m.group(kind)))
    return tokens


def logical_expr_to_sql(expr):
    items = []
    for kind, val in tokenize(expr):
        if kind == 'str':
            inner = val[1:-1]
            m = re.match(r'^\[(\w+)\]$', inner)
            items.append(('id', m.group(1)) if m else ('lit', inner))
        elif kind == 'fld':
            items.append(('id', val[1:-1]))
        elif kind == 'op':
            op = {'==': '=', '!=': '<>'}.get(val, val)
            items.append(('op', op))
        elif kind == 'par':
            items.append(('par', val))
        else:  # word
            lw = val.lower()
            if lw in ('and', 'or', 'not'):
                items.append(('kw', lw.upper()))
            elif lw in WORD_OPS:
                items.append(('op', WORD_OPS[lw]))
            elif re.match(r'^-?\d+(\.\d+)?$', val):
                items.append(('num', val))
            else:
                raise Unsupported('hitz ezezaguna: %s' % val)
    parts = []
    j = 0
    while j < len(items):
        t = items[j]
        if (j + 2 < len(items) + 0 and t[0] == 'id' and items[j + 1] == ('op', '~')
                and items[j + 2][0] == 'lit'):
            like = regex_to_like(items[j + 2][1]).replace("'", "''")
            parts.append('"%s" LIKE \'%s\'' % (t[1], like))
            j += 3
            continue
        if t[0] == 'id':
            parts.append('"%s"' % t[1])
        elif t[0] == 'lit':
            parts.append("'%s'" % t[1].replace("'", "''"))
        elif t[0] == 'op':
            if t[1] in ('~', '~*'):
                raise Unsupported('"~" eragilea testuinguru ezezagunean')
            parts.append(t[1])
        else:
            parts.append(t[1])
        j += 1
    return ' '.join(parts)


def expression_to_sql(expr, classitem):
    e = expr.strip()
    if e.startswith('('):
        return '(%s)' % logical_expr_to_sql(e)
    if len(e) > 1 and e.startswith('/') and e.endswith('/') and classitem:
        return '"%s" LIKE \'%s\'' % (classitem, regex_to_like(e[1:-1]).replace("'", "''"))
    if e[:1] in '"\'' and classitem:
        return '"%s" = \'%s\'' % (classitem, unq(e).replace("'", "''"))
    return '(%s)' % logical_expr_to_sql(e)


# ------------------------------------------------------------ layer helpers

def num(v, default):
    if v is None:
        return default
    try:
        return float(unq(v))
    except ValueError:
        return default


def scale_range(node):
    mn = num(node.get('minscaledenom'), 0.0)
    mx = num(node.get('maxscaledenom'), -1.0)
    if mx < 0:
        mx = float('inf')
    return mn, mx


def in_range(scale, node):
    mn, mx = scale_range(node)
    return mn <= scale < mx


def epsg_of(node):
    for sub in node.kids('projection'):
        for k, v in sub.props:
            m = re.search(r'epsg:(\d+)', k, re.I)
            if m:
                return 'EPSG:%s' % m.group(1)
        txt = ' '.join(k for k, v in sub.props if k.startswith('+'))
        if txt:
            return txt
    return None


def metadata_of(node):
    md = {}
    for sub in node.kids('metadata'):
        for k, v in sub.props:
            md[k.lower()] = unq(v)
    return md


def resolve_scaletokens(layer, scale):
    result = {}
    for st in layer.kids('scaletoken'):
        name = unq(st.get('name'))
        pairs = []
        for vb in st.kids('values'):
            for k, v in vb.props:
                try:
                    pairs.append((float(k), unq(v)))
                except ValueError:
                    pass
        pairs.sort()
        chosen = None
        for k, v in pairs:
            if k <= scale:
                chosen = v
        if chosen is None and pairs:
            chosen = pairs[0][1]
        result[name] = chosen
    return result


def substitute(text, tokens):
    for name, val in tokens.items():
        if name and val is not None:
            text = text.replace(name, val)
    return text


def class_filter(layer, scale):
    """(aktibo?, where) bueltatzen du. where None bada, iragazkirik ez."""
    classes = layer.kids('class')
    classitem = unq(layer.get('classitem'))
    if not classes:
        return True, None
    active = [c for c in classes if in_range(scale, c)]
    if not active:
        return False, None
    conds = []
    for c in active:
        expr = c.get('expression')
        if not expr:
            return True, None      # espresiorik gabeko klaseak dena onartzen du
        try:
            conds.append(expression_to_sql(expr, classitem))
        except Unsupported as exc:
            warn('geruza "%s": expression ez da itzuli (%s); iragazkirik gabe '
                 'utzi da' % (unq(layer.get('name')), exc))
            return True, None
    return True, ' OR '.join(conds)


def build_entry(layer, mapnode, scale, mapdir, shapepath, args):
    name = unq(layer.get('name'))
    if unq(layer.get('status', 'on')).lower() == 'off':
        return None
    if not in_range(scale, layer):
        return None
    active, where = class_filter(layer, scale)
    if not active:
        return None
    if layer.get('filter'):
        warn('geruza "%s": FILTER ez da kontuan hartu' % name)

    tokens = resolve_scaletokens(layer, scale)
    data = substitute(unq(layer.get('data', '')), tokens)
    ctype = (unq(layer.get('connectiontype', '')) or '').lower()

    if ctype == 'ogr':
        src = substitute(unq(layer.get('connection', '')), tokens)
        table = data
    elif ctype in ('', 'shapefile'):
        path = data
        if not os.path.isabs(path):
            path = os.path.join(shapepath, path)
        if not os.path.splitext(os.path.basename(path))[1]:
            path += args.shp_ext
        src = path
        table = os.path.splitext(os.path.basename(path))[0]
    else:
        warn('geruza "%s": connectiontype "%s" ez da onartzen' % (name, ctype))
        return None

    if not src.startswith(('PG:', 'MySQL:', 'http')) and not os.path.exists(src):
        warn('fitxategia ez dago makina honetan: %s' % src)

    md = metadata_of(layer)
    items_raw = md.get('gml_include_items')
    aliases = {}
    for k, v in md.items():
        m = re.match(r'^gml_(.+)_alias$', k)
        if m:
            aliases[m.group(1).lower()] = v

    items = None
    if items_raw and items_raw.strip().lower() not in ('all', '*'):
        items = [i.strip() for i in items_raw.split(',') if i.strip()]
    elif not items_raw:
        warn('geruza "%s": gml_include_items gabe; eremu guztiak mantendu dira '
             '(MapServer-ek ez luke atributurik idatziko)' % name)

    if items:
        cols = []
        for it in items:
            col = '"%s"' % it
            al = aliases.get(it.lower())
            cols.append('%s AS "%s"' % (col, al) if al else col)
        select = ', '.join(cols)
    else:
        select = '*'

    sql = None
    if select != '*' or where:
        sql = 'SELECT %s FROM "%s"' % (select, table)
        if where:
            sql += ' WHERE ' + where

    srs = epsg_of(layer) or epsg_of(mapnode)
    return {
        'name': name, 'src': src, 'table': table, 'sql': sql, 'srs': srs,
        'encoding': unq(layer.get('encoding')),
    }


# ------------------------------------------------------------------- output

def write_vrt(path, z, scale, entries):
    out = ['<OGRVRTDataSource>',
           '  <!-- zooma %d (eskala ~ 1:%d) -->' % (z, round(scale)), '']
    for e in entries:
        out.append('  <OGRVRTLayer name="%s">' % escape(e['name'], {'"': '&quot;'}))
        out.append('    <SrcDataSource>%s</SrcDataSource>' % escape(e['src']))
        if e['sql']:
            out.append('    <SrcSQL>%s</SrcSQL>' % escape(e['sql']))
        else:
            out.append('    <SrcLayer>%s</SrcLayer>' % escape(e['table']))
        if e['srs']:
            out.append('    <LayerSRS>%s</LayerSRS>' % escape(e['srs']))
        out.append('  </OGRVRTLayer>')
        out.append('')
    out.append('</OGRVRTDataSource>')
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(out) + '\n')


def write_script(path, zooms, prefix, encodings, args):
    enc = ''
    if len(encodings) > 1:
        warn('kodifikazio desberdinak daude (%s); lehenengoa erabili da '
             'make_tiles.sh-n' % ', '.join(sorted(encodings)))
    if encodings:
        enc = ' --config SHAPE_ENCODING %s' % sorted(encodings)[0]

    if args.tms:
        collect = [
            '  local n=$(( (1 << z) - 1 ))',
            '  local f x y',
            '  for f in "$TMP/$z/$z"/*/*.pbf; do',
            '    [ -e "$f" ] || continue',
            '    x=$(basename "$(dirname "$f")"); y=$(basename "$f" .pbf)',
            '    mkdir -p "$OUT/$z/$x"',
            '    cp "$f" "$OUT/$z/$x/$((n - 10#$y)).pbf"',
            '  done',
        ]
    else:
        collect = ['  cp -a "$TMP/$z/$z" "$OUT/"']

    sh = [
        '#!/bin/bash',
        '# map2vrt.py-k sortua.',
        '#',
        '# Erabilera: ./make_tiles.sh [irteera-karpeta] [zoomak]',
        '#   zoomak: zerrenda koma bidez (9,11), tartea marratxoarekin (9-11)',
        '#           edo biak nahastuta (9-11,15). Lehenetsia: %d-%d' % (zooms[0], zooms[-1]),
        '#   Adibideak:',
        '#     ./make_tiles.sh teselak 9,11     -> 9 eta 11',
        '#     ./make_tiles.sh teselak 9-11     -> 9, 10 eta 11',
        'set -e',
        '',
        'OGR2OGR="%s"' % args.ogr2ogr,
        'AQUI="$(cd "$(dirname "$0")" && pwd)"',
        'OUT="${1:-teselak}"',
        'ZOOMS_ARG="${2:-%d-%d}"' % (zooms[0], zooms[-1]),
        'TMP="${OUT}_tmp"',
        '',
        '# Mezu guztiak orduarekin hasten dira: [HH:MM:SS]',
        'log() { echo "[$(date +%H:%M:%S)] $*"; }',
        '',
        'log "== Hasiera (zoomak: $ZOOMS_ARG) =="',
        '',
        '# Zoomen zerrenda aztertu',
        'ZOOMS=()',
        'IFS=\',\' read -ra PARTS <<< "$ZOOMS_ARG"',
        'for p in "${PARTS[@]}"; do',
        '  p="${p// /}"',
        '  if [[ "$p" =~ ^([0-9]+)-([0-9]+)$ ]]; then',
        '    a=$((10#${BASH_REMATCH[1]})); b=$((10#${BASH_REMATCH[2]}))',
        '    for ((i = a; i <= b; i++)); do ZOOMS+=("$i"); done',
        '  elif [[ "$p" =~ ^[0-9]+$ ]]; then',
        '    ZOOMS+=("$((10#$p))")',
        '  else',
        '    log "Zoom zerrenda okerra: \'$p\' (adibideak: 9,11 | 9-11 | 9-11,15)" >&2',
        '    exit 1',
        '  fi',
        'done',
        '',
        'make_zoom() {',
        '  local z=$1',
        '  local vrt',
        '  vrt="$(printf \'%s/' + prefix + '_z%02d.vrt\' "$AQUI" "$z")"',
        '  if [ ! -f "$vrt" ]; then',
        '    log "== zooma $z: ez dago VRT-rik, saltatu da =="',
        '    return',
        '  fi',
        '  log "== zooma $z =="',
        '  rm -rf "$TMP/$z"',
        '  "$OGR2OGR" -f MVT%s "$TMP/$z" "$vrt" -dsco FORMAT=DIRECTORY \\' % enc,
        '    -dsco MINZOOM="$z" -dsco MAXZOOM="$z" -dsco EXTENT=%d -dsco BUFFER=%d \\' % (args.extent, args.buffer),
        '    -dsco COMPRESS=NO',
    ] + collect + [
        '}',
        '',
        'rm -rf "$TMP"',
        'mkdir -p "$TMP" "$OUT"',
        'for z in "${ZOOMS[@]}"; do',
        '  make_zoom "$z"',
        'done',
        'rm -rf "$TMP"',
        'log "== Amaiera: $OUT =="',
    ]
    with io.open(path, 'w', encoding='utf-8') as fh:
        fh.write('\n'.join(sh) + '\n')
    os.chmod(path, 0o755)


def main():
    ap = argparse.ArgumentParser(
        description='MAP fitxategitik zoom bakoitzerako OGR VRT fitxategiak sortzen ditu.')
    ap.add_argument('mapfile', help='MapServer MAP fitxategia')
    ap.add_argument('-o', '--outdir', default='vrt', help='irteera-karpeta (lehenetsia: vrt)')
    ap.add_argument('--zmin', type=int, default=9)
    ap.add_argument('--zmax', type=int, default=23)
    ap.add_argument('--prefix', default=None,
                    help='VRT fitxategien aurrizkia (lehenetsia: MAP fitxategiaren izena)')
    ap.add_argument('--shp-ext', default='.shp',
                    help='extentsiorik gabeko DATA-ri gehituko zaiona (lehenetsia: .shp)')
    ap.add_argument('--extent', type=int, default=4096, help='MVT EXTENT (lehenetsia: 4096)')
    ap.add_argument('--buffer', type=int, default=80, help='MVT BUFFER (lehenetsia: 80)')
    ap.add_argument('--ogr2ogr', default='/usr/local/bin/ogr2ogr',
                    help='ogr2ogr-ren bide osoa make_tiles.sh-n (lehenetsia: /usr/local/bin/ogr2ogr)')
    ap.add_argument('--tms', action='store_true',
                    help='make_tiles.sh-k Y ardatza alderantzikatuko du (TMS)')
    ap.add_argument('--scale-z0', type=float, default=SCALE_Z0,
                    help='0. zoomeko eskala-izendatzailea (lehenetsia: %.4f)' % SCALE_Z0)
    args = ap.parse_args()

    mapnode = parse_map(args.mapfile)
    mapdir = os.path.dirname(os.path.abspath(args.mapfile))
    shapepath = unq(mapnode.get('shapepath', '')) or ''
    if shapepath and not os.path.isabs(shapepath):
        shapepath = os.path.join(mapdir, shapepath)
    prefix = args.prefix or os.path.splitext(os.path.basename(args.mapfile))[0]
    layers = mapnode.kids('layer')
    os.makedirs(args.outdir, exist_ok=True)

    zooms, vrtnames, encodings = [], [], set()
    print('%-5s %-12s %s' % ('Zoom', 'Eskala', 'Geruzak'))
    for z in range(args.zmin, args.zmax + 1):
        scale = args.scale_z0 / (2 ** z)
        entries = []
        for layer in layers:
            e = build_entry(layer, mapnode, scale, mapdir, shapepath, args)
            if e:
                entries.append(e)
                if e['encoding']:
                    encodings.add(e['encoding'])
        if not entries:
            print('%-5d 1:%-10d (geruzarik ez)' % (z, round(scale)))
            continue
        vrt = '%s_z%02d.vrt' % (prefix, z)
        write_vrt(os.path.join(args.outdir, vrt), z, scale, entries)
        zooms.append(z)
        vrtnames.append(vrt)
        print('%-5d 1:%-10d %d  %s' % (z, round(scale), len(entries),
                                       ', '.join(e['name'] for e in entries)))
    write_script(os.path.join(args.outdir, 'make_tiles.sh'), zooms, prefix, encodings, args)
    print('\nSortuta: %d VRT fitxategi + make_tiles.sh -> %s' % (len(zooms), args.outdir))


if __name__ == '__main__':
    main()
