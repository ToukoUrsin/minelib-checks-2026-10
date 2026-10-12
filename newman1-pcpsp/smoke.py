from pathlib import Path
import json,sys
sys.path.insert(0,str(Path(__file__).parent/'src'))
from exact_schedule import check_exact
from certificate_check import validate
model='inputs/newman1.pcpsp';prec='inputs/newman1.prec'
candidate=check_exact(model,prec,'candidate.sol')
incumbent=check_exact(model,prec,'incumbent.sol')
negative=check_exact(model,prec,'negative-missing-predecessor.sol')
bound=validate(model,prec,'lp-certificate.json','24486549.021618')
bad_bound=validate(model,prec,'lp-certificate.json','24486548.021618')
assert candidate['passes'] and incumbent['passes']
assert candidate['objective_numerator']=='1762493445729739'
assert candidate['objective_denominator']=='72900000'
assert not negative['passes'] and any(v[0]=='precedence' for v in negative['violations'])
assert bound['passes'] and not bad_bound['passes']
print(json.dumps(dict(candidate=candidate,incumbent=incumbent,
negative_control=negative,bound=bound,bad_bound_rejected=not bad_bound['passes']),indent=2))
