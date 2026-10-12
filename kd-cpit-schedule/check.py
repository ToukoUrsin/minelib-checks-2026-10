# Exact check of the KD CPIT schedule against the original MineLib inputs (Python stdlib only).
# Run from this directory: python3 check.py
import sys, json
sys.path.insert(0, '../cpit-lp/src')
from exact_schedule import check_exact
ok = check_exact('../cpit-lp/inputs/kd.cpit', '../cpit-lp/inputs/kd.prec', 'kd-cpit-409106631.sol')
neg = check_exact('../cpit-lp/inputs/kd.cpit', '../cpit-lp/inputs/kd.prec', 'negative-missing-predecessor.sol')
assert ok['passes'] and not neg['passes']
print(json.dumps({'passes': ok['passes'], 'objective': ok['objective_downward_rounded'], 'negative_rejected': not neg['passes']}, indent=2))
