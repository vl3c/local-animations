# Benchmarks

| Folder | What |
| --- | --- |
| `_frozen/ember/` | Benchmark inputs: the Ember brief, voice lines with word timings, plates, sound effects. Copy it to start a run. |
| `_smoke/` | A 5-second project for testing kit changes (copy it; don't render in place). |
| `ember-haiku-1/`, `ember-sonnet-1/` | Ember Track A runs (frozen assets): Claude Haiku 4.5 and Sonnet, 2026-10-09. |
| `blackwall-haiku-1/`, `blackwall-sonnet-1/` | Idea-to-film runs on a "black wall" theme, 2026-10-09. |
| `_eval_*` | Evaluations of those runs: gates, cue timings, rubric scores, director's notes. |

The run folders keep only their sources in git (brief, plan, shots.py, project.json, reports). Their briefs point
to `kit/AGENT_GUIDE.md` and `kit/ASSETS_GUIDE.md`, the guides of the time; those are now `skill/workflow/`.
Rendered media, builds and generated assets are not tracked.
