# Implementation plan: INIT-MANDATE-001

> Walk-time plan for building Mandate. Product intent: `prd/INIT-MANDATE-001.md`. Design: `prd/INIT-MANDATE-001-engineering.md`. Durable spec for the code: `mandate/docs/specification/`. Exported 21 Nov 2026.

## 1. What this initiative delivers

Mandate built to completion (every capability up to phase 3) as one initiative against the whole engineering-ready PRD, in nine product waves, followed by a sandbox fix stage and a Conduit fix stage. Programme two (phase 4) is a later initiative.

## 2. How it is built

- Built by Claude Code under KD's review (REQ-120). One pull request per WorkManifest task, about 400 changed lines, into `develop` (ADR-021). Checks run locally and are attached to each PR (ADR-018).
- Tested against the real Paperclip and real GitHub sandbox repos; nothing is faked (ADR-017).
- Branches: `feature/INIT-MANDATE-001-w<n>-<task-slug>` (ADR-025).
- `mandate` repo guide for Claude Code: `mandate/CLAUDE.md`.

## 3. Product waves and manifest waves

The product PRD names nine waves. This manifest follows prayog's `W0, W1, ...` numbering, so product wave 1 is split in two: the part that does not depend on phase 0 platform behaviour, and the part that does.

| Product wave | Manifest wave | Scope | Starts when |
| --- | --- | --- | --- |
| W1 Walking skeleton and project layout, part a | **W0** | Layout, checks, kernel, database, ledger, outbox, local stack, Paperclip client, test agents, programme readiness, gate brief and sealed call | Export merged |
| W1 Walking skeleton and project layout, part b | **W1** | Signoff reading and the required check, revised and stale voiding, signed evidence, check-gated merge, the walking-skeleton end-to-end journey | Preflight (four checks) passes |
| W2 Intake to accepted PRD | W2 | Planned when W1 closes | W1 closed |
| W3 Spec to released waves | W3 | Planned when W2 closes | |
| W4 Triage, bugs, enhancements and repos | W4 | Planned when W3 closes | prayog contract v3 tagged before W2 |
| W5 Policy and control tower | W5 | Planned when W4 closes | `paperclip-plugin-rules` ready |
| W6 Earning autonomy | W6 | Planned when W5 closes | |
| W7 Breadth | W7 | Planned when W6 closes | |
| W8 Process and context | W8 | Planned when W7 closes | |
| W9 Operational hardening | W9 | Planned when W8 closes | |
| Sandbox fix stage | | Every journey live on `mandate-sandbox`; fixes merged | W9 closed |
| Conduit fix stage | | Conduit onboarded and delivered by Mandate; fixes merged | Sandbox stage passed |

Only W0 and W1 are in the manifest below. Each later wave is planned, and added to a new revision of this plan, when the wave before it closes.

## 4. Preflight dependency

W1 tasks rest on four platform behaviours proven by preflight (`planning/preflight-report.md` when merged): the required check `mandate/gate-decision` blocks a merge into `develop` until it passes, for an org owner too (ADR-025, ADR-026); a signoff (label, attested Approve, ready) is readable and Mandate's App can write all three (ADR-006); a reusable `mandate-verify` workflow attests runs and an edited caller fails signer verification (ADR-007); Mandate works in Paperclip inside its own run, with reduced permissions (ADR-001). If any check fails, W1 waits for a design decision; W0 is unaffected.

## 5. Upstream changes this initiative needs

| Change | Repo | Needed by |
| --- | --- | --- |
| Add `workflows/` to the standard package table | `python-services-rules` | W0 (TASK-W0-01 opens the PR) |
| Contract v3: gate nodes with a class, nine kinds, deciding roles | `prayog-skills` (parallel initiative) | Before W2 |
| `paperclip-plugin-rules` repo and `profiles/paperclip-plugin.yaml` | new repo, `prayog-skills` | Before W5 |
| Launchpad authenticates as a GitHub App | `launchpad` | Before the Conduit fix stage |

## 9. WorkManifest

```yaml
apiVersion: prayog/v1
kind: WorkManifest

initiative: INIT-MANDATE-001
metadata:
  title: Mandate, the governor for an autonomous agent delivery organisation
  summary: |
    Mandate built to completion (every capability up to phase 3) as one initiative.
    This revision covers product wave 1 (walking skeleton and project layout) as
    manifest waves W0 and W1. Later waves are added when the previous wave closes.
  playbook:
    - docs/specification/product/mandate-core.md

target:
  org: drivestream-lab
  project: none (project board disabled for Mandate programmes)

defaults:
  initiative: INIT-MANDATE-001
  parent: EPIC
  labels:
    - init-mandate-001

epic:
  id: EPIC
  repo: mandate
  title: "INIT-MANDATE-001: Mandate core"
  codebase: mandate
  spec_path: docs/specification/product/mandate-core.md
  verify_command: make journeys
  body: |
    Build Mandate core against the engineering-ready PRD. One PR per task under
    human review; live tests against real Paperclip and GitHub sandbox repos.

work:
  - id: W0
    kind: issue
    repo: mandate
    title: "Walking skeleton, part a: layout and foundations"
    depends_on: []
    codebase: mandate
    spec_path: docs/specification/product/mandate-core.md
    verify_command: "make journeys -- tests/journeys/onboard_a_programme tests/journeys/decide_blind_first"
    body: |
      Everything in product wave 1 that does not depend on phase 0 platform
      behaviour: the project layout and checks, kernel, database and roles, the
      ledger hash chain, the outbox, the local platform stack, the Paperclip client
      acting inside runs, deterministic test agents, programme readiness from
      Launchpad configuration, and the gate brief with a sealed deciding-role call.
    tasks:
      - id: TASK-W0-01
        implements: [REQ-120]
        depends_on: []
        files:
          - path: .importlinter
            action: modify
          - path: pyproject.toml
            action: modify
          - path: Makefile
            action: modify
          - path: .pre-commit-config.yaml
            action: modify
          - path: src/engine/__init__.py
            action: create
          - path: src/workflows/__init__.py
            action: create
          - path: src/worker_main.py
            action: create
          - path: src/context_main.py
            action: create
          - path: scripts/record_review_decision.py
            action: create
          - path: tests/README.md
            action: create
          - path: tests/conftest.py
            action: create
          - path: docs/specification/as-built/requirements.md
            action: modify
        exit:
          criteria:
            - "src/ follows ADR-014: engine/, workflows/, worker_main.py and context_main.py exist beside the scaffold's layers"
            - "import-linter carries the rules' layer contract plus: engine imports no IO layer; workflows imports only business_services and models; context_main imports only models, engine and its own infra client; a deliberate violation fails make check"
            - "pyright runs in strict mode over src/ and tests/ with zero errors"
            - "Makefile has check, test and journeys targets; pre-commit runs make check, pre-push runs make test"
            - "tests use a pytest marker req(...) and a check fails the test run when a requirement listed for W0 and W1 has no test"
            - "scripts/record_review_decision.py writes a review decision for a merged PR as a JSON line in the ledger entry format (actor, choice, target commit, version stamp) to mandate-meta/ledger-import/"
            - "A pull request to python-services-rules adds workflows/ to the standard package table"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; import-linter reports all contracts kept; pyright 0 errors"
            evidence_expected: "PR body, check output attached"

      - id: TASK-W0-02
        implements: [REQ-54]
        depends_on: [TASK-W0-01]
        files:
          - path: src/models/kernel_models.py
            action: create
          - path: src/engine/kernel/version_stamp.py
            action: create
          - path: src/engine/kernel/idempotency_key.py
            action: create
          - path: src/engine/kernel/clock.py
            action: create
          - path: tests/unit/engine/kernel/test_version_stamp.py
            action: create
          - path: tests/unit/engine/kernel/test_idempotency_key.py
            action: create
        exit:
          criteria:
            - "A version stamp model carries contract, block versions, skills, rules, agent setup, policy revision and Mandate release (ER-05)"
            - "Idempotency keys derive deterministically from work item and step; the same inputs always give the same key (ER-01)"
            - "Time comes from an injectable clock; nothing in engine/ reads the system clock"
          proof:
            kind: command
            command: "make check && pytest tests/unit/engine/kernel -q"
            expected: "exit 0"
            evidence_expected: "PR body"

      - id: TASK-W0-03
        implements: [REQ-55]
        depends_on: [TASK-W0-01]
        files:
          - path: postgres_migrations/versions/create_capability_schemas_and_grants.py
            action: create
          - path: src/database/postgres/schema/ledger/ledger_entry_schema.py
            action: create
          - path: src/database/postgres/schema/runner/work_item_schema.py
            action: create
          - path: src/database/postgres/schema/gates/gate_schema.py
            action: create
          - path: src/database/postgres/schema/outbox/outbox_message_schema.py
            action: create
          - path: tests/journeys/database_roles/test_runtime_role_cannot_rewrite_ledger.py
            action: create
        exit:
          criteria:
            - "One Postgres schema per capability needed by W0 and W1 (ledger, runner, gates, release, programmes, policy, outbox, inbound) with tables owned by mandate_owner"
            - "mandate_app has only INSERT and SELECT on ledger.entries; an UPDATE or DELETE by mandate_app fails"
            - "A trigger rejects UPDATE and DELETE on ledger.entries even for mandate_owner unless the migration is explicitly marked for it"
            - "The migration was created with scripts/create_postgres_migration.sh; KD applies it with scripts/run_postgres_migration.sh"
          proof:
            kind: command
            command: "make check && pytest tests/journeys/database_roles -q"
            expected: "exit 0; the rewrite attempts are refused by Postgres"
            evidence_expected: "PR body"

      - id: TASK-W0-04
        implements: [REQ-54, REQ-55]
        depends_on: [TASK-W0-02, TASK-W0-03]
        files:
          - path: src/engine/ledger/hash_chain.py
            action: create
          - path: src/models/ledger_models.py
            action: create
          - path: src/business_services/ledger/ledger_append_service.py
            action: create
          - path: src/database/postgres/repository/ledger/ledger_repository.py
            action: create
          - path: tests/properties/test_ledger_chain_detects_any_edit_or_deletion.py
            action: create
          - path: tests/unit/business_services/ledger/test_ledger_append_service.py
            action: create
        exit:
          criteria:
            - "Each entry stores sequence, previous hash, own hash, type, payload and version stamp; a decision entry records actor, role, rung, options offered, choice, reasons, evidence, target version and versions"
            - "Chain verification detects any edited, deleted, inserted or reordered entry (property test)"
            - "A correction is a new entry that references the original"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0; property tests pass across generated chains"
            evidence_expected: "PR body"

      - id: TASK-W0-05
        implements: [REQ-55]
        depends_on: [TASK-W0-04]
        files:
          - path: src/business_services/outbox/outbox_dispatch_service.py
            action: create
          - path: src/database/postgres/repository/outbox/outbox_repository.py
            action: create
          - path: src/database/postgres/repository/inbound/inbound_event_repository.py
            action: create
          - path: tests/unit/business_services/outbox/test_state_change_and_action_commit_together.py
            action: create
          - path: tests/unit/business_services/outbox/test_repeated_event_has_one_effect.py
            action: create
        exit:
          criteria:
            - "A state change, its ledger entry and its outbox message commit in one transaction (ER-02, ADR-020)"
            - "The dispatcher delivers and retries outbox messages; a message sent twice has one effect downstream (ER-01)"
            - "A repeated inbound event id is recorded once and ignored after (ER-03)"
          proof:
            kind: command
            command: "make check && make test"
            expected: "exit 0"
            evidence_expected: "PR body"

      - id: TASK-W0-06
        implements: [REQ-02]
        depends_on: [TASK-W0-01]
        files:
          - path: docker/docker-compose.test-stack.yml
            action: create
          - path: scripts/test_stack_up.sh
            action: create
          - path: scripts/test_stack_down.sh
            action: create
          - path: tests/journeys/conftest.py
            action: create
        exit:
          criteria:
            - "make journeys brings up an ephemeral stack (Paperclip from drivestream-lab/paperclip:mandate-baseline-a665ed6 with its own database, Postgres, Temporal) per run and tears it down after"
            - "Two runs at once do not share Paperclip state; GitHub work is namespaced per run in the sandbox repos"
            - "The stack reads the test App's credentials from ~/.mandate/secrets/test/ by path; nothing secret is written into the repo or test output"
          proof:
            kind: command
            command: "make journeys"
            expected: "stack starts healthy, an empty journey session passes, stack is removed"
            evidence_expected: "PR body"

      - id: TASK-W0-07
        implements: [REQ-40]
        depends_on: [TASK-W0-06]
        files:
          - path: src/infra_services/paperclip_service.py
            action: create
          - path: src/models/paperclip_models.py
            action: create
          - path: src/configs/paperclip_settings.py
            action: create
          - path: tests/contract/paperclip/test_writes_carry_a_run_and_an_idempotency_key.py
            action: create
          - path: tests/contract/paperclip/test_unrecognised_release_stops_work.py
            action: create
        exit:
          criteria:
            - "Every Paperclip write by Mandate happens inside a run obtained with POST /api/agents/:id/wakeup and carries X-Paperclip-Run-Id and an idempotency key"
            - "The client refuses to run against a Paperclip release other than the pinned baseline (ER-09)"
            - "Mandate's identity can create issues, post comments, open and read a question and read state; it cannot create agents or skills or assign tasks"
          proof:
            kind: command
            command: "make journeys -- tests/contract/paperclip"
            expected: "exit 0 against the ephemeral Paperclip"
            evidence_expected: "PR body"

      - id: TASK-W0-08
        implements: [REQ-118]
        depends_on: [TASK-W0-07]
        files:
          - path: tests/agents/deciding_role.py
            action: create
          - path: tests/agents/sandbox_coder.py
            action: create
          - path: tests/agents/README.md
            action: create
          - path: src/models/role_output_models.py
            action: create
          - path: tests/journeys/test_agents/test_scripted_agent_returns_a_schema_checked_result.py
            action: create
        exit:
          criteria:
            - "Deterministic real agents run on Paperclip's process adapter with scripts from tests/agents/; they call no model (ADR-022)"
            - "Their outputs are validated against the same Pydantic models Mandate uses; an output that fails its schema counts as missing"
            - "A deciding-role script returns a structured call: option, reasons, evidence cited"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/test_agents"
            expected: "exit 0; a process-adapter agent round-trips a schema-checked result"
            evidence_expected: "PR body"

      - id: TASK-W0-09
        implements: [REQ-01, REQ-02]
        depends_on: [TASK-W0-05, TASK-W0-07]
        files:
          - path: src/business_services/programmes/programme_from_meta_service.py
            action: create
          - path: src/business_services/programmes/programme_readiness_service.py
            action: create
          - path: src/models/programme_models.py
            action: create
          - path: tests/journeys/onboard_a_programme/test_programme_created_from_launchpad_config.py
            action: create
          - path: tests/journeys/onboard_a_programme/test_readiness_names_each_failure_with_its_cause.py
            action: create
          - path: tests/fixtures/onboard_a_programme/sandbox_meta_config/programme.yaml
            action: create
        exit:
          criteria:
            - "A programme is created on a Paperclip project from the meta repo's Launchpad configuration at a commit (repos, roles, decision owner per gate class, workflow version, starting rung)"
            - "Readiness shows every role has a usable agent, GitHub access works for every repo and the pinned workflow loads; each failure is shown with its cause; nothing starts while any fails"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/onboard_a_programme"
            expected: "exit 0 against the ephemeral Paperclip and mandate-sandbox repos"
            evidence_expected: "PR body"

      - id: TASK-W0-10
        implements: [REQ-39, REQ-103, REQ-118]
        depends_on: [TASK-W0-04, TASK-W0-08]
        files:
          - path: src/engine/gates/brief.py
            action: create
          - path: src/business_services/gates/gate_opening_service.py
            action: create
          - path: src/business_services/gates/sealed_call_service.py
            action: create
          - path: src/models/gate_models.py
            action: create
          - path: tests/unit/engine/gates/test_brief_omits_the_call_at_blind_first_gates.py
            action: create
          - path: tests/journeys/decide_blind_first/test_call_sealed_before_the_holder_sees_the_decision.py
            action: create
        exit:
          criteria:
            - "A brief states what is decided, the options with their impact, the recommendation and why, evidence bound to the head commit, and what happens once it is signed off; it is posted on the gate's pull request"
            - "At intent and design gates the brief omits the deciding role's call; at verification and housekeeping gates it shows the recommendation with the evidence"
            - "The deciding role's call is hashed into the ledger before the brief is posted, never appears on the pull request, and is revealed only after the holder's signoff is recorded; a missing or invalid call is retried once, then counts as no call"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/decide_blind_first"
            expected: "exit 0; ledger order is sealed call, then decision, then reveal"
            evidence_expected: "PR body"

    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: sandbox
        command: "make journeys -- tests/journeys/onboard_a_programme tests/journeys/decide_blind_first"
        covers: [J-01, J-16, REQ-01, REQ-02, REQ-39, REQ-103, REQ-118]
        dependencies:
          - ephemeral Paperclip (pinned image)
          - postgres
          - temporal
          - mandate-sandbox-meta and mandate-sandbox-svc repos
        fixtures:
          - tests/fixtures/onboard_a_programme/sandbox_meta_config/programme.yaml
        prerequisites:
          - "Test App credentials present in ~/.mandate/secrets/test/"
          - "Docker running; the pinned Paperclip image built"
        safe_test_data:
          - "A Paperclip company created per run; GitHub work namespaced per run in the sandbox repos"
        steps:
          - "Run make journeys for the two journey folders"
        expected_observations:
          - "A programme is created from the sandbox meta config and passes readiness"
          - "A blind-first gate opening records the sealed call before the decision and reveals it after"
        evidence_expected: "KD's review of the wave's last PR"
        cleanup:
          - "make journeys removes the ephemeral stack and the run's namespaced branches and issues"
        stop_conditions:
          - "Any journey failure or an unrecognised Paperclip release: stop and report"

  - id: W1
    kind: issue
    repo: mandate
    title: "Walking skeleton, part b: signoff, check, evidence, merge"
    depends_on: [W0]
    codebase: mandate
    spec_path: docs/specification/product/mandate-core.md
    verify_command: "python tests/verify/verify_walking_skeleton.py"
    body: |
      Starts only after preflight passes. A gate is a merge into develop. A PRD pull
      request on mandate-sandbox-meta and one toy wave on mandate-sandbox-svc are each
      signed at L0 blind-first on the pull request (label, attested Approve, ready),
      with the deciding role's call sealed in the ledger and never on the PR. Mandate's
      one required check, mandate/gate-decision, allows each merge only when the
      signoff matches the head; the wave also needs run-signed evidence for that head.
    tasks:
      - id: TASK-W1-01
        implements: [REQ-40, REQ-43, REQ-86, REQ-121]
        depends_on: []
        files:
          - path: src/infra_services/github_app_service.py
            action: create
          - path: src/business_services/gates/signoff_service.py
            action: create
          - path: src/business_services/gates/gate_decision_check_service.py
            action: create
          - path: src/models/signoff_models.py
            action: create
          - path: tests/journeys/sign_a_gate/test_merge_blocked_until_the_signoff_matches_the_head.py
            action: create
          - path: tests/journeys/sign_a_gate/test_signoff_by_someone_not_holding_the_gate_is_refused.py
            action: create
          - path: tests/journeys/sign_a_gate/test_non_blocking_decisions_are_recorded_without_stopping_work.py
            action: create
        exit:
          criteria:
            - "Mandate reads a gate's signoff on the current head: the gate's label, an Approve carrying the attestation, and the pull request marked ready; all three are required"
            - "Mandate posts mandate/gate-decision as success only when the signoff matches the head, the signer held the gate at its rung and the decision is in the ledger; otherwise it posts failure with the reason; a human-held gate never passes on timeout or by default"
            - "Decisions that are not merges are recorded in the ledger with their holder and do not block work: a review on the pull request when there is one (technical review, clarification checkpoints), otherwise a Paperclip question (triage, hiring, adding a repo), with the deciding role's call sealed first"
            - "No endpoint or view offers a second place to decide"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/sign_a_gate"
            expected: "exit 0 against the mandate-sandbox repos"
            evidence_expected: "PR body"

      - id: TASK-W1-02
        implements: [REQ-42, REQ-121]
        depends_on: [TASK-W1-01]
        files:
          - path: src/business_services/gates/signoff_voiding_service.py
            action: create
          - path: tests/journeys/work_changes_after_approval/test_push_after_signoff_voids_it.py
            action: create
          - path: tests/journeys/work_changes_after_approval/test_upstream_change_marks_the_downstream_signoff_stale.py
            action: create
          - path: tests/journeys/work_changes_after_approval/test_recorded_no_fails_the_next_downstream_merge.py
            action: create
        exit:
          criteria:
            - "A new commit after signoff voids it: Mandate applies the -revised label, posts failure on the new head and records the void"
            - "An upstream change after a downstream signoff (the PRD after the spec is signed) applies the -stale label and the downstream gate must be signed again on its new head"
            - "A recorded no on a non-merge decision (a technical review rejecting the spec) does not stop work, but the next downstream merge fails mandate/gate-decision until the artifact is revised and decided again or the holder withdraws the no"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/work_changes_after_approval"
            expected: "exit 0"
            evidence_expected: "PR body"

      - id: TASK-W1-03
        implements: [REQ-60, REQ-61, REQ-62, REQ-108]
        depends_on: []
        files:
          - path: src/infra_services/attestation_service.py
            action: create
          - path: src/business_services/release/evidence_verification_service.py
            action: create
          - path: src/models/evidence_models.py
            action: create
          - path: tests/journeys/release_a_wave/test_evidence_from_an_edited_caller_is_rejected.py
            action: create
          - path: tests/unit/business_services/release/test_partial_evidence_counts_as_missing.py
            action: create
        exit:
          criteria:
            - "Mandate accepts evidence only when the attestation's signer workflow is mandate-verify at the pinned tag and the commit and protected test-set digest match the target (ADR-007)"
            - "A report, environment manifest and commit binding for the same commit are all required; partial or truncated evidence counts as missing"
            - "The reusable workflow in mandate-verify (merged by named humans only) builds the exact commit into a clean environment, runs the protected test set and attests the bundle"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/release_a_wave"
            expected: "exit 0; the pinned caller's evidence verifies and an edited caller's does not"
            evidence_expected: "PR body"

      - id: TASK-W1-04
        implements: [REQ-63, REQ-109, REQ-122]
        depends_on: [TASK-W1-01, TASK-W1-03]
        files:
          - path: src/business_services/release/merge_service.py
            action: create
          - path: src/infra_services/github_app_service.py
            action: modify
          - path: tests/journeys/release_a_wave/test_wave_merge_allowed_only_on_the_verified_head.py
            action: create
          - path: tests/unit/business_services/release/test_app_applies_the_signoff_and_merges_at_the_verified_head.py
            action: create
          - path: src/business_services/release/unguarded_merge_sweep_service.py
            action: create
          - path: tests/journeys/release_a_wave/test_merge_without_a_passing_check_is_detected_and_reverted.py
            action: create
          - path: tests/journeys/release_a_wave/test_unauthorised_ruleset_change_is_detected_and_escalated.py
            action: create
        exit:
          criteria:
            - "For a wave, mandate/gate-decision also requires run-signed evidence for that exact head; a moved head fails the check and triggers re-verification"
            - "At L0 the merger the workflow names merges once the check passes; Mandate does not merge"
            - "At L2 and L3 Mandate's App applies the three signoff artifacts and merges through the merge API with sha pinned to the verified head (unit-tested here; exercised live when a gate first reaches L2)"
            - "Within one sweep, a merge into develop or main whose head had no passing check, or a gate ruleset change no decided Launchpad run made, is recorded as a policy breach, escalated to the owner, and answered with a revert pull request that goes through the gate; on Mandate's own repos the named emergency humans are the only bypass actors"
          proof:
            kind: command
            command: "make journeys -- tests/journeys/release_a_wave"
            expected: "exit 0"
            evidence_expected: "PR body"

      - id: TASK-W1-05
        implements: [REQ-01, REQ-02, REQ-39, REQ-40, REQ-42, REQ-43, REQ-54, REQ-55, REQ-60, REQ-61, REQ-62, REQ-63, REQ-86, REQ-103, REQ-108, REQ-109, REQ-118, REQ-121, REQ-122]
        depends_on: [TASK-W1-01, TASK-W1-02, TASK-W1-03, TASK-W1-04]
        files:
          - path: src/workflows/walking_skeleton_workflow.py
            action: create
          - path: src/business_services/runner/walking_skeleton_runner_service.py
            action: create
          - path: tests/verify/verify_walking_skeleton.py
            action: create
          - path: tests/fixtures/walking_skeleton/toy_prd.md
            action: create
          - path: tests/fixtures/walking_skeleton/toy_change.patch
            action: create
          - path: docs/specification/as-built/requirements.md
            action: modify
        exit:
          criteria:
            - "On mandate-sandbox-meta a toy PRD pull request is signed at L0 blind-first with the call sealed and never on the PR; the check passes only after the signoff and the merger merges"
            - "On mandate-sandbox-svc one toy wave is verified with run-signed evidence, signed the same way, and merged at the verified head; every step is in the ledger and the chain verifies"
            - "The as-built rows for all W1 requirements are updated with evidence"
          proof:
            kind: command
            command: "python tests/verify/verify_walking_skeleton.py"
            expected: "PASS; ledger chain verifies; each merge commit's parent is the signed, verified head"
            evidence_expected: "PR body and as-built rows"

    verification:
      check: "make check"
      unit: "make test"
      live:
        applicable: true
        mode: sandbox
        command: "python tests/verify/verify_walking_skeleton.py"
        covers: [J-06, J-09, J-16, REQ-40, REQ-42, REQ-43, REQ-60, REQ-61, REQ-62, REQ-63, REQ-86, REQ-103, REQ-108, REQ-121, REQ-122]
        dependencies:
          - ephemeral Paperclip (pinned image)
          - postgres
          - temporal
          - mandate-sandbox-meta and mandate-sandbox-svc with mandate/gate-decision as the one required check
          - mandate-verify at the pinned tag
        fixtures:
          - tests/fixtures/walking_skeleton/toy_prd.md
          - tests/fixtures/walking_skeleton/toy_change.patch
        prerequisites:
          - "Preflight passed (planning/preflight-report.md merged)"
          - "Test App credentials present in ~/.mandate/secrets/test/"
        safe_test_data:
          - "Toy PRD and toy change on namespaced branches of the sandbox repos; a Paperclip company per run"
        steps:
          - "Run verify_walking_skeleton.py; sign each gate on its pull request on GitHub when prompted"
        expected_observations:
          - "Each merge is blocked until mandate/gate-decision passes on the signed head; the ledger chain verifies"
        human_observations:
          - locus: "The two gate pull requests on GitHub"
            expect: "A brief on the PR without the deciding role's call; the call appears only after the signoff is recorded; merging is blocked until the check passes"
            covers: [J-16]
        evidence_expected: "KD's review of the wave's last PR"
        cleanup:
          - "Revert the toy PRD and toy change on each sandbox repo's develop; remove the run's Paperclip company"
        stop_conditions:
          - "Any merge allowed without a passing mandate/gate-decision, any evidence accepted from an edited caller, the call visible on a PR before signoff, or a ledger chain failure: stop and report"
```

