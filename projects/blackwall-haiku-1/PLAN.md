# PLAN: "Hairline" (the black wall)

Idea (from BRIEF.md): a short narrated cyberpunk film about a vast ancient firewall at the edge of the network,
holding back something hostile and intelligent. Somewhere, the wall is starting to crack.

Theme update from the director (applied before any asset was made): the inspiration is the Blackwall of the
Cyberpunk universe. The film evokes that lore and look in my own words and images. It does not name the source
(no "Blackwall", "NetWatch", "Cyberpunk", "Night City", "DataKrash", "Bartmoss", "Old Net", no characters, no
quoted lines). Title and wording are original. Every voice take was checked for those names in the transcript;
one take (a random seed) said "Blackwall" and was rejected.

Lore evoked (in the film's own terms):
- A catastrophe killed the first network in one night.
- The minds left in its ruins turned alien and hostile.
- Wardens sealed them behind a vast black wall.
- Our net lives on this side. Beyond the wall is the dead net, haunted, full of hungry minds that whisper.
- The wall is cracking, and something on the other side speaks.

Format: 1920x1080, 24 fps, 28.08 s, fades in from black and ends on black. No music.

## Decisions

- Title: HAIRLINE (the thinnest crack, the first one in the wall).
- Voice (one voice for the whole film): local-voice `ancient-male` with a custom voice description (a steady,
  measured, moderate pace; the built-in "very slowly" delivery ran at about one word a second), seed 74525861,
  preset `harbinger`, blend 0.3, tempo 1.25, reverb room. The narrator is the machine behind the wall.
  - Preset test on the same dry take: reaper-drone with tempo 1.15 scored 87% wet (garbled "first");
    harbinger scored 87% at blend 0 and 100% at blend 0.3. Harbinger blend 0.3 was chosen.
  - Lines 2 to 5 were cloned from line 1 with `--like`.
  - The built-in voice ran long (about 30 s of speech for 59 words), so tempo 1.25 was applied to all takes.
  - A human narrator was considered and rejected: the film is about the machine behind the wall speaking.
- Plates: 2 from local-image (Qwen-Image), 1664x928, cover-fitted, no enhance pass used (the enhance added a
  stray structure in the lower middle).
  - "wall": a colossal wall of near-black glitching data, crimson static, scanlines, fractured red light; tiny
    cyan and magenta city lights at the bottom edge (the human side only).
  - "beyond": dark red static with faint pale glints (read as eyes), scanlines.
- Sound: 3 effects, quiet under the voice: hum (ambience, 24 s, -18 dB), glitch (on "whispering", -16 dB),
  crack (on "cracking", -12 dB). Each was ranked best of N by the tool; the delivered take had no warnings.
- Palette: near-black, crimson red static and red light; cyan/magenta only on the far human-side lights.
- Restraint: procedural elements are scanlines, glitch slices, static rows, one red seam with its branches and
  glow, four glints, a red sweep, dust, and the title. No extra characters or props.

## Script (5 lines, 59 words)

- L1: The first network fell in one night, and what survived in its ruins turned strange.
- L2: The wardens sealed them behind a black wall, and built our net on this side.
- L3: Beyond it, the dead net waits, and whispers to anyone who comes too close.
- L4: Tonight, red static crawls across the stone, and something behind it speaks.
- L5: The wall is cracking.

## Shots and cues (film times from `finish --info`)

| Shot | Film time | Plate | Content | Cue (voice word) and film time |
| --- | --- | --- | --- | --- |
| 1 | 0.00 to 6.50 s | wall | L1 from 1.00 s; wall glitch and scanlines | none |
| 2 | 6.50 to 11.79 s | wall | L2 from 6.80 s; a red band sweeps down the wall | "L2:wall" = 8.58 s, sweep 8.58 to 9.78 s |
| 3 | 11.79 to 17.58 s | beyond | L3 from 12.09 s; glints open | "L3:whispering" = 14.79 s, glitch sound |
| 4 | 17.58 to 23.29 s | wall | L4 from 17.88 s; crimson static rows | "L4:static" = 19.02 s; "L4:speaks" = 22.60 s, seam draws to 24.2 s |
| 5 | 23.29 to 25.50 s | wall | L5 from 23.59 s; seam flares, branches, glow | "L5:cracking" = 24.19 s, crack sound, flare to 25.8 s |
| 6 | 25.50 to 28.08 s | black | title HAIRLINE, letters from 25.8 s, hairline from 26.3 s | none |

Note: the cue on "L3:whispering" is at 14.79 s and the eye glints brighten from there.

## Plate prompts

- wall: "Cinematic matte painting, a colossal wall of black glitching data filling the frame, near-black fractured
  surface with crimson red static, horizontal scanlines and pixel-shattered bands, fractured red light leaking
  through cracks, the middle of the wall is clean and uncracked, at the very bottom edge tiny distant cyan and
  magenta city lights far away, deep black and red palette, no people, no text, no logos, wide cinematic
  composition, painterly, high detail." (draft 2 of 2 used: qwen21_00093)
- beyond: "Cinematic matte painting, the far side of a dead digital void, dark red static fog, vast shadowy shapes
  and faint pale eyes glimpsed deep inside the red static, horizontal scanlines, deep crimson and near-black
  palette, empty clean space in the center, no people, no text, no logos, wide cinematic composition, painterly."
  (draft 1 of 2 used: qwen21_00094)

## Sound prompts (the delivered take in each case)

- hum: "low electrical hum of a vast machine, steady and deep, a dark drone" (ambience, 24 s)
- glitch: "a single soft digital glitch burst, distant" (1.04 s)
- crack: "a sharp stone crack with a short electric spark, one impact" (1.54 s)

## Budgets (this film)

- Voice takes: 10 generated in total, at most 4 per line (L1: 4, L2: 3, L3: 1, L4: 1, L5: 1). Limit 5 per line.
  Effects re-runs on the same dry take (`--fx`) are not counted.
- Image generations: wall 3 (2 drafts and 1 enhance; enhance rejected), beyond 2. Limit 5 per plate.
- Sound generations: 1 per effect. Limit 2.
- Stills/sample calls: 3 (two stills calls, one sample call). Limit 30.
- Full renders: 2 (draft 1, and the one improvement pass). Limit 3.

## Self-review (draft 1: contact sheet, the 1-per-second check, a sample --per 4 sheet and the brightness log)

1. Exposure: the film is too dark to read. Wall shots average luma about 0.018 (about 5 of 255) and the beyond
   shot about 0.043. On a phone the wall would read as near-black texture. Fix: raise the wall plate exposure
   (1.25 to 2.3) and drop the beyond exposure (1.3 to 1.0) so the cut between them is balanced.
2. Composition: the wall reads as horizontal streaks, not as a colossal wall of blocks. Fix: procedural block
   seams (dark mortar lines with a faint red edge light) drawn over the wall from shot 1.
3. Readability: the crimson static on "static" (L4) is too faint to read at one-second spacing. Fix: more rows,
   stronger.
4. Physical logic: the seam is almost straight and reads as a ruled line, not a fracture. Fix: a larger wander
   in its path.
5. Restraint: the four glints in the far side read as LEDs in a constellation. Fix: a wider, softer glow and a
   smaller core, so they read as watchers in the haze.
6. Transition wall to beyond: a brightness jump of about 2.4 times at the cut. Fixed by item 1; the 0.4 s fade-in
   stays.
7. Title: the kinetic reveal and the hairline read well and do not overlap anything. No change.
8. Timing: all five beats land on their words (table above). No drift.
9. Leftovers: none found in the stills.
10. Sound: the hum is quiet, the voice sits at about -16 LUFS, the crack and glitch are sparse. No change.
11. Not in the brief, left alone: the draft file is 246 MB at crf 16.

Improvement pass (one only): fixes 1 to 5 were made in shots.py (wall exposure 1.25 to 2.3, block seams, static
rows 0.90 to 0.84 at 0.16 strength, seam jitter 13 to 20, beyond exposure 1.3 to 1.0, glints wider and softer),
then re-rendered, mixed and finished. Result: the wall's mean luma went from about 0.018 to 0.027 and the
seam now wanders and branches. Items 1 and 6 are only partly fixed: the film is still very dark by design
(near-black with deep red), and the block seams are faint at contact-sheet scale. Left as they are, because the
brief allows one improvement pass.

## Budget used

See the Budgets section above (the final numbers are there).
