# MineLib checks (October 2026)

Exact, standard-library checkers against the current MineLib input files.

- `cpit-lp/`: KD and Marvin CPIT LP. Feasible LP points exceed the LP upper bounds on the results page
  (KD +13,064, Marvin +18,374). An exact dual certificate puts the KD LP within 0.06 of its point.
- `newman1-pcpsp/`: Newman1 PCPSP feasible schedule 24,176,864.82 (table: 23,658,230; MPES 2018: 24,176,861).
- `kd-cpit-schedule/`: KD CPIT integer schedule 409,106,631.55. It is a one-move improvement (+115) of the public
  schedule at https://github.com/douglasmazzinghy/2026-MME (409,106,516.43) and is 2,506.73 above the
  409,104,124.828 reported by Elsayed et al., Information Sciences 523 (2020), Table 2. `python3 check.py` in that dir.

Touko Ursin
