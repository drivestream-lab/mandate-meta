# Preflight report: INIT-MANDATE-001

Run on 21 Nov 2026 against `drivestream-lab/mandate-sandbox-svc`, the Mandate test App, `mandate-verify` at tag `preflight-1` (`e4a7d77`) and the lab Paperclip. It replaces the phase 0 run (closed `mandate-meta` PR 2), whose approval-stage, App-only-merge and required-workflow checks no longer apply under the merge-gate model (engineering-ready PRD section 11).

**Result: all four checks pass. W1 may start.**

| Check | Decision it proves | Result |
| --- | --- | --- |
| 1. The required check gates the merge into `develop` | AD-8, REQ-63, REQ-122 | Pass |
| 2. A signoff is readable, and writable by the App | AD-6, REQ-40 | Pass |
| 3. Signer-verified evidence from the reusable `mandate-verify` workflow | AD-7, REQ-108 | Pass, with one finding |
| 4. Mandate works in Paperclip inside its own run | AD-1, CTR-01, CTR-02 | Pass |

## Setup

- Ruleset `mandate-gate-decision` (id 27788560) on `develop`: pull request required, 0 approvals, required status check `mandate/gate-decision` from the Mandate test App only, no bypass actors. Kept in place for W1.
- Launchpad's branch protection on `develop`: pull request required, 0 approvals, no status checks, admins not enforced.
- Scripts: `planning/preflight/preflight.py` (GitHub, as the test App) and `planning/preflight/paperclip_check.py` (Paperclip, as Mandate's agent). Neither prints a secret.

## Check 1: the required check gates the merge

| Step | Observation |
| --- | --- |
| PR 1, no check posted | Normal merge refused ("the base branch policy prohibits the merge") |
| PR 1, owner merge with `--admin` | Refused: "Required status check mandate/gate-decision is expected" |
| App posts `success` on head `8f10ce7` | `201 success`; merge state `CLEAN` |
| App merges with `sha` pinned to that head | Merged by `mandate-test[bot]` (merge commit `df37bcf`) |
| PR 2: App posts `success` on head `ac7b77b` | Merge state `UNSTABLE` (mergeable; only Launchpad's non-required `ci` pending) |
| Push a new commit `e520bbe` after the check | Merge state `BLOCKED` |
| Owner merge with `--admin` on the new head | Refused: "Required status check mandate/gate-decision is expected" |

Note: PR 1's App merge happened before the planned push-after-check step, because an interrupted helper script raced the manual steps. The push-after-check behaviour was therefore proven on PR 2. Nothing unchecked reached `develop`.

## Check 2: a signoff is readable, and writable by the App

| Direction | Observation |
| --- | --- |
| App signs PR 2 (authored by `nikd10x`) | Label `200`, Approve with attestation `200`, mark ready `200`, no errors |
| Read back PR 2 | Label `preflight-lgtm`, `ready: true`, Approve by `mandate-test[bot]` on head `e520bbe` with the attestation body |
| Human signs PR 3 (opened by the App, so the human is not the author) | `gh pr edit --add-label`, `gh pr review --approve --body <attestation>`, `gh pr ready` all succeeded |
| Read back PR 3 | Label `preflight-lgtm`, `ready: true`, Approve by `nikd10x` on head `a6a12e0` with the attestation body |

## Check 3: signer-verified evidence

| Bundle | `gh attestation verify --signer-workflow drivestream-lab/mandate-verify/.github/workflows/verify.yml` |
| --- | --- |
| Pinned caller (run 44889253051, delegates to `verify.yml@preflight-1`) | Pass. Signer: `drivestream-lab/mandate-verify/.github/workflows/verify.yml@refs/tags/preflight-1` |
| Edited caller (run 44889256299, attests inside the sandbox repo) | Fail: "Sigstore verification failed" |
| Edited caller against its own workflow (control) | Pass, so its signature is real and only the signer differs |

**Finding for TASK-W1-03.** `--signer-workflow` matches `verify.yml` at any ref. Mandate must additionally require the signer ref to be the pinned tag (or exact commit) of `mandate-verify`, read from the attestation's certificate, so a run of `verify.yml` from an unreviewed branch is rejected.

## Check 4: Mandate works in Paperclip inside its own run

| Step | Observation |
| --- | --- |
| Mandate's agent permissions | `canAssignTasks`, `canCreateAgents`, `canCreateSkills` all false |
| Wake-up | `202`, run `72d8a3ac-59c7-4e8d-87fa-383dc1c82bb7` |
| Create an issue with `X-Paperclip-Run-Id` | `201`, MAN-3 |
| Ask a two-option question in that run | `201`, interaction `f8cd1812`, created by Mandate's agent, status `pending` |
| Human answers in Paperclip | Read back: status `answered`, `option-a`, resolved by user `QoBL4tu8xFmYU8D8ssfpm7uOvn8H9oSk` |

Observation: the question was opened without an addressee. Mandate's real questions should name the addressee so they reach the holder's inbox directly.

## Clean-up

Preflight PRs 2 and 3 on `mandate-sandbox-svc` are closed unmerged; the `preflight/*` and `feature/preflight-*` branches are deleted. The ruleset, the `preflight-lgtm` label and the `preflight-1` tag stay.
