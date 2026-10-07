"""EDL -> timeline: where every word lands in the finished reel.

    run.py timeline <project>                 rebuild timeline.json from edl.json
    run.py timeline <project> find "seed oils"   print the reel time of a phrase (to time lists and overlays)

timeline.json holds words with reel times, the cut points, and the total duration. Captions, lists,
overlays and sound effects are all timed against this file, so rebuild it whenever edl.json changes.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json, save_json  # noqa: E402


def build(project):
    edl = load_json(os.path.join(project, 'edl.json'))
    words, cuts, t = [], [], 0.0
    for seg in edl:
        dur = seg['out'] - seg['in']
        cuts.append(round(t, 3))
        for w in seg['words']:
            if seg['in'] <= w['s'] < seg['out']:
                words.append({'w': w['w'], 's': round(t + w['s'] - seg['in'], 3),
                              'e': round(t + min(w['e'], seg['out']) - seg['in'], 3), 'seg': seg['id']})
        t += dur
    tl = {'duration': round(t, 3), 'cuts': cuts[1:], 'words': words}
    save_json(os.path.join(project, 'timeline.json'), tl)
    return tl


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def find(tl, phrase):
    want = [norm(x) for x in phrase.split() if norm(x)]
    ws = [norm(w['w']) for w in tl['words']]
    hits = []
    for i in range(len(ws) - len(want) + 1):
        if ws[i:i + len(want)] == want:
            hits.append((tl['words'][i]['s'], tl['words'][i + len(want) - 1]['e']))
    return hits


if __name__ == '__main__':
    proj = sys.argv[1]
    tl = build(proj)
    if len(sys.argv) > 3 and sys.argv[2] == 'find':
        hits = find(tl, ' '.join(sys.argv[3:]))
        print('\n'.join(f'{s:.2f}s - {e:.2f}s' for s, e in hits) or 'not found')
    else:
        print(f'timeline.json: {len(tl["words"])} words, {len(tl["cuts"]) + 1} segments, {tl["duration"]:.1f}s')
