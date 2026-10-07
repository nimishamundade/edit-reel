"""Turn transcripts into an edit list with no dead air.

    run.py plan_cuts <project> [--clips c1,c2] [--pre 0.07] [--post 0.10] [--no-zoom]

Every run of continuous speech becomes one segment. A gap between words is cut down to pre+post seconds
(the padding kept around each word) whenever it is longer than that, so pauses, breaths and filler words
vanish while the word edges stay unclipped. Writes <project>/edl.json.

After this, YOU choose takes: delete the segments of weaker takes from edl.json (keep the last clean take of a
repeated line), reorder if the script needs it, then run `run.py timeline <project>` to re-flow the timings.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, save_json  # noqa: E402

FILLERS = {'um', 'uh', 'uhm', 'umm', 'erm', 'er', 'ah', 'hmm', 'mm', 'mhm'}


def is_filler(w):
    return w.lower().strip('.,!?…-') in FILLERS


def plan(words, duration, pre, post):
    words = [w for w in words if not is_filler(w['w'])]
    segs, run_ = [], []
    for w in words:
        if run_ and w['s'] - run_[-1]['e'] > pre + post:
            segs.append(run_)
            run_ = []
        run_.append(w)
    if run_:
        segs.append(run_)
    out = []
    for r in segs:
        out.append({'in': round(max(0.0, r[0]['s'] - pre), 3),
                    'out': round(min(duration, r[-1]['e'] + post), 3),
                    'words': r})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--clips', default='')
    ap.add_argument('--pre', type=float, default=0.07)
    ap.add_argument('--post', type=float, default=0.10)
    ap.add_argument('--no-zoom', action='store_true')
    a = ap.parse_args()

    tr = load_json(os.path.join(a.project, 'transcript.json'))['clips']
    order = [c for c in a.clips.split(',') if c] or list(tr)
    edl, n, zoom_flip = [], 0, False
    for cid in order:
        prev_clip = None
        for seg in plan(tr[cid]['words'], tr[cid]['duration'], a.pre, a.post):
            n += 1
            # consecutive jump cuts inside one take alternate wide / punched-in so they read as intentional
            if prev_clip == cid and not a.no_zoom:
                zoom_flip = not zoom_flip
            else:
                zoom_flip = False
            seg.update({'id': f's{n}', 'clip': cid, 'zoom': 1.24 if zoom_flip else 1.0, 'cx': 0.5, 'cy': 0.45})
            edl.append(seg)
            prev_clip = cid
    save_json(os.path.join(a.project, 'edl.json'), edl)
    kept = sum(s['out'] - s['in'] for s in edl)
    src = sum(tr[c]['duration'] for c in order)
    print(f'{len(edl)} segments, {kept:.1f}s kept of {src:.1f}s ({src - kept:.1f}s of dead air and retakes cut)')
    print('next: remove weaker takes from edl.json, then: run.py timeline <project>')


if __name__ == '__main__':
    main()
