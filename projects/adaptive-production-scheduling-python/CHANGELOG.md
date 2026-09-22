# Changelog

## 0.1.0 - 2026-08-29

- Initial packaged release.
- Added deterministic stochastic-disruption simulation via seeded RNG.
- Fixed preservation of explicitly supplied machine `current_capacity`.
- Fixed allocation so the provided machine mapping is actually honored.
- Removed the undefined-demand rebalancing failure mode from the original prototype.
- Enforced integer production quantities and non-negative unmet demand.
- Added KPI calculation, reporting helpers, tests, Ruff checks, and GitHub Actions CI.
- Added a strict non-commercial source license.
