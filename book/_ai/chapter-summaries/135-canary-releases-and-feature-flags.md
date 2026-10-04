# Chapter 135 continuation

Status: complete

## Written material

Canary purpose and distinction from feature flags; request/host/identity cohorts; attribution and sample size; SLI gates and staged exposure; flag types, safe defaults, targeting, provider failure, privacy and lifecycle; kill-switch requirements; AWS AppConfig rollback scope and OpenFeature API scope; DispatchDesk flag and routing incidents; stop/pause/abort/rollback actions; exercises, answer guidance, review questions and takeaways.

## Concepts and terminology

Canary, control/treatment, cohort, representativeness, attributable metric, observation/bake window, feature flag, kill switch, flag lifecycle, rollout pause/abort, configuration rollback.

## Examples and cross-references

DispatchDesk fraud-review feature behind a stable identity flag cohort and API digest receiving partial traffic. Relative links to Chapters 134 and 136; sources from Google SRE Workbook, AWS AppConfig, OpenFeature, and Argo Rollouts.

## Open threads

Independent review approved the final body hash after the AppConfig lifecycle distinction was clarified: alarm rollback during deployment monitoring and a later, time-limited revert of a completed configuration are separate. No traffic, provider, controller, or configuration operation was run.

## Exact next section

None. Independently approved; continue to the next unfinished chapter.

## Verification

Google SRE Workbook and current OpenFeature, AWS AppConfig, and Argo Rollouts docs inspected 2026-10-04. `python3 tools/check_book.py --chapters 135-135` passed: 1,420 global local links; no errors or warnings. `git diff --check` passed.
