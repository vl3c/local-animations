# Code-first 2D / motion-graphics frameworks for an AI agent (state as of 8 Oct 2026)

Scope: Manim CE, ManimGL, Motion Canvas, Revideo, Remotion, Theatre.js, Vizzu, p5.js/canvas + frame capture (CCapture, headless browser), plus 2026 entrants found: **HyperFrames (HeyGen)**, Lottie-generating agent tools (diffusionstudio/lottie, OmniLottie), Rive, Diffusion Studio core. Repo stats were pulled live from the GitHub API on 2026-10-08 (stars, last push, latest release, commit counts).

## 1. Language, headless/deterministic CLI rendering, Windows, speed, GPU

### Takeaway
Manim CE (Python, CLI-native, CPU Cairo by default) and Remotion / HyperFrames / Revideo (TypeScript/HTML rendered frame-by-frame in headless Chromium, then FFmpeg) all render headlessly and deterministically from the command line; Motion Canvas renders only from its browser editor according to its docs. GPU use is limited everywhere: Manim CE Cairo is CPU, ManimGL is OpenGL; browser-based tools can use the GPU for WebGL/CSS effects only when enabled (`--gl=angle` in Remotion), and frame capture/encoding is usually the bottleneck.

### Cited Findings
**Manim Community Edition (Python)**
- CLI renderer; v0.22.0 (released 2026-10-08) unified output under a single `--format` option: `auto` (MP4, or MOV for transparency), `mp4`, `mov`, `webm`, `gif`, `png` (last frame only), `png-sequence`, `none`; `-p` opens result, `-l/--live-preview` shows a live OpenGL window; "the OpenGL renderer now writes files by default, just like Cairo" — [Manim v0.22.0 release notes](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- v0.22.0 adds configurable encoding: `[video_encoder]` config, `--video-codec`, `--pixel-format`, `--encoder-option KEY=VALUE` (e.g. `--video-codec libx264 --encoder-option crf=18`) — [v0.22.0 notes](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- v0.21.0 (2026-08-10): "Speed up Cairo renderer by 2.2x on animation-heavy scenes"; encoder pipelining (`--max-inflight-encoders`, `--encoder-queue-size`) "reduced an encoding-heavy benchmark by 56%" — [Manim v0.21.0 release](https://github.com/ManimCommunity/manim/releases/tag/v0.21.0)
- Two renderers: Cairo (default, CPU) and OpenGL; recent fixes still target OpenGL crashes (`arrange_in_grid`, triangulation, `ThreeDScene.set_camera_orientation` with OpenGL, Oct 2026) — [v0.21.0 release](https://github.com/ManimCommunity/manim/releases/tag/v0.21.0); [commit log](https://github.com/ManimCommunity/manim/commits/main)
- Windows: the Manim FAQ documents the `manim` executable being shadowed when ManimGL is also installed; fix via `manimce` or `python -m manim` — [Manim CE FAQ](https://docs.manim.community/en/stable/faq/general.html)

**ManimGL (3b1b/manim, Python)**
- OpenGL-based engine "for explanatory math videos"; latest tagged release v1.7.2 (2024-12-13) but 100+ commits since Oct 2025; most recent commit 2026-09-09 "Add VideoMobject and Sprite (#2521)" — [3b1b/manim](https://github.com/3b1b/manim); [commits](https://github.com/3b1b/manim/commits)
- CLI is `manimgl`, imports `from manimlib import *` — [ManiBench prompt guide (community)](https://huggingface.co/datasets/nabin2004/ManiBench/blob/main/ManiBench_Prompt_Engineering_Guide.md); [Manim CE FAQ](https://docs.manim.community/en/stable/faq/general.html)

**Remotion (TypeScript/React)**
- Renders with headless Chrome frame-by-frame; CLI `npx remotion render` with `--frames` (comma list → image sequence; ranges since v4.0.502 concatenate into one video), `--sequence`, `--image-format`, `--image-sequence-pattern`, `--concurrency`, `--gl`, `--hardware-acceleration` (since v4.0.228; disables `--crf`, use `--video-bitrate`) — [Remotion CLI render docs](https://www.remotion.dev/docs/cli/render)
- Windows-specific note: inline JSON `--props` breaks in Windows shells ("removes the `\"` character, use a file name instead") — [Remotion CLI render docs](https://www.remotion.dev/docs/cli/render)
- GPU: "By default in many cases, the GPU is disabled in headless mode, which can lead to a significant slowdown"; GPU helps WebGL (Three.js, Skia, P5.js, Mapbox), video decoding, box-shadow/text-shadow/gradients/filters/transforms, many 2D canvas ops — [Remotion GPU docs](https://www.remotion.dev/docs/gpu)
- `--gl` options: `null`, `angle`, `egl`, `swiftshader`, `vulkan`, `angle-egl`, `swangle`; Remotion 4.0 default `null` ("lets Chrome decide"); "From Remotion 5.0, angle is the default renderer"; for desktop WebGL/Three.js "angle is recommended"; warning: "Memory leaks are a known problem with angle" — split long renders — [Remotion gl-options](https://www.remotion.dev/docs/gl-options)

**HyperFrames (HeyGen; HTML/CSS/JS)**
- "Write HTML. Render video. Built for agents." Open-source framework turning HTML, CSS, media and seekable animations into deterministic MP4; CLI `npx hyperframes init / preview / render`; requires Node.js 22+ and FFmpeg — [HyperFrames README](https://github.com/heygen-com/hyperframes)
- Renderer pauses and seeks the animation to each frame before capture; GSAP, Web Animations, Lottie and other runtimes "render deterministically" because it drives them rather than reading a clock; requires paused timeline, no wall-clock reads, no unseeded randomness, and violations "fail quietly" — [HyperFrames vs Remotion guide](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)
- Supported runtime adapters: GSAP, Lottie, Three.js, Anime.js, CSS, WAAPI, TypeGPU — [README](https://github.com/heygen-com/hyperframes)
- Platform binaries listed for macOS (arm64, x64), Windows (x64, ia32), Linux; "on macOS and Windows, multi-worker capture is screenshot-based" (Chrome BeginFrame capture is the Linux path); changelog has Windows chrome-headless-shell crash hints (`HYPERFRAMES_BROWSER_PATH`) — HyperFrames docs/changelog in repo [`docs/`](https://github.com/heygen-com/hyperframes/tree/main/docs)
- Docs mention a render mode that "can use the computer's browser GPU" for HTML+shader scenes, and a `--gpu` (hardware encoder) flag — [HyperFrames docs](https://github.com/heygen-com/hyperframes/tree/main/docs)

**Revideo (TypeScript; fork lineage of Motion Canvas)**
- Repo now at midrender/revideo ("engine behind Midrender"); scenes are TypeScript generator functions (`makeScene2D`, `yield* waitFor`); headless rendering via `renderVideo()` or a render endpoint via CLI; "runs anywhere Node and a headless browser run"; parallelized rendering across workers — [Revideo README](https://github.com/midrender/revideo)

**Motion Canvas (TypeScript)**
- Docs describe only editor-based rendering: "Clicking the `RENDER` button will initialize rendering", output to `/output`; default exporter is image sequence, optional FFmpeg exporter — [Motion Canvas rendering docs](https://motion-canvas.io/docs/rendering)

**p5.js / canvas + frame capture**
- p5.js v2.3.4 (2026-09-25), actively developed — [processing/p5.js](https://github.com/processing/p5.js)
- CCapture.js 2.0.0 (2026-07-27) is a ground-up rewrite: WebCodecs MP4 (H.264/AV1) and WebM, "hardware-accelerated", GPU (WebGL2) or CPU motion blur, `TimeWarp` (clock override) + `FrameWrap` (capture/encode); breaking changes vs 1.x (default format now mp4, `save()` downloads, ffmpegserver removed) — [CCapture v2.0.0 release](https://github.com/spite/ccapture.js/releases/tag/v2.0.0)

**Others**
- Theatre.js: last public commit 2024-04-11 ("Add the 1.0 notice"); development "temporarily moved ... to a private repo" — [theatre-js/theatre README](https://github.com/theatre-js/theatre)
- Vizzu: C++/WASM chart-animation library, v0.18.0 (2026-04-20) — [vizzu-lib releases](https://github.com/vizzuhq/vizzu-lib/releases)
- Diffusion Studio core: "browser based video compositing engine powered by WebCodecs", MPL-2.0, last push 2025-11 — [diffusionstudio/core](https://github.com/diffusionstudio/core)

### Inferences
- For a Windows agent loop, Manim CE and Remotion/HyperFrames/Revideo are the ones that run fully from a CLI. Motion Canvas would need a community or custom headless wrapper (e.g. Puppeteer driving the editor), which adds risk.
- On Windows, HyperFrames uses screenshot-based capture, not the BeginFrame path, so Windows renders are probably slower than Linux/WSL ones. WSL2 is a plausible way to get the faster path, but nobody has benchmarked it.
- An RTX 5080 mostly helps the browser tools (WebGL/shaders, `--gl=angle`, NVENC-style hardware encoding) and ManimGL. Manim CE's default Cairo path is CPU-bound, so the GPU barely matters there.

### Gaps
- I found no recent, comparable render-speed benchmarks (s/frame at 1080p) for any of these frameworks, and no Windows-specific benchmark for Remotion versus HyperFrames.
- I could not confirm whether Motion Canvas has an official headless CLI. Its docs page describes only the editor.
- I did not verify how deterministic arbitrary p5.js sketches are under Puppeteer/Playwright capture.

## 2. Maintenance status, maturity, API stability (Oct 2026)

### Takeaway
The most active projects are Remotion (near-daily 4.0.x patch releases, 62.5k stars), HyperFrames (59k stars in 7 months, several releases a day, pre-1.0) and Manim CE (41k stars, minor releases every ~2-6 months, each with breaking changes). ManimGL's code is active but it has no release since Dec 2024. Motion Canvas is effectively dormant (no release since Feb 2025). Revideo is low-activity but alive. Theatre.js has been publicly frozen since 2024.

### Cited Findings
GitHub API snapshot, 2026-10-08:

| Project | Stars | Latest release | Last push | Commits since Apr 2026 | Licence |
|---|---|---|---|---|---|
| ManimCommunity/manim | 41,356 | v0.22.0 (2026-10-08); v0.21.0 (2026-08-10); v0.20.0 (2026-02-20) | 2026-10-08 | 100+ | MIT |
| 3b1b/manim (ManimGL) | 94,763 | v1.7.2 (2024-12-13) | 2026-09-09 | 100+ since Oct 2025 | MIT |
| remotion-dev/remotion | 62,518 | v4.0.534 (2026-10-07); tag v4.1.0-alpha2 | 2026-10-08 | 100+ | Remotion License (source-available) |
| heygen-com/hyperframes | 59,040 (created 2026-03-10) | v0.8.142 (2026-10-08) | 2026-10-08 | 100+ | Apache-2.0 |
| motion-canvas/motion-canvas | 19,255 | v3.18.0-alpha.0 (2025-02-16); v3.17.2 (2024-12-14) | 2026-07-02 (docs domain only) | 1 | MIT |
| midrender/revideo (ex redotvideo) | 4,091 | v0.11.0 (2026-07-10) | 2026-07-15 | 19 since Oct 2025 | MIT |
| theatre-js/theatre | 12,734 | none public since 2024 | 2024-08-14 | 0 | Apache-2.0 |
| vizzuhq/vizzu-lib | 2,039 | v0.18.0 (2026-04-20) | 2026-04-20 | 3 | Apache-2.0 |
| processing/p5.js | 24,101 | v2.3.4 (2026-09-25) | 2026-10-08 | active | LGPL-2.1 |
| spite/ccapture.js | 3,772 | v2.0.0 (2026-07-27) | 2026-07-27 | 8 | MIT |
| diffusionstudio/lottie | 5,550 | n/a | 2026-07-25 | n/a | MIT |
| airbnb/lottie-web | 32,148 | n/a | 2025-09-01 | n/a | MIT |

Sources: [ManimCommunity/manim](https://github.com/ManimCommunity/manim), [3b1b/manim](https://github.com/3b1b/manim), [remotion-dev/remotion](https://github.com/remotion-dev/remotion), [heygen-com/hyperframes](https://github.com/heygen-com/hyperframes), [motion-canvas/motion-canvas](https://github.com/motion-canvas/motion-canvas), [midrender/revideo](https://github.com/midrender/revideo), [theatre-js/theatre](https://github.com/theatre-js/theatre), [vizzu-lib](https://github.com/vizzuhq/vizzu-lib), [p5.js](https://github.com/processing/p5.js), [ccapture.js](https://github.com/spite/ccapture.js), [diffusionstudio/lottie](https://github.com/diffusionstudio/lottie), [lottie-web](https://github.com/airbnb/lottie-web)

**Breaking-change history (API stability)**
- Manim CE v0.22.0 breaking: removed `--write_to_movie`, `-g/--save_pngs`, `-i/--save_as_gif`, `--force_window`, `--custom_folders`, `--flush_cache` (now `manim cache clear`); new `Manager` object now owns the render lifecycle (`Scene.play`, `add_sound`, `add_subcaption` delegate to `scene.manager`). Plain scenes "need no changes" — [v0.22.0 notes](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- Manim CE v0.21.0 breaking: Cairo pixel-conversion changes, optional Typst text rendering, a clear error when rendered glyphs do not match input — [v0.21.0](https://github.com/ManimCommunity/manim/releases/tag/v0.21.0); v0.20.0 breaking: `ImageMobject` resampling algorithms `lanczos/antialias/box/hamming` removed — [v0.20.0](https://github.com/ManimCommunity/manim/releases/tag/v0.20.0)
- Remotion: still on 4.x. Remotion 5.0 is being prepared in an open PR with breaking changes and a WIP migration guide (`/docs/5-0-migration`) — [PR #3750](https://github.com/remotion-dev/remotion/pull/3750)
- Remotion MCP is deprecated; the hosted MCP "will shut down no earlier than August 31, 2026" — [Remotion MCP docs](https://www.remotion.dev/docs/ai/mcp)
- Motion Canvas: recent issues include "motion-canvas 3.17.2 depends on an unsupported dependency and an old dependency" (Sept 2026) and an open "modernize build/test/docs toolchain" PR (Sept 2026) — [motion-canvas issues](https://github.com/motion-canvas/motion-canvas/issues)
- CCapture 2.0 broke the 1.x API; 1.x remains on npm `ccapture.js@1`, and unversioned CDN embeds of the old bundle will 404 — [CCapture v2.0.0](https://github.com/spite/ccapture.js/releases/tag/v2.0.0)
- Theatre.js: "Theatre.js 1.0 is around the corner. We have _temporarily_ moved development to a private repo" (notice dated April 2024, still unchanged) — [Theatre.js README](https://github.com/theatre-js/theatre)

### Inferences
- HyperFrames is very popular but young: it is pre-1.0, ships several releases a day and its rules change fast. Models trained before 2026 will barely know it, so an agent depends on its skills/docs, which pin current behaviour. Expect churn.
- Manim CE breaks CLI flags and internals about every minor release, but the core scene API (`Scene.construct`, `self.play`, mobjects) has stayed stable. Old flags in LLM-written commands (e.g. `-g`, `--save_as_gif`) will now fail on v0.22.
- Motion Canvas is a poor bet for new work in 2026. Revideo is its maintained descendant, but it runs at low velocity with a single corporate backer (Midrender).

### Gaps
- I did not compute npm download trends.
- The Remotion 5.0 release date is unknown, because the PR is still open.

## 3. LLM knowledge and agent integrations

### Takeaway
Remotion and HyperFrames have first-party agent tooling: Agent Skills, Claude Code plugins and Markdown docs. Manim has the most published research on LLM code generation, but it suffers from systematic Manim CE vs ManimGL vs pre-0.18 API confusion, and its agent tooling is all community-made. Revideo explicitly targets LLM authoring but has no official skills. Motion Canvas, Theatre.js and Vizzu have no LLM-specific tooling that I found.

### Cited Findings
**Remotion**
- Official Agent Skills: `npx skills add remotion-dev/skills` (or `npx remotion skills add`). The skills are `/remotion-best-practices`, `/remotion-create`, `/remotion-markup`, `/remotion-studio`, `/remotion-render` (video or still), `/remotion-maps`, `/remotion-captions`, `/remotion-saas`, `/remotion-interactivity` and `/remotion-docs` — [Remotion Agent Skills](https://www.remotion.dev/docs/ai/skills); the remotion-dev/skills repo has 4,904 stars — [GitHub](https://github.com/remotion-dev/skills)
- Official Claude Code plugin: `claude plugin marketplace add remotion-dev/claude-code-plugin` then `claude plugin install remotion@remotion`. There are also Codex, Cursor, Kimi Code and GitHub Copilot plugins — [Remotion Claude Code plugin docs](https://www.remotion.dev/docs/ai/claude-code-plugin)
- Docs are AI-ready: appending `.md` to any doc URL returns Markdown, and an `Accept: text/markdown` header also works — [Remotion AI docs](https://www.remotion.dev/docs/ai/)
- The Remotion MCP is deprecated in favour of `/remotion-docs`, partly because "agents do not invoke them reliably" — [Remotion MCP (deprecated)](https://www.remotion.dev/docs/ai/mcp)
- Officially endorsed workflow: `npx create-video --yes --blank my-video`, install the skills, `npm run dev`, then prompt Claude Code, Codex, Kimi or OpenCode — [Prompting videos with coding agents](https://www.remotion.dev/docs/ai/coding-agents)

**HyperFrames**
- Claude Code plugin (`claude plugin marketplace add heygen-com/hyperframes`; `claude plugin install hyperframes@hyperframes`) with 21 skills. They include a router `/hyperframes`, `/faceless-explainer` ("Explaining a topic / concept from arbitrary text ... typography / abstract / diagram / data-viz"), `/general-video`, `/motion-graphics`, `/music-to-video`, `/hyperframes-core`, `/hyperframes-animation`, `/hyperframes-cli`, `/hyperframes-audio`, `/media-use` and `/remotion-to-hyperframes` — [HyperFrames README](https://github.com/heygen-com/hyperframes)
- The skills "teach agents the HyperFrames production loop: plan the video, write valid HTML, wire seekable animations, add media, lint, preview, and render" — [README](https://github.com/heygen-com/hyperframes)
- The `remotion-to-hyperframes` skill converts "about 80%" of a Remotion project mechanically, flags unsupported patterns (`useState` logic) and checks the port by comparing rendered frames — [HyperFrames vs Remotion](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)

**Manim**
- TheoremExplainAgent (Feb 2025) generates theorem-explanation videos of 5+ minutes with Manim. Its best agent (o3-mini) had a 93.8% success rate, but "most of the videos produced exhibit minor issues with visual element layout" — [arXiv 2502.19400](https://arxiv.org/abs/2502.19400)
- Code2Video (Show Lab, arXiv 2510.01174; ICML 2026) uses Planner → Coder (scope-guided auto-fix) → Critic (VLM layout refinement). It reports a 40% improvement over direct code generation — [OpenCV summary](https://opencv.org/code2video/); [ICML 2026 poster](https://icml.cc/virtual/2026/poster/65050); repo with 2,102 stars, [showlab/Code2Video](https://github.com/showlab/Code2Video)
- SGA (July 2026) intercepts LLM-generated Manim code, partially executes it to extract scene graphs and fixes spatial conflicts. It reports 73.11 on MMMC-Code with Code2Video + GPT-5.1 (+16.1%) — [alphaXiv 2607.18116](https://www.alphaxiv.org/abs/2607.18116)
- Known LLM failure modes: ManimGL or pre-0.18 names (`ShowCreation`, `TextMobject`, `GraphScene`, `Code(code=...)`), non-raw LaTeX strings, off-frame text, overlapping labels, wrong video length — [manimkit (PyPI)](https://pypi.org/project/manimkit/); ManiBench cites 145 documented ManimGL→CE incompatibilities — [ManiBench guide](https://huggingface.co/datasets/nabin2004/ManiBench/blob/main/ManiBench_Prompt_Engineering_Guide.md)
- CE uses `from manim import *`, `Create()`, `MathTex()`; GL uses `from manimlib import *`, `ShowCreation()`, `Tex()` — [ManiBench guide](https://huggingface.co/datasets/nabin2004/ManiBench/blob/main/ManiBench_Prompt_Engineering_Guide.md); [Manim CE FAQ](https://docs.manim.community/en/stable/faq/general.html)
- Community agent tooling: adithya-s-k/manim_skill (1,147 stars; separate `manimce-best-practices` and `manimgl-best-practices` skills that load based on the import) — [manim_skill](https://github.com/adithya-s-k/manim_skill); manimkit linter (flags GL or removed APIs and undefined names, with a render-and-inspect loop) — [manimkit](https://pypi.org/project/manimkit/); abhiemj/manim-mcp-server (647 stars, last push May 2025, stale) — [GitHub](https://github.com/abhiemj/manim-mcp-server)

**Revideo / Motion Canvas / others**
- Revideo README: "A scene is plain TypeScript, so Claude or Codex can produce one from a prompt." No official skills found — [Revideo README](https://github.com/midrender/revideo)
- Lottie: diffusionstudio/lottie ("Generate production-ready Lottie animations with Claude Code or Codex", 5,550 stars, MIT); the agent writes `public/lottie.json` with hot reload — [diffusionstudio/lottie](https://github.com/diffusionstudio/lottie); [pyshine overview](https://pyshine.com/DiffusionStudio-Lottie-AI-Generated-Lottie-Animations-Claude-Code/). OmniLottie is a CVPR 2026 research model that generates Lottie JSON (798 stars, Apache-2.0) — [gittrend](https://gittrend.io/repo/OpenVGLab/OmniLottie). LottieFiles has a Codex + Lottie Creator MCP tutorial (Aug 2026) — [LottieFiles tutorial](https://lottiefiles.com/de/tutorials/lottie-creator/openai-codex-tutorial-automatically-create-and-edit-lottie-animations-with-ai-xElAkr4mFbS)
- Rive: animations are authored in the proprietary Rive editor, and runtime state machines are driven through data-binding inputs. I found no AI-driven Rive authoring workflow — [Rive state machines docs](https://rive.app/docs/runtimes/react/state-machines); runtime is MIT — [rive-runtime](https://github.com/rive-app/rive-runtime)

### Inferences
- Training-data exposure is probably highest for Manim (ManimGL has 95k stars and years of 3b1b code), then Remotion and p5.js. This is likely why both CE/GL confusion and old-API errors are common. For Manim, pin the version, add the CE skill and a linter, and render-check every scene.
- HyperFrames code is mostly plain HTML/CSS/GSAP, which LLMs (including a local ~27B model) know well, even though the framework's own contract (`data-*` timing attributes, `class="clip"`) is new and must come from its skills.
- Plain-HTML/GSAP or React output is likely easier for a ~27B local model than Manim's large mobject API. This is untested.

### Gaps
- I found no head-to-head study comparing LLM success rates across Manim, Remotion, Motion Canvas and HyperFrames.
- I found no published evaluation of local ~27B models writing any of these frameworks.
- I did not check whether Manim CE publishes an official llms.txt.

## 4. Audio and narration sync, captions

### Takeaway
Manim CE + manim-voiceover is the most mature narration-first option: the voiceover block drives animation timing and supports per-word bookmarks via Whisper. HyperFrames bundles local TTS (Kokoro), local transcription (Whisper/Parakeet), captions and an audio mixer. Remotion has a full captions package and audio export. Motion Canvas and Revideo support audio tracks with sync. With p5 or canvas you build it yourself: CCapture 2 can now mux audio frame-accurately.

### Cited Findings
- Manim CE: `Scene.add_sound` and `Scene.add_subcaption` exist; in v0.22 they delegate to the `Manager` — [v0.22.0 notes](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- manim-voiceover (ManimCommunity, v0.4.0 2026-06-14, 317 stars, MIT) adds voiceovers "directly in Python", microphone recording during render, "Per-word timing of animations, i.e. trigger animations at specific words ... thanks to OpenAI Whisper". Supported TTS: Gemini TTS (recommended), Azure, gTTS, pyttsx3 — [manim-voiceover README](https://github.com/ManimCommunity/manim-voiceover)
- HyperFrames: `npx hyperframes tts` "is the local Kokoro CLI"; music can use MusicGen; transcription engine `auto` (Parakeet if installed, otherwise whisper); `/embedded-captions` skill; `/hyperframes-audio` covers voiceover ducking ("voiceover carve"), EQ/compressor/limiter and automation; `/music-to-video` does beat sync — [HyperFrames README](https://github.com/heygen-com/hyperframes); [HyperFrames docs](https://github.com/heygen-com/hyperframes/tree/main/docs)
- Remotion: the captions package has docs for transcribing, importing, exporting, `parseSrt`, `serializeSrt`, `createTikTokStyleCaptions` and `ensureMaxCharactersPerLine`; captions use a `Caption` JSON format, and `useDelayRender()` holds the render until the captions load — [Remotion captions docs](https://www.remotion.dev/docs/captions/displaying)
- Remotion CLI audio flags: `--audio-codec`, `--audio-bitrate`, `--sample-rate`, `--separate-audio-to`; `--codec` can output `mp3`/`aac`/`wav` — [Remotion CLI render](https://www.remotion.dev/docs/cli/render)
- Revideo: "`<Video/>` and `<Audio/>` components with audio export and frame-accurate synchronization" — [Revideo README](https://github.com/midrender/revideo)
- Motion Canvas: described as designed "to create informative vector animations and synchronize them with voice-overs"; an audio offset setting appears in render settings "only ... if you've set up audio" — [Motion Canvas README](https://github.com/motion-canvas/motion-canvas); [rendering docs](https://motion-canvas.io/docs/rendering)
- CCapture 2.0: "Frame-accurate audio: offline analysis (`renderAudioFrames`) + AudioBuffer muxing (AAC/Opus)" — [CCapture v2.0.0](https://github.com/spite/ccapture.js/releases/tag/v2.0.0)

### Inferences
- With local TTS that already produces word timestamps, any framework can be driven from a JSON timing file: Manim via `self.wait()` durations, Remotion via frame offsets in `<Sequence>`, HyperFrames via `data-*` timing attributes. Manim-voiceover's built-in TTS list is cloud-oriented except pyttsx3, so a local TTS would need a custom service class. Its plugin architecture suggests this is possible, but I did not verify it.
- From prior knowledge, not re-verified in this pass: Remotion sets composition duration dynamically via `calculateMetadata`, and Manim CE writes `.srt` subtitle files from `add_subcaption`.

### Gaps
- I did not verify whether Remotion's transcription helpers (e.g. a whisper.cpp installer) run fully offline on Windows.
- I did not verify whether manim-voiceover supports custom or local TTS engines.

## 5. Single-frame stills and partial re-renders (agent review loop)

### Takeaway
All the CLI-native tools support stills or frame subsets: Manim (`--format png`, `png-sequence`, plus per-animation partial-movie caching), Remotion (`remotion still`, `--frames` lists or ranges), HyperFrames (`snapshot --at 0,3,8`, `lint`, `check`). Motion Canvas supports render ranges and snapshots only in the editor.

### Cited Findings
- Manim CE: `--format png` renders the last frame only; `png-sequence` renders every frame; `--format none` evaluates the scene without writing media, which makes a fast syntax/runtime check; `manim cache clear` manages the partial-movie cache — [v0.22.0 notes](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- Remotion: `--frames=0,30,60` renders specific frames as an image sequence; ranges (v4.0.502+) concatenate into one video; the `/remotion-render` skill can "Invoke a render into a video or a still" — [CLI render](https://www.remotion.dev/docs/cli/render); [Agent Skills](https://www.remotion.dev/docs/ai/skills)
- HyperFrames: `npx hyperframes snapshot --at 0,3,8`; CLI dev loop `init`, `lint`, `check`, `snapshot`, `preview`, `render`, `doctor` — [HyperFrames docs](https://github.com/heygen-com/hyperframes/tree/main/docs); [README](https://github.com/heygen-com/hyperframes)
- Motion Canvas: a render range "is the span of frames that will be rendered"; per-frame snapshots are saved to `/still` from the editor — [Motion Canvas rendering](https://motion-canvas.io/docs/rendering)
- Code2Video's Critic uses a VLM over rendered frames to refine layout, which mirrors a stills/contact-sheet review loop — [OpenCV Code2Video summary](https://opencv.org/code2video/)

### Inferences
- The stills → contact sheet (ffmpeg tile) → fix loop is natively supported by Manim CE, Remotion and HyperFrames. HyperFrames' `lint`/`check` add a static layer before rendering.
- Manim's per-animation cache makes re-rendering an edited scene cheap, but it cannot seek to an arbitrary time inside a scene: earlier animations must still be evaluated. Remotion and HyperFrames can seek any frame independently.

### Gaps
- From prior knowledge, not re-verified: Manim CE's `-n/--from_animation_number` option for animation subranges, and `npx remotion still --frame=N`.

## 6. Visual quality ceiling and suited styles

### Takeaway
Manim is the best fit for mathematical and diagrammatic vector explainers (LaTeX/Typst typesetting), but it is weak for photographic or atmospheric work. Browser-based tools (Remotion, HyperFrames, Revideo, p5) have the highest ceiling for mixed media, typography, CSS/SVG effects, shaders/WebGL/Three.js, Lottie and colour grading. Vizzu covers only animated charts. Rive and Lottie suit character or UI animation, but authoring them is editor-centric or JSON-centric.

### Cited Findings
- Manim CE added first-class Typst text/markup rendering (optional) in v0.21 and crisper small-font text in v0.22 — [v0.21.0](https://github.com/ManimCommunity/manim/releases/tag/v0.21.0); [v0.22.0](https://github.com/ManimCommunity/manim/releases/tag/v0.22.0)
- TheoremExplainAgent found layout problems in most generated Manim videos — [arXiv 2502.19400](https://arxiv.org/abs/2502.19400)
- HyperFrames: data visualisations, chart races, maps, kinetic captions, shader transitions, LUT/curves colour grading in Studio, Three.js and TypeGPU adapters, a registry or catalog of blocks (e.g. a data-chart block) — [README](https://github.com/heygen-com/hyperframes); [HyperFrames intro](https://hyperframes.heygen.com/introduction)
- Remotion GPU-accelerated content includes Three.js, Skia, P5.js and Mapbox WebGL; the `/remotion-maps` skill covers Mapbox, MapLibre and CesiumJS 3D flyovers — [Remotion GPU](https://www.remotion.dev/docs/gpu); [Remotion skills](https://www.remotion.dev/docs/ai/skills)
- Revideo example: a 3D Rubik's cube with a custom `draw()` orthographic projection, which shows that custom canvas drawing is possible — [Revideo README](https://github.com/midrender/revideo)
- Vizzu is a "Library for animated data visualizations and data stories" — [vizzu-lib](https://github.com/vizzuhq/vizzu-lib)
- Theatre.js targets "high-fidelity motion graphics", mainly animating THREE.js objects, and is used both programmatically and visually — [Theatre.js README](https://github.com/theatre-js/theatre)

### Inferences
- For painterly or atmospheric films built on AI-generated raster plates, browser engines are stronger: CSS filters and blend modes, WebGL shaders and grading are all available. Manim can show images (`ImageMobject`) but has no compositing or blend-mode pipeline.
- Character animation is weak in all of these code-first tools. Lottie (via agent tools such as diffusionstudio/lottie) or Three.js inside HyperFrames or Remotion are the realistic code-driven routes.

### Gaps
- I found no systematic visual-quality comparison.

## 7. Licensing (Remotion company licence, Revideo, others)

### Takeaway
Remotion is source-available, not OSS. It is free for individuals, for-profit organisations of up to 3 people, non-profits and evaluation. Larger for-profit organisations pay $25/month per person writing Remotion code ("Creators") or $0.01/render with a $100/month minimum ("Automators"). Remotion 5.0 will count contractors toward team size. Everything else in scope is permissive OSS: Revideo MIT, Manim MIT, HyperFrames Apache-2.0, Motion Canvas MIT, p5.js LGPL-2.1, Theatre.js Apache-2.0, Vizzu Apache-2.0, Diffusion Studio core MPL-2.0.

### Cited Findings
- Remotion Free License eligibility: "an individual", "a for-profit organization with up to 3 employees", "a non-profit or not-for-profit organization", or someone "evaluating whether Remotion is a good fit". Free use is allowed "non-commercially or commercially for the purpose of creating videos and images". Disallowed: selling or relicensing "your own derivate of Remotion" — [Remotion LICENSE.md](https://github.com/remotion-dev/remotion/blob/main/LICENSE.md)
- Pricing: "Remotion for Creators ... costs $25/month per person who writes Remotion code themselves or using agentic coding tools"; "Remotion for Automators ... costs $0.01 per render, with a minimum spend of $100/month"; "a combined minimum spend of $100 per month applies"; there is no functional difference between the free and company licences; single-person incorporated companies qualify for free use if headcount ≤ 3; free-licence users may run automations — [Remotion License FAQ](https://www.remotion.dev/docs/license/faq)
- Remotion 5.0 licence (open PR): "Contractors also count towards team size", and the company licence will be bound to new terms and conditions — [PR #3750](https://github.com/remotion-dev/remotion/pull/3750)
- The HyperFrames comparison emphasises Apache 2.0 ("no seat count and no license review") versus Remotion's free licence for teams "up to three people, paid above that" — [HyperFrames vs Remotion](https://hyperframes.heygen.com/guides/hyperframes-vs-remotion)
- Revideo: MIT. Telemetry anonymously counts renders via PostHog and is disabled with `DISABLE_TELEMETRY=true` — [Revideo README](https://github.com/midrender/revideo)
- Licence SPDX from GitHub: Manim CE MIT, ManimGL MIT, Motion Canvas MIT, HyperFrames Apache-2.0, Theatre.js Apache-2.0, Vizzu Apache-2.0, p5.js LGPL-2.1, CCapture MIT, diffusionstudio/lottie MIT, Diffusion Studio core MPL-2.0, rive-runtime MIT — GitHub API, see repos in section 2

### Inferences
- An individual making films (even commercially) is on Remotion's Free License today. This changes if the work moves into a company with more than 3 people including contractors (under 5.0 terms).

### Gaps
- I did not fetch Enterprise pricing tiers (the remotion.pro pricing page was not reachable; the docs pricing page is a JS component).

## 8. Compositing raster images and video (AI plates, generated clips)

### Takeaway
Browser-based engines (Remotion, HyperFrames, Revideo) natively composite images, video clips and audio with CSS/WebGL effects, so they are the strongest fit for AI-generated plates and clips. Manim CE supports images (`ImageMobject`) but has weak video support. ManimGL only gained `VideoMobject` in Sept 2026.

### Cited Findings
- Revideo: `<Video/>` and `<Audio/>` components with frame-accurate sync — [Revideo README](https://github.com/midrender/revideo)
- HyperFrames: "framework-owned media playback", a background video in the quickstart example prompt, `/talking-head-recut` overlays on existing footage, HDR handling, colour grading with LUTs — [HyperFrames README](https://github.com/heygen-com/hyperframes); [HyperFrames docs](https://github.com/heygen-com/hyperframes/tree/main/docs)
- Remotion: GPU accelerates video decoding in renders when enabled; the gl-options docs warn about angle memory leaks on long renders — [Remotion GPU](https://www.remotion.dev/docs/gpu); [gl-options](https://www.remotion.dev/docs/gl-options)
- ManimGL added `VideoMobject` and `Sprite` on 2026-09-09 (not in any tagged release) — [3b1b/manim commits](https://github.com/3b1b/manim/commits)
- Manim CE `ImageMobject` exists; v0.20 changed its 3D rotation/flipping and removed some resampling filters — [v0.20.0](https://github.com/ManimCommunity/manim/releases/tag/v0.20.0)
- CCapture 2.0 supports frame-stepped `<video>`/`<audio>` capture in canvas pipelines — [CCapture v2.0.0](https://github.com/spite/ccapture.js/releases/tag/v2.0.0)

### Inferences
- For a pipeline with AI-generated background plates and video clips plus vector overlays and narration, Remotion or HyperFrames are the most direct choices. Manim works best for vector or diagram layers that are rendered with transparency (`--format mov`) and composited elsewhere, e.g. in FFmpeg or in a browser engine.

### Gaps
- I did not verify whether Manim CE has a native video mobject in v0.22. I found none in the release notes I read.
