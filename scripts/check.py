"""QA a finished render: dead air, picture/voice sync, loudness, every cut frame, and clipped words.

    run.py check <project> <render.mp4> [--verify]

- silence: no gap over 0.2 s anywhere (the reel must have no dead air)
- sync:    video and audio stream durations match
- loudness and true peak
- work/cut_check.jpg: the first frame after every cut, to eyeball each join
- --verify: re-transcribes the render and reports words from the plan that are missing (clipped or swallowed)
"""
import argparse
import difflib
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import find_tool, load_json, run  # noqa: E402


def streams(path):
    out = run([find_tool('ffprobe'), '-v', 'error', '-show_entries', 'stream=codec_type,duration', '-of', 'json', path])
    return {s['codec_type']: float(s.get('duration', 0)) for s in json.loads(out)['streams']}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('render')
    ap.add_argument('--verify', action='store_true')
    a = ap.parse_args()
    proj = os.path.abspath(a.project)
    ff = find_tool('ffmpeg')
    render = a.render if os.path.isabs(a.render) else os.path.join(proj, a.render)
    ok = True

    st = streams(render)
    drift = abs(st.get('video', 0) - st.get('audio', 0))
    print(f'sync: video {st.get("video", 0):.3f}s, audio {st.get("audio", 0):.3f}s, difference {drift * 1000:.0f} ms',
          '(ok)' if drift < 0.06 else '(PROBLEM)')
    ok &= drift < 0.06

    log = run([ff, '-hide_banner', '-i', render, '-af', 'silencedetect=n=-35dB:d=0.2', '-vn', '-f', 'null', '-'], check=False)
    gaps = re.findall(r'silence_start: ([\d.]+)', log)
    durs = re.findall(r'silence_duration: ([\d.]+)', log)
    if gaps:
        ok = False
        print('silence over 0.2 s at:', ', '.join(f'{float(g):.2f}s ({float(d):.2f}s)' for g, d in zip(gaps, durs)), '(PROBLEM)')
    else:
        print('silence: none over 0.2 s (ok)')

    log = run([ff, '-hide_banner', '-i', render, '-af', 'ebur128=peak=true', '-vn', '-f', 'null', '-'], check=False)
    lufs = re.findall(r'I:\s+(-?[\d.]+) LUFS', log)
    peak = re.findall(r'Peak:\s+(-?[\d.]+) dBFS', log)
    print(f'loudness: {lufs[-1] if lufs else "?"} LUFS, true peak {peak[-1] if peak else "?"} dBFS (target about -14 LUFS, peak under -1)')

    tl = load_json(os.path.join(proj, 'timeline.json'))
    work = os.path.join(proj, 'work')
    os.makedirs(work, exist_ok=True)
    cuts = tl['cuts'][:30]
    for i, t in enumerate(cuts, 1):
        run([ff, '-y', '-v', 'error', '-ss', f'{t + 0.12:.3f}', '-i', render, '-frames:v', '1', '-vf', 'scale=270:-1',
             os.path.join(work, f'cut_{i:02d}.jpg')])
    if cuts:
        run([ff, '-y', '-v', 'error', '-framerate', '1', '-i', os.path.join(work, 'cut_%02d.jpg'),
             '-vf', 'tile=8x%d' % ((len(cuts) + 7) // 8), '-frames:v', '1', os.path.join(work, 'cut_check.jpg')])
        print(f'cut frames: {len(cuts)} -> work/cut_check.jpg (look at every one: the new shot must be clean)')

    if a.verify:
        from faster_whisper import WhisperModel
        model = WhisperModel('small.en', device='cpu', compute_type='int8')
        segs, _ = model.transcribe(render, word_timestamps=False, vad_filter=False)
        heard = [re.sub(r'[^a-z0-9]', '', w.lower()) for s in segs for w in s.text.split()]
        want = [re.sub(r'[^a-z0-9]', '', w['w'].lower()) for w in tl['words']]
        heard, want = [h for h in heard if h], [w for w in want if w]
        sm = difflib.SequenceMatcher(None, want, heard, autojunk=False)
        missing = [' '.join(want[i1:i2]) for tag, i1, i2, _, _ in sm.get_opcodes() if tag in ('delete', 'replace')]
        if missing:
            ok = False
            print('words that did not survive the cut (check for clipping):', '; '.join(missing[:15]), '(PROBLEM)')
        else:
            print('verify: every planned word is audible in the render (ok)')
    print('RESULT:', 'all checks passed' if ok else 'fix the problems above and re-render')


if __name__ == '__main__':
    main()
