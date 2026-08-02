# Skill Benchmark: unity-developer

**Executor**: Codex collaboration agents (exact host model not exposed)  
**Date**: 2026-08-02T04:02:39Z  
**Evals**: 1, 2, 3 (1 run per configuration)

## Summary

| Metric | With Skill | Without Skill | Delta |
| --- | ---: | ---: | ---: |
| Assertion pass rate | 100% +/- 0% | 74% +/- 12% | +0.26 |
| Output characters | 19,617 +/- 5,388 | 12,522 +/- 3,102 | +7,095 |
| Execution time | unavailable | unavailable | unavailable |
| Total tokens | unavailable | unavailable | unavailable |

The host did not expose executor duration or total-token notifications, so those
values were not estimated. Output characters measure final recommendation text;
they are not token counts.

## Analyst observations

- 17 of 23 assertions pass in both configurations and therefore do not
  discriminate in this single-run sample.
- Six assertions uniquely favor the skill and none favor the baseline:
  coupling-lifecycle #1; manager-architecture #1, #7, and #8; and
  networked-squad-ai #7 and #8.
- Evidence classification separates the skill in more than one evaluation. The
  no-skill coupling and manager outputs do not explicitly separate supplied facts
  from uninspected repository/runtime facts.
- Complex lifecycle acceptance also separates the skill: the manager baseline
  omits observable destination readiness and return-to-menu/new-session coverage;
  the AI baseline leaves cancellation, despawn/pool cleanup, and a PlayMode layer
  incomplete.
- Performance treatment is mostly shared. Only the manager evaluation separates,
  because its baseline lacks a representative player-build capture and a
  reproducible before/after baseline.
- Baseline results are 6/7, 5/8, and 6/8; with-skill results are 7/7, 8/8, and
  8/8. Manager architecture has the largest observed separation.
- With-skill outputs contain 56.7% more characters on average. This accompanies
  six additional passed assertions but does not establish causal efficiency.
- One run per configuration cannot support claims about variance, consistency,
  or flakiness. Timing and token metrics remain unavailable.
