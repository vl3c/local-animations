# Evaluation: Ember, Track A (frozen assets), Claude Haiku 4.5, run 1

**Setup:** kit plus AGENT_GUIDE.md, the frozen Ember project, caps of 25 stills/sample renders and 3 full renders.

**Cost:** about 151k subagent tokens, 31 tool calls, about 7 min wall time.

**Human interventions:**
- 1 nudge: Haiku stopped twice while its full render ran in the background, before it had mixed or finished.
- The harness blocked Haiku from writing REPORT.md, so the coordinator saved it from Haiku's final message.

## Automatic gates

| Gate | Result |
| --- | --- |
| Render completes; 20.00 s, 1080p24, with sound | Pass |
| Ends on black | Pass (last frame luma 0.008) |
| Loudness | -16.0 LUFS |
| Flash/cut warnings | None |
| Layout warnings | None |

## Cues, measured on the encoded film

| Cue | Target | Measured | Result |
| --- | --- | --- | --- |
| Spark (L2:spark) | 7.14 s | absent at 7.08, visible at 7.17 | Pass |
| Flame (L2:grass) | 8.98 s | absent at 8.94, ignited at 9.04 | Pass |
| Wave (L3:stepped) | 12.59 s | absent at 12.54, visible at 12.75 | Pass |

## Rubric (0-2 each, from the Initial Condition checklist)

| Category | Score | Notes |
| --- | --- | --- |
| Timing | 2 | All beats come from cues. |
| Depth / physical logic | 1 | The spark shrinks and accelerates toward the horizon and crosses the tuft, but the occlusion is very brief. The fall is a diagonal from the upper right, which reads as a meteor more than a falling spark. |
| Composition | 1 | The flame is placed sensibly, but the "wall" is a crude dark band with a wavy edge across the top, and it stays through shots 2-3. |
| Transitions / continuity | 1 | The fades are correct (shot 3 fades out, shot 4 fades in). The foreground tuft vanishes at the 2→3 cut while the flame stays in place, which is a continuity jump. |
| Readability | 1 | The ignition and the title read well. The "dark steps back" wave reads as a drawn ring or lens flare, not darkness receding. The flame grows into an overexposed blob in shot 3. |
| Leftovers | 2 | None seen. |
| Restraint / polish | 1 | The flame is a simple teardrop sprite. The embers are barely visible. The hearth shot is the strongest. |
| Title | 2 | Clean serif "EMBER", eases in above the hearth, never overlaps. |
| **Total** | **11 / 16** | |

**Verdict:** a correct, working draft that a director would accept as a raw first pass. Every hard requirement technically holds. The visual craft is basic: the wall, the wave and the flame need a second pass. Its own improvement list matched about half of the problems found here; it missed the continuity jump and the ring look.

## Run 1, fix pass (v2): after one round of director's notes (6 notes)

**Cost of the pass:** about 51k more subagent tokens (202k in total), 17 tool calls, about 4.5 min. It used 3 stills calls and 2 full renders. One full render was wasted on a kit bug: `render all` reused stale segments after the code changed. That's fixed now: segments carry a code hash.

| Note | Result (coordinator's check on frames from the encoded film) |
| --- | --- |
| 1. Wall | Fixed. A smooth darkening from the top and edges, with no band. Side effect: shot 1 is now very dark, and the grass barely reads. |
| 2. Spark | Mostly fixed. It falls mostly downward and shrinks, and it passes behind the tuft's left flank for about 0.3 s. Still small. |
| 3. Continuity at the cut | Fixed. The tuft persists into shot 3 at the same place. Shot 3 then pushes in, so the tuft grows smoothly. |
| 4. Wave | Fixed. It's now a soft-edged reveal that opens around the flame. No ring. It reads as "the dark stepped back". |
| 5. Flame | Fixed. Layered tongues, a ground glow and no blowout. Sizes grow believably from shot 2 to 3 to 4. |
| 6. Embers | Partly fixed. They're there in a column above the hearth, but still faint at normal viewing size. |

**Rubric v2:**

| Category | v1 | v2 |
| --- | --- | --- |
| Timing | 2 | 2 |
| Depth | 1 | 1.5 |
| Composition | 1 | 1.5 (too dark in shot 1) |
| Transitions | 1 | 2 |
| Readability | 1 | 2 |
| Leftovers | 2 | 2 |
| Restraint / polish | 1 | 1.5 |
| Title | 2 | 2 |
| **Total** | **11 / 16** | **14.5 / 16** |

**Notes to "good":** one round of 6 notes took it from a raw draft to a good draft. Haiku applied every note faithfully and verified mid-motion stills. It didn't over-correct, except the darkness in shot 1.

## Run 1, round 2 (v3): two notes from the human director

1. Bring back the v1 flame. The director preferred it to the layered tongues.
2. The grass tuft popped in at the cut, so fade it in.

**Cost:** about 15k more tokens (217k in total), 9 tool calls, about 2 min. It used 1 stills call and 1 full render, and the plain `render all` picked up the changes on its own.

**Result:**
- Both notes are fixed.
  - The tuft fades in over 0.8 s from the start of shot 2: faint at 6.75 s, fully there by 7.4 s, before the spark reaches it.
  - The soft particle flame is back in shots 2-4, and in shot 3 its core stays below white (no blob).
- Everything else is unchanged.

**Totals for run 1:** three passes. About 217k tokens, 57 tool calls, about 13.5 min of agent time. 4 full renders (one wasted by the now-fixed kit bug) and 6 stills calls. Human input: one nudge, then 6 notes and 2 notes.

**Lesson for the guide:** the director's taste doesn't always follow "more detail". The simpler, softer v1 flame won. The guide's flame recipe now uses it, and the guide now says new elements never pop in.

## Run 1, round 3 (v4): two more notes from the human director

1. Remove the grass tuft entirely. The director didn't like it, so the occlusion requirement is dropped.
2. Put the spark's landing point and the flame on the horizon ground. It sat a bit above it.

**Result:** both fixed.
- Haiku measured the horizon at plate row 703, from where the rows change from blue sky to warm grass, and moved the base to y 705.
- Zoomed crops of the film at 10.5 s and 13 s confirm the flame stands on the grass line.
- Unrequested change: Haiku also lowered the flame's core brightness, which is harmless.
- Cost: +14k tokens, 11 tool calls, about 2.3 min.

**Run 1 totals:** four passes, about 231k tokens, 68 tool calls, about 16 min. Human notes: 6, then 2, then 2.
