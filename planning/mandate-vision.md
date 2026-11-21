# Mandate: product vision

> **Source of truth.** Exported from the claude.ai design doc on 21 Nov 2026. From this commit on, this file is the source of truth; the claude.ai doc is an archived snapshot. Change it by pull request.


Nov 18, 2026 · @kd

## Summary

Mandate is the delivery governor for an autonomous software organisation. It runs a programme's delivery workflow across a team of AI agents, decides at every gate who may approve (a human or an agent), records every decision with its evidence, and widens an agent's authority only when the data shows its decisions match a human's. Paperclip runs the agents; Mandate decides what they may do on their own.

The outcome it commits to: a programme moves from PRD to merged code with humans acting only where intent is set or code ships to users, and every other step either runs on its own or earns the right to.

This vision says why and what at the highest level. The [product PRD](https://claude.ai/artifact/X1AE8pwvMJxou2RXDQ1f1e) is the source of truth for capabilities, journeys, requirements, policy defaults and open questions; the engineering-ready PRD follows, with architecture and design.

## The problem

Agents can already write code, review it and open PRs. What stops an autonomous delivery organisation is not agent skill but governance: who may decide, on what evidence, and how that authority grows. ADH, the current attempt, shows each failure mode.

- **Too many human stops.** The delivery workflow puts a human on 10 transitions per initiative plus 2 per wave. A five-wave initiative stops 20 times, so the humans become the bottleneck the agents were meant to remove.
- **Autonomy is a switch, not a measurement.** ADH has human mode and god mode. God mode lets the agent decide every gate at once, with no evidence that it decides well. There is no middle ground and no data to move between modes.
- **God mode breaks the rules it runs under.** The workflow contract says human gates never move on their own and only a human merges. In code, god mode auto-plays the agent's recommendation, pre-approves a PR with a second app identity, then merges without binding the merge to the approved commit.
- **Decisions leave no usable record.** A gate outcome is a label or a comment. Nothing records what evidence it rested on, which commit it applied to, or whether it turned out right after merge. So trust cannot be earned, because nothing is measured.
- **The tools are tied to one agent.** Skills and rules assume Cursor, so the same procedure behaves differently on Claude Code or Codex.

The ADH code also carries twelve safety and correctness findings from the 18 November review. Mandate starts from scratch; those findings become its test cases.

## Vision and principles

A company runs several software programmes. Each has a team of agents in named roles and a small number of accountable humans. Work flows through the programme's delivery workflow with no one pushing it. Humans set intent, sign off what gets built and decide what ships. Everything between is done and decided by agents, and each agent's authority is exactly as wide as its record justifies.

Principles, each of which Mandate must enforce rather than assume:

1. **Authority is earned from data, automatically.** No gate becomes autonomous by configuration alone. Mandate promotes a gate when its recorded decisions and outcomes clear policy thresholds, and demotes it when the data turns. Humans are informed, and limit autonomy only by policy.
2. **Humans steer by priority and policy, not standing approval.** Every human step is a gate on the ladder. People set direction through what they prioritise and the policies they set; a gate is held for a human only where the owner's policy says so.
3. **Every decision is a record.** Who decided, at which rung, on what evidence, for which exact version of the work, and what happened afterwards. Evidence is produced and signed by the run, never typed by an agent.
4. **An approval is for what was reviewed.** If the work changes after approval, the approval no longer counts.
5. **No one reviews their own work.** Agent or human. A gate's deciding role is never the author or the challenger of the work it decides.
6. **Human mode is a policy, not a bypass.** Human mode holds every gate of a programme at L0; otherwise each gate runs at the rung it has earned, up to the ceiling its policy allows.
7. **Mandate is the only path for consequential writes to GitHub.** Merges and issue copies go through it, so the rules above cannot be skipped. The one exception is a human emergency path into Mandate's own repos when Mandate cannot act.
8. **The workflow is data.** Programmes change their workflow by editing it, not Mandate's code.
9. **Agent-neutral.** Any coding agent Paperclip can run is a valid team member; Mandate never depends on which one.
10. **The process is versioned and measured.** The workflow, skills and rules will change as we find bottlenecks. Every run and decision is stamped with the versions in effect, so any change can be judged on data.
11. **Every artifact has an author and an independent challenger.** PRD, engineering-ready PRD, spec, tests, platform, code: each is challenged against evidence its author did not produce, and the author keeps the decisions in their own domain.
12. **Execution is autonomous.** Between gates, nothing waits for a person; stuck work escalates to an agent outside the dispute before it reaches a human.
13. **Untrusted content never instructs.** Issue text, bug reports and outside code are data to every agent, marked as such wherever they appear.

## Boundary

Mandate owns four things: the workflow's progress, the gates, the decision ledger and consequential GitHub writes. It uses everything else.

[Diagram in the archived claude.ai doc: Mandate's boundary · what it owns and what it uses]

Paperclip tells Mandate what happened (a step finished, a reviewer acted); Mandate tells Paperclip what work exists next and who holds each gate. Agents push branches and open PRs; only Mandate merges and keeps the GitHub issue copies.

## The control tower

Mandate's face is a control tower inside Paperclip, not a separate app and not Buzz. People already work in Paperclip: the board, issue threads, the decision inbox, Slack. The control tower adds what Paperclip cannot show, because only Mandate knows it: where every initiative sits in its workflow, which gates are waiting and why, how much autonomy each gate has earned, and where the process is slow.

It is built as a Paperclip plugin whose screens read Mandate's API. Paperclip's plugin interface lets a plugin add full pages, tabs on issue and project pages, dashboard widgets, sidebar entries and settings pages, so no new app, login or navigation is needed.

| View | Where it appears in Paperclip | What it shows | Who uses it |
| --- | --- | --- | --- |
| Control tower | A page with its own sidebar entry | Every programme and initiative in flight, each placed on its workflow (outline, PRD, readiness, spec, waves, closure); gates waiting, with age and who holds them; escalations; the current bottleneck | Company owner, decision owners |
| Autonomy map | A tab on the control tower page | Each gate in each programme with its rung, ceiling, agreement so far, promotion eligibility and recent demotions | Company owner |
| Programme | A tab on the Paperclip project | Workflow version, role cards and the agents filling them, rungs, step and gate metrics, version comparisons | Decision owner |
| Initiative | A tab on the initiative's Paperclip issue | Position in the workflow, the outline and both PRDs, the PM and principal engineer question log, every decision with evidence and commit | Everyone on the programme; auditors |
| Gate brief | Shown with the decision in the Paperclip inbox | The agent's brief and recommendation, evidence bound to the commit, what happens if approved | The human holding the gate |
| My gates | A widget on the Paperclip dashboard | Gates and product questions waiting for you, oldest first; promotions and demotions since you last looked | Every human with a gate |
| Policy and workflows | Company settings page | Policy values (thresholds, windows, ceilings), workflow versions, the role catalogue, the outline standard | Company owner |

**Acting stays where the work is.** Approving, overruling and answering product questions happen in Paperclip's inbox and issue threads, using its decisions and interactions; the control tower links straight to them. The control tower itself is for seeing, deciding what to look at, and changing policy.

**The trade-off.** Plugin screens run as trusted code inside Paperclip and move with its upgrades. So the screens stay thin: all logic and data live behind Mandate's API, and if Mandate ever needed its own app, it would reuse that API unchanged.

## Kinds of work

Not everything is an initiative. A programme also receives bug reports, small enhancements, production incidents, dependency and security updates, and questions that need investigating before anyone can say what to build. Each kind needs its own path: running a one-line bug fix through outline, PRD, readiness and spec is waste, and letting a new capability in as an "enhancement" skips the checks that protect intent.

**Conventions come from the delivery contract, not from Mandate.** Ids, kinds and the workflow for each kind are defined in `prayog-skills` and pinned by version, exactly like `workflow.yaml`. Mandate reads them; it never hard-codes an id format. Today the contract defines `INIT-…`, waves and tasks, and ADH's team-OS spec defines `init`, `bug` and `enhancement` task kinds with `INIT-…`, `BUG-…` and `ENH-…` ids. Two gaps to close in the contract: the full `INIT-{COMPONENT}-{NUMBER}` format currently lives only in an ADH prompt, and only initiatives have a workflow.

| Kind | Id | Enters as | Path | Human stops by default |
| --- | --- | --- | --- | --- |
| Initiative | `INIT-…` | An outline from the Lead | Outline intake, PRD, engineering readiness, spec per repo, verifier's tests, waves, closure | PRD acceptance, spec sign-off, release per wave |
| Enhancement | `ENH-…` | A GitHub issue stating current behaviour, wanted behaviour, one example and the affected repo | Triage, a spec change for one repo tied to the capability it changes, verifier's test, one wave | Release |
| Bug | `BUG-…` | A GitHub issue with steps to reproduce and expected behaviour | Triage, the verifier writes a failing test that reproduces it, the coder fixes, the verifier proves the test passes and nothing else broke | Release |
| Incident fix | `HOT-…` | A production alert or report | An expedited path: investigate, minimal fix, verify, release; a follow-up review is created automatically and must be closed | Release, held for a human by default policy |
| Chore | `CHORE-…` | A dependency, security or refactoring need with no behaviour change | Change, existing tests must still pass unchanged, release | Release |
| Spike | `SPIKE-…` | A question that must be answered before work can be shaped | Time-boxed investigation producing a written finding or decision record; nothing merges to main | Reading the finding |

**Triage decides the kind, and a kind can change.** The principal engineer challenges the claimed kind against simple tests: a new capability, a new journey, more than one repo or a new contract between repos means it is an initiative, whatever the issue says. A bug whose fix changes intended behaviour becomes an enhancement. Mandate records every change of kind with its reason, so "enhancements" that should have been initiatives show up in the data.

**Three more kinds, decided 18 Nov.** A kind earns its own path only if its intake, path, evidence, default human stops or reversibility differ from an existing kind; otherwise it is an attribute.

| Kind | Id | Why it has its own path | Human stops by default |
| --- | --- | --- | --- |
| Rollout | `ROLL-…` | Turns a released feature on in steps (for example 5%, 50%, everyone). No code changes; the evidence is live health during each step; rollback is switching off | Each step until the gate earns autonomy |
| Data migration | `MIG-…` | Usually irreversible: needs a dry run on a copy, a backup, a rollback plan and before-and-after counts | Held for a human by default policy |
| Deprecation | `DEP-…` | Removing a capability is an intent decision: notice, a check of who still depends on it, then removal | Acceptance, like a PRD |

**Attributes instead of kinds:** `security` (deadline by severity, restricted visibility, security reviewer at release), `performance` (benchmark or service-level evidence before and after), `infrastructure` (production infrastructure release is held for a human by default policy), `docs` (review only). Major upgrades and refactoring are chores or initiatives by triage; experiments are an initiative plus a rollout; postmortem actions are bugs, chores or enhancements linked to their incident.

The first release runs initiatives, bugs and enhancements. Incident fixes, chores, spikes, rollouts, migrations and deprecations follow.

## Mandate across the delivery lifecycle

Every lifecycle phase maps onto Mandate, but Mandate's role differs by phase: it runs and gates the phases from intake to test, it releases, and from deployment onwards it records and links outcomes while others do the work.

| Phase | In Mandate | Who does the work | Gate and evidence | Kinds |
| --- | --- | --- | --- | --- |
| 1. Intake and triage | Outline intake; triage of issues into kinds | Lead; principal engineer challenges the kind | Outline complete; every change of kind recorded | All |
| 2. Requirements | PM lane, then engineering readiness | PM; principal engineer grounds and asks | PRD acceptance, with both PRDs and the question log | Initiative, deprecation |
| 3. Design | Spec per repo, feasibility, technical review, plan; verifier writes acceptance tests | Tech lead per repo; architect; verifier | Spec sign-off | Initiative, enhancement |
| 4. Build | Waves of tasks in dev-container workspaces | Coder; code reviewer | Code review, no self-review | All that change code |
| 5. Test and verify | Clean environment per run, tests written at spec time | Verifier | Test report, environment manifest, commit binding | All that change code |
| 6. Release | Release gate per wave; Mandate merges exactly the verified commit | Decision owner | The evidence above | All that change code |
| 7. Deploy | Continuous deployment of every merge, with the feature behind its switch; deployment status linked to the wave | Platform engineer's pipelines | None in Mandate | n/a |
| 8. Roll out | Turning the feature on in steps | Decision owner; SRE agent watches health | Live health per step; switch-off is the rollback | Rollout |
| 9. Operate | Incidents enter as incident fixes; defects linked back to the wave that caused them | SRE agent; coder | Human release for incident fixes; follow-up review created | Incident fix |
| 10. Maintain and improve | Bugs, enhancements, chores, migrations, deprecations; new workflow versions judged on data | All roles | Each kind's own path | All maintenance kinds |

Phases 4 to 8 repeat per wave and 1 to 10 per work item, so many items sit in different phases at once; the control tower shows them side by side. Every phase feeds back: a defect found in operation becomes a bug and an outcome check against the gates that passed it.

**Three gaps, closed:**

- **Prioritisation stays human.** Mandate governs how work flows, not which work comes next. What to build next is decided by people on Paperclip's board and goals; Mandate shows them the cost and delay data to decide with. (Added to non-goals.)
- **Deployment is continuous, behind switches.** Every merged wave deploys to production with its feature switched off; the user-facing decision is the rollout. There is no separate production approval after merge, which keeps the release decision and the evidence in one place.
- **Audit evidence is a capability.** Every phase leaves decision records with evidence, versions and actors, which is the process evidence ISO 27001 and CMMI assessments ask for. Mandate exports the full trail for an initiative or a period on request. (Added as a capability; first release keeps the records, the export follows.)

Among spec-driven tools, Kiro takes the same view: for bug fixes it [generates a bugfix document](https://codemyspec.com/blog/kiro-specs-explained) in place of the requirements document, rather than forcing a bug through the feature flow.

**Every kind is traced and measured.** An enhancement or bug links to the capability or requirement it touches, so the PRD stays the record of what the product does. A bug also links back to the wave that introduced it, which is the outcome check that counts against the gates that let it through. Autonomy is earned per kind as well as per gate: a release gate on chores will earn its rung long before the release gate on initiatives, and should.

## Actors

| Actor | Who | Does with Mandate |
| --- | --- | --- |
| Company owner | KD | Creates programmes, sets policies and ceilings where limits are wanted, is informed of every promotion and demotion |
| Programme decision owner | A named human per programme | Decides the gates still held by humans, blind-first at intent and design gates; can overrule within a veto window; answers escalations agents could not resolve |
| Engineering-gate reviewer | A senior engineer, possibly the same person | Decides technical gates blind-first while humans hold them, so the design decider's record can be compared |
| Role agents | PM, principal engineer, tech lead per repo, platform engineer, coder, verifier, a deciding role per gate class (intent, design, release, housekeeping) and others, one per role per programme | Do the work in Paperclip; act as reviewers at agent-held gates; raise decisions with options and a recommendation |
| Shared specialist agents | For example a security reviewer used by several programmes | Review at the gates their role is named on, across programmes |
| Platform operator | Whoever runs the stack | Installs, upgrades, restores; watches Mandate's health |
| Auditor | Anyone checking a decision later | Reads why a gate passed, on what evidence, and who held authority at that moment |

One person can hold several human roles in a small team. Mandate still records which role they acted in.

## Domain terms

| Term | Meaning |
| --- | --- |
| Company | The organisation running programmes; one Paperclip company |
| Programme | A product or system being delivered, with its repos, roles, workflow, budget and autonomy state; one Paperclip project |
| Role | A hat in a programme (PM, architect, coder, verifier); held by one agent or one human |
| Initiative | One unit of intent, from PRD to closure; the workflow runs once per initiative |
| Wave | One implementation slice within an initiative, ending in a merge |
| Workflow | The programme's delivery graph (`workflow.yaml` from `prayog-skills`): steps, gates and the outcomes that connect them |
| Step | A node in the workflow that does work: a skill run by an agent, or an action such as opening a PR |
| Gate | A node where someone decides whether work moves on; carries a policy: class, approver, rung, evidence required |
| Gate class | A: intent; B: design; C: verification; D: housekeeping. Sets how far a gate may ever climb |
| Rung | L0 human decides; L1 shadow (agent and human both decide, human counts); L2 veto window (agent decides, human may overrule in time); L3 agent decides |
| Decision | One act at a gate: who, in which role, at which rung, the outcome, the reasons, the evidence, the exact version of the work |
| Evidence | What a decision rests on: test results, review findings, a verification report, all tied to that version |
| Outcome check | What happened after a decision: merged cleanly, reverted, defect found later. It is how decisions are scored |
| Agreement | How often agent and human decisions match at a gate while it is in shadow |
| Promotion / demotion | A recorded change of a gate's rung for a programme, with the data behind it and a human approval |
| Ceiling mode | Human mode (all gates at L0) or god mode (each gate at its earned rung) |

## The autonomy model

Autonomy is the product. It is held per programme, per gate and per kind. A gate's rung says who decides there today; it rises automatically when the data earns it and falls automatically when the data turns. The owner limits it only by policy.

| Rung | Who decides | What the human does | What Mandate records |
| --- | --- | --- | --- |
| L0 | Human | At intent and design gates, decides blind-first, then sees the deciding role's call; elsewhere decides with the recommendation and run evidence | Human decision, deciding role's call, whether they matched |
| L1 shadow | Human and deciding role, independently | Decides as at L0 (verification and housekeeping gates; blind-first L0 does this elsewhere) | Both decisions, agreement, reasons where they differ |
| L2 veto window | Deciding role | May overrule before the window closes; if nobody acts, the decision stands | Decision, any overrule, outcome check |
| L3 | Deciding role | Reviews trends | Decision, outcome check |

**Who takes over a gate.** Each gate class has a deciding role (intent, design, release, housekeeping decider) that is never the author or challenger of the work. It records its own blind call from the first decision, and that record is what earns it the gate.

**What earns promotion.** At intent and design gates: blind-first and shadow agreement, plus clean outcomes. At verification and housekeeping gates, where the recommendation is visible: clean, exercised outcomes only. Every class may reach L3; ceilings and "hold for a human" rules (by default on incident fix release, data migration and production infrastructure release) are owner policy.

**Promotion** is automatic, one rung at a time after a minimum stay (intent and design gates go from L0 straight to L2), and the owner is informed. No agent promotes a gate it holds; any human with authority can reverse a promotion.

**Demotion** is automatic and immediate: one rung on an overrule or a failed outcome check, straight to L0 on a policy breach.

**Earned trust belongs to an agent setup.** A change to the model, adapter or skills behind a deciding role drops its gates one rung until a short shadow run re-earns them.

## Evolving the process

The delivery workflow, the per-stack skills and the per-stack rules are all expected to change. Each change should be justified by data and judged by data afterwards. Mandate makes that possible in three ways.

**1. Everything that shapes behaviour is versioned.**

| What | Version it carries | Pinned when |
| --- | --- | --- |
| Delivery workflow and contract | Release of `prayog-skills` | Per initiative, at start; it finishes on that version |
| Stack skills | Commit of the stack's skill source | Per step run |
| Stack rules (`AGENTS.md` and its shims) | Commit of the repo at the time of the run | Per step run |
| Agent setup | Adapter, model and role configuration | Per step run |
| Gate policy | Policy revision, including rung | Per decision |
| Mandate itself | Release | Per decision |

**2. Every step and gate is measured.** Elapsed time, split into agent working time and time waiting for a human; rework loops (how often a step bounces back with findings); first-pass acceptance; escalations; cost per step from model usage; and later outcome checks. The bottleneck is then visible directly: the step or gate with the largest share of lead time, waiting time or rework.

**3. Changes are judged against their own baseline.** Metrics are grouped by version, so a new skill or workflow version is compared with the one it replaced on the same programme. Initiatives are few, so this alone is weak evidence. Two cheaper signals sit beside it:

- **Replay:** run a new skill version against fixed past inputs before release, and compare the outputs.
- **Canary:** release a new version to one programme or one role first.

Changes to the workflow, skills or rules are themselves initiatives with a gate, so the process improves under the same governance as the product.

This ties back to autonomy. When the skills or rules behind an agent-held gate change, the version record shows exactly which decisions were made under which version, so whether to keep, lower or re-earn a rung can be decided on evidence.

## How the agent team works

Mandate assumes a mature engineering team, not a group of agents writing code. The practices below are what strong human teams do; Mandate makes them the default for agent teams, and the workflow, role cards and gates enforce them.

### Environments: three kinds, one definition

No programme relies on anyone's laptop setup. Every environment comes from code in the programme's repos, and humans and agents use the same definitions.

| Environment | Used by | Defined by | Lifetime |
| --- | --- | --- | --- |
| Workspace | Coder agents; humans on laptops | Dev container plus compose in the repo (app, database, cache, queue) | Per run or per person |
| Verification | Verifier agent; humans reviewing a wave | A clean compose project per run at first; later a namespace per PR on a cluster | Created per run, torn down after |
| Shared (dev, stage, prod) | Everyone | Infrastructure code for the cluster; GitOps for the apps | Long-lived |

Two rules follow:

- **The platform comes first.** Every programme's first initiative is a walking skeleton (one endpoint, one screen, one table) with the dev container, the verification setup and the cluster code. No feature initiative starts until it is merged.
- **Every service meets a platform contract** before its first feature wave: a standard entry point the tests can reach, health and readiness checks, an API description, seed and reset hooks for test data, and tracing. The platform role writes the contract into the stack harness; the verifier checks it at spec time.

### Roles and hiring

A role is a versioned card: responsibilities, the gates it holds, its skills bundle, the tools and environments it may use, and its budget. Who fills it is a separate choice, in this order of preference:

1. A general coding agent with our role skills (most roles stop here).
2. An open-source specialist agent, when the role needs deep tooling we would otherwise rebuild, such as [HolmesGPT](https://www.cncf.io/blog/2026/01/07/holmesgpt-agentic-troubleshooting-built-for-the-cloud-native-era/) for incident investigation.
3. Our own agent, only when the data shows a gap the first two cannot close.

Every new hire starts on probation: the gates it holds run in shadow, and it earns autonomy the same way as the rest of the team. Agents are hired for judgement; deterministic checks (security scans, infrastructure policy, cost estimates) are tools agents call, not agents.

### Verification: independent, black-box, evidence-bound

The verifier proves a wave works from the outside, against tests the coder did not write.

[Diagram in the archived claude.ai doc: verification loop · one wave]

1. **At spec sign-off,** the verifier writes acceptance tests from the PRD's requirements and journeys: API and UI tests, plus assertions on traces. They live in a protected path the coder can read and run but not change. The verifier also checks every service the initiative touches meets the platform contract.
2. **The coder builds the wave** in its workspace and may run the acceptance tests as often as it likes.
3. **When the wave PR opens,** the verifier builds from that commit into a clean verification environment with seeded data. An environment manifest records the exact version of every service in the run: the PR for the changed repo, main for the others.
4. **The verification run executes the tests** fixed at spec sign-off and signs the evidence for the commit: test report, traces, the manifest, and any database checks the spec declared. The verifier interprets it but cannot produce or change it. Logs are for diagnosis, not pass criteria.
5. **On failure,** findings go back to the coder on the PR with the failing test, the trace and a log excerpt. The loop repeats on a fresh environment. Mandate counts rounds and escalates at the limit.
6. **On pass,** the release gate decides at its rung, and Mandate merges exactly that commit. A push after acceptance voids it. With parallel waves, a merge queue re-verifies against the latest main.
7. **After merge,** a defect traced to the wave becomes an issue and an outcome check against the gates that let it through.

Issues are for defects outside the wave, defects found after merge, and flaky tests. A flaky test goes to the verifier, who owns it, not to the coder.

**As programmes grow past a few repos,** deploying every service per run stops fitting on one machine. Uber hit this and built [SLATE](https://www.uber.com/blog/simplifying-developer-testing-through-slate) for short-lived test environments; Lyft moved from fully isolated environments to [isolating requests in a shared environment](https://www.infoq.com/news/2022/03/scaling-testing-acceptance-lyft/). Mandate's path is the same: contract tests at every repo boundary, then request-level isolation on a shared cluster when compose no longer fits.

### Measuring the team against other teams

The team's practice is benchmarked with the same measures strong human teams use: verification time per wave, verification rounds per wave, flaky test rate, defects found after merge, and the share of the PRD's requirements with a passing acceptance test at merge. These feed the process metrics above, so a slow verifier or a leaky gate shows up as a bottleneck to fix.

### Author and challenger, at every stage

The coder and verifier pairing is one instance of a general rule: every artifact has an author and an independent challenger. The challenger grounds the artifact in evidence the author did not produce and asks questions; the author answers and revises; the loop repeats until nothing blocking is open; then the gate decides. Authority stays with the author's domain: a challenger proposes, it never decides for the author.

| Artifact | Author | Challenger | Challenger grounds it in | Ends at |
| --- | --- | --- | --- | --- |
| Product PRD | PM | Principal engineer | The code as built (a code graph), the service catalogue, past initiatives | Product questions answered; no blocking question open |
| Engineering-ready PRD | Principal engineer | PM, who confirms product intent is unchanged | The PRD delivery bar (`/prd-quality`): testable requirements, negative paths, contracts, open questions | PRD acceptance (human gate) |
| Per-repo spec | Tech lead for that repo | Principal engineer, against the engineering-ready PRD and its contracts | The repo's code and the cross-repo contracts | Spec sign-off (human gate) |
| Acceptance tests | Verifier | PM, for coverage of every requirement and journey | The PRD's requirement and journey ids | Part of spec sign-off |
| Platform contract | Platform engineer | Verifier | Whether the tests can reach and observe every service | Before the first feature wave |
| Wave code | Coder | Verifier, plus a code reviewer | The acceptance tests in a clean environment | Release gate |

**From PRD to per-repo specs.** The PM writes the product PRD: the job, users, journeys and outcomes. The principal engineer maps it onto the code as built, finds what the PRD leaves a builder to guess, and posts product questions, each with a scenario, an example and a recommendation. The PM decides and updates the PRD. When no blocking question is open, the principal engineer writes the engineering-ready PRD: the same intent, now grounded in the code, split by repo, with contract seeds at every repo boundary and every remaining guess named as an open question. It passes the PRD delivery bar, the PM confirms the intent survived, and the human gate accepts it. Only then does each repo's tech lead write that repo's spec.

The principal engineer never decides product questions, and the PM never decides how the code is split. Each loop is measured like any other step: question rounds per PRD, questions per round, and requirements later changed during spec are the signals that the product PRD or the grounding needs to improve.

### Engineering readiness is Mandate's, not a skill's

Today a PRD becomes engineering-ready implicitly, inside the PRD acceptance gate, where the principal engineer reviews an impact map built from the service catalogue rather than the code. Mandate makes it an explicit stage with a contract, so it no longer depends on any particular skill being installed or used.

**Where it sits.** After the PM's product PRD passes validation, before PRD acceptance. The gate then only decides; no review work happens inside it. Spec Kit (a clarify step before planning), BMAD (the architect challenges the PRD and the PM updates it) and Shape Up (de-risking with technical experts before the bet) all put this challenge before commitment, for the same reason.

**What Mandate owns.**

- **The readiness contract.** The stage is done when it has produced: a grounding report (the PRD mapped onto the code as built, the catalogue and the platform contract); a question log with every question dispositioned; an engineering-ready PRD that passes the PRD delivery bar; the impact per repo; and a contract seed at every repo boundary. Mandate checks these exist and are bound to the PRD version they were made from.
- **Product questions as first-class records,** like decisions: the question, scenario, example, recommendation, who raised it, whether it blocks, the PM's answer, and the round. Mandate runs the loop: it routes open questions to the PM, tracks rounds, escalates at the limit, and blocks the stage while a blocking question is open.
- **The authority split.** The principal engineer raises and recommends; only the PM answers product questions. Mandate records an answer only from the PM role.
- **The measures.** Question rounds per PRD, questions per round, blocking questions, and requirements changed later during spec. These show whether product PRDs or the grounding need to improve.

**What Mandate does not own.** How the principal engineer grounds the PRD. Its role card carries a skills bundle: today's `engg-reviews` skills, new ones, or a different approach entirely. Skills are replaceable and versioned; the contract is not. If a new grounding skill produces fewer late spec changes, the process metrics will show it.

### Shared codebase context

Grounding a PRD is one use of a capability every role needs: knowing what the code as built actually does. The principal engineer grounds PRDs, tech leads write specs against it, coders find where to change things, verifiers find what to test. Mandate provides this as one shared capability any agent can call, instead of each agent improvising its own.

**What it answers,** always with file paths and the commit they were read at: where a behaviour is implemented; what calls what; which repos and services a capability touches; whether a requirement already exists in some form; what data and contracts sit at a repo boundary.

**How it is built: pluggable, and chosen by benchmark.** Day 1 starts with the simplest thing that works and moves up only when the data says so:

| Level | Approach | Example | Cost |
| --- | --- | --- | --- |
| 0 | A coding agent searching and reading files | Built into Claude Code, Codex | No setup |
| 1 | A ranked repo map from parsed symbols | Aider-style repo map | Low |
| 2 | Symbol-level navigation through language servers | Serena, over MCP | Low; per-language servers |
| 3 | A code knowledge graph across code, schemas and infrastructure | Graphify, over MCP | Medium; rebuild per commit |
| 4 | A code search platform across many repos | Sourcegraph, over MCP | High; enterprise licence |

**How it is judged.** A grounding evaluation set built from the programme's own repos: questions with known answers, scored on whether the cited locations are right and complete, how fresh the answer is after new commits, time and cost. Then the downstream signal: requirements changed late during spec, and questions the principal engineer missed. A context engine is swapped like a skill: versioned, replayed against the evaluation set, released to one programme first.

**What stays out.** The capability retrieves and cites; it does not judge. Deciding what a PRD means for the code remains the principal engineer's call, so Mandate still never makes a judgement in its own name.

## Key journeys

The first five are the happy path of one programme. The rest are where governance earns its keep, so they get equal weight.

1. **Onboard a programme.** The company owner creates a programme: its repos, its roles and the agents that fill them, its decision owner, its workflow version and its budget. Every gate starts at its default rung. Mandate confirms the agents, the GitHub access and the workflow are all usable before the first initiative can start. The programme starts from a template whose first initiative is the platform walking skeleton.
2. **Run an initiative in human mode.** A PRD enters. Mandate creates each step's work for the right role agent in Paperclip, moves to the next step when one finishes, and stops at each gate. At a human gate it presents the agent's brief and recommendation; the decision owner chooses; Mandate records it and moves on.
3. **Decide blind-first.** At an intent or design gate held by a human, the human decides before seeing the deciding role's call. Mandate records both, flags disagreements for the human to read, and counts agreement.
4. **Release a wave.** The verifier builds the wave's commit into a clean environment, runs the acceptance tests it wrote at spec time, and attaches the evidence and environment manifest to that exact version. The release gate is decided at its rung. Mandate merges exactly that version, copies the outcome to the GitHub issue, and starts the next wave or closure.
5. **A gate promotes itself.** A gate clears its thresholds. Mandate moves it up, hands it to its deciding role, and informs the owner, who can cap it by policy. It moves up for that programme only.
6. **Overrule in a veto window.** At an L2 gate the agent decides; the decision owner sees it and overrules before the window closes. The work goes back; the gate drops a rung; the overrule and its reason are recorded.
7. **Work changes after approval.** A new commit lands on a PR after its gate passed. The approval no longer counts; the gate reopens for the new version.
8. **A decision turns out wrong.** A merged wave is reverted, or a defect is traced to it. Mandate links the outcome back to the decisions that let it through, and demotes those gates.
9. **Escalation.** Reviewer and author loop past the round limit, an agent is stuck, or a gate has no eligible reviewer. Mandate escalates to the decision owner with what has happened so far.
10. **Recovery.** Mandate, Paperclip or GitHub is down or restarts mid-initiative. When it comes back, nothing is lost, nothing is done twice, and no gate passes without a decision.
11. **Audit a decision.** Anyone can ask why a change shipped and get the chain: PRD, spec, waves, every gate decision with its rung, evidence and version.
12. **Change the workflow.** The programme moves to a new workflow version. Initiatives already running finish on the version they started; new ones use the new version.
13. **Evolve the process.** A bottleneck shows up in the step and gate metrics. Someone proposes a new workflow, skill or rules version as an initiative, tests it by replay, releases it to one programme first, and Mandate compares it with the previous version before it goes wider.
14. **Hire a role.** The programme needs a security reviewer. Someone proposes a role card and who fills it (a general agent with role skills, or an open-source specialist). The hire is a design gate decided at its rung; the new agent's gates start in shadow.
15. **A wave fails verification.** The acceptance tests fail. Findings go back to the coder on the PR with the failing test, trace and log excerpt; the coder fixes; the verifier reruns on a fresh environment. After the round limit, Mandate escalates.
16. **A flaky test.** A test passes and fails on the same commit. It is routed to the verifier as an issue, not to the coder, and the wave is not blocked by a test the verifier has quarantined.
17. **Make a PRD engineering-ready.** The PM's PRD passes validation. The principal engineer grounds it in the code and catalogue and raises product questions. Mandate routes them to the PM and blocks while any blocking question is open. When all are answered, the principal engineer writes the engineering-ready PRD; it passes the delivery bar; the PM confirms intent survived; PRD acceptance decides.

## Capabilities

The core capabilities are below; the [product PRD](https://claude.ai/artifact/X1AE8pwvMJxou2RXDQ1f1e) holds all twenty-one with their requirements.

| Capability | What it means | Journeys |
| --- | --- | --- |
| Programme setup | Define a programme: repos, roles and agents, decision owner, workflow version, budget link, starting rungs | 1, 12 |
| Workflow execution | Run the programme's workflow per initiative: start each step for the right role, follow outcomes, stop at gates, finish or stop cleanly | 2, 4, 12 |
| Gate decisions | Present a brief and recommendation, collect the decision from whoever holds the gate at its rung, enforce no self-review and version binding | 2, 3, 6, 7 |
| Decision ledger | Keep every decision with actor, role, rung, reasons, evidence, version and later outcome; answer audit questions | 3, 8, 11 |
| Autonomy management | Record clean agreement from the first decision; promote gates to their deciding roles automatically on policy thresholds; demote on overrule, failed outcome or breach; apply owner limits | 5, 6, 8 |
| Governed GitHub writes | Merge only the approved version; copy every issue and its status to GitHub; nothing else writes there on consequential paths | 4, 7 |
| Escalation | Route stuck loops, missing reviewers and stalled steps to the right human with context | 9 |
| Resilience | Survive restarts and outages of itself, Paperclip or GitHub without losing state, repeating effects or skipping a gate | 10 |
| Process measurement | Stamp every run and decision with the versions in effect; measure every step and gate; compare versions | 12, 13 |
| Programme templates | Start a programme from a template that fixes the first initiative (platform walking skeleton) and the platform contract every service must meet | 1 |
| Role catalogue and hiring | Keep versioned role cards; hire an agent into a role with approval; start every new hire's gates in shadow | 14 |
| Engineering readiness | Run the stage between product PRD and PRD acceptance: enforce the readiness contract, keep product questions as records, route them to the PM, track rounds, block while a blocking question is open | 2, 17 |
| Shared codebase context | Answer questions about the code as built for any agent, citing files at a commit; keep the index fresh per commit; let the engine be swapped and benchmarked | 17, 13 |
| Audit evidence export | Export the complete decision trail (decisions, evidence, versions, actors) for an initiative or a period, for internal review or ISO 27001 and CMMI assessments | 11 |

## Success measures

| Measure | Why it matters | Target (Conduit, the first programme) |
| --- | --- | --- |
| Required human stops per five-wave initiative | The bottleneck Mandate exists to remove | 20 today; 8 at first release; then only the stops the owner keeps by policy |
| Human minutes per initiative | Stops undercount the real load | Baseline, then falling |
| Gates above L0 | Autonomy actually earned | At least 4 at L2 or higher within 10 initiatives, at least 2 of them design or verification gates, if the data supports it |
| Agreement at blind-first and shadow gates | Whether agent judgement can be trusted | Measured from the first decision |
| Escaped decisions | Wrong decisions found after merge | Every one traced to its gate and acted on |
| Unbound approvals and unsigned evidence | Anything shipped on something other than the verified commit and run | Zero, ever |
| Lead time, outline to first release | Faster, not just more autonomous | Baseline, then falling |
| Cost per initiative | Autonomy must cost less than it saves | Baseline, then a target |

**Kill assumption.** Mandate fails if agent decisions never earn a gate where judgement matters; it is then a ledger of human decisions, useful for audit but not worth the system. Conduit tests this: if after ten initiatives, or the phase 3 time box, no design or verification gate on a code-changing kind has reached L2, we stop and rethink.

## Non-goals and constraints

**Non-goals.** Each is something Mandate could drift into, and the reason it should not.

- **Running agents.** Paperclip launches, schedules, budgets and recovers agent runs. Mandate tells it what work exists and who holds each gate.
- **Being the board or the chat.** Paperclip's board, threads and channels are where people and agents work. Mandate adds no second UI for that; its own screens cover gates, the ledger and autonomy.
- **Writing or reviewing code itself.** All work is done by role agents. Mandate never asks a model to judge anything in its own name.
- **Owning skills and rules.** `prayog-skills` and each repo's `AGENTS.md` own those; Paperclip delivers skills to agents.
- **Two-way sync with GitHub issues.** Paperclip is the source of truth; GitHub issues are copies.
- **Multi-tenant SaaS.** One company per deployment for now.
- **Ticket tools beyond GitHub.** Jira, Linear or Notion copies can come later through the same path; not in the first release.

* **Prioritising the backlog.** Which work comes next is a human decision on Paperclip's board and goals. Mandate supplies the data (cost, delay, rework per item) but does not rank.

**Constraints, decided.**

| Constraint | Detail |
| --- | --- |
| Language | Python |
| Storage | Postgres, Mandate's own database |
| Runtime platform | Paperclip, forked to `drivestream-lab`, pinned to a release; Mandate uses only its API and a thin bridge plugin (the plugin is TypeScript, as Paperclip requires) |
| GitHub | Mandate's own GitHub App; no Paperclip Cloud in the path; Paperclip telemetry off |
| Model traffic | Agents' model calls go through LiteLLM with per-role keys |
| Workflow source | `workflow.yaml` and the delivery contract in `prayog-skills`, with the gate schema change from the autonomy design |
| Built by | Claude Code, following our own delivery process |
| Starting point | Greenfield; the old ADH code is reference only, its review findings become tests |

## Phasing

The first release is governed delivery done properly: briefs, blind-first decisions, recorded decisions, version-bound approvals, run-signed evidence and governed merges. It starts with Mandate's walking skeleton, built by Claude Code. Then Conduit, the first programme, run as a real product, proves the delivery swarm end to end; Mandate's own development joins as a programme after that. Autonomy then grows automatically on data.

[Diagram in the archived claude.ai doc: Mandate roadmap · 5 phases, 4 gates]

Each gate is a real stop, with a time box and spend cap: if Conduit cannot run one initiative end to end, shadow work does not start. Phase 3's gate is the kill assumption, judged on a design or verification gate.

## Open questions

The questions this vision raised were settled in the [decision briefs](https://claude.ai/artifact/RYjkPjL3eryoc6P8iwzrmk) and the [product PRD](https://claude.ai/artifact/X1AE8pwvMJxou2RXDQ1f1e). What remains open lives in the product PRD's section 13.
