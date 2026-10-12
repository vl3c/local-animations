# 4. Review: checkpoints, self-review, notes

## Running a checkpoint

Each checkpoint is **one labelled contact sheet** (send it with SendUserFile, or Read it so it shows in the app)
plus **one AskUserQuestion** (1-4 questions, options labelled to match the sheet, "Other" for free text).

- **Lettered, labelled tiles:** the shot id and a letter in every tile (`3-drive A/B/C/D`), the subtitle line on
  the sheet. Unlabelled tiles led to picks like "upper right" and one pick applied to the wrong image.
- **Recommend one option** and say why in a few words ("B: the wheel is on the correct side").
- **Name the checks you did** ("checked: one mouth, four fingers, the wheel on the image right"), so the user judges
  taste, not errors.
- **Batch per act,** at most 4 questions per call. Short picks are fastest ("upper left", "the right one is great").
- **Ask story decisions as decisions, not images:** "Should the boss wear her bow from her first appearance, or only
  from the reveal?"
- **Offer your ideas as options** rather than doing them silently.
- **Combining is a valid answer:** "A's face with C's cape" is a multi-reference edit.
- **Echo every pick** into DECISIONS.md (and REFERENCES.md for designs) straight away, and paste the relevant lines
  into every later prompt. That stops regressions (a character losing her accessories, an older car reference).
- **Keep working** on independent assets while the user decides.

## The checkpoints

| # | Send | Decides | Notes it would have caught (from real films) |
| --- | --- | --- | --- |
| **C0** | 4-6 questions | tone limits, staging, ending, loudness, subtitles, style, which checkpoints | no religious cross; accessories from the start or at the reveal; end on a hug; -14 vs -18 LUFS |
| **C1** | 4 drafts of the hero, then 4 of each recurring character | reference image + attribute string | cross → cape → pendant settled before 3 scene batches; a chubby round-eyed monster |
| **C2** | 2-4 drafts of each recurring prop and set | references + attributes (colours, the wheel's side, a prop's shape) | a prop changing design between shots; the car's colours and wheel side |
| **C3** | one cheap frame per shot, numbered, its line under it, its gags listed | per shot: keep / change / idea | the establishing shot; the title idea; the ending; staging (side, direction, who looks where) |
| **C4** | 2-4 lettered finals per shot, per act | one letter per shot, or a combination | a plate with two mouths; six fingers; a seat outside the car |
| **C5** | 2-3 stills per shot with every overlay, tiled per act; the subtitle list | overlay placement, size, look; subtitle grouping | drip placement, a ruler too short, a wallpaper past the phone rim, a leftover disc, the halo's width, a split subtitle |
| **C6** | the draft MP4 + contact sheet | timing and pacing; the audio level | — |

A plate the user never saw before the draft film cost 7 draft folders and three spatial errors found at once. No
plate goes into the film without passing C4 (or the user waiving it at C0).

## Self-review (before every sheet you send)

Render stills **inside** motions, not only at the start and end of shots: at least 3 frames per animation.
Look at them against this checklist. These are defaults from human directors' notes; STYLE.md may overrule one on
purpose.

| Area | Default rule |
| --- | --- |
| **Timing** | Every beat on its word, from a cue. No drifting beats. |
| **Proportion** | Believable relative sizes: a spark is small, a fire grows from it; a knife isn't "puny" in a fist; an object isn't hidden by what holds it. |
| **Composition** | The subject near the visual centre unless there's a reason. Things that converge meet at the centre. Nothing important outside the safe margin. |
| **Physical logic** | Falling things accelerate. Light spreads from its source. Weapons extend away from the body. Depth uses occlusion and scale toward a vanishing point. Things standing on the ground sit exactly on the plate's ground line. |
| **Spatial logic** | Characters look at what they react to; vehicles face the right way; the same layout across shots of one scene. |
| **Consistency** | Every character and prop matches REFERENCES.md in every shot: attributes, counts, design. |
| **Less is more** | No elements the brief doesn't need. An extra silhouette or prop distracts more than it helps. Strong plates plus a few well-timed procedural elements beat busy overlays. |
| **Transitions** | Fade in after a bright frame; no hard cut from dark to bright. Elements don't jump at cuts. Old elements hand over quickly. Nothing pops in: fade or move it in. |
| **Readability** | Each shot's idea reads in a second. Objects have a dark body or outline. Titles readable, never overlapping, never colliding mid-motion. Nothing too dark to read (mean luma under about 0.04 for seconds). |
| **No leftovers** | No debug shapes or guide lines. Particles stay inside their area. |
| **Restraint** | Fewer, better effects. Soft glows, not blown-out white. |
| **Sound** | Few, subtle effects. No abrupt audio cuts; long fades (5-7 s for returning music). The film ends on black. |
| **Subtitles** | Readable size, full brightness, a speaker tag kept with its quote. |

**Sort what you find** into "fix in code" and "regenerate the asset". Code can't save a weak plate: spend the
remaining budget on regenerations.

**Automatic checks** (`finish`): duration, loudness and peak, brightness jumps (FLASH/CUT warnings), ending on black,
layout warnings. **Not automated yet** (BACKLOG): darkness, flash rate (at most 3 large flashes a second), palette
rules, words lost in the speech band. If the film needs them, write a small script for the film, or check by eye and
say so in the report.

A **fresh-eyes reviewer** (a subagent with no context, shown frames sampled every few seconds) gave a concrete
polish list late in one film, ranking the weakest long holds (needs motes, embers, reflections, a light pulse,
secondary motion). Use one before C6 on longer films. Advisor subagents (an art director, a score advisor) gave
useful advice on a long film too; they advise, you decide, the user has the last word.

## The notes loop

The user watches the draft and sends notes, often timecoded, sometimes with screenshots ("at 04:38 ...").

For each note:

1. Map the timecode to a shot and its cue (`finish --info`).
2. Change the code (or regenerate the asset, through the relevant checkpoint: send lettered options).
3. Render 2-6 stills of the shot and look at them; iterate until right.
4. **Send the stills of each fix first** ("show me the images before regenerating the whole video").
5. Re-render only the touched shots (`all --redo 3,7`), mix, finish.
6. Report what changed, briefly. Log each note and its fix in DECISIONS.md.

- **Number the cuts:** name each sent preview with its version (`<Title> v3 (preview).mp4`). A note about a sound
  already removed came from an older copy the user was still watching, and an approved sound was taken out because
  of it.
- **Reviewing from a phone:** when the user is remote, send only the preview (15 MB) and one proof image per hard
  fix (a sync chart, a mid-transition frame), not sheets.
- **Don't morph generated art to align it.** Align rigidly (scale and shift) and let a short fade carry the rest: a
  homography morph that aligned two views perfectly was rejected at once ("it changes geometry by melting it")
  (Church of Superintelligence).

Batch notes into one re-render where you can: each round costs the user a viewing. If notes after C6 are mostly
design notes, a checkpoint was skipped or rushed; note it for the harvest.
