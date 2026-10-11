---
name: animate
description: Make a short animated film (narrated, music-driven or comedic; any style) from an idea, an approved script or a finished soundtrack, with the user in the loop at checkpoints (interview, characters, props, storyboard, plate picks, animatic stills, draft film, notes). Assets come from the local GPU tools (local-voice, local-music, local-image, local-sounds); the picture is code, made with the animkit Python engine (pycairo + numpy + OpenCV + ffmpeg). Use when the user asks to make, continue, fix or give notes on an animation, an animated short or video, or to animate an audio file.
---

# animate: animated shorts, made with the user in the loop

## Five principles

1. **A decision is cheapest at the stage where it's made.** A design pick on a draft tile costs one prompt. The same
   pick after the film is rendered costs a regeneration, a re-render, an encode and a viewing. So every visual
   decision gets a checkpoint *before* the work that depends on it.
2. **You cannot watch video or hear audio.** You review pictures by rendering stills and reading them. The user
   judges sound, motion and taste: send them audio candidates and draft films, and ask.
3. **Timing comes from the audio.** Every visual beat is a cue on a word (`"L2:spark"`), never a hard-coded time.
4. **The style changes from film to film.** Nothing in this workflow assumes a look. Each film writes its own
   `STYLE.md`; the [cookbook](cookbook/README.md) offers recipes from earlier films, tagged by style. The quality
   checklist holds defaults; a film's STYLE.md may overrule one on purpose (a manga smash-cut is a hard cut).
5. **A check exists only if a script runs it.** If a rule matters (palette, flashes, loudness), run something that
   measures it, and say which checks you ran and which you only eyeballed.

## Setup

This skill's folder is a link into the `local-animations` repository. Find the repository and put the engine on the
path (Git Bash):

```bash
REPO=$(python -c "import os,sys; print(os.path.dirname(os.path.realpath(sys.argv[1])))" "<this skill's base dir>")
export PYTHONPATH="$REPO/kit"
```

Python 3.13 with pycairo, numpy, OpenCV, Pillow, scipy, soundfile and pyloudnorm; ffmpeg on PATH.

The asset tools are separate skills, each from its own repository: local-voice, local-music, local-image,
local-sounds and local-gpu (github.com/vl3c/<name>). If one is missing from `~/.claude/skills/`, tell the user
and point them to its repository's install section; don't improvise a substitute or use a cloud service.

## Where the work starts (entry modes)

| The user gives you | Start at | Notes |
| --- | --- | --- |
| An idea | C0, then the script | The full workflow below. |
| An approved script | C0 | Mark the script APPROVED in BRIEF.md; never rewrite it silently. |
| A finished soundtrack (voice + music mix) | C0, then pictures | The "from a finished soundtrack" mode in [animation](workflow/3-animation.md#from-a-finished-soundtrack). |
| An audio-first piece (the sound drives the film) | C0, then an audio session | Make the soundtrack first, hand over three files, then animate: [assets](workflow/2-assets.md#audio-first-two-sessions). |
| An existing film and notes | The notes loop | [review](workflow/4-review.md#the-notes-loop). |
| Frozen assets (a benchmark) | The animation | Don't generate assets; follow the brief's hard requirements. |

## The phases and checkpoints

At C0 you propose which checkpoints this film needs, and the user confirms. A 20-second abstract piece may skip
C1 and C2; a character comedy needs all of them. Each checkpoint is **one lettered contact sheet plus one short
multiple-choice question** with a recommended option ([how to ask](workflow/4-review.md#running-a-checkpoint)).
Keep working on independent assets while the user decides; never block on a checkpoint the next batch doesn't
depend on.

| Phase | Checkpoint | What it decides | Read |
| --- | --- | --- | --- |
| Pre-production | **C0 interview** (before any GPU work) | tone limits, story staging, ending, length, voice, music, loudness, subtitles, style direction, which checkpoints, time budget, delivery folder | [1-preproduction](workflow/1-preproduction.md) |
| | *(script gate)* | the script and brief: nothing is generated until the user says "go" | |
| | **C1 characters** | a locked reference image and attribute string per character | |
| | **C2 props and locations** | locked references for every recurring prop and set | |
| | **C3 storyboard** | one cheap draft frame per shot, with its line and gags: keep / change / idea | |
| Assets | *(audio picks)* | voice auditions and music candidates, picked by ear | [2-assets](workflow/2-assets.md) |
| | **C4 plate picks** (per act) | one letter per shot, or "combine 3A+3C" | |
| Animation | **C5 animatic stills** | overlays, text, gags, subtitle grouping, before the full render | [3-animation](workflow/3-animation.md) |
| | **C6 draft film** | timing and pacing (if C0-C5 did their job) | [4-review](workflow/4-review.md) |
| Notes | *(notes loop)* | stills of each fix first, then partial re-renders | |
| Delivery | | the master, the film README, the rebuild, the harvest | [5-delivery](workflow/5-delivery.md) |

## Hard rules

- **The script gate.** Iterate the script and brief in chat. Generate nothing until the user says "go". Praise plus
  an edit ("it's good, change this line") is not a go.
- **Lock characters (C1) before any scene batch.** A design change mid-batch means relaunching the batch.
- **One GPU server at a time.** Use local-gpu `status` and `switch`; ask once up front for the switches the plan
  needs. Never stop a server you didn't start without a yes.
- **Keep every draft and every source of the final.** Drafts let a choice be revisited; sources let the film be rebuilt.
- **Original content.** A film can be *inspired by* a work, genre or setting, but never names its trademarks,
  characters, places or quoted lines, in the film or in generation prompts: describe the look or the sound instead.
- **No AI credits or tool logos** in the film unless the user asks.
- **Run renders in the foreground and wait.** A job is done when its outputs exist and you have looked at them.
- **Record as you go:** every pick and rule in `DECISIONS.md`, every character and prop in `REFERENCES.md`, every
  generation command as run in `gen/` scripts. Paste the relevant REFERENCES lines into every later prompt.

## A film's folder

Films live in `../Animations/<Title>/` next to this repository (ask the user at C0 if they want elsewhere). Create one
from the templates:

```bash
FILM="$REPO/../Animations/<Title>"
mkdir -p "$FILM"/{gen,source,assets/{vo/takes,music,plates/ref,plates/drafts,sfx/gen}}
cp -r "$REPO/skill/templates/." "$FILM/" && cp -r "$REPO/kit" "$FILM/kit"
```

```
<Title>/
  BRIEF.md          the locked script, intent per beat, characters, style reference, budget, deliverables
  STYLE.md          this film's look as a system: palette rules, effect vocabulary, taste rules, overrides
  REFERENCES.md     each character and prop: reference image, verbatim attribute string, counts
  DECISIONS.md      dated log of every pick and rule, plus the time spent per stage
  PLAN.md           per shot: layout, what moves on which cue, what must never overlap
  CUES.md           (audio-first) time | voice phrase or music event | bar grid
  project.json      lines, shots, sfx, music, lufs, duration
  shots.py          one function per shot (the picture)
  gen/              the image, voice, music and SFX commands, exactly as run
  assets/           vo/ (takes/), music/, plates/ (ref/, drafts/<shot>/), sfx/ (gen/)
  source/           what the final soundtrack is built from, plus a rebuild script
  kit/              a snapshot of animkit (the film rebuilds on its own)
  build/  output/   regenerated; never edit
  README.md         story, files, rebuild command, licences
```

## When the film is done

Run the **harvest** in [5-delivery](workflow/5-delivery.md#the-harvest): port kit fixes back to the repository,
add reusable recipes to the cookbook, and turn new lessons into edits of these workflow files or the repository's
BACKLOG.md. The workflow improves with every film.
