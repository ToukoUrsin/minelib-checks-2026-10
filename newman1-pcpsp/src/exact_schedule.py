"""Check an ASCII schedule against original data using exact rational arithmetic.

Optional export repair changes only decimal serialization residuals in destination
totals (<=1e-8); no extraction period, mined block, or meaningful fraction changes.
The repaired schedule is then independently checked, without solver matrices.
"""
import argparse
from collections import defaultdict
from fractions import Fraction as F
import hashlib
import json
from pathlib import Path

def check_exact(model,prec,solution,repair_output=None):
    h={};s={};section=None
    for line in Path(model).read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('%') or line=='EOF':continue
        if ':' in line:
            key,v=map(str.strip,line.split(':',1))
            if v:h[key]=v;section=None
            else:section=key;s[key]=[]
        else:s[section].append(line.split())
    n,T,D,R=map(int,[h['NBLOCKS'],h['NPERIODS'],h.get('NDESTINATIONS','1'),h['NRESOURCE_SIDE_CONSTRAINTS']])
    assert int(h.get('NGENERAL_SIDE_CONSTRAINTS','0'))==0
    pcpsp=h['TYPE']=='PCPSP';rate=F(h['DISCOUNT_RATE'])
    values={};groups=defaultdict(list);repairs=[]
    for line in Path(solution).read_text().splitlines():
        if not line.strip():continue
        b,d,t,v=line.split();key=(int(b),int(d),int(t));value=F(v)
        assert key not in values and 0<=key[0]<n and 0<=key[1]<D and 0<=key[2]<T
        values[key]=value;groups[key[0],key[2]].append(key)
    if repair_output:
        for (b,t),keys in groups.items():
            total=sum(values[key] for key in keys);target=round(total)
            assert target in [0,1] and abs(total-target)<=F('0.00000001')
            if total!=target:
                key=max(keys,key=lambda key:values[key]);change=F(target)-total
                values[key]+=change
                repairs.append({'key':key,'change':str(change)})
        # Decimal export remains exact because all fractions originated as decimals.
        from decimal import Decimal,localcontext
        with localcontext() as ctx:
            ctx.prec=100
            Path(repair_output).write_text(''.join(f'{b} {d} {t} '+str(Decimal(v.numerator)/Decimal(v.denominator))+'\n'
                for (b,d,t),v in sorted(values.items()) if v))
        return {'repairs':repairs,'post_repair_check':check_exact(model,prec,repair_output)}
    extraction=[[F(0)]*T for _ in range(n)];usage=[[F(0)]*T for _ in range(R)]
    profit={int(row[0]):list(map(F,row[1:])) for row in s['OBJECTIVE_FUNCTION']};q={}
    for row in s['RESOURCE_CONSTRAINT_COEFFICIENTS']:
        if pcpsp:b,d,r=map(int,row[:3]);v=F(row[3])
        else:b,r=map(int,row[:2]);d=0;v=F(row[2])
        q[b,d,r]=v
    objective=F(0);violations=[]
    for (b,d,t),v in values.items():
        if not 0<=v<=1:violations.append(['fraction',b,d,t,str(v)])
        extraction[b][t]+=v
        objective+=profit[b][d]*v/(1+rate)**t
        for r in range(R):usage[r][t]+=q.get((b,d,r),F(0))*v
    cumulative=[]
    for b in range(n):
        if any(v not in [0,1] for v in extraction[b]):violations.append(['integer_extraction',b])
        if sum(extraction[b])>1:violations.append(['at_most_once',b])
        c=[];v=F(0)
        for amount in extraction[b]:v+=amount;c.append(v)
        cumulative.append(c)
    for line in Path(prec).read_text().splitlines():
        if not line.strip() or line.lstrip().startswith('%'):continue
        b,count,*parents=map(int,line.split());assert count==len(parents)
        for p in parents:
            for t in range(T):
                if cumulative[b][t]>cumulative[p][t]:violations.append(['precedence',b,p,t])
    for row in s['RESOURCE_CONSTRAINT_LIMITS']:
        r,t=int(row[0]),int(row[1]);sense=row[2];v=F(row[3]);used=usage[r][t]
        if ((sense=='L' and used>v) or (sense=='G' and used<v) or
            (sense=='I' and not v<=used<=F(row[4]))):violations.append(['resource',r,t,str(used)])
    unit=10**6;v=objective*unit;floor=v.numerator//v.denominator
    return {'passes':not violations,'scope':'exact integer extraction, rational destinations, original input coefficients',
        'objective_numerator':str(objective.numerator),'objective_denominator':str(objective.denominator),
        'objective_downward_rounded':f'{floor//unit}.{floor%unit:06d}',
        'resource_usage_exact':[[str(v) for v in row] for row in usage],
        'nonzero_allocations':len(values),'violations':violations[:20],
        'model_sha256':hashlib.sha256(Path(model).read_bytes()).hexdigest(),
        'precedence_sha256':hashlib.sha256(Path(prec).read_bytes()).hexdigest(),
        'solution_sha256':hashlib.sha256(Path(solution).read_bytes()).hexdigest()}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('model');p.add_argument('prec');p.add_argument('solution')
    p.add_argument('--repair-output');p.add_argument('--out',required=True);a=p.parse_args()
    r=check_exact(a.model,a.prec,a.solution,a.repair_output)
    Path(a.out).write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
    raise SystemExit(0 if r.get('post_repair_check',r)['passes'] else 1)
