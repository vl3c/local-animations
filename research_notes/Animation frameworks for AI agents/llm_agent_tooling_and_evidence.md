# LLM- and agent-native tooling for animation/video, and evidence on LLM capability (as of Oct 2026)

Scope note: research done 2026-10-08. Model names below are reproduced exactly as the sources print them. Results from 2025 papers use models that are now 1-2 generations old; these are marked "(older, 2025)". Most third-party pages were read via a summarizing fetch tool, so exact figures should be spot-checked against the primary PDFs before they are quoted publicly.

## 1. MCP servers and agent integrations for animation tools (Blender, Manim, Remotion, Motion Canvas/Revideo, HyperFrames)

### Takeaway
Agent integration is mature for Blender (an official Blender Lab MCP server since April 2026, plus the very popular community server) and for Remotion and HyperFrames (official agent skills). Manim and Motion Canvas/Revideo only have thin community wrappers that run code and return a video. All of these run locally. For animation work, MCP buys little over "write a file, run the CLI renderer, look at stills", which Claude Code already does natively. The more valuable integrations are the skills and API-doc lookup that fight version drift.

### Cited Findings
**Blender**
- The official Blender MCP server is by Blender Lab: v1.0.0 shipped 27 Apr 2026, latest v1.0.3 on 11 Sep 2026. It is GPL-3.0-or-later, needs Blender 5.1+, and is what Anthropic's Blender connector for Claude uses. It is positioned for scene analysis, debugging and batch scripting, "not generating art". — [StraySpark comparison 2026](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026) (vendor of a competing server; facts about the official server look neutral but are unverified against blender.org)
- The official server has 26 tools: code execution, blend-file/object/collection summaries, screenshots, viewport navigation, thumbnail and viewport renders, and two search tools over a bundled copy of the Blender Python API reference and manual. Six tools have `_for_cli` variants that run a background Blender for batch auditing. It works through a local TCP socket in a Blender add-on, relayed by a stdio `blender-mcp` process. The docs warn that it runs LLM code unguarded and recommend a VM. — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- The community server ahujasid/blender-mcp (MIT, created March 2025) had about 29.3K stars on 25 Sep 2026. It was renamed "MCP for Blender" on 16 Sep 2026 (PyPI `mcp-for-blender`; `uvx blender-mcp` still works) and supports Blender 3.0+. It has 36 tools, including a live `bpy_api_lookup` and Poly Haven / Sketchfab / Hyper3D Rodin integrations (3D generation is a paid Premium tier). Python exec is on by default, the socket is unauthenticated, four CVEs were published in 2026, and anonymous telemetry is on by default. — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026); [Enterprise DNA directory](https://enterprisedna.co/directories/mcp/ahujasid-blender-mcp)
- Models trained on older Blender code call APIs that changed or were removed in Blender 5.x; the comparison presents bundled or live API lookup as the fix. Neither server is documented as having keyframe or animation-specific tooling. — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)

**Manim**
- abhiemj/manim-mcp-server (MIT, about 597 stars, last update listed as 2025-05-19, so older) runs a Manim script and returns the rendered video. It is configured in Claude Desktop/Cursor with a `MANIM_EXECUTABLE` env var. Gorav22/Animated_video is a near-identical clone. — [mcpservers.org](https://mcpservers.org/ko/servers/abhiemj/manim-mcp-server); [mcpservers.org Animated_video](https://mcpservers.org/en/servers/Gorav22/Animated_video)
- paulnegz/manim-mcp is a text-to-animation CLI/agent/MCP server built on manimgl (3b1b's fork), not Manim CE. — [README via jsDelivr](https://cdn.jsdelivr.net/gh/paulnegz/manim-mcp@main/README.md)
- Nous Research's Hermes Agent bundles a `manim-video` skill (v1.0.0, MIT, 2026) with the flow PLAN → CODE → RENDER → STITCH → AUDIO (optional) → REVIEW. It writes `plan.md`, then one `script.py` with one independently renderable Scene class per scene. Drafts render at `-ql` and finals at `-qh`, and clips are stitched with ffmpeg. Review means "render preview stills (`manim -ql --format=png -s`), verify against plan, adjust". It pins Manim CE v0.20+ (docs tested on v0.20.1). TTS is optional (ElevenLabs or Qwen3-TTS). Timing is explicit in code (`run_time`, `self.wait()`, `add_subcaption(duration=N)`), with no word-level sync. The skill also has layout rules: minimum font_size 18, `buff >= 0.5` at edges, opacity tiers 1.0/0.4/0.15, FadeOut before replacing text, and standard holds (title 1.5 s, key equation 2.0 s, aha reveal 2.5 s). — [Hermes Agent docs](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/creative/creative-manim-video)

**Remotion**
- The official agent skills install with `npx skills add remotion-dev/skills` (or are offered by `bun create video`). They are in the Remotion monorepo under `packages/skills`. The skills are: `/remotion-best-practices` (umbrella), `-create`, `-markup` (compositions, animation, layout, typography, media, audio, fonts, timing), `-studio`, `-render`, `-maps`, `-captions`, `-saas`, `-interactivity`, `-docs` (search docs and fetch as Markdown), `-upgrade`, and `-multimedia` (Mediabunny). Claude Code, Codex, Kimi Code and Cursor are named as supported agents. — [Remotion docs: AI skills](https://www.remotion.dev/docs/ai/skills)
- An Aug 2026 Tella guide uses `npx remotion skills add` instead, so the install commands differ by source. — [Tella blog](https://www.tella.com/blog/how-to-use-remotion-agent-skills-with-claude-code.md); [mer.vin May 2026](https://mer.vin/2026/05/remotion-agent-skills-install-remotion-dev-skills-for-claude-code-and-cursor/)
- The Remotion docs are agent-readable: append `.md` to any docs URL, or send `Accept: text/markdown`. Pasting a docs link into Claude Code makes it fetch the Markdown. The fetched AI pages did not mention an llms.txt or an official MCP server. — [Remotion docs: AI](https://www.remotion.dev/docs/ai/)
- `@remotion/install-whisper-cpp` installs whisper.cpp locally, downloads a model (e.g. `medium.en`), and transcribes with `tokenLevelTimestamps: true`. `toCaptions` then turns the output into a captions JSON array. The docs recommend 16 kHz WAV input and use whisper.cpp 1.5.5 as the example version. — [Remotion docs: install-whisper-cpp](https://www.remotion.dev/docs/install-whisper-cpp/)

**Motion Canvas / Revideo**
- Revideo is an open-source TypeScript framework built on Motion Canvas that adds audio, faster rendering and a programmatic render API. No official agent or LLM tooling was found. Its founder's later YC company, Midrender, is an AI motion-graphics editor. — [YC Revideo](https://www.ycombinator.com/companies/revideo); [YC Midrender](https://www.ycombinator.com/companies/midrender)
- The only Motion Canvas agent found was a Gradio demo Space by Patrick Rathje. — [HF Space](https://huggingface.co/spaces/prathje/gradio_motioncanvas_agent/blob/af6ade43b266650ec8f4543ee281c3d356b26731/README.md)

**HyperFrames (HeyGen), a new agent-native entrant**
- HyperFrames is described as "Write HTML. Render video. Built for agents." It is Apache-2.0. Headless Chromium loads the HTML composition, advances a deterministic clock, captures frames, and muxes with FFmpeg. It runs locally, in Docker or in CI, with no API key. It ships about 20 agent skills and 17 caption effects. — [noqta.tn](https://www.noqta.tn/en/blog/heygen-hyperframes-html-to-mp4-ai-agent-video-2026); [yuv.ai](https://yuv.ai/blog/hyperframes-heygen)
- The sources conflict on details. The open-source date is given as 10 Mar 2026 by one source and 17 Apr 2026 by another. Star counts are quoted as 23K, about 32.5K (v0.7.22, 30 Jun 2026) and "50k+" (HeyGen's own claim, Sep 2026). — [jimmysong landscape](https://landscape.jimmysong.io/projects/hyperframes/); [yuv.ai](https://yuv.ai/blog/heygen-hyperframes-html-video); [HeyGen research](https://www.heygen.com/research/introducing-code2video-benchmark)

### Inferences
- For a local Claude Code skill, an MCP server for Manim or a custom pycairo stack adds nothing beyond Bash plus a render CLI. The useful pieces to copy are (a) bundled API docs with a lookup tool (official Blender MCP, `/remotion-docs`), (b) a stills-render command, and (c) skills that encode best practices.
- Blender MCP fits interactive 3D scene work. It is not a natural fit for a narrated-explainer pipeline, and its security posture (unauthenticated socket, CVEs) argues for running it only when needed.
- Remotion and HyperFrames are the two frameworks with first-party agent skills. HTML/React has heavy training-data exposure, which probably explains why HeyGen frames HTML as "agent-native".

### Gaps
- Remotion licence terms could not be retrieved; both fetch attempts on remotion.dev/docs/license returned only the TOC. From pre-2026 training knowledge, unverified: free for individuals and companies of up to 3 employees, with a paid company licence otherwise. Verify before recommending.
- No official llms.txt for Remotion, Manim or Motion Canvas was confirmed.
- The HyperFrames GitHub README was not read directly; its details come from secondary blogs.
- No evidence was found that either Blender MCP server handles keyframed animation or final Cycles/EEVEE animation renders as first-class tools (code exec could do it).

## 2. Research systems and papers (2024-2026): architectures and reported success rates

### Takeaway
The consistent winning architecture is planner (storyboard) → per-scene coder with an error-driven fix loop → render → visual critic on frames. The two largest measured gains came from the planner and from structured layout (Code2Video: removing the planner cost about 41 points). RAG over API docs has mixed effects: it helps weak models and hurts strong ones (TheoremExplainAgent). Renderer-in-the-loop with docs lifts a 30B local Qwen coder to about GPT-4.1 level (ManimTrainer/ManimAgent).

### Cited Findings
**TheoremExplainAgent (TIGER-AI-Lab, arXiv 2502.19400, ACL 2025; older, 2025)**
- The architecture has a planner agent (scene plan → visual elements, animations and transitions, plus the narration script) and a coding agent that writes Manim per scene. An error-fix loop allows up to N=5 attempts. Agentic RAG over the Manim docs (ChromaDB, threshold 0.5, k=2) issues queries at storyboard, implementation and error-correction time. Videos run over 5 minutes, and the benchmark is TheoremExplainBench (240 theorems). — [arXiv HTML](https://arxiv.org/html/2502.19400)
- Success rates: o3-mini (medium) 93.8% (with RAG 82.1%), GPT-4o 55.0% (45.8%), Gemini 2.0-Flash 14.6% (20.4%), Claude 3.5-Sonnet v1 2.1% (14.6%). Overall quality scores were about 0.71-0.79 for all of them, vs 0.77 for human-made Manim videos. — [arXiv HTML](https://arxiv.org/html/2502.19400)
- With o3-mini, success at N=5 retries was 93/91/96% for easy/medium/hard, and success "significantly improves with more attempts". — [arXiv HTML](https://arxiv.org/html/2502.19400)
- The failure categories were Manim API hallucination (the most common), then LaTeX rendering errors, then generic errors (imports, undefined variables). Most videos had minor layout issues: misaligned text, overlapping shapes, inconsistent sizes. — [arXiv HTML](https://arxiv.org/html/2502.19400); [arXiv abs](https://arxiv.org/abs/2502.19400)
- The repo uses LiteLLM model naming (OpenAI, Azure, Vertex, Gemini, Bedrock), so Ollama and vLLM are not documented but are plausibly routable. It uses local Kokoro TTS (ONNX) through a custom KokoroService derived from kokoro-manim-voiceover, an optional `--use_visual_fix_code` flag ("Use VLM to fix code with rendered visuals"), and Python 3.12.8. It was tested on macOS and Linux. — [GitHub](https://github.com/TIGER-AI-Lab/TheoremExplainAgent)

**Code2Video (Show Lab NUS, arXiv 2510.01174, NeurIPS 2025 workshop / ICML 2026)**
- It uses three agents. The Planner turns content into a timed storyboard and fetches assets. The Coder writes Manim CE v0.19.0 code with "ScopeRefine" (scope-guided auto-fix: repair at line, then block, then scene scope). The Critic is a VLM (Gemini 2.5 Pro) that uses "visual anchor prompts" to fix layout. — [GitHub](https://github.com/showlab/Code2Video); [arXiv HTML](https://arxiv.org/html/2510.01174)
- In the visual anchor method, the canvas is a 6×6 grid of anchor points mapped to fixed Manim coordinates. Elements get a point anchor or a region of anchors, and an occupancy table records anchors, scale and code lines so the critic can trace an overlap to source and reassign free cells. 6×6 beat 4×4 and 8×8 (8×8 caused clutter), and self-directed placement was barely better than centring everything. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- Main results (aesthetics avg / TeachQuiz): direct code generation scored Claude Opus 4.1 37.8/40.0, GPT-5 32.7/36.5 and GPT-4.1 34.2/37.0. The Code2Video agent scored Claude Opus 4.1 87.9/86.0 (best), GPT-4.1 79.0/82.0, GPT-5 72.2/80.0, o4-mini 67.8/48.5, GPT-4o 60.0/44.0 and Gemini-2.5 Pro 57.4/72.0. Human 3B1B videos scored 99.7/97.1, and pixel video models scored about 4-9 (Veo3 9.0/2.5). — [arXiv HTML](https://arxiv.org/html/2510.01174)
- Cost: the agent takes about 9-17 min and 19-49K tokens per video vs about 2 min and 1-2K tokens for direct generation. Without parallel scene rendering it is 5.6× slower, and without ScopeRefine 2.5-2.8× slower and 1.4-1.6× more tokens. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- Ablations (GPT-4.1 backbone, aesthetics/quiz): full 79.0/82.0; without Planner 38.1/40.5; without external asset database 68.1/52.0; without visual anchor 69.2/55.2; without Critic 72.5/60.7. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- In the human study, humans gave Code2Video lower layout scores than the VLM judges did, because they notice brief occlusions that VideoLLMs miss. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- The repo needs cloud LLM and VLM APIs (best results: Claude-4-Opus for code, gemini-2.5-pro for the critic). It does not document local models, and the README does not describe narration/TTS. — [GitHub](https://github.com/showlab/Code2Video)

**ManimTrainer / ManimAgent (Rammuni Silva et al., 2026; page dated 31 Aug 2026)**
- The paper evaluates 17 open-source sub-30B LLMs × 9 training/inference combinations on "ManimBench". Inference uses renderer-in-the-loop (RITL), either alone or with API docs added (RITL-DOC). The best result was Qwen 3 Coder 30B + GRPO + RITL-DOC: 94% render success and 85.7% visual similarity to reference videos, about 3 points above a GPT-4.1 baseline. SFT mainly improved code quality, and GRPO improved visuals and responsiveness to feedback. — [deeplearn.org abstract](https://deeplearn.org/arxiv/815516/training-and-agentic-inference-strategies-for-llm-based-manim-animation-generation) (only the abstract was read; arXiv id not confirmed, possibly [2604.05266](https://arxiv.org/abs/2604.05266))

**Other 2026 systems with critic loops**
- DATAREEL (arXiv 2604.25220) is a data-video system. A Director produces an animation plan, a Plan Critic checks it against intent, and a Coder writes HTML/D3.js. A Video Critic then reviews the rendered output for timing, narration alignment and visual quality, and sends corrections back to the coder. — [arXiv](https://arxiv.org/pdf/2604.25220)
- ArtiMo (arXiv 2608.20699) does articulated mesh animation in Blender, with Gemini 3.1 Pro as the VLM critic and "ChatGPT 5.4" as the LLM, and at most 3 critic-actor rounds. CutsceneBench (arXiv 2604.25318) has a director agent with animation, cinematography and sound subagents and a visual feedback loop, in a game engine. — [ArtiMo](https://arxiv.org/pdf/2608.20699); [CutsceneBench](https://awesomepapers.io/papers/2604.25318)
- PhysicsSolutionAgent (arXiv 2601.13453) is a Manim explainer for physics problems. It cites Manim code hallucinations and LaTeX errors as the main failure categories in prior systems. — [arXiv](https://arxiv.org/pdf/2601.13453)
- Blender/bpy benchmarks: BlenderGym (2504.01786, 245 scene-editing tasks, older, 2025) found that even SOTA VLM systems struggle on tasks easy for human Blender users, and studied verifier-guided inference scaling. 3DCodeBench (2606.01057) reports that multi-turn agentic refinement with a VLM Visual Critic over multi-view renders "significantly improves" quality. — [BlenderGym](https://arxiv.org/html/2504.01786v1); [3DCodeBench](https://hyper.ai/ko/papers/2606.01057)
- Caution on VLM critics: StoryAgent (2411.04925, older) found that MLLMs could not distinguish ground-truth from generated storyboards. — [arXiv](https://arxiv.org/pdf/2411.04925)

### Inferences
- The ablations point to a clear priority order: (1) an explicit storyboard/plan, (2) a structured layout system (anchor grid plus occupancy table), (3) a render-error fix loop with scoped repair, and (4) a VLM critic on frames. The critic helps, but less than the planner and layout structure, and it misses brief occlusions that humans see.
- This matches the Initial Condition lessons, where stills mode and contact sheets were the core loop. A skill should add a machine-readable layout/occupancy record so overlaps can be detected without a VLM.
- RAG is not a free win. For strong models, a short curated cheat sheet (version pins plus forbidden APIs) is probably better than top-k doc retrieval; the ManiBench result below supports this.

### Gaps
- Per-model numbers for current Claude Sonnet/Haiku (4.5+/5) on Manim or Remotion were not found in any paper.
- I could not find how TheoremExplainAgent or Code2Video time their narration (the TEA README is silent beyond Kokoro).
- The full ManimTrainer paper (per-model table, Qwen 2.5 vs 3 breakdown) was not accessed.

## 3. Evidence on model capability (frontier vs local), failure modes and mitigations

### Takeaway
On raw zero-shot Manim, frontier models execute about 33-67% of hard problems; small or older open models execute about 0-25%, and Qwen-2.5-Coder 0% in the ManiBench pilot. With an agent harness and renderer feedback, everything improves sharply: about 94% render success for both o3-mini (2025) and a GRPO-tuned Qwen3-Coder-30B (2026). On motion design quality (HeyGen, Sep 2026), the frontier is tightly bunched (top four within 12 Elo), and the best open-weight models are within 50 Elo. The main remaining failures are visual (timing between beats, text collisions, flat "safe" layouts), not syntactic.

### Cited Findings
- ManiBench pilot (arXiv 2603.13251, Feb-Mar 2026): zero-shot executability, with version-conflict rate in brackets, was Claude-Sonnet-4 .667 (.000), Kimi-K2.5 .667 (.083), Gemini-2.5-Pro .333 (.000), Qwen3.5+ .333, Qwen3-235B .250, DeepSeek-R1-0528 .139 (VC .806, inflated by reasoning-token extraction failures), Llama-3.1-8B .083, Qwen-2.5-Coder .000 and Gemma-3-27B .000. The pilot set is small (12 problems in the pilot phase; the full benchmark targets 150-200), so these are low-n numbers. Alignment and coverage are keyword heuristics. — [ManiBench HTML](https://arxiv.org/html/2603.13251v1); [arXiv abs](https://arxiv.org/abs/2603.13251)
- ManiBench catalogues 145 ManimGL→CE mapping items, including `ShowCreation`→`Create`, `FadeInFrom`→`FadeIn(shift=...)`, `CONFIG` dict→`__init__` params, `manim_imports_ext`→`from manim import *`, and `InteractiveScene`/`GraphScene`→`Scene`/`Axes`; PiCreature does not exist in CE. Hallucinated classes such as `MCircle` also appear. — [ManiBench HTML](https://arxiv.org/html/2603.13251v1)
- Prompting ablation on Gemma-3-27B: listing the forbidden ManimGL constructs ("version-aware" prompting) drove the version-conflict rate to 0%. Few-shot examples were the only strategy that raised executability (+11.1 pp). Chain-of-thought introduced version conflicts (2.8%). — [ManiBench HTML](https://arxiv.org/html/2603.13251v1)
- HeyGen "Benchmarking Code-to-Video" (18 Sep 2026, with Kaggle): 168 human-made motion-graphics beats (8 categories, examples about 3.6-7.5 s) generated as HTML via HyperFrames and ranked by pairwise Elo on five axes (Engagement, Prompt-Intent, Composition, Temporal, Craft). Overall ranking: gpt-6-astra #1, gpt-5.5 #2, claude-opus-5 #3, gpt-5.6-sol #4, claude-fable-5 #11, glm-5.2 #16, deepseek-v4-pro #18. The top four are within 12 Elo with overlapping intervals. Open-weight qwen3.8-max, deepseek-v4.1-flash, kimi-k3 and glm-5.3 are "within 50 Elo of first place". Models are closest on Prompt-Intent and furthest apart on Composition and Craft. claude-opus-5 underperformed claude-opus-4-8 on one brief. Sonnet and Haiku are not reported. — [HeyGen Research](https://www.heygen.com/research/introducing-code2video-benchmark) (a vendor benchmark of its own framework; the overall Elo values are only in an image; the page says 16 models but cites a #18)
- HeyGen's failure modes: models "hit every beat" but "the timing between beats breaks". "Text is laid out for the final frame, not for the path it travels" (collisions mid-motion). "Safe means flat": elements are shrunk to stay legible. Easing is linear or abrupt with frame-to-frame jitter, and headlines are small or cropped at the edges. HeyGen calls skills, harnesses, multi-agent review, retrieval and style-guide injection helpful but "a ceiling, not a fix", and reports no measurements for them. — [HeyGen Research](https://www.heygen.com/research/introducing-code2video-benchmark)
- Code2Video shows that the harness matters more than the model. Direct code generation with Claude Opus 4.1 scored 37.8 aesthetics vs 87.9 inside the agent, and the agent improved every backbone by about 40-50 points. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- Local models: the best sub-30B configuration (Qwen 3 Coder 30B + GRPO + renderer-in-the-loop with docs) reached 94% render success and 85.7% visual similarity, slightly above GPT-4.1. — [deeplearn.org](https://deeplearn.org/arxiv/815516/training-and-agentic-inference-strategies-for-llm-based-manim-animation-generation). Community fine-tunes exist, e.g. Qwen2.5-Coder-7B-manim and nabin2004/qwen-Manimator-1. — [featherless](https://featherless.ai/models/Harish102005/Qwen2.5-Coder-7B-manim); [featherless](https://featherless.ai/models/nabin2004/qwen-Manimator-1-merged)
- Blender version drift: models call APIs removed in Blender 5.x, and bundled or live API lookup is the stated mitigation. — [StraySpark](https://www.strayspark.studio/blog/official-blender-mcp-server-comparison-2026)
- In TheoremExplainAgent (2025), RAG hurt the stronger models (o3-mini 93.8→82.1%, GPT-4o 55.0→45.8%) and helped the weaker ones (Claude 3.5 Sonnet 2.1→14.6%). — [arXiv HTML](https://arxiv.org/html/2502.19400)

### Inferences
- Failure modes by type, with the matching mitigation:
  - API hallucination and ManimGL/CE confusion → pinned version plus a forbidden-API list plus few-shot examples
  - LaTeX errors → pre-compile check or Text instead of MathTex
  - layout overlap and edge cropping → anchor grid or occupancy checks plus frame review
  - timing between beats → drive timing from voice word timestamps, not model-chosen `run_time`s
  - collisions along motion paths (not just in end frames) → sample several frames per animation, not one still
- For a local 27-32B Qwen model, expect weak zero-shot results. Qwen-2.5-Coder scored 0 on the ManiBench pilot, though the paper's "Qwen-2.5-Coder" size is unspecified. A tight harness (templates, renderer-in-the-loop, docs) closes most of the gap. This supports the plan in LESSONS §8 to use the local model as a sub-worker for well-specified shot functions.
- A custom pycairo engine has zero training-data exposure, so models will need the skill's own API reference and examples, which acts as RAG by construction. Manim, Remotion and HTML/CSS have the most prior exposure.

### Gaps
- There is no head-to-head published data on Claude Haiku/Sonnet/Opus (current generation) for Manim, Remotion or Blender in the same harness.
- No published numbers were found for Qwen3.x 27B-class dense models on animation code (the user's local model is "Qwen3.8-27B").
- No study was found that quantifies timing drift between narration and visuals.

## 4. Open-source end-to-end "text → narrated explainer" projects and narration sync

### Takeaway
Few open projects are fully local end to end. TheoremExplainAgent (Kokoro TTS plus Manim, LiteLLM) is the closest, and the Hermes `manim-video` skill is a lightweight agent-skill template. Sync approaches split into three. Per-scene or per-sentence durations (generate audio, then set waits/run_time) is the most common. Word-level Whisper timestamps are available through manim-voiceover's bookmarks or Remotion's whisper.cpp package. The third is explicit `run_time`s with audio added afterwards via ffmpeg (Hermes).

### Cited Findings
- manim-voiceover (latest PyPI 0.3.7) is a Manim plugin that lets you trigger animations at specific words, both for TTS and for recordings, "thanks to OpenAI Whisper". The listed TTS services are Azure (recommended), Coqui, gTTS and pyttsx3, plus a RecorderService for microphone recording. A source noted that it is temperamental on Python 3.13. — [GitHub](https://github.com/sueskind/manim-voiceover); [PyPI](https://pypi.org/project/manim-voiceover/); [nshipster](https://nshipster.com/manim/)
- TheoremExplainAgent uses local Kokoro TTS via a custom KokoroService (credited to kokoro-manim-voiceover, i.e. a manim-voiceover service). Its README does not state the sync method. — [GitHub](https://github.com/TIGER-AI-Lab/TheoremExplainAgent)
- Hermes manim-video: explicit `run_time`/`wait()` and `add_subcaption(duration=N)`, with voiceover and music muxed by ffmpeg; TTS is ElevenLabs or Qwen3-TTS. — [Hermes docs](https://hermes-agent.nousresearch.com/docs/user-guide/skills/bundled/creative/creative-manim-video)
- Remotion: local whisper.cpp token-level timestamps turned into captions JSON. — [Remotion docs](https://www.remotion.dev/docs/install-whisper-cpp/)
- DATAREEL's Video Critic explicitly checks narration alignment. — [arXiv](https://arxiv.org/pdf/2604.25220)
- No project found combines Ollama or a local LLM with local TTS and Manim out of the box; that needs custom wiring. Manim AI (peerlist) is cloud-only (OpenAI plus cloud rendering). — search summary; [peerlist](https://peerlist.io/itshp/project/manimai)

### Inferences
- The Initial Condition approach (Whisper word timings, cue specs like `"L27:end+0.3"`, pin slots) is more precise than most published systems, which mostly use per-scene durations. manim-voiceover bookmarks are the closest published equivalent and confirm that the pattern is portable to Manim.
- For a framework-agnostic skill, keep the timeline (word timings → cue resolution → timeline.json) separate from the renderer, so a Manim, Remotion/HyperFrames or pycairo backend can consume the same timeline.

### Gaps
- I did not confirm whether manim-voiceover has a local-TTS service, such as Kokoro, in the main package or only via forks like kokoro-manim-voiceover.
- No README of a project using per-word timing for visual beats (rather than captions) was read in full.

## 5. How systems evaluate quality, and a fair small benchmark

### Takeaway
Published evaluation mixes three things: (a) execution and render success, (b) VLM or LLM judges on keyframes and transcripts with rubric dimensions, and (c) small human studies or quizzes. VLM judges correlate poorly with humans on several dimensions, and HeyGen's trained pairwise judge (82% human agreement vs 75% for VLMs) is the strongest automated option but is not public. A fair 20-second benchmark should combine automatic checks, a rubric scored on a contact sheet plus sampled in-motion frames, and blind human pairwise preference, while tracking cost (tokens, time, human notes).

### Cited Findings
- TheoremExplainAgent had five dimensions: Accuracy & Depth and Logical Flow (GPT-4o on the SRT transcript), Visual Relevance and Element Layout (GPT-4o on keyframes), and Visual Consistency (Gemini 2.0 Flash on video chunks). These were combined by geometric mean on a 0-1 scale at temperature 0. Human validation (40 videos, 12 annotators) gave Spearman correlations of only 0.14 (accuracy), 0.72 (visual relevance), 0.16 (logical flow), 0.42 (layout) and 0.17 (consistency). — [arXiv HTML](https://arxiv.org/html/2502.19400)
- Code2Video used VLM-as-judge aesthetics with five sub-scores (EL, AT, LF, VC, AD) and TeachQuiz, in which a model made to "unlearn" a topic is quizzed after watching the video. It also tracked time and tokens. In a human study of 8 people per group, aesthetics and quiz correlated at r=0.971, and humans penalised brief occlusions that VLMs missed. — [arXiv HTML](https://arxiv.org/html/2510.01174)
- HeyGen used a trained pairwise preference judge giving P(A preferred) per axis, with 82% human alignment vs 75% for VLM judges (Gemini 3.5, GPT-5.5, order-swapped to offset position bias). Agreement rises with judge confidence: 98.8% when |P−0.5| ≥ 0.40. Rankings were round-robin Elo, and human examples used 5-rater votes. — [HeyGen Research](https://www.heygen.com/research/introducing-code2video-benchmark)
- ManiBench: executability (pass@1), version-conflict error rate, and keyword-heuristic alignment/coverage. The authors recommend frame-level comparison or VLM grading because the heuristics saturate. — [ManiBench HTML](https://arxiv.org/html/2603.13251v1)
- ManimTrainer: render success rate plus visual similarity to reference videos. — [deeplearn.org](https://deeplearn.org/arxiv/815516/training-and-agentic-inference-strategies-for-llm-based-manim-animation-generation)
- VLM evaluators of story imagery were unreliable in StoryAgent (older). — [arXiv](https://arxiv.org/pdf/2411.04925)

### Inferences
Proposed fair small benchmark ("20-second piece"), synthesized from the sources plus the LESSONS §5 checklist:
- **Inputs, fixed per run:** one brief (idea plus a 40-60 word script or 3-4 voice lines), pre-generated voice takes with word timings, a fixed asset budget (e.g. ≤3 Qwen-Image plates), a fixed framework version, and an identical skill/harness per arm. Arms: Claude Haiku/Sonnet/Opus, the local Qwen 27B, and local Qwen as sub-worker under Claude. Run 3 seeds per arm, since single runs are noisy and the frontier is tightly bunched.
- **Automatic gates:** renders without error; duration within ±0.5 s; every cue fires within ±100 ms of its word timestamp; no text or element outside safe margins; bounding-box overlap check from a layout/occupancy log (Code2Video-style); palette/loudness checks as in Initial Condition.
- **Rubric on a contact sheet plus 3 in-motion frames per animation** (HeyGen shows collisions occur mid-path): readability, composition/centering, proportion, transitions, timing to voice, leftovers/debug shapes, prompt intent. Score with a VLM judge but report it alongside human scores, given the weak correlations TEA found.
- **Human:** blind pairwise preference between arms, with at least 3 raters and order swapped, aggregated with Elo or Bradley-Terry.
- **Cost:** tokens, wall time, number of render-fix iterations, and number of human notes to reach "good" (the most decision-relevant metric for this user).

### Gaps
- HeyGen's judge model and dataset are not publicly available (judge details are "forthcoming").
- There is no published benchmark for narrated pieces of about 20 s with voice-synced timing; existing ones are long-form lectures (TEA, Code2Video) or silent 4-8 s motion beats (HeyGen).
- The MMMC (Code2Video) and TheoremExplainBench datasets are on HF/GitHub but were not inspected for reusable short items.
