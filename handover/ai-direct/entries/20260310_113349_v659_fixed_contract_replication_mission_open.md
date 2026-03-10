# V659 Fixed-Contract Replication Mission Open

Status: Mission-open authority
Date: 2026-03-10 11:33 UTC
Mission: V659 Fixed-Contract Replication Audit

## Owner-confirmed direction

The owner confirmed execution of V659 after the draft and Gemini spec audit passed.

V659 is now the active mission.

## Single allowed change axis

Change only the evaluation sample:

- from the H1 2023 selection slice used in V657 / V658
- to the first non-overlapping contiguous replication block under the same frozen forge and sign-aware threshold semantics

## Frozen contract

Keep fixed:

- signal:
  - `dPsiAmpE_10d`
- side:
  - `negative`
- thresholds:
  - `90`
  - `95`
  - `97.5`

Keep frozen:

- `tools/forge_campaign_state.py`
- daily spine
- tradable labels
- triple-barrier semantics
- same-sign pulse compression
- V655A soft-mass candidate stream
- V655B amplitude-aware fold
- V656 transition derivations
- V657 sign-aware threshold semantics
- V658 blocked admission contract
- broader ML / Vertex / holdout closure

## Replication block chosen for wave 1

First non-overlapping contiguous post-selection block chosen from available `linux1` L1/L2 coverage:

- `20230508 -> 20230927`

Observed source coverage:

- `l1_count=73`
- `l2_count=101`

This block:

- does not overlap the H1 2023 V657 / V658 slice
- is the first sufficiently long post-selection block to support the frozen `10d/20d` horizon semantics and the `>= 40 scored dates` pass requirement

## Runtime intent

Wave 1 remains:

- non-ML
- local-only
- no Vertex
- no holdout

Runtime steps:

1. forge the unchanged V655B campaign matrix on `20230508 -> 20230927`
2. run the fixed-contract V659 replication audit on that matrix
3. decide pass / block from the frozen V659 rules only
