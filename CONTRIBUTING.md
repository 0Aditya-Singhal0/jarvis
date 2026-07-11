# Contributing to Jarvis

## Human-in-the-loop workflow

1. Agree the task list with the project owner before work begins.
2. Track each approved task in a GitHub Issue.
3. Create one branch for that issue: `codex/issue-<number>-<short-slug>`.
4. Keep the branch focused on the issue and open a draft pull request that links it.
5. Do not merge until the project owner has reviewed and explicitly approved it.

Never use Git worktrees. Never install dependencies, configure credentials, enable an external connector, or change the agreed task list without a project-owner checkpoint.

## Validation

This project does not create automated tests at the project owner's direction. Each pull request must instead state the manual, human-led validation performed and any validation deliberately deferred.

## Labels

Use one label from each applicable group:

- Phase: `phase:1-foundation`, `phase:2-communication`, `phase:3-android`, `phase:4-nvr`, `phase:5-hardening`
- Area: `area:governance`, `area:compose`, `area:api`, `area:policy`, `area:hermes`, `area:security`, `area:ui`
- Priority: `priority:now`, `priority:next`, `priority:later`
- HIL status: `hil:needs-review`, `hil:blocked-install`, `hil:blocked-decision`, `hil:approved`

## Pull requests

Use the pull-request template. The description must link the Issue, summarize changes, list manual validation, list installations and external changes (normally none), and identify the next human approval required.
