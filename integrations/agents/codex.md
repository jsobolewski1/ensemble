# codex - adapter for OpenAI Codex

An adapter under the contract in `contract.md` next to it. Each RESULT names the codex-cli version it was verified on. On another version, re-run it before trusting it: this is alpha software, and its flags move.

## Detect
Codex ships in three places, and more than one may be installed:
* a standalone CLI (e.g. npm `@openai/codex`), on `PATH`
* the macOS ChatGPT desktop app, **not** on `PATH`: `/Applications/ChatGPT.app/Contents/Resources/codex`
* the VS Code ChatGPT extension, usually an older copy

```bash
command -v codex
ls -la /Applications/ChatGPT.app/Contents/Resources/codex
find /Applications ~/.vscode/extensions ~/.cursor/extensions -maxdepth 6 -type f \
  -perm +111 -name codex 2>/dev/null          # GNU find: -perm /111
"$CODEX" --version                             # e.g. codex-cli 0.155.0-alpha.9.2
"$CODEX" login status                          # "Logged in using ChatGPT", exit 0
```
If several copies are found, use the highest `--version`. `login status` was verified on 0.155.0-alpha.9.2. Config, auth and session logs live in `$CODEX_HOME`, which defaults to `~/.codex/` (`config.toml`, `auth.json`, `sessions/`). Some tools set `CODEX_HOME` to a directory of their own, so read the config the agent actually uses, `"${CODEX_HOME:-$HOME/.codex}/config.toml"`, never `~/.codex` by assumption. With the desktop app, sign-in is through ChatGPT and there is no API key. Nothing here spends tokens.

## Start
```bash
"$CODEX" exec -C <project dir> -s workspace-write \
  -o <reply file> "<spawn prompt>" < /dev/null
```
The session id is a UUID in the run header, as `session id: 01a0bf4c-...`. Record it; it is the handle. `resume --last` exists, but with several roles running, "newest" is a guess.

`< /dev/null` is required. Without it, `exec` waits for more prompt on stdin, forever, in a non-interactive shell. The line `Reading additional input from stdin...` still prints, and it is harmless.

## Turn
```bash
"$CODEX" exec resume <session id> -c sandbox_mode='"workspace-write"' \
  -o <reply file> "Your turn." < /dev/null
```
`exec resume` accepts neither `-s`, `-C` nor `--add-dir` (verified on 0.154.0-alpha.6.2, and its `--help` on 0.155.0-alpha.9.2). Permissions are set through `-c` on every turn (see Permissions).

## Reply
The `-o` file holds exactly the final message. Stdout carries the banner, the reasoning trace and the token line, so it is never parsed. Use one reply file per role, e.g. `$TMPDIR/converge-<spec>-<role>.txt`.

## Skills
By path, as the contract's default: the spawn prompt says `Read <skill dir>/SKILL.md and follow it as the <name> skill.` That works whatever Codex has imported. The desktop app can import Claude's user-level skills (`~/.claude/skills/`), but that covers neither skills installed by a plugin nor a project's `.claude/skills/`.

## Permissions
`workspace-write` covers the workdir, `/tmp` and `$TMPDIR`. The project's `.git` sits inside the workdir, so commits work.
* **The sandbox may not survive a resume.** A session started `-s read-only` came back as `sandbox: workspace-write [workdir, /tmp, $TMPDIR]` on an `exec resume` that set nothing (0.154.0-alpha.6.2). On 0.155.0-alpha.9.2 the same resume kept `sandbox: read-only`. Which versions reset it is not known, so every Turn passes `-c sandbox_mode='"<mode>"'` again, together with the settings below, and the Arbiter checks that the resumed run's `sandbox:` header line matches the first run's.
* A directory outside the workdir, such as a sibling checkout: `--add-dir <dir>` on Start, `-c 'sandbox_workspace_write.writable_roots=["<dir>"]'` on every Turn.
* Network, e.g. for a build that downloads dependencies: `-c sandbox_workspace_write.network_access=true`, on Start and on every Turn.

Decide both when the roster is written. Otherwise the role's first turn fails and comes back as BLOCKED.

## Model and effort
`-m <model>` on Start and Turn. Effort: `-c model_reasoning_effort='"<effort>"'`. ensemble's five levels map one to one: `low`, `medium`, `high`, `xhigh`, `max`. Each returned a reply on `gpt-5.6-sol` (0.155.0-alpha.9.2). The model also accepts `none` and `minimal`.

An unsupported value fails the turn with HTTP 400 and lists the supported ones: `Supported values are: 'none', 'minimal', 'low', 'medium', 'high', 'xhigh', and 'max'.` The run header echoes whatever value was set, even an invalid one, so the header is not evidence that a value is accepted. Supported values depend on the model, so re-check them when the model changes.

## Stats
```bash
python3 <this folder>/codex-turn-stats.py <session id>          # newest turn; honours $CODEX_HOME
python3 <this folder>/codex-turn-stats.py <session id> --all
```
It reads the rollout log under `$CODEX_HOME/sessions/`. Output: `<in>(<cached> cached)/<out> <min>m`. Codex counts cached input inside input, so the row is not comparable with a Claude row.

Never use the `tokens used` line the CLI prints. It is the session total so far, not the turn's figure. It has no input/output/cache split, and its thousands separator is a space (`20 141`).

## Verify
```bash
"$CODEX" exec -s read-only -o "$TMPDIR/ping.txt" "Reply with exactly: PONG" < /dev/null
cat "$TMPDIR/ping.txt"                          # PONG
"$CODEX" exec resume <session id> -c sandbox_mode='"read-only"' \
  -o "$TMPDIR/ping.txt" "What did you reply last time? One word." < /dev/null
cat "$TMPDIR/ping.txt"                          # PONG
```
Run it from the project directory. Outside a git repository, `exec` refuses to start unless it gets `--skip-git-repo-check`.

If the second answer shows no memory of the first, Turn starts a new session instead of continuing one, and every turn would pay for a cold context.

## Gotchas
* This line appears on many runs and means nothing, so it is not a failed turn:
  `ERROR codex_models_manager::manager: failed to refresh available models: timeout waiting for child process to exit`
  (0.154.0-alpha.6.2).
