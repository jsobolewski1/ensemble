---
name: spec
description: "Specification-driven multi-model software development protocol. Use whenever a spec is started, continued, planned, implemented or reviewed. Read fondue/specs/<spec>/current-state.txt first; it names the live stage. fondue/specs/archive/ is history, never current truth. Bugs live in fondue/bugs/ and run on hunt instead."
license: MIT
metadata:
  owner: "Jakub Sobolewski"
  version: 4
  status: "living doc — update in place when the workflow changes"
---

# spec — from idea to merged code

A spec goes from the User's brief to merged code through fixed stages. Each AI session holds one role. Sessions take turns and share nothing but the files in the spec folder and fixed control messages.

**This skill runs on the fondue engine.** Read `protocol/engine.md` at the plugin root, `../../protocol/engine.md` from this skill's directory, before anything below. The engine holds state, turns, replies, rulings, review, and commits. This skill fills in the engine's hooks: stages, roles, artifacts, transitions, the turn table, and what counts as a Blocker.

## Glossary
The engine's glossary holds, with these additions:

* **Kind** - `specs`: a spec's folder is `fondue/specs/<spec>/`.
* **Stage** - one of `brief`, `pre-plan`, `plan`, `implementation`, `handover`, then the engine's `done` or `abandoned`.
* **Phase** - one numbered part of the implementation. `NN` is always two digits, from `01`.
* **Role** - the engine's User and Arbiter, and Architect, Architecture Reviewer, Coder, Code Reviewer. An ad-hoc Handover Writer is not a roster role.
* **Topic** - `pre-plan` and `plan`, whose author is the Architect and whose reviewer is the Architecture Reviewer, and `phase-NN`, whose author is the Coder and whose reviewer is the Code Reviewer.
* **Attempt** - one approach to the spec's goal, from brief to its end: `pre-plan/`, `plan/` and `review/`. The live attempt sits at the spec root. A failed one is moved to `attempts/NN/` (see Reopening).

## Folder layout
```
fondue/specs/
  <spec>/
    current-state.txt, roster.md, 99-user.md, stats.md     (engine)
    landed.md
    pre-plan/
      00-brief.md
      01-research.md
      02-reviewer-research.md
      03-draft.md, 04-draft.md, ...
    plan/
      plan.md
      research.md
      phase-01.md, phase-02.md, ...
    review/
      pre-plan/   00-request.md, 01-review.md, 02-answer.md, ...
      plan/       ...
      phase-01/   ...
    handover/
      00-request.md, 01-request.md, ...
    reopen.md                  (only while a reopen is pending)
    attempts/                  (only after a reopen)
      01/
        pre-plan/  plan/  review/  reopen.md
  archive/
    <spec>/
```

## Stages
The spec starts as the engine's Starting a spec says, with first state `brief`.

### brief
User writes `pre-plan/00-brief.md`, alone or with any AI help they choose. The stage ends when the User tells the Arbiter the brief is signed off. The Arbiter commits and sets `pre-plan:Draft`.

### pre-plan
Pre-plan settles **how the goal is reached**: the approach, the decisions that shape it, and the phases with the gate each must pass. The technical decisions inside each phase belong to plan.

Architect researches what the approach rests on, records it in `01-research.md`, writes the first draft `03-draft.md` and opens `review/pre-plan/` with `00-request.md`.

Why two planning stages: a frame the reviewer rejects throws away everything built on it. Approving the approach first means that only a draft is thrown away, never a set of detailed phase files. The evidence is in `design-notes.md`.

Architecture Reviewer's first turn runs in this order, and the order is the rule:
1. read `00-brief.md`, and every earlier attempt's `plan.md` and `reopen.md` if the spec was reopened, and decide how they would implement it
2. read `01-research.md` if it exists, and do their own research if needed
3. write the research results and their own intended approach into `02-reviewer-research.md`
4. only then open the draft, and write the review

Why: a reviewer who reads the draft first finds problems inside its frame and never questions the frame.

Rounds follow Review. Every accepted fix goes into a new draft file with the next free number. Draft files are never edited. The stage closes on verdict `approved` or `closed`, and the final draft is the subject that verdict names.

### plan
Plan turns each phase of the approved approach into technical decisions and tasks. Architect copies the final draft to `plan/plan.md` with `cp` - never by re-typing it - researches what the technical decisions rest on into `plan/research.md`, writes `plan/phase-NN.md` for every phase, and opens `review/plan/` naming the phase files. The Architecture Reviewer reviews the phase files against `plan.md` and the research, and checks with `diff` that `plan.md` is identical to the final draft. Answer turns edit phase files in place and name the files touched. The stage closes on verdict `approved` or `closed`.

Plan may not change the approach. A plan-stage RESULT that shows the approach cannot work leads to Reopening.

**Light mode.** Light mode is for a spec whose design is settled and whose work is mechanical (a refactor, a move, a rename). The brief opts in with `Mode: light`. The final draft already carries each phase's tasks and gate: in mechanical work the tasks are the approach, and it is the one case where a draft carries them. Architect copies it to `plan.md`, splits its phases verbatim into `phase-NN.md` files, writes no `research.md` and opens no review. Nothing new was written, so there is nothing to review and the stage closes on that turn. Without the line, the spec runs in full mode.

### implementation
How long a Coder and a Code Reviewer live is the roster's **Sessions:**. With `fresh`, the default, every phase gets a new Coder and a new Code Reviewer: the Arbiter spawns each of them before its first turn and sends it no more turns once the phase closes. With `continue`, the pair spawned for the attempt's first phase takes every later phase too, and the Arbiter sends it each phase's turns by its handles. Why `fresh` is the default: a session kept into the next phase re-reads the context it carries on every call of that phase, and in the measured runs that cost more than a new session reading the plan and one phase file. `continue` is an experiment for specs with small phases, where it may cost less. `design-notes.md` has the arithmetic and the results so far.

Coder implements the phase under the engine's Code turns: commit, build green, every gate the phase file names reported. Code Reviewer checks that the change is correct, introduces no problems and follows the project's guidelines, under the same section's limits. Anything missing, such as a test or a case, is a finding.

The stage closes when the last phase closes.

### Reopening
Not a stage: the way out of `plan` or `implementation` when the approved approach turns out not to work. What the new attempt needs most is the previous plan and why it failed, so both are carried forward on disk, never through a message.

1. **Evidence.** The role that hits it, whichever it is, writes `reopen.md` at the spec root and replies BLOCKED, naming it in the reply's sentence. The file holds the RESULT, the `plan.md` lines of every decision the RESULT breaks, and the state it was found in. A Coder leaves the tree at its last green commit. A BLOCKED with no `reopen.md` is an ordinary BLOCKED.
2. **Ruling.** The User reopens, abandons the spec (engine: abandoned), or rules the problem local and names who fixes it. Not every broken task breaks the approach.
3. **The move.** On a reopen, the Arbiter moves `pre-plan/`, `plan/`, `review/` and `reopen.md` into the next `attempts/NN/`, sets the Handle cells of the Architect, the Architecture Reviewer, the Coder and the Code Reviewer in `roster.md` back to `-`, commits `fondue/specs/<spec>/` and sets `brief`. `roster.md`, `99-user.md`, `stats.md` and `landed.md` stay at the root: they span attempts.
4. **The brief.** The User writes a new `pre-plan/00-brief.md`. It may start from the previous one, and it says whether the goal has changed.
5. **The new pair.** A fresh Architect and a fresh Architecture Reviewer, and later a fresh Coder and Code Reviewer for the new attempt's first phase, whatever **Sessions:** says. Why: the pair that designed and approved the failed frame is the pair most anchored to it, and a Coder or Code Reviewer kept from the failed attempt carries that frame in its context.
6. **What they read.** Every attempt's `plan/plan.md` and `reopen.md`: what was planned, and why it failed. The Architect also reads `landed.md`, for the Landed work section. The research files of earlier attempts are a source: a FACT carried forward is restated in the new research with its origin, and a RESULT about the mechanism that failed is re-run. Drafts, reviews and phase files of earlier attempts are never read. Why: they argue for the frame that failed, while `plan.md` states it and `reopen.md` states what broke it.

The new attempt then runs from `brief` like the first, with its phases numbered from `01` again. Its draft carries two more sections (see `pre-plan/NN-draft.md`).

### handover
User decides whether any further document is needed, e.g. a project-level skill. For each one, the User names the model and effort that write it. The Arbiter writes the User's request into the next `handover/NN-request.md`, and spawns a Handover Writer with that model and effort (engine: Starting a role). The stage closes when the User tells the Arbiter to close it, and the spec goes to the engine's `done`.

## State
`current-state.txt` is `<stage>[:<NN>][:<Step>]`. `NN` appears in `implementation` only. `Step` appears in `pre-plan`, `plan` and `implementation` only. Examples: `brief`, `pre-plan:Review`, `plan:Answer`, `implementation:03:Draft`, `done`, `abandoned`.

### Transitions
The engine's rows hold. This skill adds:

| state | reply | next state |
|---|---|---|
| `brief` | User signs the brief off | `pre-plan:Draft` |
| `plan:Draft` | DONE, `light: phases split` | `implementation:01:Draft` |
| `pre-plan:Review` / `pre-plan:Answer` | DONE, `approved` / `closed` | `plan:Draft` |
| `plan:Review` / `plan:Answer` | DONE, `approved` / `closed` | `implementation:01:Draft` |
| `implementation:NN:Review` / `implementation:NN:Answer` | DONE, `approved` / `closed` | `implementation:<NN+1>:Draft`; after the last phase, `handover` |
| `handover` | DONE | `handover` (User asks for another document, or closes the stage: `done`) |
| `plan:<Step>`, `implementation:NN:<Step>` | BLOCKED with `reopen.md`, User rules to reopen | `brief` (see Reopening) |

The last phase is the highest `NN` in `plan/`. Listing that folder is the one listing the Arbiter needs.

### What the Arbiter does on a transition
* **Landed work.** When the new state is `implementation:01:Draft`, or a reply closed a phase, it appends the line to `landed.md`.
* **Fresh sessions.** With **Sessions:** `fresh`, a new phase spawns a new Coder and a new Code Reviewer. With `continue`, only the attempt's first phase does, and later phases reach the same pair by its handles. A reopen spawns a new Architect and a new Architecture Reviewer, and the new attempt's first phase a new Coder and Code Reviewer.
* **Commit points.** When brief, pre-plan and plan end, when each phase ends, on a reopen after the move to `attempts/`, and when handover ends, including the documents it produced, wherever they landed.

## Who reads and writes what
R = reads, W = writes (and reads). A role reads nothing in the spec that this table does not give it.

| artifact | Arbiter | Architect | Arch. Reviewer | Coder | Code Reviewer |
|---|---|---|---|---|---|
| `current-state.txt`, `roster.md`, `99-user.md` | W | R | R | R | R |
| `stats.md` | W | | | | |
| `landed.md` | W | R, after a reopen | | | |
| `pre-plan/00-brief.md` (User writes) | | R | R | | |
| `pre-plan/01-research.md` | | W | R | | |
| `pre-plan/02-reviewer-research.md` | | R | W | | |
| `pre-plan/NN-draft.md` | | W | R | | |
| `plan/plan.md` | | W | R | R | R |
| `plan/research.md` | | W | R | | |
| `plan/phase-NN.md` | lists | W | R | R, own phase | R, own phase |
| `review/pre-plan/`, `review/plan/` | | W request, answers | W reviews | | |
| `review/phase-NN/` | | | | W request, answers | W reviews |
| `handover/NN-request.md` | W | | | | |
| `reopen.md` | moves | W | W | W | W |
| `attempts/NN/plan/plan.md`, `attempts/NN/reopen.md` | moves | R | R | | |
| `attempts/NN/pre-plan/*research.md`, `attempts/NN/plan/research.md` | | R, as a source | R, as a source | | |

The Handover Writer reads its request and what the request names. The User reads and may write anything, including `99-user.md` directly.

## Artifacts

### roster.md
As the engine says, with one more line under **Skill:**, `**Sessions:** fresh | continue`: whether a Coder and a Code Reviewer live for one phase or for every phase of an attempt (see implementation). The Arbiter asks the User for it with the rest of the roster; `fresh` is the default. The default roster runs every role at effort `high`, on Opus, except the Architect, which runs on Fable. The reasons for them are in `design-notes.md` next to this skill. Only the User reads that file, when choosing a roster.

### landed.md
Owned by the Arbiter, and appended when the implementation of an attempt starts and whenever a phase closes. It records where each phase's code ends, so a reopened spec can tell which commits belong to which phase. It works whether or not the spec folder is committed.
```
attempt-<NN> implementation starts at <sha>
attempt-<NN> phase-<NN> closed at <sha>
```
`<sha>` is `git rev-parse HEAD` when the line is written. It is a command the Arbiter runs, not an artifact it reads. `attempt-<NN>` is the number the live attempt would take in `attempts/`: one more than the highest there, or `01` if there is none.

### pre-plan/00-brief.md
Written and signed off by the User. It states what the spec must deliver, everything known that matters, and what is still open. A good brief leaves the Architect knowing the goal and what research the approach needs. Its open questions are the ones whose answer shapes the approach. A technical question may be listed too, and the draft passes it to the phase that answers it.
```
# <spec title>
Mode: full | light

## Goal
<what exists when the spec is done>

## Context
<everything known that matters: code areas, constraints, prior decisions>

## Open questions
<unknowns whose answer shapes the approach; technical ones may be listed, for plan>
```

### pre-plan/01-research.md and 02-reviewer-research.md
Owned by Architect and Architecture Reviewer respectively. Each reads the other's. Every entry is under the engine's Research rule.

Pre-plan research covers what the approach, the phase split or a gate rests on, e.g. whether a library provides a capability at all. Which API it offers, and how it is configured, is research for plan.

`02-reviewer-research.md` also holds the reviewer's own intended approach, written before they open the draft (see pre-plan): a few lines on how they would deliver the brief and the decisions they would take.

### pre-plan/NN-draft.md
The high-level delivery plan, owned by the Architect, numbered from `03` up. It states the approach, the decisions that shape it, each with the alternatives it rejects, and the phases. Each phase states what it delivers and the gate it must pass. The draft answers every open question of the brief that shapes the approach, and names the phase that will answer each of the others.

What goes in the draft is decided by one test: **would getting this wrong change the approach, the phase split or a gate?** If so, it belongs in the draft. If not, it is a technical decision and belongs to plan: a config value, a label name, a class, an API call, a task list. Why: every technical decision a draft carries can be wrong and costs a whole new draft to fix. It also crowds the review, so findings about the frame arrive rounds late.

A draft in a reopened spec carries two more sections:
* **Earlier attempts** - for each one: its approach in a few lines, the assumption its `reopen.md` shows broken, and why this approach does not rest on that assumption.
* **Landed work** - every commit the spec has landed so far, by phase and attempt, including a phase that never closed: keep, amend or revert, each with its reason. An amend or a revert is a phase of this plan like any other. The phase boundaries are in `landed.md`: a phase's commits are those after the line before it, up to its own sha. The commits after the last line belong to the phase that never closed.

### plan/research.md
Owned by the Architect, under the engine's Research rule. It covers the mechanisms that the technical decisions in the phase files rest on. The Architecture Reviewer reads it, and may re-run a RESULT as the anchor of a finding.

### plan/plan.md
A verbatim copy of the final draft. It is never rewritten or summarised, because it carries that draft's approval. From here on it is the plan, and pre-plan is history.

### plan/phase-NN.md
The technical design of one phase: what the Coder needs to build it without making a decision that is not theirs. It holds an introduction, the essential knowledge, the phase's technical decisions, and the tasks that complete the phase, each with how it is tested and its gate.

A technical decision is a choice that fixes a contract, is visible outside the phase, or would be expensive to reverse, e.g. a config key, a metric name and its labels, a histogram's buckets, a wire format, which library API to call. A decision that more than one phase depends on is made in the first of those phases and restated in the others. What the Coder's first build or grep finds - file and importer counts, test counts, paths, line numbers - stays out. Why: a count in a plan can be wrong and costs a round to find, while the Coder finds it in minutes.

**Every research FACT the phase depends on, from pre-plan or plan research, is restated in the phase document, together with what it was verified against.** A pointer to the research is not enough. Why: Coder and Code Reviewer never read the research, so a mechanism reaches implementation only if the Architect carries it forward.

A phase document may list skills for its phase on top of those in `roster.md`.

### review/<topic>/
As the engine says. The subject of `pre-plan` is a draft file, of `plan` a list of phase files, of `phase-NN` a commit range. `phase-NN` is a code topic: its request and answers carry `Build:` and `Gates:`.

### handover/NN-request.md
Written by the Arbiter in the User's own words: what to write, what it is for, and where the finished document belongs, usually in the project and not in the spec folder. The Handover Writer is sent nothing else.

## Roles
The engine's User and Arbiter, and:
* **Architect** - author of the research, drafts and plan. Lives across pre-plan and plan of one attempt.
* **Architecture Reviewer** - reviews drafts and phase files for whether they meet the brief, answer its questions, and are deliverable and testable. Lives across pre-plan and plan of one attempt.
* **Coder** - implements the phases. Lives for one phase, or with **Sessions:** `continue` for every phase of one attempt.
* **Code Reviewer** - reviews the phases. Lives as long as the Coder.

The User also decides the handover.

## Turns
The engine's A turn, with this table:

| state | role | folder | the turn |
|---|---|---|---|
| `pre-plan:Draft` | Architect | `pre-plan/` | research the approach, write `03-draft.md`, open `review/pre-plan/`; after a reopen, read every earlier attempt's `plan.md` and `reopen.md` first |
| `pre-plan:Review` | Architecture Reviewer | `review/pre-plan/` | review the draft the newest file names (first turn: see pre-plan) |
| `pre-plan:Answer` | Architect | `review/pre-plan/` | answer every finding of the newest review; a new draft file if any fix was accepted |
| `plan:Draft` | Architect | `review/pre-plan/` | copy the final draft the newest file names to `plan.md`, research the technical decisions, write the phase files, open `review/plan/`; in light mode split verbatim and open no review |
| `plan:Review` | Architecture Reviewer | `review/plan/` | review the phase files the newest file names, against `plan.md` and `plan/research.md` |
| `plan:Answer` | Architect | `review/plan/` | answer every finding of the newest review, editing phase files and `plan/research.md` in place |
| `implementation:NN:Draft` | Coder (new for phase NN) | `plan/` | implement `phase-NN.md`, commit, build green, open `review/phase-NN/` |
| `implementation:NN:Review` | Code Reviewer (new for phase NN) | `review/phase-NN/` | review the commit range the newest file names; never run the build or the test suite |
| `implementation:NN:Answer` | Coder | `review/phase-NN/` | fix what was accepted, commit, build green, answer |
| `handover` | Handover Writer | `handover/` | write what the newest request asks, where it says |

Reply keywords for turns with no verdict, beyond the engine's `request opened`: `light: phases split` and `handover written`.

## What counts as a Blocker
* On `pre-plan`, a finding is a Blocker only if it is wrong about **the approach, the phase split or a gate**. A finding about a technical decision is a Nit at most, however wrong the decision: it belongs to plan, and the Architect carries it there. So is a technical decision the draft should not carry. In a reopened spec, a draft that rests on an assumption an earlier `reopen.md` shows broken is a Blocker, and so is landed work the draft does not account for.
* On `plan`, a finding is a Blocker when a technical decision is wrong, rests on a mechanism with no RESULT, or is left for the Coder although it fixes a contract or crosses phases; when a task's gate cannot fail; or when the phase files do not deliver what `plan.md` says. A wrong detail the Coder's first build or grep would expose (a count, a path) is a Nit at most.
* On `phase-NN`, a finding is a Blocker when the change is wrong, introduces a problem, breaks the project's rules, or leaves out what the phase file asks for, a test or a case included.
* The Architecture Reviewer judges against the brief, the research and the plan. The Code Reviewer judges against `plan.md`, the phase file, the code and the project's rules, and never opens pre-plan or `plan/research.md`.
