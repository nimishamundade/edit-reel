# Instagram Refined: the look

Fast, bold and clean. One accent colour, lowercase type, words that pop on the frame they are spoken, nothing on
screen that is not earning its place. Canvas 1080 x 1920, 30 fps.

## Footage
- Natural colour, real background. No heavy grade, no grain, no vignette. The footage should look like a good phone shot.
- Jump cuts inside one take alternate wide and a 1.24x punch-in aimed at the chest, so the cuts feel chosen.

## Captions (`captions.py`)
- Font: Arial Black by default (present on Windows and macOS). Set `"font"` and `"fontsdir"` in `<project>/style.json`
  to use another bold static font.
- 92 px, lowercase, tight tracking (-2), white, soft shadow, no outline or box.
- Groups of 1-3 words (about 16 characters), centred at y 1235. Each word pops in on its spoken frame
  (`scale 118% -> 100%`, 140 ms, with a fade).
- Punch words (`emphasis` in events.json) are the accent colour `#F5D36B` (warm gold), pop from 130% and settle slightly
  larger (112%).
- A sentence end or a gap over 0.35 s starts a new group. Captions are suppressed while a list is on screen.

## Lists
- One line per item, 78 px (66 px past four items), centred, starting at y 880, line height up to 104 px.
- Each line pops in (115% -> 100%) on the frame its item is spoken, stays until the list ends, and the stack fades out together.
- `"numbered": true` prefixes gold numbers. Maximum 5 items.

## Hook
- Dictated text shown verbatim, 80 px, centred at y 360, for about 3 seconds, popping in at 110%.

## Overlays
- Anchors: `lower-left`, `lower-middle`, `lower-right`, `chest`, `center`, `full`, or explicit `x`/`y`. All keep
  clear of the safe-zone margins. Default width 560 px (1080 for `full`).
- 120 ms fade in and out. Stills hold; videos start at `src_start`. Overlay audio is dropped.

## Sound
- Voice first, normalised to about -14 LUFS with peaks under -1.5 dBFS.
- Synthesised effects (`make_sfx.py`): `pop`, `click`, `click-soft`, `whoosh`. Used sparingly (SKILL.md, rule 5).

## Not in this version
Words behind the speaker's head need a person cut-out from every frame. That is a planned extra step, not part
of this version, so every word is drawn in front of the footage.
