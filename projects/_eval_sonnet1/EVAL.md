# Evaluation: Ember, Track A (frozen assets), Claude Sonnet, run 1

**Setup:**
- Same frozen assets and the same original brief as Haiku run 1.
- A newer AGENT_GUIDE: the stale-render fix, the foreground/finish rule, the effect recipes (soft particle flame, veil/reveal, depth fall), and the ground-line and less-is-more rules.

**Cost:**
- about 156k subagent tokens, 42 tool calls, about 9 min
- 6 stills/sample calls (about 41 frames), 1 full render
- No nudges: it finished all deliverables in one go.

## Automatic gates

| Gate | Result |
| --- | --- |
| Duration | 20.00 s |
| Loudness | -16.0 LUFS |
| Ends on black | Yes |
| Flash/layout warnings | None |
| Title-box check | Ran its own check over all 110 frames of shot 4: 0 overlaps, minimum gap 59 px |

## Cues, measured on the encoded film

| Cue | Result |
| --- | --- |
| Spark | Appears between 7.08 and 7.17 s (target 7.14). |
| Ignition | A flash at the horizon by 9.04 s (target 8.98). |
| Wave | Starts after 12.54 s (target 12.59). |

All three pass.

## Rubric (0-2 each)

| Category | Score | Notes |
| --- | --- | --- |
| Timing | 2 | |
| Depth | 2 | Accelerates, shrinks and dims to the horizon. Hidden in bursts behind the blades, verified with an occlusion map it computed. |
| Composition | 1.5 | The flame sits on the horizon (it didn't need the note Haiku got). The grass silhouette is huge and dominates shots 2-3, which is exactly the element the director disliked in Haiku's film. |
| Transitions | 2 | The silhouette fades and rises in (no pop). The cut frames match. Fades are correct. |
| Readability | 2 | The wall is a smooth darkening (no band). The reveal in shot 3 strongly reads as "the dark stepped back": the whole field turns golden. |
| Leftovers | 2 | |
| Restraint / polish | 1.5 | Shot 3 gets very bright, with a teal/khaki sky. The hearth shot is warm and good, with visible embers. |
| Title | 2 | Fades in and glides up while its letter-spacing tightens. Logged and verified. |
| **Total** | **15 / 16** | first draft (Haiku run 1: 11 at v1, about 15 after three note rounds) |

**Verdict:** Sonnet's first draft is about where Haiku landed after three rounds of notes. It self-verified more rigorously (occlusion map, a box check over every frame) and finished without a nudge. It costs about the same tokens as Haiku's first pass, but Sonnet tokens cost several times more.

**Caveat:** the guide improved between the two runs, so part of the gap is the guide, not the model. A fresh Haiku run on the current guide would separate the two effects.

## Round 1 (v2): two notes from the director

1. Remove the grass.
2. Put the fire on the horizon.

**Result:** both fixed in one pass. Crops confirm the flame stands on the sky/land edge in shots 2 and 3, and it doesn't move at the cut.
- Sonnet measured the horizon at plate row 704.5, from the sharpest drop in the blue channel, and checked it under the camera push. Haiku's measurement was 703.
- Cost: +18k tokens, 14 tool calls, about 2.6 min, 1 stills call, 1 full render.

**Sonnet totals:** about 174k tokens, 56 tool calls, about 11.7 min, 1 round of notes (2 notes).
**Haiku totals:** about 231k tokens, 68 tool calls, about 16 min, 3 rounds (10 notes).

Taking Sonnet's higher price per token into account, Sonnet probably cost more per finished film. It needed far fewer human notes, though, and those are the scarce resource.
