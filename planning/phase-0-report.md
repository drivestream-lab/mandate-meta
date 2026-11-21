# Phase 0 report

Date: 2026-11-21. Company: Mandate Gubernix Ind (`75fffebf-40f4-4e05-a5ff-c4efa6d8a513`). Paperclip image: `drivestream-lab/paperclip:mandate-acpx-root-pack` on the `a665ed6a` baseline. Org plan: GitHub Free.

This run stopped being a full 13-check pass. Checks 1, 7, and 8 do not meet the written pass line. Checks 3, 5, 6, and 9 through 13 were not run.

## Task 6 identity

Agent Mandate `bb97b5d0-b2ca-40ae-83bf-c0e84ff1187d`. API key name `mandate-lab`, stored at `~/.mandate/secrets/lab/paperclip-mandate-token`.

Recorded permissions: `canCreateAgents: true`, `canCreateSkills: true`. Heartbeat timer off, `wakeOnDemand: true`. Those permissions are wider than "create decisions, set and clear approval stages, update issues, read state." Check 1 does not show them to be sufficient or minimal. The key alone cannot change an issue or open a decision. Paperclip requires `X-Paperclip-Run-Id` for those writes.

## Checks

| # | Result | Evidence |
|---|---|---|
| 1 | Fail | Issue `MAN-1`. The stage's only approver is the assignee, Mandate. `PATCH` to `done` returns `No eligible approval participant is configured for this issue`. A board user was not shown a pending stage that only Mandate could advance. |
| 2 | Pass | Decision `69dd0fc8-536b-4ba6-8eb8-fa6baa5f8bf7`. Mandate opened it on run `cba07f17-f968-430b-8c65-83990b1701a8` with a markdown brief and options A and B. Board user `QoBL4tu8xFmYU8D8ssfpm7uOvn8H9oSk` chose A. Mandate read back `chosenOptionId: A` and that user id. |
| 3 | Not run | No plugin listener was attached on `lab_local`. |
| 4 | Pass | `company_decision_models` has 0 rows. No decision model ran. |
| 5 | Not run | No `process` adapter agent was created. |
| 6 | Not run | No coding agent was launched against `mandate-sandbox-svc`. |
| 7 | Fail | Workflow `.github/workflows/phase0-evidence.yml` is on `mandate-sandbox-meta` `main` (PRs 2, 3, and 4). Creating a ruleset that requires it returned `Invalid rule 'workflows'` for the real workflow and for a minimal one. No attestation was produced. The org is on the free plan. |
| 8 | Fail | `mandate-sandbox-svc` `main` has classic protection (strict check `local`, push list only `mandate-test`, administrators included) and ruleset `phase0-merge` (id `27785422`). `nikd10x` still merged PRs 2, 3, 4, 5, and 6. GitHub ruleset evaluations for those merges say `pass`. A refused person merge, a refused `mandate-lab` merge, and a `mandate-test` merge of only the verified head were not shown. |
| 9 | Not run | Poll budget was not measured. |
| 10 | Not run | Webhook secret was deferred. Delivery stays inactive. |
| 11 | Not run | No Temporal restore drill. |
| 12 | Not run | No `mandate` database restore drill. |
| 13 | Not run | `launchpad status` was not captured as a gate. |

## Re-run on 2026-11-21

Stopped at the first failure, check 1. Checks 7 and 8 were not re-run.

### Identity

`PATCH /api/agents/bb97b5d0-b2ca-40ae-83bf-c0e84ff1187d/permissions` with `canCreateAgents: false`, `canCreateSkills: false`, `canAssignTasks: false` returned 200. Heartbeat stayed `enabled: false` and `wakeOnDemand: true`.

Final permissions: `canCreateAgents: false`, `canCreateSkills: false`, `canAssignTasks: false`.

A run id is not minted by the agent key. `POST /api/agents/:id/wakeup` (or an assignment wakeup) creates a heartbeat run. Inside that run the runner sends `X-Paperclip-Run-Id` with the heartbeat run id. Issue and decision writes require that header.

Check 2 was not repeated after the permission change because check 1 failed first.

### Check 1

Worker `sandbox-coder` `88db5b6e-13fc-4f25-bb6d-0f9a1fd74534`, status `idle`. Issue `MAN-2` `c7e8b9ce-5c3d-41bb-9787-dc6d37b15db9`, assignee `sandbox-coder`, only approver Mandate.

`PATCH /api/issues/c7e8b9ce-5c3d-41bb-9787-dc6d37b15db9` `{"status":"in_review"}` as the board returned 200. Status `in_review`, stage `pending`, participant Mandate.

`PATCH` `{"status":"done"}` as the board returned 200. Status `done`. Expected a refusal. Stopped. Mandate did not approve inside a run.

## Spike branches

These are unmerged throwaway branches. They are not on `mandate-meta`.

- `mandate-sandbox-meta`: `chore/phase0-evidence`
- `mandate-sandbox-svc`: `chore/phase0-ci`, `chore/phase0-merge`, `chore/phase0-ruleset`, `chore/phase0-ruleset-2`, `chore/phase0-ruleset-3`
