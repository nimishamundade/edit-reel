# events.json

Everything that is not the speaker's footage. Times are seconds in the finished reel; get them with
`run.py timeline <project> find "phrase"`. Every key is optional.

```json
{
  "hook": {"text": "your mayo is lying to you", "start": 0, "end": 3},
  "emphasis": ["avocado", "oil"],
  "lists": [
    {"numbered": false,
     "items": [{"text": "seed oils", "at": 5.77}, {"text": "refined oils", "at": 6.38},
               {"text": "additives", "at": 7.15}, {"text": "fillers", "at": 7.56}],
     "end": 8.3}
  ],
  "overlays": [
    {"file": "assets/overlays/dairy-expose.mp4", "start": 21.4, "end": 25.0, "pos": "lower-middle", "width": 600}
  ],
  "sfx": [
    {"name": "pop", "at": 5.77, "gain": 0.5}
  ]
}
```

- **hook**: shown verbatim, centred near the top.
- **emphasis**: words drawn in the accent colour and slightly bigger wherever they are captioned.
- **lists**: `at` is the reel time the item starts being said; `end` is when the whole stack clears (just after the
  last item). Max 5 items.
- **overlays**: `file` relative to the project (or absolute). `pos` is one of lower-left, lower-middle, lower-right,
  chest, center, full. Optional `x`, `y` (ffmpeg expressions or pixels), `width`, and `src_start` for videos.
  Show an overlay from the first word of its topic until about 0.3 s after the last; at least 1.2 s.
- **sfx**: `name` is a file in `<project>/assets/sfx/` or the skill's `assets/sfx/` (`pop`, `click`, `click-soft`,
  `whoosh`, or the user's own). `gain` is 0-1 relative to the voice.

Per-project look overrides go in `style.json`, for example:

```json
{"accent": "#E8C872", "size": 96, "caption_y": 1200, "font": "Arial Black"}
```
