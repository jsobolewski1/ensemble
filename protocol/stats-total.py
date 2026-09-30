#!/usr/bin/env python3
"""Totals of one spec's or bug's stats.md, by role and by stage.

Usage:
    stats-total.py <stats.md> [--write-weight W]

Reads both the table rows and the one-line rows of older specs. Claude rows are summed
per role and model, and weighted into input-equivalent tokens: input 1, output 5, cache
read 0.1, cache write W. W is 2 for the one-hour cache the roles use, 1.25 for the
five-minute cache of specs run before it. Input-equivalent tokens are in the row's own
model's input price, so a total over roles on different models compares specs only when
they ran the same roster.

Rows of another agent are summed apart and never weighted: their columns are not
comparable with Claude's. Rows without figures are only counted.
"""
import re
import sys
from collections import defaultdict

UNIT = {'': 1, 'k': 1e3, 'M': 1e6, 'G': 1e9}
OLD_CLAUDE = re.compile(r'(\d+)/(\d+)/(\d+)cc/(\d+)cr (\d+)m')
OLD_OTHER = re.compile(r'(\d+)\((\d+) cached\)/(\d+) (\d+)m')
FIGURE = r'([\d.]+)([kMG]?)'


def human(n):
    """A token count to three significant digits: 98, 16.6k, 5.43M."""
    for size, suffix in ((1, ''), (1e3, 'k'), (1e6, 'M')):
        if float(f'{n / size:.3g}') < 1000:
            return f'{n / size:.3g}{suffix}'
    return f'{n / 1e9:.3g}G'


def number(value, unit):
    return float(value) * UNIT[unit]


def split_head(head):
    """'2026-09-26 Architecture Reviewer codex gpt-5.6-sol/xhigh' -> role, model.
    Role words are capitalised; the agent and model that follow them are not."""
    words = head.split()[1:]
    end = max(i for i, w in enumerate(words) if '/' in w)
    start = end
    while start > 0 and words[start - 1][0].islower():
        start -= 1
    return ' '.join(words[:start]), ' '.join(words[start:end + 1])


def parse_line(line):
    """One old-format row: <date> <role> <model> | <reply> | <figures>."""
    fields = line.split(' | ')
    role, model = split_head(fields[0])
    reply = fields[1].split() if len(fields) > 1 else []
    state = reply[1] if len(reply) > 1 and reply[0] in ('DONE', 'BLOCKED', 'CONFLICT') else '?'
    figures = fields[-1]
    if m := OLD_CLAUDE.search(figures):
        i, o, cc, cr, t = map(int, m.groups())
        return role, model, state, {'in': i, 'out': o, 'write': cc, 'read': cr}, t, 'claude'
    if m := OLD_OTHER.search(figures):
        i, cached, o, t = map(int, m.groups())
        return role, model, state, {'in': i, 'cached': cached, 'out': o}, t, 'other'
    return role, model, state, {}, 0, None


def parse_row(line):
    """One table row: Date | Role | Model | State | Result | Counts | Tokens | Time."""
    cells = [c.strip() for c in re.split(r'(?<!\\)\|', line.strip().strip('|'))]
    if len(cells) < 8 or not re.match(r'\d{4}-\d\d-\d\d$', cells[0]):
        return None
    _, role, model, state, _, _, tokens, time = cells[:8]
    t = int(time[:-1]) if re.match(r'\d+m$', time) else 0
    if m := re.search(FIGURE + r' cached', tokens):
        cached = number(*m.groups())
        i = re.search(r'in ' + FIGURE, tokens)
        o = re.search(r'out ' + FIGURE, tokens)
        return role, model, state, {'in': number(*i.groups()), 'cached': cached,
                                    'out': number(*o.groups())}, t, 'other'
    found = {}
    for key in ('in', 'out', 'write', 'read'):
        if m := re.search(rf'\b{key} ' + FIGURE, tokens):
            found[key] = number(*m.groups())
    return role, model, state, found, t, 'claude' if found else None


def weighted(n, write_weight):
    return n.get('in', 0) + 5 * n.get('out', 0) + 0.1 * n.get('read', 0) + write_weight * n.get('write', 0)


def main(argv):
    write_weight = 2.0
    if '--write-weight' in argv:
        at = argv.index('--write-weight')
        write_weight = float(argv[at + 1])
        argv = argv[:at] + argv[at + 2:]
    paths = [a for a in argv if not a.startswith('--')]
    if len(paths) != 1:
        sys.exit(__doc__)

    rows = []
    for line in open(paths[0]):
        line = line.rstrip('\n')
        if line.startswith('|'):
            row = parse_row(line)
        elif re.match(r'\d{4}-\d\d-\d\d ', line):
            row = parse_line(line)
        else:
            row = None
        if row:
            rows.append(row)
    if not rows:
        sys.exit(f'no stats rows in {paths[0]}')

    claude = defaultdict(lambda: defaultdict(float))
    stages = defaultdict(lambda: defaultdict(float))
    other = defaultdict(lambda: defaultdict(float))
    without = 0
    for role, model, state, n, t, kind in rows:
        if kind is None:
            without += 1
            continue
        group = other[(role, model)] if kind == 'other' else claude[(role, model)]
        group['turns'] += 1
        group['min'] += t
        for k, v in n.items():
            group[k] += v
        if kind == 'claude':
            stage = stages[state.split(':')[0]]
            stage['turns'] += 1
            stage['min'] += t
            stage['equiv'] += weighted(n, write_weight)

    print(f'Claude roles (input-equivalent: in 1, out 5, read 0.1, write {write_weight:g})')
    print(f"{'Role':24} {'Model':14} {'Turns':>5} {'Time':>6} {'Output':>7} {'Write':>7} {'Read':>7} {'Input':>7} {'In-equiv':>9}")
    total = 0
    for (role, model), g in claude.items():
        eq = weighted(g, write_weight)
        total += eq
        print(f"{role:24} {model:14} {int(g['turns']):5} {int(g['min']):5}m {human(g['out']):>7} "
              f"{human(g['write']):>7} {human(g['read']):>7} {human(g['in']):>7} {human(eq):>9}")
    print(f"{'All Claude roles':60} {human(total):>34}\n")

    print('Claude turns by stage (mixes models: compare specs with the same roster)')
    for stage, g in stages.items():
        print(f"{stage:24} {int(g['turns']):5} turns {int(g['min']):5}m {human(g['equiv']):>9}")

    if other:
        print('\nOther agents (not weighted, not comparable with Claude rows)')
        for (role, model), g in other.items():
            print(f"{role:24} {model:24} {int(g['turns']):3} turns {int(g['min']):4}m  "
                  f"in {human(g['in'])} ({human(g['cached'])} cached) · out {human(g['out'])}")

    if without:
        print(f'\n{without} turns without figures')


if __name__ == '__main__':
    main(sys.argv[1:])
