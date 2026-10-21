#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
vt_fix_mvt_orientation.py

MapServer-ek sortutako MVT teselen (PBF) poligonoetan, batzuetan lehen
eraztuna (kanpo-eraztuna) alderantzizko orientazioan idazten da. MVT
espezifikazioaren arabera kanpo-eraztunek azalera zeinuduna positiboa izan
behar dute (tesela-koordenatuetan, Y behera), eta zuloek negatiboa.

Script honek poligono-elementu bakoitzean lehen eraztunaren azalera negatiboa
bada, eraztun hori bakarrik alderantzikatzen du. Gainerakoa (zuloak, beste
elementuak, atributuak, geruzak) byte-mailan ukitu gabe uzten da.

Erabilera:
  python3 vt_fix_mvt_orientation.py tesela.pbf -o zuzenduta/
  python3 vt_fix_mvt_orientation.py karpeta/ --inplace
  python3 vt_fix_mvt_orientation.py karpeta/ -n          # probatu, ez idatzi

Fitxategiak gzip-ekin konprimatuta badaude, konprimatuta mantentzen dira.
Python 3.6+ (kanpoko libururik gabe).
"""

import argparse
import gzip
import os
import sys

POLYGON = 3


# --------------------------------------------------------------- protobuf

def read_varint(b, i):
    r = 0
    s = 0
    while True:
        c = b[i]
        i += 1
        r |= (c & 0x7f) << s
        s += 7
        if not c & 0x80:
            return r, i


def write_varint(v):
    out = bytearray()
    while True:
        c = v & 0x7f
        v >>= 7
        if v:
            out.append(c | 0x80)
        else:
            out.append(c)
            return bytes(out)


def parse(b):
    """(eremua, wire, balioa) zerrenda, jatorrizko ordenean."""
    i = 0
    out = []
    while i < len(b):
        k, i = read_varint(b, i)
        f, w = k >> 3, k & 7
        if w == 0:
            v, i = read_varint(b, i)
        elif w == 2:
            n, i = read_varint(b, i)
            v = b[i:i + n]
            i += n
        elif w == 1:
            v = b[i:i + 8]
            i += 8
        elif w == 5:
            v = b[i:i + 4]
            i += 4
        else:
            raise ValueError('wire type ezezaguna: %d' % w)
        out.append((f, w, v))
    return out


def serialize(fields):
    out = bytearray()
    for f, w, v in fields:
        out += write_varint((f << 3) | w)
        if w == 0:
            out += write_varint(v)
        elif w == 2:
            out += write_varint(len(v))
            out += v
        else:
            out += v
    return bytes(out)


def unpack_varints(b):
    i = 0
    out = []
    while i < len(b):
        v, i = read_varint(b, i)
        out.append(v)
    return out


def pack_varints(vals):
    return b''.join(write_varint(v) for v in vals)


def zigzag(n):
    return (n << 1) ^ (n >> 63) if n < 0 else n << 1


def unzigzag(n):
    return (n >> 1) ^ -(n & 1)


# --------------------------------------------------------------- geometria

def decode_rings(cmds):
    """MVT geometria-komandoak -> eraztunen zerrenda (puntu absolutuak)."""
    rings = []
    cur = None
    x = y = 0
    i = 0
    while i < len(cmds):
        c = cmds[i]
        i += 1
        cmd, cnt = c & 7, c >> 3
        if cmd == 1:
            for _ in range(cnt):
                x += unzigzag(cmds[i])
                y += unzigzag(cmds[i + 1])
                i += 2
                cur = [(x, y)]
                rings.append(cur)
        elif cmd == 2:
            for _ in range(cnt):
                x += unzigzag(cmds[i])
                y += unzigzag(cmds[i + 1])
                i += 2
                cur.append((x, y))
        elif cmd == 7:
            pass
        else:
            raise ValueError('komando ezezaguna: %d' % cmd)
    return rings


def encode_rings(rings):
    out = []
    x = y = 0
    for ring in rings:
        out.append((1 & 7) | (1 << 3))
        px, py = ring[0]
        out += [zigzag(px - x), zigzag(py - y)]
        x, y = px, py
        if len(ring) > 1:
            out.append(2 | ((len(ring) - 1) << 3))
            for px, py in ring[1:]:
                out += [zigzag(px - x), zigzag(py - y)]
                x, y = px, py
        out.append(7 | (1 << 3))
    return out


def signed_area2(ring):
    s = 0
    n = len(ring)
    for k in range(n):
        x0, y0 = ring[k]
        x1, y1 = ring[(k + 1) % n]
        s += x0 * y1 - x1 * y0
    return s


# ------------------------------------------------------------------- tesela

def fix_feature(fbytes):
    """(bytes berriak, zuzendu al den) bueltatzen du."""
    fields = parse(fbytes)
    ftype = None
    gi = None
    for idx, (f, w, v) in enumerate(fields):
        if f == 3 and w == 0:
            ftype = v
        elif f == 4 and w == 2:
            gi = idx
    if ftype != POLYGON or gi is None:
        return fbytes, False
    rings = decode_rings(unpack_varints(fields[gi][2]))
    if not rings or signed_area2(rings[0]) >= 0:
        return fbytes, False
    rings[0] = rings[0][::-1]
    fields[gi] = (4, 2, pack_varints(encode_rings(rings)))
    return serialize(fields), True


def fix_tile(data):
    """(tesela berria, poligono kopurua, zuzendutakoak) bueltatzen du."""
    top = parse(data)
    npoly = 0
    nfixed = 0
    out = []
    for f, w, v in top:
        if f == 3 and w == 2:
            lf = parse(v)
            new = []
            for f2, w2, v2 in lf:
                if f2 == 2 and w2 == 2:
                    nb, fixed = fix_feature(v2)
                    nfixed += 1 if fixed else 0
                    new.append((f2, w2, nb))
                else:
                    new.append((f2, w2, v2))
            out.append((f, w, serialize(new)))
        else:
            out.append((f, w, v))
    for f, w, v in top:
        if f == 3 and w == 2:
            for f2, w2, v2 in parse(v):
                if f2 == 2 and w2 == 2:
                    for f3, w3, v3 in parse(v2):
                        if f3 == 3 and w3 == 0 and v3 == POLYGON:
                            npoly += 1
    return serialize(out), npoly, nfixed


def process_file(src, dst, dry):
    with open(src, 'rb') as fh:
        raw = fh.read()
    gz = raw[:2] == b'\x1f\x8b'
    data = gzip.decompress(raw) if gz else raw
    new, npoly, nfixed = fix_tile(data)
    if nfixed and not dry:
        out = gzip.compress(new, 6) if gz else new
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        tmp = dst + '.tmp'
        with open(tmp, 'wb') as fh:
            fh.write(out)
        os.replace(tmp, dst)
    elif not nfixed and dst != src and not dry:
        os.makedirs(os.path.dirname(os.path.abspath(dst)), exist_ok=True)
        with open(dst, 'wb') as fh:
            fh.write(raw)
    return npoly, nfixed


def iter_inputs(paths):
    for p in paths:
        if os.path.isdir(p):
            for root, _, files in os.walk(p):
                for name in sorted(files):
                    if name.lower().endswith(('.pbf', '.mvt')):
                        full = os.path.join(root, name)
                        yield full, os.path.relpath(full, p)
        else:
            yield p, os.path.basename(p)


def main():
    ap = argparse.ArgumentParser(
        description='MVT teselen poligonoen kanpo-eraztunen orientazioa zuzentzen du.')
    ap.add_argument('inputs', nargs='+', help='PBF fitxategiak edo karpetak (errekurtsiboki)')
    g = ap.add_mutually_exclusive_group()
    g.add_argument('-o', '--outdir', help='zuzendutako teselak karpeta honetan idatzi')
    g.add_argument('--inplace', action='store_true', help='fitxategiak bertan ordezkatu')
    ap.add_argument('-n', '--dry-run', action='store_true',
                    help='ez idatzi ezer; zenbat zuzenduko liratekeen bakarrik erakutsi')
    ap.add_argument('-q', '--quiet', action='store_true', help='fitxategi bakoitzaren lerroa ez erakutsi')
    args = ap.parse_args()
    if not (args.outdir or args.inplace or args.dry_run):
        ap.error('-o, --inplace edo -n behar da')

    files = fixed_files = fixed_feats = 0
    for src, rel in iter_inputs(args.inputs):
        dst = src if args.inplace else (os.path.join(args.outdir, rel) if args.outdir else src)
        try:
            npoly, nfixed = process_file(src, dst, args.dry_run)
        except Exception as exc:   # noqa
            sys.stderr.write('ERROREA %s: %s\n' % (src, exc))
            continue
        files += 1
        if nfixed:
            fixed_files += 1
            fixed_feats += nfixed
            if not args.quiet:
                print('%s: %d poligono-elementu zuzendu dira (%d poligono guztira)' % (src, nfixed, npoly))
    print('Eginda: %d fitxategi aztertu, %d zuzendu, %d elementu zuzendu%s.' % (
        files, fixed_files, fixed_feats, ' (dry-run)' if args.dry_run else ''))


if __name__ == '__main__':
    main()
