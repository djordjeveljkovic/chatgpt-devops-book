# Agent assignments

Only the coordinator updates this index. Agent IDs are session-local; file ownership and exact continuation notes persist across sessions.

| Assignment | Chapters | Exclusive writing ownership | Phase |
|---|---|---|---|
| Writer foundations | 001–070, Volumes 1–7 | Chapters and matching summaries | Assigned |
| Writer delivery | 071–140, Volumes 8–14 | Chapters and matching summaries | Assigned |
| Writer operations | 141–190 and 201–210, Volumes 15–19 and 21 | Chapters and matching summaries | Assigned |
| Coordinator architecture and references | 191–200 and 211–220, Volumes 20 and 22 | Chapters and matching summaries | References drafted; architecture writing |

The assigned foundations and delivery writers are not available in this session. The coordinator assumes correction ownership for reviewed findings in Chapters 026–030, 034–049, 050–052, 090, 092–093 and 095–100; changes to reviewed prose require fresh independent review before promotion. A replacement writer currently owns Chapters 061–070 only.

Writers report completed volumes to the coordinator and continue their assignment. After drafting, independent review is assigned to a different worker. A reviewer writes review records only until explicitly assigned correction ownership. No worker edits another active writer's chapters or shared state.

## Rolling independent review

- `/root/write_foundations` reviews ready drafts 141–220 from `/root/write_operations` and the coordinator.
- `/root/write_delivery` reviews ready drafts 001–070 from `/root/write_foundations`.
- `/root/write_operations` reviews ready drafts 071–140 from `/root/write_delivery`.

Review happens at completed-volume boundaries, only after a chapter reports `draft`. Writers keep ownership of their own prose and resolve findings there. Review records must identify the reviewer, actual inspection scope, source checks, findings and `Verdict: approved` or `Verdict: changes-required`. The coordinator promotes only approved chapters after validation. Session-local agent names above do not imply that a future session still has live workers.
