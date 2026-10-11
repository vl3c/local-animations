# Evaluation: idea to film (Track B), "black wall" theme, Claude Sonnet, run 1

**Result:** "HAIRLINE", 25.58 s, four lines, three plates, three effects, plus a first draft, a self-review and one improvement pass.

**Cost:** about 201k subagent tokens, 71 tool calls, about 23 min wall time (Haiku: 228k tokens, 74 calls, about 19 min). No nudges. All GPU servers were down at the end (verified).

**The title is the same as Haiku's.** Both models independently titled the film "HAIRLINE". The transcript shows Sonnet never opened Haiku's project, so this is convergence on the brief's "starting to crack" image.

## Creativity (the director's question)

Sonnet made bolder creative choices than Haiku:

| Element | Sonnet | Haiku |
| --- | --- | --- |
| Narrator | **The thing behind the wall speaks in the first person:** "Long ago, you built a wall, and called the silence safety. / We waited in the dark. We learned your names. / Listen. Your wall is cracking. / Come closer. We are almost through." It's courteous and menacing. | A third-person machine narrator telling the history |
| Voice | **ai-choir** on the ancient-female voice ("many minds as one") | harbinger |
| Plates | **3:** a wall, the far side, and a wall close-up | 2 |
| Staging | A scan beam ignites the wall on "wall". A crowd of eyes opens on "dark", "learned" and "names". On "cracking" the crack runs; on "almost" it opens into a rift; on "through" a huge slit eye opens in it. The title assembles letter by letter. | Simpler beats, ending on a thin zigzag crack |
| Story arc | **A real escalation:** dormant wall, eyes, crack, rift, eye. The most "film-like" arc of all the benchmark runs. | Mostly static |

## Tool use

| Area | Score | Notes |
| --- | --- | --- |
| GPU juggling | 2/2 | Voice, then image, then sound, each stopped before the next. Clean at the end. |
| Voice | 1.5/2 | It chose a creative preset and found the slow-pace problem itself (`--tempo 1.4`). All lines are 100% intelligible. It trimmed the echo tails itself (the last word + 1.2 s, with a fade). The "speech low under the bass" warning stayed even with `--bass -6`, `-8` and `-12`. **That's a possible local-voice issue:** the flag doesn't move the metric that triggers the warning. It also stayed within the brief's tighter take budget, so it read the raised budget conservatively. |
| Images | 1.5/2 | It made a third plate (a close-up) for variety. The prompts carry scale cues ("seen from far away", "tiny distant skyline at the bottom"), so the wall reads better than in Haiku's run, but it still shows as a faint purple expanse in shot 1. It accepted the first round (2 drafts plus enhance) for every plate. |
| Sound | 2/2 | It measured the effects against the voice (about 10-21 dB under) and raised them to useful levels: hum -14, crack -5, swell -11 dB. That's the only run that checked the mix numerically. |
| Self-review | 2/2 | 8 concrete items, 6 fixed and 2 partly fixed (the flat rift interior, the overall darkness). |

## Shared weakness: darkness

Max brightness is 0.09 for Sonnet and 0.05 for Haiku, against 0.12-0.17 for Ember. Both models leaned near-black for this theme, and neither had a threshold telling it to stop. Backlog items 2-4 (a darkness warning, a plate acceptance check, prompt craft) apply to both runs.

## Verdict

Sonnet is more creative and more cinematic: a stronger concept, voice and arc. Haiku is a bit cheaper and faster, and equally disciplined with the tools. For idea-to-film work, where creative direction matters, Sonnet's lead is clearer than in the frozen-asset test.
