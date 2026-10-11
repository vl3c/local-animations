# local-animations

Make short animated films with a coding agent, on one local GPU, with a human art-directing at checkpoints.

- **The workflow** is a Claude Code skill (`skill/`, invoked as `animate`): an interview, a locked script, character
  and prop references, a storyboard, plate picks, animatic stills, a draft, notes, delivery, and a harvest that
  feeds each film's lessons back. It is style-neutral; each film defines its look in a `STYLE.md`, and a cookbook
  collects recipes from earlier films.
- **The engine** (`kit/animkit`) makes the picture as code: one Python function per shot (pycairo + numpy +
  OpenCV), timing from word-level timestamps of the voice, a stills mode for review (the agent can't watch video),
  segment rendering, a mixer, and automatic checks.
- **Assets** come from local open-weights models through companion tools, each its own repository and Claude Code
  skill (below). Models are downloaded by their installers; none are in this repository.

## Requirements

Windows 11 with an NVIDIA GPU (16 GB was enough for every tool, one at a time), Python 3.13 with pycairo, numpy,
OpenCV, Pillow, scipy, soundfile and pyloudnorm, ffmpeg on PATH, and Claude Code. The companion tools, each
installed as a skill under `~/.claude/skills/<name>` (see each one's README):

| Tool | What it makes |
| --- | --- |
| [local-voice](https://github.com/vl3c/local-voice) | speech in a designed voice, machine and creature effects, word timings and subtitles |
| [local-music](https://github.com/vl3c/local-music) | instrumental music beds and stems, voice-over-music mixes |
| [local-image](https://github.com/vl3c/local-image) | background plates, character and prop references, multi-reference edits, cut-outs |
| [local-sounds](https://github.com/vl3c/local-sounds) | sound effects and ambiences, frame-ready, from a cue sheet |
| [local-gpu](https://github.com/vl3c/local-gpu) | which tool holds the GPU, and switching between them |

Then link this repository's skill (PowerShell):

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\animate" -Target "<this repo>\skill"
```

## Films made with it

| Film | What | Lessons now in |
| --- | --- | --- |
| Initial Condition (6:27) | A machine intelligence narrates humanity's history with tools; the engine was extracted from it | the engine, checklist, glitch and palette recipes |
| Ember (0:20, benchmark) | A spark becomes the first fire; frozen assets, Haiku and Sonnet runs | recipes, checklist |
| Black wall / Hairline Fracture (0:26) | Something behind a wall speaks; idea-to-film runs | plate checks, prompt craft |
| Lantern Cantor (1:12) | A deadpan action-comedy sermon; audio first, then animation | checkpoints C0-C6, references, audio-first mode |

## Layout

See [CLAUDE.md](CLAUDE.md). Start with [skill/SKILL.md](skill/SKILL.md).

## Licence

[MIT](LICENSE). The repository contains no models and no generated media. The local tools download their models
on install, and what they generate has its own licence terms (several are non-commercial only); see
`skill/workflow/2-assets.md`.
