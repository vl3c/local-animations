# animkit

A small engine for procedural 2D animation timed to a voice: pycairo + numpy + OpenCV + ffmpeg.

```bash
export PYTHONPATH="<this folder>"
python -m animkit.finish FILM --info       # the timeline and every word's time
python -m animkit.render FILM stills 1:0.5 # frames to look at
python -m animkit.render FILM all          # the picture
python -m animkit.mix FILM                 # the soundtrack
python -m animkit.finish FILM              # the mp4, contact sheet and checks
```

The guide (project.json, the shot API, the review loop) is in the `animate` skill: `skill/workflow/3-animation.md`
in the local-animations repository. A film keeps a snapshot of this folder so it rebuilds on its own.
