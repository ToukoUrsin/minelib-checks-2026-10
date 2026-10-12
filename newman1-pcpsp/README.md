# Newman1 PCPSP feasible schedule: 24,176,864.82

Run `python3 smoke.py` here (Python standard library only).

`candidate.sol` (block, destination, period, fraction; zero-based): 1,059 blocks, each sent wholly to one
destination. Exact objective 1762493445729739 / 72900000 = 24,176,864.824825, checked against the original
`newman1.pcpsp` / `newman1.prec` (identical to https://minelib.org/v1/data/ on 12 Oct 2026) with the official
`pcpsp.mod` semantics. The MineLib incumbent (`incumbent.sol`, 23,658,229.88) is checked the same way, a
missing-predecessor negative is rejected, and an exact LP certificate gives <= 24,486,549.021618.

Comparators: the MineLib table lists 23,658,230; Jelvez et al., MPES 2018, Table 4 report 24,176,861 (OPBSP), so
this schedule is only 3.82 above that published value. Integer optimality is not claimed.
