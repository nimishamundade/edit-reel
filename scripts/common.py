"""Shared helpers: tool discovery, ffprobe wrapper, json io, path handling."""
import glob
import json
import os
import shutil
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def find_tool(name):
    """Path to ffmpeg / ffprobe. Falls back to the usual winget install folder on Windows."""
    p = shutil.which(name)
    if p:
        return p
    if os.name == 'nt':
        base = os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Microsoft', 'WinGet', 'Packages')
        hits = glob.glob(os.path.join(base, 'Gyan.FFmpeg*', '**', 'bin', name + '.exe'), recursive=True)
        if hits:
            return hits[0]
    sys.exit(f'{name} not found. Install ffmpeg first (see README), then reopen your terminal.')


def run(cmd, cwd=None, check=True, quiet=False):
    """Run a command list, return stdout. Raises SystemExit with ffmpeg's tail on failure."""
    r = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if check and r.returncode != 0:
        tail = '\n'.join((r.stderr or '').strip().splitlines()[-15:])
        sys.exit(f'command failed ({r.returncode}): {" ".join(map(str, cmd[:3]))} ...\n{tail}')
    # check=True callers want clean stdout (ffprobe json); check=False callers parse ffmpeg's stderr log
    return r.stdout if check else (r.stdout + r.stderr)


def filter_file_args(path):
    """ffmpeg 7+ reads a filter graph from a file with -/filter_complex; older builds use -filter_complex_script."""
    import re
    m = re.search(r'version n?(\d+)', run([find_tool('ffmpeg'), '-version'], check=False))
    if m and int(m.group(1)) < 7:
        return ['-filter_complex_script', path]
    return ['-/filter_complex', path]


def probe(path):
    out = run([find_tool('ffprobe'), '-v', 'error', '-show_entries',
               'format=duration:stream=codec_type,width,height,r_frame_rate',
               '-of', 'json', path])
    d = json.loads(out)
    v = next((s for s in d['streams'] if s['codec_type'] == 'video'), None)
    a = next((s for s in d['streams'] if s['codec_type'] == 'audio'), None)
    return {'duration': float(d['format']['duration']),
            'width': v and v.get('width'), 'height': v and v.get('height'),
            'has_audio': a is not None}


def load_json(path, default=None):
    if not os.path.isfile(path):
        if default is not None:
            return default
        sys.exit(f'missing {path}')
    with open(path, encoding='utf-8') as f:
        return json.load(f)


def save_json(path, data):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=1, ensure_ascii=False)
        f.write('\n')


def fmt(t):
    return f'{t:.3f}'
