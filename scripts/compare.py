#!/usr/bin/env python3

from typing import NamedTuple, List, Set, Tuple

class Visit(NamedTuple):
    when: str
    tags: Tuple[str]

def vdiff(a: Set, b: Set):
    if a is None:
        a = set()
    if b is None:
        b = set()
    # if a is None:
    #     return (None, b)
    # if b is None:
    #     return (a, None)
    return a.difference(b), b.difference(a)

def compare(old, new, ignore_new=False):
    o = old
    n = new
    all_keys = set(o.keys()).union(n.keys())

    incr = []
    decr = []

    def getv(x, u):
        r = x.get(u, None)
        if r is None:
            return None
        vis = r[0]
        res = set()
        for v in vis:
            res.add(Visit(v[0], tuple(v[1])))
        return res


    for k in all_keys:
        vo = getv(o, k)
        vn = getv(n, k)
        onotn, nnoto = vdiff(vo, vn)
        if len(onotn) == 0 and len(nnoto) == 0:
            continue
        if len(nnoto) > 0 and ignore_new:
            # print(f'ignoring new {k}') # TODO FIXME
            continue
        errs = []
        errs.append(f"ERROR: {k}")
        if len(onotn) > 0:
            errs.append(f'    old only {onotn}')
        if len(nnoto) > 0:
            errs.append(f'    new only {nnoto}')
        print('\n'.join(errs))
        # if vo != vn:
        #     print(f'ERROR: difference at {k}: {vo} vs {vn}')
            # ll = f"{v1:3d} {v2:3d} {k}"
            # if v1 < v2:
            #     incr.append(ll)
            # else:
            #     decr.append(ll)

    print("---------INCREASED")
    for ll in incr:
        print(ll)


    print("---------DECREASED")
    for ll in decr:
        print(ll)

def load_visits(p):
    import json
    from pathlib import Path
    return json.loads(Path(p).read_text())

def main():
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument('--old', required=True)
    p.add_argument('--new', required=True)
    p.add_argument('--ignore-new', action='store_true', help="do not report items that weren't present in old links database")
    args = p.parse_args()
    vold = load_visits(args.old)
    vnew = load_visits(args.new)
    compare(old=vold, new=vnew, ignore_new=args.ignore_new)



if __name__ == '__main__':
    main()