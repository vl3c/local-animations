# 1. Pre-production: interview, script, style, references, storyboard

Everything here happens before the GPU is touched, except cheap reference drafts at C1-C3.

## C0: the interview

Ask before any generation, with AskUserQuestion (at most 4 questions per call, each with a recommended option first
and a few words of why). Skip what the user already said. Pick from this bank:

| Topic | Ask about |
| --- | --- |
| Tone limits | What's off-limits (religious symbols, gore, edginess); how far the humour goes. For a risqué idea, offer stagings that keep the gag and show nothing (Puff Ahoy: "topless on deck" became a top blown off as two scallops cover her in the same frame; the user picked it over "face-down" and "keep the bikini"). |
| Story staging | How the twist is revealed and when; whether a character shows key attributes from the start or only at the reveal. |
| Ending | How it ends (on black, on a gag, on a hug, on the title). |
| Length and pace | Target length; how many words that allows at the voice's pace (below). |
| Voice | Who speaks; ask for 2-3 contrasting auditions (age, depth) instead of fixing one. |
| Music | None, a bed under the voice, or the music leads; structure tied to words (where it builds, where it hits). |
| Loudness | The final target. Offer -14 LUFS (louder, matches music platforms) and -16 (the kit default). -18 has been too quiet. |
| Subtitles | On or off. Default: on, burned in, readable, timed from the word timings. |
| Style | The look, as references the user likes (inspiration only), and the medium: painted plates + vector, flat vector, kinetic type, glitch, cartoon... |
| Checkpoints | Which of C1-C6 this film needs (propose; the user confirms). |
| Budget | Wall time and the number of review passes ("~1 h, 2 review passes" worked). |
| Delivery | The folder name and where the film lives; master format; a preview copy. |

Write the answers into BRIEF.md and the rules into DECISIONS.md immediately.

**Mark rules as defaults or fixed points.** Authors lift their own rules later ("no music, for now"; "never stretch the
voice", then "make it 10% faster"). Ask which rules are fixed, and treat the rest as defaults.

## The script

- **Measure the pace, don't assume it.** Pacing words in a voice instruction can halve the speaking rate:
  - "slow, long sustained vowels, dramatic pauses": about 1.0 words/s
  - "a steady, measured pace with short pauses": about 1.7 words/s
  - the kit's narrated benchmarks: about 2.0-2.2 words/s of speech (45-70 words for 20-30 s)
  - the built-in local-voice voices are slow for narration; a later tempo of 1.15-1.3 helps

  For a deliberately slow character voice, write a shorter script, or make one test take before the script is final.
- **Short, concrete sentences, each visual beat landing on a word.** Note the word each beat lands on.
- **Keep a speaker tag with its quote** ("The ring texted: Maybe don't.") so subtitles never split them.
- **For comedy, write the intent per beat:** the setup, the punchline, and the twist with the word that reveals it.

When the user says "go", lock the script word for word in BRIEF.md, marked APPROVED.

**A film without words** gets a beat sheet instead: one row per shot with its bars, time, what happens and the
sounds, at the music's planned tempo (120 BPM: a 4/4 bar is 2 s, a 20 s film is 10 bars). It is locked the same way,
then re-timed to the chosen take's real grid (Puff Ahoy: one beat sheet, "go" on the first version).

**Named characters from other works** (the user asks for a famous hero or a branded doll): translate them into
looks at once ("a caped vigilante in a bat-eared cowl", "a blonde fashion doll"), say so in C0, and leave logos
and emblems out; a generated chest emblem was erased with one edit (Puff Ahoy).

## The brief (`BRIEF.md`)

The brief is self-contained: a fresh session could make the film from it. Its sections (the template has them):

1. The locked script, marked APPROVED.
2. Intent per beat: setup, punchline, twist and where it's revealed.
3. Characters: the look, the props that never change, the voice direction.
4. A style reference, as inspiration only. Never named in generation prompts.
5. The music's structure tied to words, if there is music.
6. The mix plan: loudness target, music level options (offer 0 dB as well as -6/-9/-12 under the voice).
7. The time budget and number of review passes.
8. Deliverables and the report.

If the user wrote messages about the film, keep them verbatim (`brief/AUTHOR.md`) and rank them above the spec.
Give the builder explicit freedom to deviate elsewhere, with a log entry for each deviation.

## The style (`STYLE.md`)

Write the style as a **system, not adjectives**. "Chaotic, unsteady, edgy, as much as tasteful" became, in one film:

- 3-5 taste rules ("glitch only on the machine's lines", "never fully blown-out white")
- an effect vocabulary: the named effects this film uses, and nothing else
- intensity levels (0-3) per shot, and protected windows around key cues where effects stay off
- palette rules that a script can check ("no colour within ΔE 12 of #F5D27A before 4:20", "at most 0.02% of #D7263D")
- overrides of the default quality checklist, with the reason ("hard smash-cuts on impacts")

Then:

- **Check the rules against your own references.** A palette checker run over one film's style frames found two
  of them breaking the rules they illustrated. Fix the reference before anything is built from it.
- **When the picture is procedural, style frames drawn in code beat generated images.** Ship their source; the
  shots can import the same drawing functions, so a design holds by construction.
- **Look in the [cookbook](../cookbook/README.md)** for recipes tagged with this style, and name the ones you'll use.

## Read the tools before writing the spec

Read each tool's SKILL.md (local-voice, local-music, local-image, local-sounds, local-gpu) before planning around
it. Specs written from memory went wrong:

- local-image has no negative prompt, so plate prompts describe what is there and never name what to avoid.
- local-voice returns a processed and a human stem of the same take, sample-aligned: a voice that turns from machine
  to human is a blend of one take, not a crossfade between two takes (which never align).
- You cannot hear: voice auditions and mixes go to the user.

## C1: characters, C2: props and locations

For each recurring character, then each recurring prop and set (vehicle, weapon, room, street):

1. Draft 4 lettered options (`--preview`), on one labelled sheet. Use `--cutout` for a shape you will trace or
   composite.
2. The user picks, or combines ("A's face with C's cape": a multi-reference edit).
3. Save the pick as `assets/plates/ref/<name>.png` and write its entry in `REFERENCES.md`:
   - the reference image path (and a wide or full-body variant if scenes need one)
   - a one-line attribute string, pasted verbatim into every prompt that shows it ("chubby purple kaiju, round
     eyes with round black pupils, claws, horns, pink bow, red lipstick on her ONE mouth, a pink handbag")
   - counts ("one mouth", "four fingers and a thumb", "only one car")
   - spatial facts (the steering wheel's side, which side faces the window)

**Lock C1 before any scene batch.** In one film the hero's design changed three times (a cross, a cape, a pendant)
while scene batches ran with the old reference; each batch was relaunched.

## C3: the storyboard

One draft frame per shot (`--preview`, about 1024 px wide), numbered, with the subtitle line under each and the
planned gags or beats listed per shot. **When the picture is composited from cut-outs**, build the storyboard with
the real compositor from the C1 picks instead (`render sample --per 3`): it costs no GPU, the frames become the
animatic, and the notes are concrete (Puff Ahoy: 5 notes on the first storyboard, none on the draft). The user answers per shot: keep / change / their idea. Ideas you have go in as
options ("the ring lands as the O of the title: yes or no?"), never silently.

For a longer film, also write `storyboard.md` in this section order (short pieces need a fraction of it):

1. fixed rules (and which are defaults)
2. tools
3. timing model (from the voice, or from a finished soundtrack)
4. look (palette rules, any style system)
5. sound
6. script table: line id, shot, voice setting, text
7. shots: pre/post roll, what lands on which word, the style frame
8. acceptance checks, each with the script that will run it

Keep `storyboard.jpg` with the film.
