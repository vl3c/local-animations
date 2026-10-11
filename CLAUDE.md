# local-animations

The toolkit for making animated shorts with an agent and a human in the loop: the `animate` skill (the workflow),
the animkit engine, benchmarks and research. Films themselves are made in `../Animations/<Title>/`, not here.

## Layout

| Path | What |
| --- | --- |
| `skill/` | The `animate` skill: `SKILL.md` (entry point), `workflow/` (pre-production, assets, animation, review, delivery), `cookbook/` (style-tagged recipes), `templates/` (a new film's files). |
| `kit/animkit/` | The engine: `core` (drawing helpers), `timeline` (cues from word timings), `render` (stills, samples, segments), `mix`, `finish` (mux, contact sheet, checks). |
| `kit/tools/` | Helpers run with other environments (`words.py`: Whisper word timings, run with the local-voice venv). |
| `projects/` | Benchmarks: `_frozen/` (inputs), `_smoke/` (kit test), runs and `_eval_*` (evaluations). See its README. |
| `reports/`, `research_notes/` | The framework survey (Oct 2026) and its notes. |
| `BACKLOG.md` | What isn't built yet, prioritized. |

## The skill is linked, not copied

`~/.claude/skills/animate` is a directory junction to `skill/`, so edits here are live in every session. To create it
on a new machine (PowerShell):

```powershell
New-Item -ItemType Junction -Path "$HOME\.claude\skills\animate" -Target "<repo>\skill"
```

## Working on the kit

- Films snapshot `kit/` into their own folder, so **keep the API backward compatible**: new parameters get defaults,
  nothing is renamed. A film's snapshot may run ahead of this copy; the harvest ports fixes back.
- Test every change on a copy of the smoke project, not in place (its `build/` and `output/` are ignored):
  ```bash
  export PYTHONPATH="$PWD/kit"; T=$(mktemp -d); cp projects/_smoke/{project.json,shots.py} "$T/"
  python projects/_smoke/make_assets.py "$T"
  python -m animkit.render "$T" stills 1:0.5 2:50% && python -m animkit.render "$T" all --workers 2 \
    && python -m animkit.mix "$T" && python -m animkit.finish "$T"
  ```
- When the kit changes, update `skill/workflow/3-animation.md` (commands, project.json fields, toolbox) in the same
  commit.
- Python 3.13 with pycairo, numpy, OpenCV, Pillow, scipy, soundfile, pyloudnorm; ffmpeg on PATH.

## Working on the workflow

- The workflow is style-neutral. Style-specific code and lessons go to `skill/cookbook/` with style tags; the
  quality checklist holds defaults a film's STYLE.md may overrule.
- Lessons from a film become edits to the workflow file they belong to, with a short evidence note (film, what
  happened), not a separate lessons file. Undone ideas go to BACKLOG.md.
- Local tool flags change: the tools' own SKILL.md files are the authority. Keep commands here minimal and check
  them against those files when editing.
- Write plainly: short sentences, tables for lookups, numbers with their evidence.

## Keeping the repository publishable

It may become public. Never commit personal information: no absolute paths with a user name (use `~`, `$REPO`,
relative paths), no emails, no names of private people, no credentials. Generated media, renders and caches stay
out of git (see `.gitignore`): no model output is committed, not even benchmark inputs. Before pushing, scan:

```bash
git grep -n -I -i -E 'users[/\\][a-z0-9]+|@gmail|@[a-z0-9-]+\.(com|ro)|api[_-]?key|token|password' -- . ':!*.lock'
```
