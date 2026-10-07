"""Instagram Refined captions, hook text and on-screen lists -> captions.ass (burned in by render.py).

    run.py captions <project>

Reads timeline.json (word times in the finished reel) and events.json (hook, emphasis words, lists).
Look: lowercase heavy sans, white, one accent colour on the punch words, each word popping in on the
frame it is spoken. Spoken lists are shown as a stack of lines, one per item, as each item is said.
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_json  # noqa: E402

DEFAULTS = {
    'font': 'Arial Black',      # installed on Windows and macOS; drop a static TTF in <project>/fonts and set "fontsdir" to change
    'size': 92,                 # caption size (PlayRes 1080x1920)
    'list_size': 78,
    'hook_size': 80,
    'accent': '#F5D36B',        # warm gold: punch words and list numbers
    'caption_y': 1235,          # centre of the caption line; the safe zone ends at y 1470
    'list_top': 880,            # y of the first list line
    'hook_y': 360,              # centre of the hook text (safe zone starts at y 220)
    'max_words': 3,
    'max_chars': 16,
}


def bgr(hex_):
    h = hex_.lstrip('#')
    return f'&H00{h[4:6]}{h[2:4]}{h[0:2]}&'


def ts(t):
    t = max(0.0, t)
    h, m, s = int(t // 3600), int(t % 3600 // 60), t % 60
    return f'{h}:{m:02d}:{s:05.2f}'


def norm(s):
    return re.sub(r'[^a-z0-9]', '', s.lower())


def clean(w):
    w = w.replace('—', ' ').replace('–', ' ')
    return w.lower().strip(',.;:!"“”‘’ ') or w


def chunk_words(words, st):
    out, cur = [], []
    for w in words:
        t = clean(w['w'])
        if cur:
            chars = sum(len(c['t']) for c in cur) + len(cur) + len(t)
            gap = w['s'] - cur[-1]['e']
            ended = cur[-1]['raw'].rstrip('"”')[-1:] in '.?!'
            if len(cur) >= st['max_words'] or chars > st['max_chars'] or gap > 0.35 or ended:
                out.append(cur)
                cur = []
        cur.append({'t': t, 's': w['s'], 'e': w['e'], 'raw': w['w']})
    if cur:
        out.append(cur)
    return out


def caption_events(tl, ev, st, windows):
    white, accent = bgr('#FFFFFF'), bgr(st['accent'])
    emph = {norm(x) for x in ev.get('emphasis', [])}
    chunks = chunk_words(tl['words'], st)
    lines = []
    for i, ch in enumerate(chunks):
        start = ch[0]['s']
        nxt = chunks[i + 1][0]['s'] if i + 1 < len(chunks) else None
        end = ch[-1]['e'] + 0.25
        if nxt is not None and nxt - ch[-1]['e'] < 0.4:
            end = nxt
        for w0, w1 in windows:               # lists replace captions while they are on screen
            if start >= w0 and start < w1:
                end = start
            elif start < w0 < end:
                end = w0
        if end - start < 0.08:
            continue
        parts = []
        for c in ch:
            a = int(round((c['s'] - start) * 1000))
            hot = norm(c['t']) in emph
            s0, s1 = (130, 112) if hot else (118, 100)
            parts.append(r'{\1c%s\alpha&HFF&\fscx%d\fscy%d\t(%d,%d,\alpha&H00&)\t(%d,%d,\fscx%d\fscy%d)}%s '
                         % (accent if hot else white, s0, s0, a, a + 1, a, a + 140, s1, s1, c['t']))
        text = r'{\an5\pos(540,%d)}' % st['caption_y'] + ''.join(parts).rstrip()
        lines.append(f'Dialogue: 0,{ts(start)},{ts(end)},Cap,,0,0,0,,{text}')
    return lines


def list_events(ev, st):
    lines, windows = [], []
    white, accent = bgr('#FFFFFF'), bgr(st['accent'])
    for lst in ev.get('lists', []):
        items = lst['items']
        if not items:
            continue
        n = len(items)
        line_h = min(104, 560 // max(n, 1))
        size = st['list_size'] if n <= 4 else int(st['list_size'] * 0.85)
        end = lst['end']
        windows.append((items[0]['at'] - 0.05, end))
        for i, it in enumerate(items):
            y = st['list_top'] + i * line_h + line_h // 2
            label = ''
            if lst.get('numbered'):
                label = r'{\1c%s}%d  {\1c%s}' % (accent, i + 1, white)
            text = (r'{\an5\pos(540,%d)\fs%d\1c%s\fad(0,120)\fscx115\fscy115\t(0,130,\fscx100\fscy100)}%s%s'
                    % (y, size, white, label, it['text'].lower()))
            lines.append(f'Dialogue: 1,{ts(it["at"])},{ts(end)},Cap,,0,0,0,,{text}')
    return lines, windows


def hook_events(ev, st):
    h = ev.get('hook')
    if not h:
        return []
    text = (r'{\an5\pos(540,%d)\fs%d\fad(0,150)\fscx110\fscy110\t(0,150,\fscx100\fscy100)}%s'
            % (st['hook_y'], st['hook_size'], h['text'].replace('\n', r'\N')))
    return [f'Dialogue: 1,{ts(h.get("start", 0))},{ts(h.get("end", 3))},Cap,,0,0,0,,{text}']


def build(project):
    tl = load_json(os.path.join(project, 'timeline.json'))
    ev = load_json(os.path.join(project, 'events.json'), default={})
    st = dict(DEFAULTS)
    st.update(load_json(os.path.join(project, 'style.json'), default={}))
    lst_lines, windows = list_events(ev, st)
    body = caption_events(tl, ev, st, windows) + lst_lines + hook_events(ev, st)
    head = f"""[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{st['font']},{st['size']},&H00FFFFFF,&H00FFFFFF,&H00000000,&H99000000,-1,0,0,0,100,100,-2,0,1,0,5,5,70,70,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    path = os.path.join(project, 'captions.ass')
    with open(path, 'w', encoding='utf-8') as f:
        f.write(head + '\n'.join(body) + '\n')
    return len(body)


if __name__ == '__main__':
    n = build(sys.argv[1])
    print(f'captions.ass: {n} events')
