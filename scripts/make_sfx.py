"""Synthesise the small sound-effect set with ffmpeg, so the skill ships no third-party audio.

    run.py make_sfx

Creates assets/sfx/{pop,click,click-soft,whoosh}.wav. They are simple generated sounds. To use your own
(royalty-free) ones, drop wav/mp3 files with the same names into <project>/assets/sfx/ and they win.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import ROOT, find_tool, run  # noqa: E402

SOUNDS = {
    # a short falling-pitch blip
    'pop': ['-f', 'lavfi', '-i', "aevalsrc='0.9*sin(2*PI*(900-5200*t)*t)*exp(-t*38)':d=0.14:s=48000"],
    # a tight noise tick plus a tiny tone
    'click': ['-f', 'lavfi', '-i', "aevalsrc='0.8*(random(0)*2-1)*exp(-t*900)+0.3*sin(2*PI*2400*t)*exp(-t*500)':d=0.05:s=48000"],
    'click-soft': ['-f', 'lavfi', '-i', "aevalsrc='0.45*(random(0)*2-1)*exp(-t*700)+0.2*sin(2*PI*1800*t)*exp(-t*420)':d=0.05:s=48000"],
    # filtered pink noise that swells and fades
    'whoosh': ['-f', 'lavfi', '-i', 'anoisesrc=d=0.5:c=pink:a=0.7:r=48000'],
}
FILTERS = {
    'pop': 'lowpass=f=5000',
    'click': 'highpass=f=1200',
    'click-soft': 'highpass=f=900,lowpass=f=6000',
    'whoosh': 'highpass=f=250,lowpass=f=7000,afade=t=in:d=0.2,afade=t=out:st=0.2:d=0.3',
}


def main():
    out = os.path.join(ROOT, 'assets', 'sfx')
    os.makedirs(out, exist_ok=True)
    for name, src in SOUNDS.items():
        run([find_tool('ffmpeg'), '-y', '-v', 'error'] + src + ['-af', FILTERS[name] + ',alimiter=limit=0.8',
            '-ac', '1', os.path.join(out, name + '.wav')])
        print('made', name + '.wav')


if __name__ == '__main__':
    main()
