# <Title>

<One paragraph: what the film is, length, the story in a few lines.>

Made on <date> with the `animate` workflow: voice (local-voice), music (local-music), plates (local-image),
sound effects (local-sounds), and the animkit engine.

## Files

| Path | What |
| --- | --- |
| `output/<Title>.mp4` | Master: 1920x1080, 24 fps, H.264 CRF 16, AAC 256k, <LUFS> LUFS |
| `output/<Title> (preview).mp4` | A smaller copy for watching |
| `output/contact.jpg`, `output/checks.txt` | One frame a second; the automatic checks (deliberate warnings: ...) |
| `shots.py`, `project.json` | The animation and the timeline |
| `BRIEF.md`, `STYLE.md`, `REFERENCES.md`, `DECISIONS.md`, `PLAN.md` | How it was decided |
| `assets/` | Voice takes with word timings, music, plates with drafts and references, sound effects |
| `gen/` | Every generation command, as run |
| `source/` | What the soundtrack is built from, and its rebuild script |
| `kit/` | A snapshot of the animkit engine |

## Rebuild

```bash
export PYTHONPATH="$PWD/kit"
python -m animkit.render . all --workers 4 && python -m animkit.mix . && python -m animkit.finish .
```

`finish` writes `output/<slug>.mp4`; rename it to `<Title>.mp4`. Needs Python 3 with pycairo, numpy, OpenCV, Pillow,
scipy, soundfile, pyloudnorm, and ffmpeg on PATH.

## Licences

Voice: Breeze TTS 2 (research / non-commercial). Plates: Qwen-Image (research / evaluation). Music and SFX: Stable
Audio 3 (Stability AI Community License). Check the licences before any commercial use.
