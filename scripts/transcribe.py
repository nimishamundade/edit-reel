"""Word-level transcription of the raw clips.

    run.py transcribe <project> <clip> [<clip> ...] [--model small.en] [--prompt "Names, Keywords"]

Writes <project>/transcript.json. Clips get ids c1, c2, ... in the order given.
The prompt biases Whisper toward product names and jargon it would otherwise mishear.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import probe, save_json  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('clips', nargs='+')
    ap.add_argument('--model', default='small.en')
    ap.add_argument('--prompt', default='')
    a = ap.parse_args()

    from faster_whisper import WhisperModel
    model = WhisperModel(a.model, device='cpu', compute_type='int8')
    out = {'clips': {}}
    for i, path in enumerate(a.clips, 1):
        path = os.path.abspath(os.path.expanduser(path))
        cid = f'c{i}'
        info = probe(path)
        print(f'{cid}: {os.path.basename(path)} ({info["duration"]:.1f}s) transcribing...', flush=True)
        segs, _ = model.transcribe(path, word_timestamps=True, vad_filter=False,
                                   initial_prompt=a.prompt or None, condition_on_previous_text=False)
        words = []
        for s in segs:
            for w in s.words or []:
                t = w.word.strip()
                if t:
                    words.append({'w': t, 's': round(w.start, 3), 'e': round(w.end, 3)})
        out['clips'][cid] = {'path': path, 'duration': info['duration'],
                             'width': info['width'], 'height': info['height'], 'words': words}
        print(f'{cid}: {len(words)} words', flush=True)
    save_json(os.path.join(a.project, 'transcript.json'), out)
    print('wrote transcript.json')


if __name__ == '__main__':
    main()
