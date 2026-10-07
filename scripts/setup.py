"""First-run setup. Safe to re-run.

    python3 scripts/setup.py        (or: python scripts/setup.py   |   py -3 scripts/setup.py)

Checks ffmpeg and Python, builds a private virtual environment inside the skill (faster-whisper for
transcription), generates the sound effects, and prints one STATUS line per item and then READY or NOT READY.
Standard library only, because it runs before the environment exists.
"""
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

# av 19 changed an argument that faster-whisper 1.2.x still passes, so keep av below 19
REQUIREMENTS = ['faster-whisper==1.2.1', 'av>=11,<19']

FIX = {
    'ffmpeg': {'nt': 'winget install --id Gyan.FFmpeg -e   (then quit and reopen your terminal / Claude Code)',
               'darwin': 'brew install ffmpeg', 'posix': 'sudo apt install ffmpeg'},
    'python': {'nt': 'winget install --id Python.Python.3.12 -e', 'darwin': 'brew install python',
               'posix': 'sudo apt install python3 python3-venv'},
}


def fix(what):
    key = 'nt' if os.name == 'nt' else ('darwin' if sys.platform == 'darwin' else 'posix')
    return FIX[what][key]


def venv_python():
    sub = os.path.join('Scripts', 'python.exe') if os.name == 'nt' else os.path.join('bin', 'python')
    return os.path.join(ROOT, '.venv', sub)


def say(s):
    print(s, flush=True)


def main():
    ready = True
    try:
        from common import find_tool
        find_tool('ffmpeg'), find_tool('ffprobe')
        say('STATUS ffmpeg OK')
    except SystemExit:
        say(f'STATUS ffmpeg MISSING -> {fix("ffmpeg")}')
        ready = False

    if sys.version_info < (3, 10):
        say(f'STATUS python too old ({sys.version_info.major}.{sys.version_info.minor}, need 3.10+) -> {fix("python")}')
        sys.exit(1)

    py = venv_python()
    if not os.path.isfile(py):
        say('STATUS venv: creating .venv (about 1 minute)')
        r = subprocess.run([sys.executable, '-m', 'venv', os.path.join(ROOT, '.venv')])
        if r.returncode != 0:
            say(f'STATUS venv FAILED -> {fix("python")}')
            sys.exit(1)
    test = [py, '-c', 'import faster_whisper']
    if subprocess.run(test, capture_output=True).returncode != 0:
        say('STATUS venv: installing faster-whisper')
        subprocess.run([py, '-m', 'pip', 'install', '-q', '--upgrade', 'pip'])
        r = subprocess.run([py, '-m', 'pip', 'install', '-q'] + REQUIREMENTS)
        if r.returncode != 0 or subprocess.run(test, capture_output=True).returncode != 0:
            say('STATUS venv FAILED (pip install error above)')
            ready = False
    if ready:
        say('STATUS venv OK')

    if ready:
        r = subprocess.run([py, os.path.join(HERE, 'make_sfx.py')], capture_output=True, text=True)
        say('STATUS sound effects OK' if r.returncode == 0 else f'STATUS sound effects FAILED: {r.stderr[-200:]}')
    say('READY' if ready else 'NOT READY')
    sys.exit(0 if ready else 1)


if __name__ == '__main__':
    main()
