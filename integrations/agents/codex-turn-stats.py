#!/usr/bin/env python3
"""Token figures for one fondue turn, read from a Codex rollout log.

Usage:
    codex-turn-stats.py <session-id> [--all]

<session-id> is the Codex session id printed in the `codex exec` run header and recorded
in the role's Handle cell in roster.md. The log is found under
$CODEX_HOME/sessions/<yyyy>/<mm>/<dd>/rollout-<timestamp>-<session-id>.jsonl, where
$CODEX_HOME defaults to ~/.codex.
Default prints the newest turn as the Tokens and Time cells of a stats.md row; --all
prints every turn of that session, oldest first.

A turn is one task_started .. task_complete span. Its tokens are the sum of the
last_token_usage of every token_count event inside it; its duration is completed_at minus
started_at. Never use the `tokens used` line the CLI prints: it is the session total so far.

Codex counts input differently from Claude: input_tokens includes cached input, so the
cached figure is printed in parentheses as a subset, not an addition. output_tokens
includes reasoning tokens. The columns are not comparable with turn-stats.py's.

Output: in <in> (<cached> cached) · out <out> | <min>m, with 3-digit k/M figures
"""
import glob
import json
import os
import sys


def human(n):
    """A token count to three significant digits: 98, 16.6k, 5.43M."""
    for size, suffix in ((1, ''), (1e3, 'k'), (1e6, 'M')):
        if float(f'{n / size:.3g}') < 1000:
            return f'{n / size:.3g}{suffix}'
    return f'{n / 1e9:.3g}G'


def turns(path):
    found, current = [], None
    with open(path) as f:
        for line in f:
            event = json.loads(line)
            payload = event.get('payload')
            if event.get('type') != 'event_msg' or not isinstance(payload, dict):
                continue
            kind = payload.get('type')
            if kind == 'task_started':
                current = {'start': payload.get('started_at'), 'in': 0, 'cached': 0, 'out': 0}
            elif kind == 'token_count' and current is not None and payload.get('info'):
                usage = payload['info'].get('last_token_usage') or {}
                current['in'] += usage.get('input_tokens', 0)
                current['cached'] += usage.get('cached_input_tokens', 0)
                current['out'] += usage.get('output_tokens', 0)
            elif kind == 'task_complete' and current is not None:
                end = payload.get('completed_at')
                current['min'] = round((end - current['start']) / 60) if end and current['start'] else '?'
                found.append(current)
                current = None
    return found


def main(argv):
    ids = [a for a in argv if not a.startswith('-')]
    if len(ids) != 1:
        sys.exit(__doc__)
    home = os.environ.get('CODEX_HOME') or os.path.expanduser('~/.codex')
    logs = sorted(glob.glob(f'{home}/sessions/*/*/*/rollout-*{ids[0]}.jsonl'))
    if not logs:
        sys.exit(f'no rollout log for {ids[0]} under {home}/sessions')
    found = turns(logs[-1])
    if not found:
        sys.exit(f'no finished turn in {logs[-1]}')
    for t in found if '--all' in argv else found[-1:]:
        print(f"in {human(t['in'])} ({human(t['cached'])} cached) · out {human(t['out'])} | {t['min']}m")


if __name__ == '__main__':
    main(sys.argv[1:])
