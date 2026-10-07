# Instagram Refined
### A Claude Code skill by [@nimishamundade](https://github.com/nimishamundade)

Film your talking-head clips on your phone, drop them in a folder, type `/edit-reel`, and Claude edits them
into a fast, tight Instagram reel. You never open an editor: you watch a phone copy, send notes, and it re-renders.

## What it does

- Transcribes every clip with word-level timing and picks the best take of each line.
- **Cuts every pause**, breath and filler word, including the gaps between items when you say a list. No dead air.
- Keeps picture and voice **in sync** (video and audio are cut together in a single pass) and protects word edges
  from clipping, then proves both with a built-in check.
- **Instagram Refined captions:** bold lowercase words that pop in as you say them, with gold punch words.
- **Lists on screen:** when you say a list, each item appears on its own line the moment you say it.
- **Your overlays:** hand it screen recordings, screenshots or product shots and it places them exactly when you
  talk about that topic.
- **Sparing sound design** (pop, click, whoosh), never one per caption.
- Keeps everything inside the Reels safe zone, checks every cut frame, and gives you a 720p phone copy.

## Requirements

Windows, macOS or Linux. It was built and tested on **Windows**; macOS and Linux should work but have not been tested yet.

| | Windows (PowerShell) | Mac | Linux |
|---|---|---|---|
| ffmpeg | `winget install --id Gyan.FFmpeg -e` | `brew install ffmpeg` | `sudo apt install ffmpeg` |
| Python 3.10+ | `winget install --id Python.Python.3.12 -e` | `brew install python` | `sudo apt install python3 python3-venv` |

After installing on Windows, quit Claude Code completely and reopen it.

## Install

Open Claude Code and paste:

```
Install this skill for me: https://github.com/nimishamundade/edit-reel
```

Or in a terminal:

```bash
git clone https://github.com/nimishamundade/edit-reel "$HOME/.claude/skills/edit-reel"
```

Then run `/edit-reel`. The first run checks your computer, tells you the exact line to paste for anything
missing, and builds its own Python environment (about 2 minutes, once; it downloads a speech model on first use).

## Use

Put your raw clips in `Downloads` (or tell it where they are) and run:

```
/edit-reel I just dropped 4 clips in my downloads
```

Overlays go with the footage. Tell it which files they are and when they belong:

```
/edit-reel these are overlays: dairy.mp4, study.png. Show dairy.mp4 when I talk about cow dairy being exposed.
```

Send notes in the same chat ("cut the pause before 'or you can get'", "make the captions bigger") and it re-renders.

Tips: film vertically, keep the camera still for each setup, and repeat a line until it feels right. It picks the best take.

## Sounds

The skill generates its own pop, click and whoosh, so it ships no third-party audio. Trending Instagram/TikTok audio is
licensed and can't be bundled: put your own royalty-free `.wav`/`.mp3` files in `<project>/assets/sfx/` and name them
in the edit.

## Roadmap

Words that sit *behind* your head (needs a person cut-out), more looks, and macOS/Linux testing.

## Credits

Built on [ffmpeg](https://ffmpeg.org) and [faster-whisper](https://github.com/SYSTRAN/faster-whisper) (OpenAI Whisper).
MIT licensed, see `LICENSE`.
