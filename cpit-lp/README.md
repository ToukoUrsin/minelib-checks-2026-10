# KD and Marvin CPIT LP: feasible LP points above the published LP upper bounds

Run `python3 smoke.py` here (Python standard library only, ~10 s).

Inputs are the current MineLib files (`kd.cpit`, `kd.prec`, `marvin.cpit`, `marvin.prec`, identical to
https://minelib.org/v1/data/ on 12 Oct 2026). Semantics follow the official `cpit.mod` (included):
same-period precedence allowed, at most one extraction per block, first period undiscounted.

| Instance | Published CPIT LP upper bound | Exact feasible LP point (this packet) | Exact LP upper bound (dual certificate) |
|---|---|---|---|
| KD | 409,498,555 | >= 409,511,619.214132 | <= 409,511,619.267333 |
| Marvin | 863,916,131 | >= 863,934,504.905759 | <= 863,934,505.094970 |

The primal points are fractional LP solutions, checked with exact rationals against every original precedence
arc, resource row and bound. `negative.sol` (predecessor allocations erased) is rejected.
`python3 smoke.py --with-kd-dual` also checks the KD dual certificate.
