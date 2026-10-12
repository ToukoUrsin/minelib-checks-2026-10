"""Exact rational upper bound for the original MineLib LP.

For any row weights w with finite selected bounds, c*x <=
sum(w_i * selected_bound_i) + sum(max(0, c_j - (A^T w)_j))
for 0 <= x <= 1. Every coefficient is reparsed as an exact Fraction from
the original ASCII files; no optimizer, numpy, or floating point arithmetic.
This checks an upper bound, not LP optimality or an integer solution.
"""
import argparse
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path
import re

def validate(model, prec, certificate, claimed=None):
    header={}; sections={}; current=None
    for line in Path(model).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('%') or line=='EOF':continue
        if ':' in line:
            key,value=map(str.strip,line.split(':',1))
            if value:header[key]=value;current=None
            else:current=key;sections[current]=[]
        else:sections[current].append(re.split(r'[\s:]+',line))
    assert int(header.get('NGENERAL_SIDE_CONSTRAINTS','0'))==0
    n,T,D,R=(int(header['NBLOCKS']),int(header['NPERIODS']),
        int(header.get('NDESTINATIONS','1')),int(header['NRESOURCE_SIDE_CONSTRAINTS']))
    is_pcpsp=header['TYPE']=='PCPSP';nz=n*T
    nv=nz+n*D*T if is_pcpsp else nz
    z=lambda b,t:b*T+t
    y=lambda b,d,t:nz+(b*D+d)*T+t
    discount=[(1+F(header['DISCOUNT_RATE']))**(-t) for t in range(T)]
    residual=[F(0)]*nv
    for row in sections['OBJECTIVE_FUNCTION']:
        b=int(row[0])
        if is_pcpsp:
            for d in range(D):
                for t in range(T):residual[y(b,d,t)]=F(row[d+1])*discount[t]
        else:
            for t in range(T):residual[z(b,t)]=F(row[1])*(discount[t]-(discount[t+1] if t<T-1 else 0))
    arcs=set()
    for row in Path(prec).read_text().splitlines():
        if not row.strip() or row.lstrip().startswith('%'):continue
        b,count,*pred=map(int,row.split());assert count==len(pred)
        arcs.update((b,p) for p in pred)
    limits={}
    for row in sections['RESOURCE_CONSTRAINT_LIMITS']:
        r,t=int(row[0]),int(row[1]);sense=row[2];lo=hi=None
        if sense=='L':hi=F(row[3])
        elif sense=='G':lo=F(row[3])
        elif sense=='I':lo,hi=F(row[3]),F(row[4])
        else:raise ValueError(sense)
        limits[r,t]=(lo,hi)
    resource={r:[] for r in range(R)}
    for row in sections['RESOURCE_CONSTRAINT_COEFFICIENTS']:
        if is_pcpsp:b,d,r=map(int,row[:3]);value=F(row[3])
        else:b,r=map(int,row[:2]);d=0;value=F(row[2])
        resource[r].append((b,d,value))
    cert=json.loads(Path(certificate).read_text())
    assert cert['model_sha256']==hashlib.sha256(Path(model).read_bytes()).hexdigest()
    assert cert['precedence_sha256']==hashlib.sha256(Path(prec).read_bytes()).hexdigest()
    total=F(0)
    for entry in cert['weights']:
        tag,*fields,weight=entry;w=F(weight)
        if tag=='m':
            b,t=fields;assert 0<=b<n and 1<=t<T and w>=0
            residual[z(b,t-1)]-=w;residual[z(b,t)]+=w
        elif tag=='p':
            b,p,t=fields;assert (b,p) in arcs and 0<=t<T and w>=0
            residual[z(b,t)]-=w;residual[z(p,t)]+=w
        elif tag=='l':
            b,t=fields;assert is_pcpsp and 0<=b<n and 0<=t<T
            residual[z(b,t)]+=w
            if t:residual[z(b,t-1)]-=w
            for d in range(D):residual[y(b,d,t)]-=w
        elif tag=='r':
            r,t=fields;assert (r,t) in limits
            lo,hi=limits[r,t];selected=hi if w>=0 else lo
            assert selected is not None,'Multiplier selects an infinite bound'
            total+=w*selected
            for b,d,value in resource[r]:
                if is_pcpsp:residual[y(b,d,t)]-=w*value
                else:
                    residual[z(b,t)]-=w*value
                    if t:residual[z(b,t-1)]+=w*value
        else:raise ValueError(tag)
    total+=sum(v for v in residual if v>0)
    # Round upward to a micro-unit for a short, still rigorous bound.
    unit=10**6;scaled=total*unit;ceiling=-(-scaled.numerator//scaled.denominator)
    text=f'{ceiling//unit}.{ceiling%unit:06d}'
    passes=claimed is None or total<=F(str(claimed))
    return {'passes':passes,'upper_bound_upward_rounded':text,
        'exact_upper_bound_numerator':str(total.numerator),
        'exact_upper_bound_denominator':str(total.denominator),
        'claimed_upper_bound':claimed,'variables':nv,'nonzero_row_weights':len(cert['weights']),
        'scope':'exact rational bound for original CPIT/PCPSP LP (therefore also integer extraction)',
        'model_sha256':cert['model_sha256'],'precedence_sha256':cert['precedence_sha256']}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('prec');p.add_argument('certificate')
    p.add_argument('--claimed-upper-bound');a=p.parse_args()
    result=validate(a.model,a.prec,a.certificate,a.claimed_upper_bound)
    print(json.dumps(result,indent=2));raise SystemExit(0 if result['passes'] else 1)
