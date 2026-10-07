"""Assemble, caption, overlay, mix sound and export.

    run.py render <project> [--guides] [--no-captions]

1. aroll.mp4   every EDL segment is trimmed from video and audio in ONE ffmpeg graph, so picture and voice are
               cut at identical points (no drift) and joined with a 6 ms audio fade to avoid clicks.
2. renders/<name>-vN.mp4   captions + lists + hook (captions.ass), uploaded overlays, sound effects, loudness
               normalised to about -14 LUFS. Plus a 720p phone copy.

Overlays and sound effects come from <project>/events.json (see SKILL.md for the schema).
--guides draws the Reels safe-zone margins in red, for checking layout only.
"""
import argparse
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import captions  # noqa: E402
import timeline  # noqa: E402
from common import ROOT, filter_file_args, find_tool, load_json, run  # noqa: E402

W, H, FPS = 1080, 1920, 30
IMAGES = ('.png', '.jpg', '.jpeg', '.webp')
POS = {  # overlay anchors, all inside the safe zone (bottom 450 and right 100 kept clear)
    'lower-left': ('60', '1440-h'),
    'lower-middle': ('(W-w)/2', '1440-h'),
    'lower-right': ('W-w-100', '1440-h'),
    'chest': ('(W-w)/2', '900'),
    'center': ('(W-w)/2', '(H-h)/2'),
    'full': ('0', '(H-h)/2'),
}


def build_aroll(project):
    edl = load_json(os.path.join(project, 'edl.json'))
    tr = load_json(os.path.join(project, 'transcript.json'))['clips']
    clips = sorted({s['clip'] for s in edl})
    idx = {c: i for i, c in enumerate(clips)}
    f, labels = [], []
    for i, s in enumerate(edl):
        k, z = idx[s['clip']], s.get('zoom', 1.0)
        cx, cy, d = s.get('cx', 0.5), s.get('cy', 0.5), s['out'] - s['in']
        f.append(f"[{k}:v]trim=start={s['in']}:end={s['out']},setpts=PTS-STARTPTS,fps={FPS},"
                 f"crop=iw/{z}:ih/{z}:(iw-iw/{z})*{cx}:(ih-ih/{z})*{cy},"
                 f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H},setsar=1,format=yuv420p[v{i}]")
        f.append(f"[{k}:a]atrim=start={s['in']}:end={s['out']},asetpts=PTS-STARTPTS,aresample=48000,"
                 f"afade=t=in:d=0.006,afade=t=out:st={max(d - 0.006, 0):.3f}:d=0.006[a{i}]")
        labels.append(f'[v{i}][a{i}]')
    f.append(''.join(labels) + f'concat=n={len(edl)}:v=1:a=1[v][a]')
    work = os.path.join(project, 'work')
    os.makedirs(work, exist_ok=True)
    script = os.path.join(work, 'aroll_graph.txt')
    with open(script, 'w', encoding='utf-8') as fh:
        fh.write(';\n'.join(f))
    cmd = [find_tool('ffmpeg'), '-y', '-v', 'error']
    for c in clips:
        cmd += ['-i', tr[c]['path']]
    cmd += filter_file_args(script) + ['-map', '[v]', '-map', '[a]', '-c:v', 'libx264', '-preset', 'veryfast',
            '-crf', '17', '-pix_fmt', 'yuv420p', '-r', str(FPS), '-c:a', 'aac', '-b:a', '192k',
            os.path.join(project, 'aroll.mp4')]
    run(cmd)
    return os.path.join(project, 'aroll.mp4')


def sfx_path(project, name):
    for base in (os.path.join(project, 'assets', 'sfx'), os.path.join(ROOT, 'assets', 'sfx')):
        for ext in ('.wav', '.mp3', '.m4a'):
            p = os.path.join(base, name + ext)
            if os.path.isfile(p):
                return p
    sys.exit(f'sound effect "{name}" not found. Run: run.py make_sfx, or put {name}.wav in <project>/assets/sfx/')


def final_render(project, guides, no_captions):
    ev = load_json(os.path.join(project, 'events.json'), default={})
    dur = load_json(os.path.join(project, 'timeline.json'))['duration']
    cmd = [find_tool('ffmpeg'), '-y', '-v', 'error', '-i', 'aroll.mp4']
    fc, vlast, n = [], '0:v', 1

    for j, o in enumerate(ev.get('overlays', [])):
        path = o['file'] if os.path.isabs(o['file']) else os.path.join(project, o['file'])
        if not os.path.isfile(path):
            sys.exit(f'overlay not found: {path}')
        s, e = float(o['start']), float(o['end'])
        d = e - s
        still = path.lower().endswith(IMAGES)
        cmd += (['-loop', '1', '-t', f'{d:.3f}'] if still else []) + ['-i', path]
        x, y = POS.get(o.get('pos', 'lower-middle'), POS['lower-middle'])
        x, y = str(o.get('x', x)), str(o.get('y', y))
        width = int(o.get('width', 560 if o.get('pos') != 'full' else W))
        src = float(o.get('src_start', 0))
        trim = f'trim=start={src}:duration={d:.3f},' if not still else ''
        fc.append(f"[{n}:v]format=rgba,{trim}setpts=PTS-STARTPTS,scale={width}:-2,"
                  f"fade=t=in:st=0:d=0.12:alpha=1,fade=t=out:st={max(d - 0.12, 0):.3f}:d=0.12:alpha=1,"
                  f"setpts=PTS+{s}/TB[ov{j}]")
        fc.append(f"[{vlast}][ov{j}]overlay={x}:{y}:eof_action=pass:enable='between(t,{s},{e})'[vo{j}]")
        vlast, n = f'vo{j}', n + 1

    tail = []
    if not no_captions:
        sub = 'subtitles=captions.ass'
        st = load_json(os.path.join(project, 'style.json'), default={})
        if st.get('fontsdir'):
            sub += f":fontsdir={st['fontsdir']}"
        tail.append(sub)
    if guides:
        tail += [f'drawbox=x=0:y=0:w={W}:h=220:color=red@0.3:t=fill', f'drawbox=x=0:y=1470:w={W}:h=450:color=red@0.3:t=fill',
                 f'drawbox=x=0:y=0:w=35:h={H}:color=red@0.3:t=fill', f'drawbox=x={W - 35}:y=0:w=35:h={H}:color=red@0.3:t=fill']
    fc.append(f"[{vlast}]{','.join(tail) if tail else 'null'}[vout]")

    alabels = ['[0:a]']
    for k, sx in enumerate(ev.get('sfx', [])):
        cmd += ['-i', sfx_path(project, sx['name'])]
        ms = int(float(sx['at']) * 1000)
        fc.append(f"[{n}:a]adelay={ms}|{ms},volume={sx.get('gain', 0.5)}[sx{k}]")
        alabels.append(f'[sx{k}]')
        n += 1
    fc.append(''.join(alabels) + f"amix=inputs={len(alabels)}:normalize=0:duration=first,"
              "loudnorm=I=-14:TP=-1.5:LRA=11[aout]")

    script = os.path.join(project, 'work', 'final_graph.txt')
    with open(script, 'w', encoding='utf-8') as fh:
        fh.write(';\n'.join(fc))
    os.makedirs(os.path.join(project, 'renders'), exist_ok=True)
    slug = os.path.basename(os.path.abspath(project))
    v = 1
    while os.path.exists(os.path.join(project, 'renders', f'{slug}-v{v}.mp4')):
        v += 1
    out = os.path.join('renders', f'{slug}-v{v}.mp4')
    cmd += filter_file_args(os.path.join('work', 'final_graph.txt')) + ['-map', '[vout]', '-map', '[aout]',
            '-c:v', 'libx264', '-preset', 'medium', '-crf', '18', '-pix_fmt', 'yuv420p', '-r', str(FPS),
            '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-t', f'{dur:.3f}', '-movflags', '+faststart', out]
    run(cmd, cwd=project)
    phone = out.replace('.mp4', '-phone.mp4')
    run([find_tool('ffmpeg'), '-y', '-v', 'error', '-i', out, '-vf', 'scale=720:-2', '-c:v', 'libx264', '-crf', '26',
         '-preset', 'veryfast', '-c:a', 'aac', '-b:a', '128k', '-movflags', '+faststart', phone], cwd=project)
    return os.path.join(project, out), os.path.join(project, phone)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('project')
    ap.add_argument('--guides', action='store_true')
    ap.add_argument('--no-captions', action='store_true')
    a = ap.parse_args()
    p = os.path.abspath(a.project)
    tl = timeline.build(p)
    print(f'timeline: {tl["duration"]:.1f}s, {len(tl["cuts"]) + 1} segments')
    build_aroll(p)
    print('aroll.mp4 done')
    captions.build(p)
    out, phone = final_render(p, a.guides, a.no_captions)
    print('render:', out)
    print('phone copy:', phone)


if __name__ == '__main__':
    main()
