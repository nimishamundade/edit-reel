---
name: instagram-refined
description: "Edits raw vertical talking-head clips into a fast, tight Instagram reel in the Instagram Refined style: picks the best take of every line, cuts every pause and filler word, keeps picture and voice in sync, adds bold lowercase captions with gold punch words, shows spoken lists on screen as they are said, places the overlays you upload (screen recordings, screenshots, product shots) exactly when their topic is spoken, adds sparing sound effects, and checks every cut. Trigger with /instagram-refined or phrases like 'edit these clips', 'I dropped clips in my downloads', 'cut this into a reel'."
---

# /instagram-refined

Raw clips in, finished reel out. The creator never opens an editor: they review a phone copy, send notes in the
same chat, and every round is a re-render of a minute or two.

All tools run through one launcher, with the skill's own Python environment:

    python3 SK/scripts/run.py <tool> <args>      (Windows: python or py -3 instead of python3)

`SK` is the folder holding this file (usually `~/.claude/skills/instagram-refined`). Tools: `transcribe`,
`plan_cuts`, `timeline`, `captions`, `render`, `check`, `make_sfx`. One command per call, full paths in double quotes.

## First run (once)

1. If `SK/.venv` does not exist, run `python3 SK/scripts/setup.py` (`py -3` on Windows if `python3` is the Store stub).
   It prints STATUS lines and READY. Anything MISSING comes with the exact fix for the machine: give it to the
   user and stop until READY. After a winget install on Windows the user must quit and reopen Claude Code.
2. Ask once: name, Instagram handle, where clips usually land (default `~/Downloads`), where projects go
   (default `~/reel-edits`). Save them to `SK/config.json` (never secrets).

## Hard rules (every reel)

1. **Fast paced, zero dead air.** Every pause, breath, "um"/"uh", false start and retake is cut. A gap between words
   is cut down to the 0.17 s of padding kept around each word; `check` must report no silence over 0.2 s.
   Something on screen (a cut, a caption, a list line, an overlay) changes every 2-3 seconds.
2. **Pauses inside lists are dead air too.** When the speaker lists things, the gaps between the items are cut
   so the items come out back to back.
3. **Lists appear as they are spoken.** For a list ("it has A, B, C and D"), show one line per item on the frame it is
   said, earlier lines staying until the list ends, then the stack clears together. Up to 5 items. This replaces the
   normal captions for that stretch.
4. **Uploaded overlays are placed, never redrawn.** Screen recordings, screenshots, logos and product shots the
   user supplies go on screen while their topic is spoken. If the user names the trigger ("show the screen recording
   when I talk about cow dairy being exposed") that trigger wins over any guess. Overlays are muted. Credit other
   creators on screen when their content appears.
5. **Sound effects are the exception.** No click per caption, no pop per list item. At most a pop on the single
   highest-impact list or key reveal, a click on a screen-recording or UI moment, and a few quiet whooshes on
   section changes. Never louder than the voice. Trending audio from Instagram or TikTok is licensed and cannot be
   bundled; the skill synthesises its own pop, click and whoosh, and users can drop their own files in
   `<project>/assets/sfx/`.
6. **Picture and voice stay in sync.** Video and audio are always trimmed together in one graph (`render` does
   this). Never cut audio and video as separate pieces and rejoin them.
7. **No clipped words.** Keep the default padding (0.07 s before, 0.10 s after each run of speech). After
   rendering run `check --verify`: any word it reports missing was clipped or swallowed, so widen the padding
   (`plan_cuts --pre 0.09 --post 0.13`) and re-render.
8. **Safe zone.** Nothing important in the top 220 px, the bottom 450 px (below y 1470), the left and right 35 px,
   or the right 100 px from y 1155. Never cover the face with text or cards. Use `render --guides` to check.
9. **Say what was said.** Captions show the real words: fix Whisper's mishearings of names and products (use
   `transcribe --prompt "Names, Keywords"`). A hook the user dictates is shown verbatim for about 3 seconds. No em
   dashes in on-screen text.
10. **Originals are read, never modified or deleted.**

## Workflow

### 1. Intake
Clips: the files the user names, else the newest videos in the clips folder. Create `<projects>/<short-slug>/`.
Other files they name (or drop with the clips) are overlays: copy them to `<project>/assets/overlays/`.

### 2. Transcribe
    run.py transcribe <project> <clip1> <clip2> ... --prompt "product names, keywords"
Clips get ids c1, c2... Read `transcript.json` to learn the script and spot repeated lines and lists.

### 3. Plan the cuts and choose takes
    run.py plan_cuts <project>
Writes `edl.json`: one segment per run of continuous speech, with dead air already gone. People repeat a line until it
lands, so rebuild the script from the takes: keep the LAST clean take of each line (unless told otherwise) and delete
the segments of the weaker takes from `edl.json`. Reorder segments only if the script needs it. Consecutive cuts
inside one take alternate wide and punched-in (`zoom` 1.0 / 1.24, `cx`/`cy` aim the punch at the chest).
Show the user a short table (line, take) and keep going.

### 4. Time everything against the reel
    run.py timeline <project>                       rebuilds timeline.json after any edl.json edit
    run.py timeline <project> find "seed oils"      prints the reel time of a phrase
Write `<project>/events.json` (schema in `references/events.md`): the hook, emphasis words, lists, overlays,
sound effects. Get every time from `find`, never by guessing.

### 5. Render and check
    run.py render <project> --guides      layout pass, safe-zone margins drawn in red; look at frames
    run.py render <project>               final render + 720p phone copy in <project>/renders/
    run.py check <project> <render.mp4> --verify
Look at `work/cut_check.jpg`: every after-cut frame must show a clean new shot. Fix anything `check` flags and
re-render. Each render is a new version (`-v1`, `-v2`), nothing is overwritten.

### 6. Deliver and iterate
Point to the phone copy and the full render. Say plainly what changed and what needs the user's call. Notes come
back in the same chat ("cut the pause before 'or you can get'", "caption too small"): change `edl.json`,
`events.json` or `style.json`, re-run `render`, never start over.

## The look
See `references/instagram-refined.md` for exact values (type, colours, positions, motion). Colours, sizes and
the font can be overridden per project in `<project>/style.json`.
