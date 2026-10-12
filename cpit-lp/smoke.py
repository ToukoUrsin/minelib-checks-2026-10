import sys,json
sys.path.insert(0,'src')
from exact_schedule import check_exact
from certificate_check import validate
from fractions import Fraction as F
out={}
for name,reported in [('kd',409498555),('marvin',863916131)]:
 c=check_exact('inputs/'+name+'.cpit','inputs/'+name+'.prec','primal/'+name+'.sol',relaxation=True)
 assert c['passes']
 assert F(int(c['objective_numerator']),int(c['objective_denominator']))>reported
 out[name]={'primal':c,'published_lp_upper_bound_counterexample':True}
bad=check_exact('inputs/kd.cpit','inputs/kd.prec','negative.sol',relaxation=True)
assert not bad['passes'] and any(r[0]=='precedence' for r in bad['violations'])
out['precedence_negative_rejected']=not bad['passes']
print(json.dumps(out,indent=2))
if '--with-kd-dual' in sys.argv:
 b=validate('inputs/kd.cpit','inputs/kd.prec','dual/kd.json','409511619.267333')
 assert b['passes']
 print(json.dumps({'optional_kd_upper_bound':b},indent=2))
