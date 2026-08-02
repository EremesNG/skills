# Skill benchmark: unity-gc-free

**Host model identity**: unavailable  
**Generated**: 2026-08-02T20:16:40Z  
**Artifacts**: three prompts, one with-skill and one without-skill response per prompt

## Objective assertion result

| Configuration | Passed | Total | Mean pass rate |
| --- | ---: | ---: | ---: |
| With skill | 27 | 27 | 100.0% |
| Without skill | 9 | 27 | 33.3% |
| Observed difference | +18 | — | +66.7 percentage points |

All three final with-skill artifacts passed their nine predeclared assertions.
The baseline passed 2/9 for diagnosis, 3/9 for dependency selection, and 4/9 for
pool lifecycle. Nine assertions passed in both configurations, eighteen passed
only with the skill, and none passed only without it.

## Measurement limitations

- One artifact per prompt/configuration cannot estimate run-to-run variance or
  flakiness. Variation across three different prompts is not repeated-run variance.
- The host exposed neither duration nor total-token telemetry. Zero durations in
  `benchmark.json` are placeholders. Its `tokens` field is populated from output
  character counts by the installed aggregator and must not be read as tokens.
- With-skill output averaged 26,860 characters and baseline output averaged
  9,207 characters. Length is descriptive and does not establish efficiency,
  quality, or causality.
- The skill was refined against failures on these same prompts before the final
  result. This is convergence evidence, not a held-out generalization estimate.
- Executors were isolated from assertions and expected outputs, but exact host
  model identity and execution transcripts were unavailable.
- No human preference comparison was observed. Objective assertion grading is
  not a substitute for reviewer preference or usability feedback.
