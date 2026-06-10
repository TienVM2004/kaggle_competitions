# Report 01 — Data grounding (raw-CSV verification)

Facts below verified directly against raw files, not assumed. Each underwrites a design choice; a wrong assumption
here silently corrupts every downstream number. Source files: `data/raw/train/000d7d20__horizontal_well.csv`,
`data/raw/test/000d7d20__horizontal_well.csv`, `data/raw/sample_submission.csv`.

## Verified facts
| Fact | Value | Evidence | Underwrites |
|---|---|---|---|
| `id` index | **0-based row position** in lateral | train first-blank-`TVT_input` = row 1442 ↔ submission `000d7d20_1442` | id construction, scored-row reproduction |
| Scored region | **post-PS only** | submission starts at PS row, not row 0 | eval scores post-PS only |
| PS definition | first row `TVT_input` is NaN; contiguous tail | rows 1442+ blank, filled before | `split_ps` contract |
| Z sign | **negative** (`-9258`), TVT positive (`11236`) | row 0 values | `D = TVT + Z`; B2/B3 use `−Z_i` |
| `D` scale | ~+1977 absolute, ~230 ft range | `11236 + (−9258)` | D smooth/extrapolable; per-well offset |
| `TVT_input` pre-PS | `== TVT` exactly | row 1440 both `11747.34` | baselines read `TVT_input`, never `TVT` |
| Z post-PS | complete (no NaN at transition) | row 1444 `Z=-9735.07`, `TVT_input` blank | B2/B3 predict every post-PS row |
| GR | sparse, blank both sides of PS | rows 1440–1445 GR blank | irrelevant to baselines |
| Train cols | `MD,X,Y,Z,ANCC,ASTNU,ASTNL,EGFDU,EGFDL,BUDA,TVT,GR,TVT_input` | header | leak cols + `TVT` train-only |
| Test cols | `MD,X,Y,Z,GR,TVT_input` | header | no target/leak in test → portability |
| MD spacing | ~1 ft, **not exact** (1440 rows ↔ 1438 MD) | head vs row 1440 | fit D vs **MD**, not row index |
| Test = train overlap | 3 test wells byte-identical basenames to first 3 train | glob both dirs | confirms public-LB leak trap |

## Unresolved
- Confirm sum of post-PS rows over the 3 test wells = **14,151** (official scored count) — cheap check at build,
  double-validates the entire PS contract.
