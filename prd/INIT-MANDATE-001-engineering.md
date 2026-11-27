# Mandate: engineering-ready PRD

> **Source of truth.** Exported from the claude.ai design doc on 21 Nov 2026. From this commit on, this file is the source of truth; the claude.ai doc is an archived snapshot. Change it by pull request.

Nov 19, 2026 · @kd

| Field | Value |
| --- | --- |
| Status | Engineering-ready candidate, 19 Nov 2026 |
| Owner | Principal engineer (KD during bootstrap); the PM confirms product intent survived |
| Product intent | [Mandate: product PRD](https://claude.ai/artifact/X1AE8pwvMJxou2RXDQ1f1e) and [product vision](https://claude.ai/artifact/MJn8beQ3JorGSSyUWeDeoR) |
| Grounding baseline | Paperclip a665ed6 (18 Nov 2026); `prayog-skills` d3bc8a1; Launchpad 0.5.39 (30 Sep 2026); GitHub Actions and artifact attestations as documented in Nov 2026 |
| Ids | Reuses the product PRD's `CAP-*`, `J-*` and `REQ-*` unchanged; adds `AD-*` (architecture decisions), `CTR-*` (contracts), `ER-*` (engineering rules) and `EOQ-*` (engineering open questions) |

**What this document is for.** It tells Claude Code what to build and how: the architecture, the seams, the data, the flows and the rules every component follows. It adds no product behaviour; every requirement it serves is in the product PRD. Where it constrains design it says so, and where it leaves a choice to the spec it says that too.

**How it was produced.** The twelve architecture decisions were asked and answered in chat on 19 Nov 2026, each with an explanation, a Conduit example, options and a recommendation. Each decision that depends on Paperclip's behaviour was grounded in Paperclip's code at the baseline commit first.

## 1. Architecture decisions

| Id | Decision | Choice | Why | Serves |
| --- | --- | --- | --- | --- |
| AD-1 | Who owns a work item's state | Split by field. Mandate owns workflow position, gate holders, signoffs, evidence and rungs; collaboration fields stay native to Paperclip. **A gate is a merge into `develop`** (and `develop` into `main`): the PRD, the spec, each wave and the closure purges. Nothing else blocks; every other decision (technical review, triage, hiring, outline acceptance) is recorded in the ledger without stopping work (a recorded no fails the next downstream merge until resolved), and upstream changes mark downstream work `-stale` or `-revised` as the workflow already does. Paperclip carries the agents' work, questions and escalations; it holds no gate | First principles (21 Nov 2026): only unverified work becoming irreversible needs a hard stop, and in the delivery workflow that is a merge into `develop`. Enforcing gates through Paperclip approval stages or extra GitHub rules added failure modes (board overrides, plan limits) without protecting anything a merge check does not already protect | REQ-23, 40, 42, 43 |
| AD-2 | How Mandate learns what happened | Events trigger, state is truth: the plugin forwards Paperclip events; GitHub is polled by the sweep at first, with webhook ingress built, tested and kept disabled behind a policy switch until Mandate has a public endpoint; Mandate reads current state before acting; every action is safe to repeat; a sweep (default every minute) reconciles expected and actual state | Paperclip events reach only plugins, at least once, without ordering; Paperclip itself reconciles; meets nothing-lost and 1-minute responsiveness together | REQ-21, 90 to 92 |
| AD-3 | How workflows run | One generic runner arranging a fixed set of tested building blocks: agent step, gate, fan-out per repo, wave loop, wait for evidence, timer, park. The pinned contract only arranges blocks; each contract version declares the block versions it needs | Workflows stay data where they change; behaviour stays tested code where correctness matters | REQ-21 to 25, 114 |
| AD-4 | Durable execution | Work-item state, pinned versions and timers are rows in Mandate's Postgres; timers fire from the sweep. Self-hosted Temporal (persisting to Postgres) runs only short step workflows. Idempotency keys on every step; an outbox for every state change that leaves Mandate | Weeks-long work never replays history across Mandate upgrades; Temporal's maturity and tooling for the risky, exactly-once moments | REQ-90 to 92, 113, 114 |
| AD-5 | Decision ledger | A hash-chained, append-only ledger separate from working state, holding decisions, sealed calls, promotions, demotions, emergency merges and policy changes, each with evidence hashes; a signed checkpoint of the chain, including the current policy hash, committed daily and signed by an artifact attestation from a workflow in `mandate-meta` | Tampering is detectable even by database administrators; exports can be verified by auditors | REQ-54, 55, 93 to 95, 107 |
| AD-6 | How gates reach people | On the gate's pull request, as the delivery workflow defines. The signoff is three artifacts on the current head: the gate's label (`impact-map-lgtm`, `spec-lgtm`, `wave-accepted`), an Approve carrying the attestation (initiative, head SHA, digests, artifact paths) and the PR marked ready. At L0 the human holder signs on GitHub; Mandate posts the brief on the PR without the deciding role's call, and the call lives only in Mandate's ledger (sealed before the human signs, revealed after), never as a PR comment or review before the signoff. At L2 and L3 the deciding role signs and Mandate's App applies the three artifacts. Non-merge decisions are made as a review on the pull request when there is one, otherwise as a Paperclip question, with the call sealed first either way. Paperclip's inbox carries those questions, product questions and escalations; Paperclip's own decision model stays off | Keeps the team's existing workflow and GitHub surface; blind-first holds because nothing on the PR shows the deciding role's call before the holder signs | REQ-39, 86, 103 |
| AD-7 | Run-signed evidence | A central reusable GitHub Actions workflow in `mandate-verify`, called by each governed repo's caller workflow at a pinned tag, builds the exact commit into a clean environment, runs the protected test set fixed at spec sign-off, and signs the evidence bundle with an artifact attestation (governed repos are public). GitHub Free cannot force a workflow to run, so enforcement sits in Mandate: it accepts evidence only when the attestation's signer workflow is `mandate-verify` at the pinned tag (`--signer-workflow`), with matching commit and test-set digest, and only then posts the required check `mandate/gate-decision`. A PR that edits its CI gets no valid attestation, so the check never posts and the ruleset blocks the merge | The signer is outside the reach of everyone it judges, without turning Mandate into a CI system | REQ-59 to 62, 108 |
| AD-8 | GitHub merge control | One required check on `develop` and `main`: `mandate/gate-decision`, which Mandate posts only when the gate's label, attested approval and ready state all match the PR's current head, the signer held the gate at its rung, the decision is in the ledger, and (for waves) the run-signed evidence verifies. A push after signoff voids it (the workflow's `-revised`). Who presses merge follows the workflow (PM for the PRD, engineering for spec and waves); at L2 and L3 Mandate's App merges. No other branch rule is needed | Exactly the verified commit by construction at Conduit's early load | REQ-63, 109, 121, 122 |
| AD-9 | Policy | Typed values in Mandate's database, edited on the control tower settings page; every change a ledger entry; every decision cites the policy revision | Simple and immediate; tamper-evident through the daily checkpoint | REQ-75 to 77, 110, 111 |
| AD-10 | Deciding-role calls | The deciding role receives the same brief as the human, without the author's recommendation, runs as a Paperclip task, returns a structured call (option, reasons, evidence cited); Mandate seals it in the ledger before the human decision opens and reveals it after; a missing or invalid call is retried once, then counts as no call | Independent, tamper-proof agreement data; the agent-side twin of blind-first | REQ-46, 47, 105, 118 |
| AD-11 | Codebase context | A separate Python service, `mandate-context`: an MCP gateway in front of pluggable engines (level 0 pass-through, level 2 Serena, higher later), indexing per commit, sending Mandate a usage record for every answer; agents fall back to level 0 when it is down | Governance stays independent of the heaviest, most experimental part | REQ-34 to 38 |
| AD-12 | Code structure | A modular monolith in `mandate`: one package per capability with small public interfaces and an enforced import-boundary check; the API, Temporal workers and the sweep run as separate processes from the same code. The control tower is a thin TypeScript plugin holding no state | Small enforced seams for Claude Code; one database keeps the outbox and idempotency rules simple | All |

## 2. System context and components

(The system context diagram is in the archived claude.ai doc; the component table below is authoritative.)

Mandate is a separate Python service beside a forked, pinned Paperclip. People decide in Paperclip's inbox; agents work in Paperclip; code and evidence live in GitHub. Mandate reaches Paperclip only through its API and a thin plugin, and GitHub only through its own App, so neither platform's core is changed.

| Component | Repo | What it does | Owns |
| --- | --- | --- | --- |
| Mandate core | `mandate` | API and plugin backend; generic runner and building blocks; gates, deciding-role calls and autonomy; policy; release and merge control; measures; escalation; sweep and timers; ledger and checkpoint job | Work-item state, gates, rungs, policy, ledger, outbox |
| Temporal (self-hosted) | deployment in `mandate` | Runs short step workflows: post a brief or check, apply a signoff at L2 and L3, request a sealed call, merge a commit, copy an issue | Step history only |
| Postgres | deployment in `mandate` | Mandate's database; Temporal's persistence in its own database | All durable state |
| Control tower plugin | `mandate-control-tower` | Paperclip plugin: control tower page, autonomy map, programme and work-item tabs, my-gates widget, settings page; forwards Paperclip events to Mandate | Nothing |
| Context service | `mandate` (own package and container, PL-1) | MCP gateway in front of pluggable engines (level 0 pass-through, level 2 Serena); indexes per commit; sends a usage record of every answer to Mandate | Indexes |
| Verification workflow | `mandate-verify` | Central reusable GitHub Actions workflow: clean environment, protected test set, signed evidence bundle | Nothing; the signature is the output |
| Meta | `mandate-meta` | Company configuration, daily signed ledger checkpoints, these documents | Checkpoint history |

## 3. Seams and contracts

Every seam is a contract with its own tests. What crosses it is fixed here; field-level schemas are the spec's job.

| Id | Seam | What crosses it | Guarantees Mandate relies on or gives | Requirements |
| --- | --- | --- | --- | --- |
| CTR-01 | Mandate to Paperclip: issues and execution policy | Create and update issues for steps and sealed-call requests; write governed fields; read current state; every write inside a run Mandate obtains by waking its own agent | Every write carries an idempotency key; Mandate refuses to run against an unrecognised Paperclip release | REQ-21, 23, 40, 43 |
| CTR-02 | Mandate to Paperclip: decisions | Questions only (product questions, escalation choices, and non-merge decisions with no pull request: triage, hiring, adding a repo): title, body, options, expiry within Paperclip's 30-day limit, idempotency key; read the choice and decider. Merge gates are not decided here | The decision's signed spec snapshots what was asked | REQ-39, 42, 103 |
| CTR-03 | Plugin to Mandate: event relay | The subset of Paperclip events Mandate needs: issue created, updated and released; comments; approval decided; agent runs started, finished, failed; cost events; budget incidents | At least once, unordered: Mandate deduplicates by event id and treats events only as hints to read state | REQ-90 to 92 |
| CTR-04 | Mandate to agents, through Paperclip | Step work and sealed-call requests as issues assigned to role agents, with structured inputs; results as documents or comments in a fixed schema per artifact type; the deciding-role call schema: option, reasons, evidence cited | Output that fails its schema counts as missing; untrusted content arrives marked (REQ-104) | REQ-25, 104, 118 |
| CTR-05 | Mandate and GitHub, through Mandate's App | Read pull requests, reviews, labels, ready state and workflow runs (polled; webhooks built and kept off); post the brief and the required check mandate/gate-decision; at L2 and L3 apply the gate's label, attested Approve and ready state for the deciding role and merge with sha pinned to the head; update a branch; create and update issue copies | GitHub refuses a merge into develop or main without the check; the check is tied to a head commit, so a push voids it | REQ-63, 68 to 70 |
| CTR-06 | Verification workflow to Mandate: evidence bundle | Test report, environment manifest, commit, protected test-set digest, quarantine list in force, signed with the `mandate-verify` workflow's identity | Mandate verifies signer workflow and pinned commit, the target commit and the test-set digest; anything else counts as missing evidence | REQ-60 to 62, 108 |
| CTR-07 | Delivery contract to Mandate | A versioned `prayog-skills` release: workflows as arrangements of building blocks, required block versions, gate classes, kinds and attributes, id conventions, outline standard, readiness contract | Mandate refuses a contract that needs a block version it lacks | REQ-11, 22, 24, 32 |
| CTR-08 | Launchpad configuration to Mandate | The meta repo's programme, governance (repos, stacks) and service catalogue files at a commit; Launchpad's readiness result for a new repo | Read-only; a repo joins only when its readiness check passes | REQ-01, 99, 100 |
| CTR-09 | Mandate to control tower plugin | Read views scoped to the viewing user; policy edits from the settings page | No endpoint decides a gate | REQ-82 to 87 |
| CTR-10 | Context service | Agents ask over MCP; answers cite repo, path, lines and commit; the service sends Mandate a usage record per answer with engine, level and any fallback | Answers never judge; a fallback to level 0 is recorded | REQ-34 to 38 |
| CTR-11 | Mandate core and Temporal | Step workflow inputs carry work item, step and idempotency key; results come back to Mandate in one transaction with the state change | A step run twice has one effect | REQ-90, 91 |

## 4. Conceptual data model

What Mandate stores, at the level a builder needs to agree on before the spec. Tables, columns and indexes belong to the spec.

| Entity | Holds | Notes |
| --- | --- | --- |
| Programme | Paperclip project, meta repo, calendar and time zone, decision owners per gate class | Created from Launchpad configuration |
| Repo | Name, stack, readiness status, date joined | Joins only after Launchpad's readiness check |
| Role card, hire | Versioned role definition; the agent setup filling it on a programme; probation and two-setup proof status | Hiring is a design gate |
| Work item | Kind, attributes, pinned contract and block versions, current position (block and state), links to Paperclip issue and GitHub issue | One row per item; the runner's state lives here |
| Gate | Class, rung, ceiling, deciding role, minimum-stay clock, hold-for-human flag | Per programme, per gate, per kind |
| Gate opening | One occasion a gate is decided: the PR and its head commit, brief hash, signoff artifacts (label, approval, attestation, ready state), check id, status | Opens, seals, decides, reveals, closes |
| Sealed call | Deciding role's option, reasons and cited evidence, hashed into the ledger before the human decision opens | Revealed after the choice |
| Evidence bundle | References and hashes of report, manifest, test-set digest, attestation; retention clock | Content expires at 30 days or at the gate's next promotion; hashes stay |
| Ledger entry | Sequence, previous hash, own hash, type (decision, sealed call, promotion, demotion, emergency merge, policy change, escalation outcome), payload, version stamp | Append-only; separate from working state |
| Checkpoint | Chain head hash, policy hash, signature, commit in `mandate-meta` | Daily |
| Policy revision | Typed values, author, reason, effective from | Every decision cites one |
| Timer | What fires, when, for which work item | Fired by the sweep |
| Outbox message | Action leaving Mandate, idempotency key, status | Written in the same transaction as the state change |
| Inbound event | Source, event id, received at | Deduplication only |
| Product question | Question, scenario, example, recommendation, blocking flag, answer, round | Readiness stage |
| Escalation | Trigger, target agent then humans, resolution | Agent outside the dispute first |
| Step run measure | Times, waiting time, human minutes, rework rounds, cost, version stamp | Feeds measures and DORA benchmark |
| Context answer record | Question type, repo, commit, engine, level, fallback, latency | From the context service |

## 5. Key flows

### Gate lifecycle

Gate lifecycle at L0 (a gate is a merge into `develop`, or `develop` into `main`):

1. **PR ready to sign.** The gate's pull request exists with the artifact at its head (PRD, spec, wave or closure purge).
2. **Brief posted.** Mandate posts the brief on the pull request, bound to the head commit.
3. **Call requested.** The deciding role gets the brief, without the author's recommendation.
4. **Call sealed, never on the PR.** Its hash goes into the ledger before the holder signs; nothing of it appears on the pull request.
5. **Holder signs.** On GitHub, under their own identity: the gate's label, an Approve carrying the attestation, and the pull request marked ready.
6. **Mandate checks.** The signoff matches the head, the signer held the gate at its rung, and for a wave the run-signed evidence verifies.
7. **Recorded and revealed.** The decision goes into the ledger; the call is revealed on the pull request; agreement is counted.
8. **Merge allowed.** Mandate posts `mandate/gate-decision` as success on that head, and the workflow's merger merges. A push after signoff voids it.

A gate is a merge into `develop` (or `develop` into `main`), signed on its pull request. At L0 the human holder signs on GitHub with the gate's label, an Approve carrying the attestation and the PR marked ready; the deciding role's call was sealed in the ledger before and is never shown on the PR until the signoff is recorded. At L2 the deciding role signs, Mandate's App applies the three artifacts, and the veto window runs before the check is posted; at L3 the check is posted at once. A push after signoff voids it (`-revised`); an upstream change marks it `-stale`. Work before the merge is never held: agents keep going, and a sent-back PR is ordinary rework.

### Release of a wave

1. The coder opens the wave's draft PR; its caller workflow runs `mandate-verify` at the pinned tag on that commit.
2. Mandate fetches the attested evidence bundle and verifies the signer workflow, commit and test-set digest. Anything that fails counts as missing evidence and goes back to the coder as findings.
3. Mandate posts the brief on the PR (gate lifecycle above). The verifier's interpretation is part of the brief.
4. The holder signs (`wave-accepted`, attested Approve, ready). Mandate checks the signer held the gate, the artifacts match the head and the evidence verifies, records the signoff, and posts `mandate/gate-decision`.
5. The merger merges into `develop` (at L2 and L3, Mandate's App, with `sha` pinned to the head). If `develop` moved, the branch is updated, verification reruns, and a new signoff is needed only if the evidence changed.
6. Mandate records the merge in the ledger, updates the issue copy, links deployment status, and the runner starts the next wave.

### Promotion and demotion

- After every closed gate opening and every outcome that lands, Mandate re-evaluates that gate against the policy revision in force: decisions at the rung, minimum stay, critical misses, and the evidence its class counts (agreement plus clean exercised outcomes at intent and design gates; clean exercised outcomes only at verification and housekeeping gates).
- A pass promotes one rung (L0 to L2 at intent and design gates), writes a ledger entry with the evidence, hands the gate to its deciding role, and informs the owner and decision owner.
- An overrule or failed outcome demotes one rung at once; a policy breach drops the gate to L0. Emergency merges are excluded from all of it.

### Recovery

- On restart, the runner reads each work item's row and carries on; in-flight Temporal steps resume; the outbox resends anything not yet acknowledged; idempotency keys make every repeat harmless.
- The sweep compares expected and actual state in Paperclip and GitHub every minute and fires due timers. While either platform is unreachable, nothing advances and no gate is decided.

### Emergency path (Mandate's own repos only)

- A named human merges directly in GitHub using the bypass only they hold. When Mandate returns, the sweep finds the merge, records it in the ledger with its evidence, and opens a follow-up review due within the policy window. Any governed programme's work that waited is then merged by Mandate as normal.

### A repo joins

- The design gate accepts the repo; the platform engineer adds it to the meta repo's configuration and runs Launchpad; Mandate reads Launchpad's readiness result and takes the repo in, registering it with the context service and the verification workflow's branch rules. Its first feature wave waits for the platform contract.

## 6. Engineering rules

Every component follows these; each has a check in the build or a test.

| Id | Rule | Why |
| --- | --- | --- |
| ER-01 | Every step and every write to Paperclip or GitHub carries an idempotency key derived from the work item and step, so a repeat has one effect | Nothing runs twice (REQ-91) |
| ER-02 | A state change and the action it causes leave in one transaction through the outbox; a sender delivers and retries; receivers are idempotent | Two stores (Mandate, Temporal) never disagree after a crash |
| ER-03 | Events are hints. Mandate reads current state from the source before acting on any event | Events are at least once and unordered |
| ER-04 | Mandate's code applies typed policy rules, schema checks and comparisons only. Any judgement is a role agent's call or a human's decision | Mandate never judges in its own name |
| ER-05 | Every step run and ledger entry carries the version stamp: contract, block versions, skills, rules, agent setup, policy revision, Mandate release | Measures and promotion compare like with like (REQ-78) |
| ER-06 | Content from outside the programme is marked at intake; the mark follows anything derived from it; marked content never sits where an agent reads instructions; briefs show it raw | Untrusted content never instructs (REQ-104) |
| ER-07 | Times are stored in UTC; every window is computed on the programme's calendar and time zone | REQ-110 |
| ER-08 | Secrets live only in Mandate's secret store; they never appear in artifacts, the ledger, logs or exports; no agent holds merge rights | Security attribute |
| ER-09 | When something is unknown or unverifiable (a Paperclip release, a contract block version, a signature), Mandate stops that work and escalates; it never falls back to a default | ADH accepted defaults and fallbacks |
| ER-10 | Every action records its actor; Mandate's own identity performs only mechanical steps the workflow or a recorded decision requires | REQ-40 |
| ER-11 | Personal data is redacted from evidence at intake, before hashing | REQ-107 |
| ER-12 | Packages talk only through their public interfaces; the import-boundary check fails the build otherwise | Claude Code can change one capability safely |

## 7. Requirements to components, with negative paths

Each capability has one owning package in `mandate` (or a separate repo). Negative paths marked ADH are failures the old system had; each becomes an acceptance test.

| Capability | Owner | Negative paths that must be impossible |
| --- | --- | --- |
| CAP-01 Programme setup and growth | `programmes` | Work starting before every role, repo and the workflow are usable; a repo joining before Launchpad's readiness check passes |
| CAP-02 Role catalogue and hiring | `roles` | An agent acting outside its role or programme; a role card counting toward promotion before its two-setup proof |
| CAP-03 Outline intake | `intake` | An initiative without an accepted outline; a resubmitted outline creating a second initiative |
| CAP-04 Kinds and triage | `intake` | A new capability entering as an enhancement unchallenged; a kind change without a recorded reason |
| CAP-05 Workflow execution | `runner` | A transition the pinned workflow does not define; work moving to a newer workflow mid-flight; a contract needing a block version Mandate lacks running anyway |
| CAP-06 Engineering readiness | `readiness` | Spec work starting before the readiness gate passes; a product question answered by anyone but the PM role |
| CAP-07 Shared codebase context | `mandate-context` | An answer without repo, path and commit; a fallback to level 0 not recorded |
| CAP-08 Gate decisions | `gates` | Anyone deciding on work they authored or challenged; an app identity deciding (ADH: second app pre-approving); default, fallback or timeout acceptance (ADH: first allowed option, accepted by default); a decision applied to a changed target; the deciding role's call visible before the human chooses at a blind-first gate |
| CAP-09 Autonomy management | `autonomy` | Promotion on anchored agreement at verification and housekeeping gates; an agent promoting its own gate; promotion from emergency merges; a rung carried across programmes |
| CAP-10 Ledger and outcomes | `ledger` | An entry changed or deleted without the chain breaking against the last checkpoint; a clean outcome counted for a change nobody exercised |
| CAP-11 Governed release | `release` | A merge of a commit other than the verified one (ADH: merge without the verified commit); evidence the run did not sign; a test set other than the protected one; truncated evidence accepted (ADH: evidence cut to fit); a bypass on any repo but Mandate's own |
| CAP-12 GitHub issue copies | `github` | Two issues for one work item (ADH: matching by title); a GitHub edit changing Mandate state |
| CAP-13 Rollout and outcomes | `release` | A rollout step without live health evidence; a revert not linked to the decisions behind it |
| CAP-14 Policy | `policy` | A decision without a policy revision; a programme loosening a company ceiling |
| CAP-15 Measures and evolution | `measures` | A measure without a version stamp; a process change released without replay or canary |
| CAP-16 Control tower | `mandate-control-tower`, `api` | A decision taken from the control tower; a viewer seeing another programme |
| CAP-17 Escalation | `escalation` | Escalation to a party to the dispute; an escalation dropped silently |
| CAP-18 Resilience | `runner`, `ops` | A step lost, repeated or skipped across restart or outage; a gate decided while Paperclip or GitHub is unreachable |
| CAP-19 Audit export | `ledger`, `api` | An export that omits missing evidence instead of marking it; an export an auditor cannot verify against a checkpoint |
| CAP-20 Multi-programme | `programmes` | Work visible across programmes; a shared specialist's record merged across programmes |
| CAP-21 Operating Mandate | `ops` | An upgrade changing pinned work; a restore that loses in-flight work; Mandate failing silently |

## 8. Quality attributes: how the design meets them

| Attribute (product PRD section 10) | Design that delivers it |
| --- | --- |
| Autonomous execution | The runner moves work between gates on events and the sweep (AD-2, AD-3); escalations go to an agent outside the dispute first |
| Integrity | State as rows plus short Temporal steps (AD-4); idempotency and outbox (ER-01, ER-02); read before act (ER-03) |
| Evidence integrity | Central signed verification workflow and signature checks (AD-7, CTR-06) |
| Auditability | Hash-chained ledger with daily signed checkpoints (AD-5); verifiable export |
| Authority | Signoffs only by the holder at its rung; Mandate posts the merge check only after the signoff is recorded in the ledger (AD-6, AD-8, ER-10) |
| Security | Nothing merges into develop or main without Mandate's check (AD-8); secret store (ER-08); untrusted content marked (ER-06); Paperclip's decision model off |
| Isolation | Programme scoping in every query and in the plugin's API (CTR-09) |
| Privacy | Redaction at intake (ER-11); 30-day evidence retention with hashes kept |
| Recovery within 1 hour | One Postgres and Temporal on Postgres, backed up with point-in-time restore; stateless processes restart; the sweep repairs gaps |
| Responsiveness within 1 minute | Events as triggers with a one-minute sweep behind them |
| Platform independence | API and plugin only; refuse unknown Paperclip releases (ER-09) |
| Buildability | Modular monolith with enforced boundaries (AD-12, ER-12); test strategy in section 9 |

## 9. Test strategy

| Layer | What it proves | Runs |
| --- | --- | --- |
| Acceptance tests | Every requirement has at least one test tagged with its REQ id; the build fails if a requirement has none | Every change |
| Journey scenarios | Each of J-01 to J-29 runs end to end against real Paperclip (an ephemeral pinned instance per run) and real GitHub (sandbox repos, namespaced per run), with deterministic real agents; no fakes (PL-5) | Every change |
| Sandbox end to end | After the last wave of INIT-MANDATE-001 (the sandbox fix stage), every journey runs against real Paperclip, real GitHub and real agents on `mandate-sandbox`, a small throwaway programme (a meta repo plus one or two toy repos) created through Launchpad. Failures are fixed in Mandate until every journey passes; the phase 0 checks run here before any code | Phase 0, the sandbox fix stage, then nightly |
| Contract tests | Each seam (CTR-01 to 11) live against the pinned Paperclip release and the sandbox's GitHub repos; no recordings | Every change and nightly |
| Fault injection | Processes killed mid-step; events duplicated, reordered and dropped; webhooks lost; Paperclip or GitHub unreachable. Nothing lost, repeated or skipped; no gate decided while a platform is down | Every change |
| Property tests | Ledger chain verifies and detects any edit or deletion; idempotency holds for every step | Every change |
| Autonomy simulation | Synthetic decision streams, including anchored agreement, critical misses, unexercised changes and emergency merges, show that gates promote and demote exactly as policy says | Every change to `autonomy` or `policy` |
| Security tests | Hostile issue text (J-29); forged or unsigned evidence; a changed test set; attempts to merge without the check, or with a check on an old head; a signoff by someone who does not hold the gate; attempts to decide through an app identity | Every change |
| ADH regressions | Each of the twelve ADH review findings as a named test | Every change |
| Upgrade tests | Work pinned to an older contract and block versions keeps running correctly across a new Mandate release (REQ-114) | Every release |
| Drills | Point-in-time restore with in-flight work (REQ-115); emergency merge on Mandate's own repo (REQ-109) | Quarterly |
| Conduit acceptance run | Once Mandate is complete, Conduit is onboarded and delivered by Mandate; every issue found is fixed in Mandate and the run continues | Once, after the sandbox fix stage |

## 10. Impact per repo

| Repo | Change |
| --- | --- |
| `mandate` (new, Python) | Core service: packages per capability, Temporal workers, sweep, checkpoint job, API; deployment for Postgres and Temporal |
| `mandate-control-tower` (new, TypeScript) | Paperclip plugin: views, settings page, event relay; no state |
| `mandate-context` (new, Python) | MCP gateway, engine adapters (level 0, Serena at level 2), per-commit indexing, usage records |
| `mandate-verify` (new) | Central reusable verification workflow: clean environment, protected test set, signed evidence bundle |
| `mandate-meta` (new) | Company configuration, daily ledger checkpoints, product and engineering documents |
| `prayog-skills` | Contract v3: building-block vocabulary and versions, workflows as block arrangements, gate classes, the nine kinds and attributes, outline standard, readiness contract, id conventions moved out of prompts (OQ-01 decides whether this is a parallel initiative) |
| Paperclip fork | No code change. Pinned release; telemetry off; Paperclip's decision model off for Mandate programmes |
| Launchpad | Closes OQ-11 to 13: no GitHub project board for Mandate programmes; delivery labels only display state; a programme-scoped token for the platform engineer's tooling; a readiness result Mandate can read |
| Conduit repos | New repos created through Launchpad (greenfield; nothing is reused from earlier work); onboarded as the first programme only after Mandate is complete, as Mandate's acceptance run (issues found are fixed in Mandate); until then Mandate is built and tested against mandate-sandbox, a throwaway programme created through Launchpad; branch rules requiring `mandate-verify` and the merge check mandate/gate-decision |

### Project layout

Decided in chat on 19 Nov 2026, one question at a time (PL-n). INIT-MANDATE-001's first wave builds this layout whole.

**PL-1 Repos (closes product OQ-03).** All public, in `drivestream-lab`. Repos are split wherever the trust boundary differs.

| Repo | Holds | Who can merge |
| --- | --- | --- |
| `mandate` | Python modular monolith; `mandate-context` is its own package and container inside it, kept apart by the import-boundary check | Mandate's App once Mandate governs itself; until then human review of Claude Code's work (REQ-120) |
| `mandate-control-tower` | TypeScript Paperclip plugin | As `mandate` |
| `mandate-verify` | The reusable verification workflow only; every governed repo references it by pinned tag | Named humans only, never a programme's agents |
| `mandate-meta` | Launchpad meta repo for Mandate's own programme; daily ledger checkpoint commits | As `mandate`, checkpoint written by its workflow |
| `mandate-sandbox-meta`, `mandate-sandbox-svc` | The sandbox programme: Launchpad meta repo and one toy service; a second toy repo is added during the sandbox fix stage to exercise adding a repo | Mandate's App, as for any governed programme |

**PL-2 Inside `mandate`.** `mandate` is a standard `python-backend` repo under `python-services-rules` (v0.5.12 read on 19 Nov 2026), mounted as a submodule at `.cursor/rules/` and never edited in place. The rules' layered `src/` layout, naming, DI, typing and tooling apply unchanged; the section 7 capabilities become sub-packages inside each layer.

```
src/
  main.py, app.py            entry and composition root (API process)
  worker_main.py             Temporal workers and the sweep
  context_main.py            mandate-context gateway (own container)
  configs/  logging/  di/  exceptions/  utils/
  api/                       plugin backend, webhooks (built, disabled), health
  business_services/<capability>/   *_service.py per use case
  engine/<capability>/       pure rules, no IO: promotion and demotion, policy evaluation, ledger hash chain, wave planning
  workflows/                 Temporal workflow definitions; activities call business services
  infra_services/            paperclip, github_app, temporal, litellm, context engine clients (*_service.py)
  database/postgres/repository/<capability>/   database/postgres/schema/
  models/<capability>_models.py   every Pydantic model
```

Rules applied as written: pyright `strict` from the first commit; Pydantic v2 at every boundary, never a `dict`; closed vocabularies as `StrEnum` with a `Type` suffix; no `Any`, no `# type: ignore`, no `TYPE_CHECKING` imports; `injector` with `@inject`; loguru; Alembic; Poetry, Black, Ruff.

**Extension points** are typed `Protocol`s with a `StrEnum` registry, bound in `di/modules/`: building blocks (AD-3), context engines (REQ-36), outcome checks per gate class, merge strategy (AD-8). Adding one is a class, an enum value and a binding; pyright flags every unhandled `match`.

**Import contracts** (import-linter, CI): the rules' layer contract (`api` → `business_services` → repository → schema); `engine` imports no IO layer; `workflows` imports `business_services` and `models` only; the `mandate_context` entrypoint imports only `models`, `engine` and its own infra client.

**Upstream change:** one pull request to `python-services-rules` adds `workflows/` (durable workflow definitions) to the standard package table, since the rules have no slot for it today.

**PL-3 Where the documents live.** Once the layout questions close, these documents are exported to the repos, which become the source of truth; the Claude docs are then marked as archived snapshots. The export is the first commit to `mandate-meta`, before W1. It follows Launchpad's meta conventions and the rules' truth hierarchy (`.cursor/rules/` how, `docs/specification/product/` what, `adr/` why, `as-built/` what is live).

| Location | Content |
| --- | --- |
| `mandate-meta/planning/` | Product vision |
| `mandate-meta/prd/INIT-MANDATE-001.md` | Product PRD |
| `mandate-meta/prd/INIT-MANDATE-001-engineering.md` | This engineering-ready PRD |
| `mandate-meta/Implementation-Plan-INIT-MANDATE-001.md` | Wave plan; section 9 is the WorkManifest under the pinned prayog contract |
| `<repo>/docs/specification/product/` | That repo's slice: its requirements, contracts and data model |
| `<repo>/docs/specification/adr/` | AD-1 to AD-12 and PL-1 onward as ADR-001 and up; immutable, superseded only by a new ADR |
| `<repo>/docs/specification/as-built/` | One row per requirement (implemented, unit-tested, live-verified), starting empty |

Every PR updates spec, tests and as-built together (same-PR discipline) and names the initiative, issue, spec paths and verify command.

**PL-4 `mandate-control-tower`.** Scaffolded with Paperclip's `create-paperclip-plugin` against the SDK at the pinned baseline commit: typed manifest, worker entrypoint, UI on the SDK's hooks and host components, tests on `@paperclipai/plugin-sdk/testing`. TypeScript `strict`. The Mandate API client is generated from Mandate's OpenAPI schema; CI regenerates it and fails on any diff, so a Pydantic change either flows through or breaks the build. The plugin holds no logic and no state: UI and event forwarding only, and no second place to decide (REQ-86). It is enrolled under a new Launchpad stack, `paperclip-plugin`, whose constitution is a new short rules repo, `paperclip-plugin-rules` (strict TypeScript, generated client only, SDK hooks and host components only, no business logic).

**PL-5 Testing without fakes.** Mandate is tested against the real systems; nothing fakes Paperclip, GitHub or the agents. Where a condition cannot be produced live, it is validated by a unit test on the pure function that handles it.

| Situation | How it is tested |
| --- | --- |
| Rules (promotion, demotion, policy, ledger chain, wave planning) | Unit, property and simulation tests on `engine/` with an injected clock |
| Outages mid-flow | Network fault proxy (Toxiproxy) between Mandate and real Paperclip and GitHub; Mandate workers killed mid-step |
| Duplicate, reordered or lost events | Real captured Paperclip events replayed into Mandate's ingest twice, out of order or with one missing |
| Races (head moves before merge) | Test-only pause points in Mandate, then a real push. Pause points are a typed extension, off by default and refused at startup in production |
| Hostile cases | Real negatives: a genuine attestation from the wrong workflow, a real PR editing the protected test path, a real decision attempt from an app identity |
| Parallel runs | An ephemeral Paperclip from the pinned image per run, with its own database, in a local Compose stack; GitHub work namespaced per run; a dedicated test installation of Mandate's App |
| Role agents | Deterministic real agents: real Paperclip agent identities whose adapter returns scripted, schema-checked outputs without calling a model |
| GitHub-shaped errors (for example a 502 on merge) | Unit test on the pure response-handling function; the live run proves the network-fault equivalent |

Layout: `tests/unit/`, `tests/properties/`, `tests/simulation/` (pure, every push); `tests/journeys/` and `tests/fault/` (live, every PR); `tests/verify/` (sandbox and Conduit stages). Every test carries its REQ ids and the build fails if a requirement has none.

**PL-6 Where checks run.** Building Mandate runs every check locally; GitHub Actions runs only the two trust anchors.

| Where | What | Why |
| --- | --- | --- |
| Local, Mandate's own repos | `make check` (Black, Ruff, pyright strict, import-linter); `make test` (unit, properties, simulation); `make journeys` (live, against an ephemeral local Compose stack of pinned Paperclip, Postgres and Temporal, plus real GitHub sandbox repos). pre-commit on commit, pre-push on push; `mandate-runner` runs the same commands on each PR's head and posts `mandate/build-verified`, which a task merge requires (PL-16, REQ-120) | Ordinary hygiene; fastest loop; no Actions CI to maintain; evidence no agent can post |
| GitHub Actions | `mandate-verify` on governed repos (sandbox, then Conduit) and the checkpoint workflow in `mandate-meta` | The run's own identity signs the evidence and the checkpoint, which no agent controls (AD-5, AD-7, REQ-108); free for public repos |

When Mandate's own development joins as programme two, its repos switch from `mandate-runner` and the build-mode rules to the reusable `mandate-verify` workflow and Mandate's own gates; both already live in `mandate-verify`.

**PL-7 Secrets.** Secret values live outside every repo in `~/.mandate/secrets/<env>/` and reach the Compose stack as Docker secrets. `AppSettings` (per the rules) reads file paths, never values, and fails at startup if a file is missing; `.env.example` lists the paths. Each environment (lab, test) has its own GitHub App installation and private key and its own Paperclip identity token; the test installation is limited to the sandbox repos, so a test run cannot merge into Conduit. Agent workspaces never mount the secrets directory. Held this way: the GitHub App private key, the Mandate Paperclip identity token, and the Mandate and Temporal database credentials. On a later always-on host, the same paths map onto that host's secret store.

**PL-8 Database layout and ledger protection.** One database, `mandate`, with one Postgres schema per capability (`gates`, `ledger`, `autonomy`, `policy`, `runner` and the rest, matching the PL-2 sub-packages); each repository touches only its own schema. Roles split by duty: `mandate_owner` owns every object and is used only by the human-run migration script; `mandate_app` is the runtime role, with read and write on its tables but only `INSERT` and `SELECT` on `ledger.entries`. A trigger rejects `UPDATE` and `DELETE` on the ledger, even for the owner, except in a migration explicitly marked for it. One Alembic history, created and applied as the rules require (agent runs `create_postgres_migration.sh`, a human runs `run_postgres_migration.sh`). A decision, its ledger entry and its outbox row commit in one transaction (AD-4). The database prevents tampering; the hash chain and checkpoint (AD-5) detect it.

**PL-9 Pull requests within a wave.** One PR per task: one requirement or a small, tightly linked group, with spec, tests and as-built updated together; guide size about 400 changed lines, excluding generated code. Branches follow Launchpad's enforced branching policy: `feature/INIT-MANDATE-001-w<n>-<task-slug>` into `develop`, with `fix/`, `hotfix/` and `chore/` as Launchpad defines them; the WorkManifest in the implementation plan lists the tasks per wave. Each PR passes `make check` and `make test` locally, and `make journeys` for every journey it touches, with the output attached; the PR names the initiative, issue, spec paths and verify command, and each merge, review and signoff is recorded in the ledger's format (REQ-120). A task PR merges under the build-mode rules (PL-16); a wave closes when all its tasks have merged, its full journey set passes live, and KD signs the wave PR from `develop` into `main`.

**PL-10 Deterministic test agents.** Real Paperclip agents on Paperclip's built-in `process` adapter, running Python scripts from `mandate/tests/agents/`. The scripts reuse Mandate's `models/` for their output schemas, so a schema change breaks them in the same PR; one script per end-to-end flow names each role's scripted step; agent identities are created per run in the ephemeral Paperclip. No new adapter and no new repo.

**PL-11 Purpose names in the codebase.** Serial ids (REQ-nn, J-nn, CTR-nn, ER-nn, AD-n, PL-n) belong in the PRDs, tables and docs, never in names in the codebase. Modules, test files, test functions, scripts, fixtures and branches are named for what they do: `tests/journeys/spec_to_release/test_release_merges_only_the_verified_commit.py`, `tests/agents/spec_to_release.py`, `test_board_move_to_done_is_rejected_while_approval_pending`, branch `feature/INIT-MANDATE-001-w3-protected-acceptance-tests`. Ids appear in code only as traceability metadata, `@pytest.mark.req("REQ-63")`, which the coverage check reads to fail the build when a requirement has no test.

**PL-12 Sandbox service.** `mandate-sandbox-svc` is a `python-backend` service scaffolded through Launchpad from `python-fastapi-foundation`, under `python-services-rules`, with one in-memory resource (`/items`) and no database. It goes through the same stack, constitution, harness and scaffold path as Conduit's backend, so onboarding is tested for real, and it is small enough that any failure on the sandbox is Mandate's. The second toy repo added during the sandbox fix stage uses the same template.

**PL-13 Branch model and what Mandate governs.** Launchpad's enforced branching policy (GitFlow: `develop` integration line, `main` release line) is adopted unchanged. On governed repos every merge into either line is a gate, enforced by one required check, `mandate/gate-decision`:

| Merge | Gate | Signoff label | Merged by at L0 | Default holder at L0 |
| --- | --- | --- | --- | --- |
| PRD PR into meta `develop` | `prd-impact-acceptance` (intent) | `impact-map-lgtm` | PM | Principal engineer |
| Spec PR into app `develop` | `coding-readiness` (design) | `spec-lgtm` | Engineering | Principal engineer |
| Wave PR into app `develop` | `wave-acceptance` then `wave-signoff` (verification) | `wave-accepted` | Engineering | Release holder |
| Closure purge PRs | `initiative-closure-signoff-app` and `-meta` (housekeeping) | as the workflow defines | Engineering, product | Engineering gate |
| `develop` into `main` | Production release (verification); `mandate-verify` on the head being promoted | as the workflow defines | Launchpad's `release-managers` | `release-managers`; held for a human by default policy, which the owner may relax |

At L2 and L3 the deciding role signs and Mandate's App applies the label, attested Approve and ready state, and merges. `technical-review-approval` and the clarification checkpoints are recorded decisions and questions, not gates.

While Mandate itself is built (REQ-120), the same lines apply without Mandate: feature PRs go to `develop` under human review, and a human promotes `develop` to `main`.

**PL-14 Launchpad enforcement under Mandate (product OQ-12).**

| Launchpad mechanism | On governed repos | On Mandate's own repos while it is built |
| --- | --- | --- |
| Branch protection | One required check, `mandate/gate-decision`, on `develop` and `main` | Launchpad default; the human review is the gate (REQ-120) |
| `require_pr_reviews` | 0; the attested Approve is part of the signoff Mandate checks, not a GitHub count | 1 |
| Merge | The workflow's merger at L0; Mandate's App at L2 and L3; GitHub refuses either without the check | Human |
| `*-lgtm`, `wave-accepted` labels | Part of the signoff; Mandate reads them at L0 and applies them at L2 and L3; `-revised` and `-stale` as the workflow defines | As Launchpad |
| Review roles | Mapped to gate holders by rung | Human reviewer |
| Seeded `ci.yml` | Replaced by a small caller of `mandate-verify` | None (PL-6) |
| `policy-branch-name`, `policy-merge-source` | Kept | Kept |

**PL-15 Launchpad credentials (product OQ-13).** Launchpad runs under its own GitHub App, the Launchpad App, executed by a Mandate worker and never by an agent. Its key is held like Mandate's other secrets (PL-7) and never mounted into an agent workspace. The platform engineer agent proposes the run as a reviewed meta repo change (repo, stack, YAML); once the design gate is decided (REQ-99), the worker runs `init-client` and `apply-harness` on the merged config only. Mandate then reads the branch rules back to confirm they are in force; the sweep detects any branch-protection change not made by a decided Launchpad run, reverts it and escalates.

Grounding note: Launchpad 0.5.39 authenticates with a fine-grained factory PAT (`GITHUB_TOKEN`), not a GitHub App. Until Launchpad supports App authentication, the Mandate worker holds that factory PAT under the same rules (outside every repo, never mounted into an agent workspace, separate per environment). Moving Launchpad to App authentication is an upstream change to Launchpad, needed before Conduit's fix stage, when an agent first triggers a Launchpad run.

**PL-16 Build mode: a Claude Code swarm** (decided 21 Nov 2026, BP-1 to BP-8). Until Mandate's own development joins as programme two, Mandate is built by Claude Code only, organised as Mandate's own role cards run by hand. No other AI tool, CI service or GitHub Actions runner takes part.

| Role | Does | Never does |
| --- | --- | --- |
| Lead | Reads the WorkManifest and repo state, starts every task whose dependencies are merged (at most 3 builders), runs `merge_task.sh` on runner-green heads, plans the next wave, opens the wave PR | Write code, merge by judgement |
| Builder (one per task) | Code, tests and as-built row in its own worktree and branch; opens the task PR | Touch files outside its task; review its own work |
| Challenger | Read-only review against the spec, ADRs and exit criteria, reading them before the diff; posts an Approve or findings on the head commit | Edit code |
| Second challenger | An independent second review on the ledger, the signoff check, evidence verification and merge control | Edit code |
| Verifier | Deploys each PR head and runs `make verify` as a black-box test, checks the deployed app's tables and logs against the exit criteria, posts that evidence on the PR, and turns runner failures into findings and bug issues; in wave mode it checks the lab deploy and posts the wave signoff (BP-10) | Edit code, post a commit status, or produce the runner's grading |
| Integrator | Keeps open PRs current with `develop` and resolves conflicts | Change what a task does |

| Decision | Choice |
| --- | --- |
| Human gate (BP-1 B, amended 27 Nov 2026 as BP-10) | No person's account takes part in the flow. Task PRs merge through the builder App on the runner's check. A protected-path PR needs a second, independent challenger Approve. A wave close is signed by the challenger App after the verifier has checked the deployed evidence. KD audits and can suspend the builder App at any time |
| Grading (BP-2 A) | `mandate-runner`: a plain-code service (no model) living in `mandate-verify`, Mandate's verification trust anchor (human-merged only), run as a container on the lab's `lab_local` network under its own GitHub App. `mandate-verify` thus holds verification for both modes: the reusable workflow for governed programmes and the runner for the build. PR code runs only in a sidecar with its own Docker engine and no build secrets; only the runner holds its key and calls GitHub. It polls open PRs every 30 seconds, checks out the exact head, runs its pinned command set (`make check`, `make test`, `make journeys`) in a fresh stack, and posts the required check `mandate/build-verified` bound to that commit. After every merge into `develop` it deploys that head to the lab stack and runs every journey built so far against the sandbox repos; a failure opens a bug issue linked to the merge, and no task merges until it is fixed. Its key is mounted only into its own container |
| How the swarm runs (BP-3 A) | One lead with builder and challenger subagents, each in its own git worktree |
| Challenger independence (BP-4 C) | Builders on Sonnet 5.5; challengers on Opus 5.5, read-only, spec first; a second independent Opus challenger on the four trust-critical capabilities |
| Wave close (BP-5 A, amended by BP-10) | A wave PR from `develop` into `main`, opened by the builder App with a brief (tasks merged, journeys run, findings, spend) and the runner's full-journey check on its head. The verifier checks the lab deploy of the develop head against every exit criterion of the wave and posts the evidence; the builder App adds `wave-accepted` and marks it ready; the challenger App posts the signoff (`Signoff: wave`, `Initiative`, `Head`); the builder App merges it. The next wave starts only after `main` moves |
| Protected paths (BP-6 B) | `CLAUDE.md`, `.claude/agents/`, the `.cursor/rules` submodule, `docs/specification/adr/`, `docs/specification/product/`, `tests/journeys/`, `tests/verify/`, `Makefile`, tool settings in `pyproject.toml`, `.importlinter`, `.pre-commit-config.yaml`. A PR touching any of them needs a second, independent challenger Approve, which asks above all whether the change makes the swarm's own work easier to pass (BP-10) |
| Running the lead (BP-7 B, amended 27 Nov 2026) | The lead is a Claude Code session working this plan wave by wave with KD's inputs, started with KD's `GITHUB_TOKEN` removed. It rebuilds its state from GitHub and the repos (WorkManifest, as-built table, PR states and checks, and a pinned build-log issue in `mandate` it appends to) every time it starts or resumes, so a lost session loses nothing. The `make swarm` loop was built (mandate PR 3) and removed by KD's decision (mandate PR 7) |
| Bootstrap (BP-8 A, amended by BP-10) | Wave B0 builds the swarm: `mandate-runner` in `mandate-verify`, the rulesets on `mandate` and `mandate-control-tower`, the agent definitions and the lead's section of `CLAUDE.md`. KD created the GitHub Apps and applied the rulesets. B0's last PRs went through the same App-only flow as every later PR (one PR per repo, verified as a whole); nothing merges into `main` until KD says so |

**Merging.** The builder App, `mandate-builder`, merges task PRs into `develop` and wave PRs from `develop` into `main` on `mandate` and `mandate-control-tower`, always pinned to the head commit, and only when `mandate/build-verified` passes on that head. The runner encodes every review rule, so its check is the only signal a merge follows. The swarm's tokens are scoped to those two repos, so it cannot write to rulesets, `mandate-verify` or `mandate-meta`, and it is never Mandate's own App.

**Identities.** Kept apart: KD, whose account (and `0xbeefdead`) never takes part in the flow (BP-10); `mandate-builder` (the swarm pushes, opens PRs and merges); `mandate-challenger` (the only identity whose Approve counts, since GitHub does not let an identity approve its own PR); `mandate-runner` (grades and deploys); and Mandate's own test and lab Apps, which the swarm never uses. The runner is the single enforcer: `mandate/build-verified` is the one required check, and it encodes the review rules. Keys are kept apart by convention for now (BP-9 A): each role reads only its own folder under `~/.mandate/secrets/build/`; per-role containers can be added later without changing the rest. The Apps were created with broad permissions and access to all repos in the organisation by KD's choice on 21 Nov; narrowing them later changes nothing else in this design.

**Signoff by GitHub Apps only (BP-10, decided 27 Nov 2026).** KD decided that no person's account takes part in the build flow: code is generated, a PR raised, the head deployed and verified as a black box, the evidence checked in tables and logs, and then the GitHub Apps approve and merge. In the runner's config the wave signer is the challenger App (`signer_login`), and no rule counts a person's review: a protected path or the fix for a red `develop` needs `Challenger: first` and a separate `Challenger: second`; a wave PR needs the label, ready and the challenger App's `Signoff: wave` review with the attestation. This replaces KD's Approve on protected paths and KD's wave signoff (BP-1, BP-5, BP-6). What it gives up: no human looks at a change to the grading rules or a wave before it merges; the second challenger's adversarial check on protected paths and the verifier's evidence stand in for that, and KD audits afterwards. The rulesets stay a human action.

**Stop conditions.** A task that fails three rounds goes to KD. A red journey on `develop` stops all task merges until fixed. Spend at 80% of a wave's cap alerts KD. A spec question goes to KD and the lead waits; it never chooses silently. Suspending the builder App stops all merging at once.

## 11. Preflight

Preflight, run on the sandbox repos against the real lab Paperclip before W1. Revalidated on 21 Nov 2026 for the simplified gate model (gates are merges into `develop`, signed on the PR): the approval-stage, App-only-merge and required-workflow checks no longer apply. A failure changes the design before code is written.

| Check | Decision it proves | Pass when |
| --- | --- | --- |
| A required check posted by Mandate's App gates the merge into `develop` | AD-8 | With `mandate/gate-decision` required on `develop`: a merge without it is refused, a merge with it on the current head succeeds, and a push after the check leaves the new head without it, and an org owner's merge without the check is refused too |
| A signoff is readable, and writable by the App | AD-6 | Mandate reads a human's label, Approve review body (attestation) and ready state for the PR head; the App can apply a label, submit an Approve with an attestation body and mark a draft ready |
| A reusable `mandate-verify` workflow attests the run, and an edited caller fails verification | AD-7 | `gh attestation verify --signer-workflow` passes for the pinned caller and fails for an edited one |
| Mandate works in Paperclip inside its own run | AD-1, CTR-01, CTR-02 | Mandate wakes its agent, creates an issue and opens a question decision with `X-Paperclip-Run-Id`, with no agent- or skill-creation permission; the choice and decider read back |

Moved to later waves: plugin event forwarding (W5), `process` agent round trip (proved in W0 itself), coding-agent workspaces (before the sandbox fix stage), polling budget (arithmetic), webhook endpoint (tested in the wave that builds it), restore drills (W9), Launchpad readiness output (W4). The first run's results (`mandate-meta` PR 2) stand for decisions and the decision model; its approval-stage findings are superseded by this model.

## 12. Engineering open questions

| Id | Question | Decision (19 Nov 2026) |
| --- | --- | --- |
| EOQ-01 | GitHub plan and repo visibility | Governed repos are public, so GitHub artifact attestations sign evidence on any plan; no Sigstore fallback |
| EOQ-02 | Where does Mandate run? | `drivestream-lab/dev-infra-lab` (shared lab: Postgres, Redis, LiteLLM on the `lab_local` network) is extended with Temporal and Paperclip; Mandate runs in Docker as an overlay on the same network |
| EOQ-03 | Temporal topology | In `dev-infra-lab`, persisting to its own database on the shared Postgres |
| EOQ-04 | Paperclip release cadence | In `dev-infra-lab`, pinned to the baseline release; upgraded only after contract tests pass |
| EOQ-05 | Two-setup proof per role card | One agent setup runs live; the second is proven on a replay of past briefs before the role's decisions count toward promotion |
| EOQ-06 | Ledger checkpoint signing | No key: Mandate commits the ledger head to `mandate-meta`, and a workflow there signs it with an artifact attestation under its own identity |
| EOQ-07 | Mandate's identity in Paperclip | A dedicated Mandate agent identity that never runs work and holds only the permissions to create and update issues, open question decisions and read state; no permission to create agents, skills or assign tasks (phase 0, 21 Nov 2026); Paperclip requires every agent write to carry `X-Paperclip-Run-Id`, so Mandate's Paperclip client wakes its own agent (`POST /api/agents/:id/wakeup`) to obtain a run and tags each write with it, which makes every Mandate write attributable to a run |
| EOQ-08 | Language servers for level 2 on Conduit | Serena's language servers for the stacks Conduit's walking skeleton chooses; fixed when that initiative decides the stacks |
| EOQ-09 | Sweep interval | Adaptive, as policy: every minute while any work waits at a gate or for evidence, every 5 minutes when idle |

**Deployment model (EOQ-02, decided 19 Nov 2026).** Two tiers on the shared `lab_local` Docker network:

| Tier | Runs | Owned by |
| --- | --- | --- |
| Shared infrastructure, `dev-infra-lab` | Postgres, Redis, LiteLLM, Temporal and its UI, Paperclip | The lab; shared by every product, upgraded on its own schedule |
| Mandate, its own Compose stack | Mandate's API, Temporal step workers, sweep, checkpoint job; `mandate-context` as a separate container | Mandate; deployed and restarted without touching the lab |

Rules that make the split hold:

1. Mandate and Temporal each have their own database and credentials on the shared Postgres; nothing uses the lab's admin account.
2. Mandate restores from backups of its own database only; a point-in-time restore of the whole shared Postgres would rewind every product.
3. Mandate tolerates the lab being down: it waits and retries, and the sweep catches up on restart.
4. The lab pins its images; Mandate declares the versions it was tested against and refuses an unknown Paperclip release (ER-09).
5. The control tower plugin is released with Mandate but installed into Paperclip; installing it is a step in Mandate's release, and it reaches Mandate's API by its name on the shared network.
6. Coding agents launched by Paperclip need workspaces with the repo and its dev container, through the host's Docker or by running on the host; the phase 0 pressure test decides which.

**GitHub events.** The sweep polls GitHub first: open pull requests and their heads, runs of the central verification workflow and their attestations, the head of main, and issue copies, using ETags so unchanged data costs little. Mandate's GitHub App carries a webhook secret, and Mandate's webhook endpoint is built and covered by contract tests (signature check, deduplication by delivery id, events treated as hints) but delivery stays disabled. A policy switch selects poll or webhook. Switching later needs only a public address for the endpoint (a tunnel or an always-on host) and turning delivery on; the sweep keeps running as the safety net at its idle interval. Paperclip events need no tunnel: the plugin forwards them inside the lab network.

**One machine.** While the lab machine is asleep or off, governed work waits and resumes on wake, so the 1-hour recovery target applies to restarts, not to the machine being off.

**Consequences of EOQ-02.** The lab is one machine. Two things follow, both already covered by the design: GitHub webhooks cannot reach a laptop without a tunnel, so the one-minute sweep (AD-2) carries GitHub until a tunnel is added; and while the machine is asleep or off, governed work waits and resumes on wake, so the 1-hour recovery target applies to restarts, not to the machine being off.

## 13. Decision log and differences from product intent

**Decided in chat, 19 Nov 2026:** AD-1 C, AD-2 C, AD-3 C, AD-4 C on Temporal, AD-5 B, AD-6 A, AD-7 A, AD-8 C, AD-9 A, AD-10 A, AD-11 C, AD-12 A. Also on 19 Nov: Conduit is the first programme and proves the delivery swarm; Mandate's own development joins after the phase 1 gate (applied to the product PRD and vision). Later on 19 Nov: PM-1 A and PM-2 A confirmed; Mandate is built to completion before Conduit is onboarded, Conduit's delivery is Mandate's acceptance run with issues fixed in Mandate, and every initiative is proven on mandate-sandbox meanwhile (IB-2 A); "complete" means every capability up to phase 3, with phase 4 built when Mandate's own development joins as the second programme (IB-3 A); initiatives run 0 to 10 in the order in product PRD section 15, autonomy before breadth (IB-4 A), initiative 2 split by lifecycle (IB-5 A); then superseded by IB-6 A: Mandate is one initiative, INIT-MANDATE-001, against this whole PRD, with phase 0 first, the agreed order kept as nine waves (product PRD section 15), then a sandbox fix stage and a Conduit fix stage. Project layout PL-1 to PL-12 decided (section 10). Product OQ-01 decided: prayog-skills contract v3, produced by a parallel initiative as a phase 0 precondition, makes agent-decided gates legal in the contract (gate nodes with a class, moved only on the holder's recorded decision). 21 Nov 2026, after phase 0: AD-1 amended (Paperclip's stage is the board's view; Mandate's ledger and the required check are the gate; board overrides detected, reverted and recorded), AD-7 amended (enforcement by attestation signer verification, since GitHub Free has no required workflows), AD-8 amended (merge API pinned by sha, App-only ruleset bypass, detect and revert any merge the App did not make); Mandate's Paperclip writes run inside its own wake-up run. Later on 21 Nov, from first principles: a gate is a merge into develop (and develop into main), signed on its pull request with the workflow's label, an attested Approve and the ready state; Mandate's only enforcement is the required check mandate/gate-decision; every other decision is recorded without blocking work; at L0 the human signs on GitHub and the deciding role's call stays off the PR until then (option C); Paperclip carries work, questions and escalations but no gate. This supersedes the approval-stage and App-only-merge parts of AD-1, AD-6 and AD-8 recorded earlier the same day. Then, closing the gaps: a non-merge decision is made as a review on its pull request when there is one, otherwise as a Paperclip question (G-1 C); a recorded no fails the next downstream merge until resolved (G-2); REQ-40 clarified for L2 and L3, where the App carries out the deciding role's decision and never decides (G-3); REQ-122 added: merges without a passing check and unauthorised ruleset changes are detected, escalated and reverted through the gate, and preflight proves an owner cannot merge without the check (G-4); the emergency humans are the only bypass actors, on Mandate's own repos (G-5); contract v3 marks which gate nodes block (G-7). Then the build plan (BP-1 to BP-8, PL-16): Mandate is built by a Claude Code swarm only; task PRs merge without KD on the deterministic runner's check plus an independent challenger's approval, and KD signs protected paths and wave closes (BP-1 B); the runner is a plain-code container in dev-infra-lab under its own App, with no GitHub Actions runner (BP-2 A); one lead with subagents in worktrees (BP-3 A); builders on Sonnet, challengers on Opus, with a second challenger on the trust-critical capabilities (BP-4 C); waves close with a signed develop-into-main PR (BP-5 A); protected paths are the rules and what grades the work (BP-6 B); a stateless lead per round rebuilds state from the repos (BP-7 B); B0 builds the swarm, with every B0 PR merged by KD (BP-8 A); the runner was then placed in mandate-verify rather than dev-infra-lab, because it is the build-mode counterpart of Mandate's verification trust anchor and dev-infra-lab stays shared infrastructure only; PR code runs in a secret-free Docker-in-Docker sidecar. Time boxes and spend caps set (product OQ-14).

**Differences from product intent:** none. Two design points, confirmed by the PM:

1. **Confirmed 19 Nov 2026.** Mandate posts the merge check only after the gate holder's signoff is recorded in the ledger: the human at L0, the deciding role's sealed call at L3, or the expiry of the veto window at L2 (ER-10; restated 21 Nov 2026 for the merge-gate model). With no ledger entry the check is never posted, so a fault in the runner or the sweep can stall work but never push it through. REQ-40 forbids a service identity from deciding; it does not decide here.
2. **Confirmed 19 Nov 2026.** Programme configuration is split on purpose: structure (repos, stacks, harness) lives in the meta repo through Launchpad; governance policy lives in Mandate's database (AD-9). Agents therefore cannot change policy through a pull request, and the ledger plus the daily checkpoint keep policy tamper-evident. The control tower settings page shows the programme's repos read-only, taken from the meta repo, so both sit on one screen.
