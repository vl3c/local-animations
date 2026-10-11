# local-animations

Make short animated films with a coding agent, on one local GPU, with a human art-directing at checkpoints.

- **The workflow** is a Claude Code skill (`skill/`, invoked as `animate`): an interview, a locked script, character
  and prop references, a storyboard, plate picks, animatic stills, a draft, notes, delivery, and a harvest that
  feeds each film's lessons back. It is style-neutral; each film defines its look in a `STYLE.md`, and a cookbook
  collects recipes from earlier films.
- **The engine** (`kit/animkit`) makes the picture as code: one Python function per shot (pycairo + numpy +
  OpenCV), timing from word-level timestamps of the voice, a stills mode for review (the agent can't watch video),
  segment rendering, a mixer, and automatic checks.
- **Assets** come from local open-weights models through separate skills: speech (local-voice), music
  (local-music), images (local-image) and sound effects (local-sounds). They are not part of this repository.

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
