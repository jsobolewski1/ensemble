# converge — design notes

For the User choosing a roster or changing the skill. Roles do not read this file.

## Why the default roster is all Opus except the Architect

Arbiter and Coder were Sonnet until 2026-09-22. Both were changed on measured results, not preference.

- **Coder.** A Sonnet Coder's first implementation of a phase drew 12 Blockers and 10 Nits, its second answer 5 and 5; the Opus Coder that took over closed the phase on the next round.
- **Arbiter.** It looks like the safe place to save a model because it "governs whose turn it is and nothing more" — that reading is wrong. The judgment is in noticing what is *missing*: a Sonnet Arbiter ran a whole spec without ever creating `stats.md`, left `current-state.txt` naming a Review step that an approving review had already closed, and sent `Your turn.` to roles that had not yet handed back. None of those is a hard call; each needs someone who is actually reading the process rather than relaying it.

## Why two planning stages, and where the line between them runs

Pre-plan settles the approach and plan settles the technical decisions, because a frame the reviewer rejects throws away everything built on it. In the archived runs, frame-level Blockers arrived late: a required capability left out, raised in round 1 and re-asserted in round 3; a design option shown to be an estimate rather than exact, in round 4. Had the phase files already been written, each ruling would have discarded them too.

The line matters as much as the split. When pre-plan drafts answered every technical question in the brief, 60-80% of each final draft sat before its phases, as decisions like identifier lengths, metric labels and refresh threads. The pre-plan reviews mixed frame Blockers with technical ones ("the gate cannot query the histogram by its contract name"). Each technical Blocker cost a new draft file and buried the frame findings among them. Plan reviews caught the kind of Blocker plan should catch: a phase consuming a window it never creates, a contract value left for the Coder to invent. Hence the boundary test, and the rule that a technical finding at pre-plan is a Nit.

## Why a reopen starts a new attempt instead of a new draft

A failed approach can surface at plan or deep in implementation, with phases already landed. Continuing the draft sequence would skip the step that matters most at that point: the reviewer writing their own approach before reading the draft, because `02-reviewer-research.md` already exists. So a reopen moves the failed attempt aside, re-signs the brief and seats a fresh pair, who are the least anchored to the old frame.

What the new pair must not lose is why the old plan failed. So they read each earlier `plan.md`, which states the approach on a page because pre-plan drafts carry no technical detail, and each `reopen.md`, which holds the RESULT that broke it. They do not read the drafts, reviews and phase files, which argue for the failed frame. The draft must show that it does not rest on a broken assumption, and it must account for every landed commit, which makes knowing the failure something the reviewer can check.
