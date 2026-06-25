#!/usr/bin/env python3
"""
Generátor dashboardu Prostavěnost RD Kunín.
Čte data/prostavenost.json (jediný zdroj pravdy) a píše konstanty AUTH / D_A / D_Z
do public/index.html (mezi `const AUTH=` a `const SKEY=`). Veškerý React/UI kód zůstává beze změny.

Použití:
  python3 generators/gen_dashboard.py \
      --data data/prostavenost.json \
      --html prostavenost-Kunin/public/index.html
"""
import json, argparse, sys, re

def jstr(s):
    return '"' + str(s).replace('\\','\\\\').replace('"','\\"') + '"'

def jnum(x):
    if isinstance(x,bool): return 'true' if x else 'false'
    if x is None: return '0'
    f=float(x)
    if f.is_integer(): return str(int(f))
    s=f"{f:.2f}".rstrip('0').rstrip('.')
    return s

def jarr_num(a): return '['+', '.join(jnum(v) for v in a)+']'

def ser_auth(A):
    bo=','.join(f'{jstr(k)}:{{budget:{jnum(v["budget"])},p:{jarr_num(v["p"])}}}' for k,v in A['byObj'].items())
    return ('const AUTH={budget:'+jnum(A['budget'])
            +',periods:['+', '.join(jstr(p) for p in A['periods'])+']'
            +',totP:'+jarr_num(A['totP'])
            +',cum:'+jnum(A['cum'])
            +',byObj:{'+bo+'}};')

def ser_active(items):
    rows=[f'{{s:{jstr(it["s"])},d:{jstr(it["d"])},b:{jnum(it["b"])},p:{jarr_num(it["p"])},st:{jstr(it["st"])}}}' for it in items]
    return 'const D_A=[\n'+',\n'.join(rows)+'\n];'

def ser_zero(items):
    rows=[f'{{s:{jstr(it["s"])},d:{jstr(it["d"])},b:{jnum(it["b"])}}}' for it in items]
    return 'const D_Z=[\n'+',\n'.join(rows)+'\n];'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--data',required=True)
    ap.add_argument('--html',required=True)
    ap.add_argument('--out',default=None,help='výstup (default = přepíše --html)')
    a=ap.parse_args()
    src=json.load(open(a.data,encoding='utf-8'))
    AUTH=src['auth']; D_A=src['items_active']; D_Z=src['items_zero']

    html=open(a.html,encoding='utf-8').read()
    i=html.find('const AUTH=')
    j=html.find('const SKEY=')
    if i<0 or j<0 or j<i:
        sys.exit('CHYBA: kotvy const AUTH= / const SKEY= nenalezeny — nic nezapisuji.')
    block=ser_auth(AUTH)+'\n'+ser_active(D_A)+'\n'+ser_zero(D_Z)+'\n'
    new=html[:i]+block+html[j:]
    out=a.out or a.html
    open(out,'w',encoding='utf-8').write(new)
    # report
    NP=len(AUTH['periods'])
    dsum=[round(sum((it['p'][p] or 0) for it in D_A)) for p in range(NP)]
    print(f"OK → {out}")
    print(f"  období: {AUTH['periods']}")
    print(f"  Dashboard totP: {AUTH['totP']}  cum={AUTH['cum']}")
    print(f"  Detail sumy:    {dsum}")
    for p in range(NP):
        g=dsum[p]-AUTH['totP'][p]
        tag='' if g==0 else (f'  (rozdíl {g:+} = nefakturované vícepráce)' if g>0 else f'  (!!! {g:+})')
        print(f"   P{p+1} {AUTH['periods'][p]:>10}: detail {dsum[p]:>9} vs fakturováno {AUTH['totP'][p]:>9}{tag}")
    print(f"  položek: {len(D_A)+len(D_Z)} (aktivní {len(D_A)} + nezahájené {len(D_Z)})")

if __name__=='__main__':
    main()
