"""One entry point for every tool, using the skill's own Python environment.

    python3 scripts/run.py <tool> [args]      tools: transcribe, plan_cuts, timeline, captions, render, check, make_sfx

Run `python3 scripts/setup.py` once before using it.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TOOLS = ('transcribe', 'plan_cuts', 'timeline', 'captions', 'render', 'check', 'make_sfx')


def main():
    if len(sys.argv) < 2 or sys.argv[1] not in TOOLS:
        sys.exit('usage: run.py <' + '|'.join(TOOLS) + '> [args]')
    sub = os.path.join('Scripts', 'python.exe') if os.name == 'nt' else os.path.join('bin', 'python')
    py = os.path.join(ROOT, '.venv', sub)
    if not os.path.isfile(py):
        sys.exit('not set up yet: run  python3 scripts/setup.py  (or py -3 scripts/setup.py) first')
    sys.exit(subprocess.call([py, os.path.join(HERE, sys.argv[1] + '.py')] + sys.argv[2:]))


if __name__ == '__main__':
    main()
