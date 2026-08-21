# Analyzer qualification evidence

Evaluation date: 2026-08-21. Toolchain: Node.js 24.19.0 and pnpm 11.22.0.

Candidate: `kuromoji@0.1.2` with bundled IPADIC. The decision rule is mechanical: only five PASS results permit a runtime dependency; any FAIL or UNKNOWN selects the internal fallback.

| Gate | Status | Command | Exit code | Artifact/evidence |
| --- | --- | --- | ---: | --- |
| Maintainability | FAIL | `rg -n 'releaseは2018年' docs/decision-evidence/DEC-002-006-objective-evidence.md` | 0 | `RELEASE_AGE_GT_24_MONTHS`; published in 2018, so age exceeded 24 months on 2026-08-21 |
| Node 24 performance | UNKNOWN | Not run: maintainability rejected the candidate before installation | N/A | No benchmark artifact; required cold/warm 30-run result is absent |
| Range conversion | UNKNOWN | Not run: candidate was not installed | N/A | No surrogate, combining-mark, or repeated-token adapter artifact |
| Determinism | UNKNOWN | Not run: candidate was not installed | N/A | No ten-process normalized hash artifact |
| Offline | UNKNOWN | Not run: candidate was not installed | N/A | No network-denial or socket/DNS artifact |

Decision: **REJECT** by `ANY_FAIL_OR_UNKNOWN`. `kuromoji`, `kuromojin`, and `@faanau/kuromoji` remain absent from the runtime manifest and lock importer. Delivery uses the internal `H102`, `H106`, `H107_TOKEN`, and `H108_TOKEN` contracts. The machine-readable result is in `analyzer-qualification.json`; `python3 .codex/spec-verifiers/verify_pbi04.py` validates it and returns exit 0 only with all fallback contract tests green.
