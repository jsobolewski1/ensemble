#!/usr/bin/env python3
"""Token figures for one fondue turn, read from a Claude Code transcript.

Usage:
    turn-stats.py <id> [--all] [--project DIR]

<id> is a session id (a role User started) or an agent id (a role Arbiter spawned);
the transcript is found either way. Default prints the newest turn as the Tokens
and Time cells of a stats.md row; --all prints every turn of that session, oldest first.

A transcript writes one line per content block and every line repeats its message's
whole usage, so each message is counted once, by id, with its last line winning.
Summing every line counts input and cache two to three times over.
"""
import json, os, sys, glob
from datetime import datetime

KEYS = ['input_tokens', 'output_tokens', 'cache_creation_input_tokens', 'cache_read_input_tokens']


def transcript(ident, project):
    slug = project.replace('/', '-')
    root = os.path.expanduser(f'~/.claude/projects/{slug}')
    for pattern in (f'{root}/{ident}.jsonl', f'{root}/*/subagents/agent-{ident}.jsonl'):
        hit = glob.glob(pattern)
        if hit:
            return max(hit, key=os.path.getmtime)
    sys.exit(f'no transcript for {ident} under {root}')


def turns(path):
    """A turn starts at each prompt sent into the session; assistant messages follow it."""
    out, cur = [], None
    for line in open(path):
        rec = json.loads(line)
        msg = rec.get('message') or {}
        if rec.get('type') == 'user' and isinstance(msg.get('content'), str):
            cur = {'usage': {}, 'stamps': []}
            out.append(cur)
        elif rec.get('type') == 'assistant' and cur is not None:
            cur['usage'][msg.get('id')] = msg.get('usage') or {}
            cur['stamps'].append(rec['timestamp'])
    return [t for t in out if t['stamps']]


def human(n):
    """A token count to three significant digits: 98, 16.6k, 5.43M."""
    for size, suffix in ((1, ''), (1e3, 'k'), (1e6, 'M')):
        if float(f'{n / size:.3g}') < 1000:
            return f'{n / size:.3g}{suffix}'
    return f'{n / 1e9:.3g}G'


def line(turn):
    i, o, cc, cr = (sum(u.get(k, 0) for u in turn['usage'].values()) for k in KEYS)
    at = [datetime.fromisoformat(s.replace('Z', '+00:00')) for s in (turn['stamps'][0], turn['stamps'][-1])]
    return f"out {human(o)} · write {human(cc)} · read {human(cr)} · in {human(i)} | {round((at[1] - at[0]).seconds / 60)}m"


args = [a for a in sys.argv[1:] if not a.startswith('--')]
flags = {a for a in sys.argv[1:] if a.startswith('--')}
if not args:
    sys.exit(__doc__)
project = os.getcwd()
if '--project' in flags:
    project = sys.argv[sys.argv.index('--project') + 1]

found = turns(transcript(args[0], project))
for t in (found if '--all' in flags else found[-1:]):
    print(line(t))
