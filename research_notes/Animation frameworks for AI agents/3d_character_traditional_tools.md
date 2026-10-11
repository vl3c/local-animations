# 3D, character and traditional 2D animation tools an AI agent can drive from code (state as of October 2026)

Scope: Blender (bpy, `blender -b`, Eevee/Cycles, Grease Pencil v3, VSE), Synfig, OpenToonz, Lottie (python-lottie, glaxnimate, rlottie, ThorVG, lottie-web), MoviePy v2, the custom pycairo + numpy + OpenCV + ffmpeg stack from "Initial Condition", and other 2025-2026 options (Godot Movie Maker, three.js headless capture, Spine CLI, HyperFrames). Use case: an agent writes code from a script, renders a narrated 20 s to 7 min film at 1080p 24-30 fps offline on Windows 11 with an RTX 5080 (16 GB), reviews stills and contact sheets, and iterates.

Research was done on 2026-10-08 with web search and fetches of primary docs where possible. Items marked "(prior knowledge, not re-verified)" come from the researcher's background knowledge and should be checked before they go into the report as fact.

Quick fit matrix (researcher's synthesis of the findings below, not a sourced table):

| Tool | Headless CLI on Windows | LLM API familiarity | Churn risk | Audio in tool | Best styles | License |
|---|---|---|---|---|---|---|
| Blender 5.2 LTS (bpy) | Yes (`blender -b ... -P script.py`), Eevee/Cycles on GPU | Very high, but much of it is for 2.8-4.x | High (4.3, 4.4, 5.0, 5.1 all broke APIs) | Yes, VSE sound strips, FFmpeg mux | 3D, rigged characters, cut-out, GP hand-drawn, atmospheric | GPL (prior knowledge) |
| Synfig 1.4.5 / 1.5.5 dev | Yes (`synfig` CLI, single-frame `--time`) | Low (.sif XML rarely seen) | Low (slow project) | Weak (gap) | Vector cut-out, bone rigs, tweened 2D | GPL (prior knowledge) |
| OpenToonz 1.8.0 | Partial (batch render, tconverter; scripting limited) | Very low | Low | Scene sound, "Fast Render to MP4" | Hand-drawn/traditional, cel, screentone | BSD-style (prior knowledge) |
| Lottie (python-lottie / ThorVG / lottie-web) | Yes (python-lottie MP4 export; puppeteer-lottie) | Medium (JSON schema known, terse keys error-prone) | Low for format | None in format | Flat motion graphics, UI-style, icons | python-lottie AGPLv3; ThorVG MIT |
| MoviePy 2.2.1 | Yes (pure Python) | High, but mostly v1 code | v2 broke API in Nov 2024 | Yes (AudioFileClip, CompositeAudioClip) | Compositing, titles, slideshows | MIT |
| pycairo+numpy+OpenCV+ffmpeg (own stack) | Yes | High for each library | Very low | Via ffmpeg/own mixer | Stylized vector + plates, procedural FX | LGPL/MPL (pycairo), BSD/Apache (others) (prior knowledge) |
| Godot 4 Movie Maker | Yes (`--write-movie`, `--fixed-fps`) | Medium (GDScript 3 vs 4 confusion likely) | Medium | Yes (records game audio into AVI) | Real-time 2D/3D, rigs via Skeleton2D | MIT (prior knowledge) |
| three.js + headless Chrome | Yes (puppeteer/Node) | Very high | Medium | None (mux with ffmpeg) | Real-time 3D, stylized shaders | MIT (prior knowledge) |
| Spine (CLI) | Needs OpenGL + window system | Low for project files | Low | No | Skeletal 2D cut-out characters | Proprietary editor + runtime license |

## Headless/scriptable rendering from the command line on Windows, determinism, render speed and GPU use

### Takeaway
Blender is the strongest headless renderer in this group: a fully documented CLI (`-b`, `-P`, `-f`, `-s/-e`, `-o` with `#` padding, `--cycles-device OPTIX`) and GPU rendering for both Eevee and Cycles. Synfig and python-lottie also render headless but on the CPU. Godot and three.js render offline only through fixed-timestep capture modes. Spine needs an OpenGL window even from its CLI. The custom pycairo stack proved itself at 6:27 / 9,280 frames in 40-60 minutes with 4-5 worker processes.

### Cited Findings
**Blender (5.2 LTS manual)**
- Usage is `blender [args ...] [file] [args ...]`. `-b/--background` runs without UI, and audio is off by default in background mode unless `-setaudio Default` is added. `-a` renders the range. `-f <frame>` renders given frames: it accepts `+N/-N`, comma lists without spaces, and `..` ranges. `-s/-e` set the range and `-j` the frame step. `-o` sets output, where `//` is relative to the .blend and each `#` is a padded frame number. `-F` sets the format (FFMPEG/OPEN_EXR depend on the build). `-E` sets the engine (`-E help` lists them) and `-t 0` uses all threads — [Blender 5.2 manual, Command Line Arguments](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- Arguments run in order, and loading a .blend overwrites render settings, so `-o` must come after the file and before `-f`. `blender --background test.blend --render-frame 1 --render-output "/tmp"` fails because the frame renders before the output path is set — [Blender 5.2 manual](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- Cycles options follow a double dash: `blender -b file.blend -f 20 -- --cycles-device OPTIX`. Valid devices are CPU, CUDA, OPTIX, HIP, ONEAPI and METAL, and appending `+CPU` adds hybrid rendering. `--cycles-print-stats` logs memory and time — [Blender 5.2 manual](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- `-P/--python <file>` runs a script and `--python-expr` runs inline code. `--python-exit-code <0-255>` sets a non-zero exit on a Python exception, which an agent needs to detect failures. `--factory-startup` ignores the user's startup.blend — [Blender 5.2 manual](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- Blender 5.0 renamed the Eevee engine identifier from `BLENDER_EEVEE_NEXT` back to `BLENDER_EEVEE`, and `ImageFormatSettings` now needs `media_type` set before `file_format`. Both break scripts that set video output — [Blender 5.0 Python API release notes](https://developer.blender.org/docs/release_notes/5.0/python_api/)
- Blender 5.0 changed the logging output format, "which may affect add-ons or render farms that parse it" — [Blender 5.0 Python API release notes](https://developer.blender.org/docs/release_notes/5.0/python_api/)
- RTX 5080 GPU performance: Renderjuice (derived from Blender Open Data medians, updated March 31, 2026) gives the RTX 5080 a Blender benchmark score of about 9,126-9,134. That is about 4.5% above the RTX 4080, about 8% above the 4080 SUPER, and about 64% below the RTX 5090 (15,017). The score is not split by OptiX vs CUDA — [Renderjuice RTX 5080 vs 4080](https://www.renderjuice.com/gpus/compare/rtx-4080-vs-rtx-5080); [Renderjuice RTX 5080 vs 5090](https://www.development.renderjuice.com/gpus/compare/rtx-5080-vs-rtx-5090)
- A vendor blog claims a moderately complex 2K product render at 256 samples with OptiX denoising takes 2-4 minutes on the RTX 5080. This is marketing-grade and unverified — [Evetech Evezone](https://evezone.evetech.co.za/performance-pulse/rtx-5080-blender-performance-benchmark-real-world-test-2026/)
- Open Blackwell issues in the 5.2 changelog: "Bright Red Artifacts When GPU Rendering With Nvidia 50 Series GPU's", and rendering artifacts with texture cache plus cubic interpolation on RTX 5000 cards. The page doesn't say whether they're fixed. 5.2.1 also fixed "Eevee sampling resetting every frame" — [Blender 5.2 LTS release page](https://www.blender.org/releases/5-2/)

**Synfig**
- The `synfig` CLI renders .sif/.sifz with `-t` (target), `-o` (output), `-w/-h` (size), `-Q` (quality), `-a` (antialias), `--fps`, `--time <seconds>` (a single frame), `--begin-time/--end-time` and `-T` (threads). `-c` renders a named sub-canvas, and `--targets` lists the output targets in the build — [Ubuntu manpage synfig 1.5.1](https://manpages.ubuntu.com/manpages/lunar/man1/synfig.1.html)
- The Cobra rendering engine (2016) made the Synfig CLI use all CPU threads by default (dated, 2016) — [Morevna Project](https://morevnaproject.org/2016/06/21/synfig-studio-builds-updated-2/)
- Arch Linux packages synfig 1.4.5 as a CLI-only renderer — [Arch Linux package](https://archlinux.org/packages/extra/x86_64/synfig/)

**OpenToonz**
- The older `tconverter` CLI takes a source, destination, scene file and optional width and frame-range flags (2016 post). CLI was missing from AppImage builds before 2016-11-23 — [Morevna: How to use OpenToonz CLI](https://morevnaproject.org/2016/11/27/use-opentoonz-cli)
- The official docs have a "Rendering Scenes in Batch Mode" page and a Toonz Farm page for distributed rendering — [OpenToonz docs: Using the Toonz Farm](https://opentoonz.readthedocs.io/en/latest/using_the_toonz_farm.html)
- The Morevna Edition fork can run `.toonzscript` scripts by passing the script path to the executable. This is a fork, not upstream — [WebSearch summary of morevnaproject.org](https://morevnaproject.org/opentoonz/)

**Lottie**
- python-lottie (`lottie` on PyPI, 0.7.2) exports MP4, AVI and WebM (animated only) with the `video` extra (cairosvg, numpy, OpenCV), plus GIF, WebP, PNG stills, SVG, Synfig, dotLottie, PDF and HTML — [PyPI lottie](https://pypi.org/project/lottie/)
- The Glaxnimate Python bindings can render Lottie to GIF in a headless environment (examples use PIL to write frames) — [PyPI glaxnimate](https://pypi.org/project/glaxnimate/0.5.0.3/)
- puppeteer-lottie renders Lottie through lottie-web in headless Chrome to images, GIF or MP4, and needs ffmpeg for MP4 — [puppeteer-lottie README](https://github.com/TheJizel/puppeteer-lottie/blob/master/readme.md)
- ThorVG is an MIT-licensed C++ vector engine for SVG and Lottie with per-frame rendering. Canva moved its video-export Lottie rendering from rLottie to ThorVG and reports about 80% faster rendering — [LottieFiles blog on Canva and ThorVG](https://lottiefiles.com/blog/working-with-lottie-animations/canva-enhances-ios-rendering-faster-and-efficient-with-thorvg)

**Godot 4**
- `godot --path <project> --write-movie output.avi` records in non-real-time: the `_process` delta is constant whatever the render speed. `--fixed-fps 30` sets the frame rate and `--resolution 1280x720` the size. Both work in exported projects too. A relative output path resolves against the project folder — [Godot docs: Creating movies](https://docs.godotengine.org/de/4.4/_sources/tutorials/animation/creating_movies.rst.txt); [MovieWriter class](https://godot.readthedocs.io/cs/4.x/classes/class_moviewriter.html)
- The resolution override works only with the `disabled` or `canvas_items` stretch modes and is clamped to the display resolution, with a separate guide for higher resolutions. The built-in AVI writer is MJPEG with uncompressed audio — [Godot docs: Creating movies](https://docs.godotengine.org/de/4.4/_sources/tutorials/animation/creating_movies.rst.txt)

**three.js and browser capture**
- puppeteer-capture uses Chrome's HeadlessExperimental CDP domain for deterministic frame capture with a virtual clock, and supports Linux and Windows. `setTimeout`, `requestAnimationFrame`, `Date` and `performance.now` must be overridden before page load — [puppeteer-capture](https://github.com/alexey-pelykh/puppeteer-capture)
- CCapture.js fakes time by hooking `Date.now`, `setTimeout` and `requestAnimationFrame`, which can break scenes (a Cesium forum report). The last README version found is 1.0.9 — [CCapture.js README](https://cdn.jsdelivr.net/gh/spite/ccapture.js@1.0.9/README.md); [Cesium forum](https://community.cesium.com/t/how-to-run-cesium-on-server-side-and-capture-animation-frames/5435)
- HeyGen's open-source HyperFrames renders HTML in headless Chrome to deterministic MP4. Its three.js adapter drives scenes from explicit seek events and time values (`window.__hfThreeTime`) rather than wall clock — [HyperFrames three skill listing](https://www.vibeindex.ai/skills/heygen-com/hyperframes/three)

**Spine**
- The Spine CLI starts the editor, runs exports or atlas packing, and exits. Most parameters work headless, but "to export images or video an OS windowing system and OpenGL are required". Video export settings come from a JSON file saved in the editor's Export dialog — [Spine CLI docs](https://esotericsoftware.com/spine-command-line-interface)

**Custom pycairo stack (Initial Condition)**
- 6:27 at 1920x1080, 24 fps (about 9,280 frames). Full render about 40-60 min with 4-5 worker processes. Fixed 221-frame segments rendered in parallel, each piped to its own ffmpeg (x264 CRF 16), with resume. A partial re-render after a note takes 3-5 min — LESSONS-FROM-INITIAL-CONDITION.md

### Inferences
- On Windows, Blender in `-b` mode still creates a GPU context for Eevee and Grease Pencil, so Eevee runs on the RTX 5080 headless without a visible window (prior knowledge, not re-verified). This is the key advantage over Spine, which needs a real window.
- Eevee 1080p frames for stylized or NPR scenes typically take well under a second to a few seconds on a 5080-class card, so a 7-minute film (about 10,000 frames) is plausible in under an hour. Cycles with OptiX at production samples could take many hours. No measured Eevee benchmark was found, so treat this as an estimate.
- Determinism: Blender Cycles is seeded (a fixed `cycles.seed`, or animated seed off) and Eevee is deterministic per frame given the same build and driver. Simulations (cloth, particles, rigid bodies) need baked caches before splitting renders across processes, or segments disagree. The pycairo stack is fully deterministic as long as RNG is seeded per frame.
- Synfig, python-lottie and MoviePy are CPU-bound. They parallelize only by splitting time ranges across processes (Synfig's `--begin-time/--end-time`; python-lottie by frame), the same pattern as the pycairo segments.
- Godot is the lightest real-time 3D/2D engine with an official offline-capture mode, but the display-resolution clamp and stretch-mode rules mean 1080p capture needs a 1080p+ display or the high-res guide. On a desktop PC that's fine.
- Given open RTX 50-series artifact reports in 5.2.x, an agent should render test stills and check for red speckle artifacts after each Blender or driver update.

### Gaps
- No measured Eevee frame times on an RTX 5080 at 1080p were found. Blender Open Data covers Cycles only.
- I could not confirm whether the RTX 50-series red-artifact bug is fixed in 5.2.2+ or which driver versions trigger it.
- No first-hand documentation for running OpenToonz batch render from a script on Windows (exact flags for 1.8).
- Whether Godot 4.5/4.6 changed Movie Maker flags. Only the 4.1-4.4 docs were checked.
- python-lottie render speed for long (minutes) animations: not found.

## How well LLMs already know each API, API churn between versions, and known problems with LLM-written code

### Takeaway
Blender has the most training data by far, but its API has broken in nearly every release since 4.3: Grease Pencil v3, sequences renamed to strips, slotted Actions, and the 5.0 removals. LLM-written bpy code therefore often targets an older API. Retrieval or a pinned "API cheatsheet" skill for 5.2 LTS is needed, and the measured compile-success rate without one is low. MoviePy has the same v1-to-v2 trap. Synfig, OpenToonz and Spine formats are thinly represented. Lottie JSON is known but terse. The custom pycairo/numpy/OpenCV stack uses very stable, very well-known libraries.

### Cited Findings
**Blender API churn (primary release notes)**
- 4.3: Grease Pencil v3 replaced GPv2. The add operator changed from `bpy.ops.object.gpencil_add` to `bpy.ops.object.grease_pencil_add`, and the object type, RNA ID and mode names changed. Strokes are now attributes reached through `frame.drawing` (`frame.drawing.strokes`) instead of `frame.strokes`, and the high-level stroke API is slow, so the attributes API is recommended for heavy code. Frame numbers live on the layer, not the frame. Screen-space thickness was removed. GP modifiers became regular modifiers. Files saved in 4.3 can't be opened correctly in 4.2 — [Grease Pencil migration to 4.3](https://developer.blender.org/docs/release_notes/4.3/grease_pencil_migration/); [devtalk GPv3 feedback](https://devtalk.blender.org/t/blender-4-3-grease-pencil-v3-feedback/32115)
- A 4.3 beta tester reported that each access to a stroke returns a different Python reference, so code must not cache stroke objects — [devtalk GPv3 feedback](https://devtalk.blender.org/t/blender-4-3-grease-pencil-v3-feedback/32115?page=4)
- The 4.3 migration page did not list every breaking change (the operator rename was missing) — [blender-developer-docs issue #89](https://projects.blender.org/blender/blender-developer-docs/issues/89)
- 4.4: `bpy.types.Sequence` was renamed to `bpy.types.Strip` along with all related types. `context.sequences` became `context.strips`, `SequenceEditor.sequences_all` became `strips_all`, and `MetaStrip.sequences` became `.strips`, with the old names deprecated for removal in 5.0. Text strip `align_x/align_y` became `anchor_x/anchor_y`. Slotted Actions arrived: assigning `animation_data.action` may not assign a slot, so set `animation_data.action_slot`. `action.fcurves`, `action.groups` and `action.id_root` were deprecated — [Blender 4.4 Python API notes](https://developer.blender.org/docs/release_notes/4.4/python_api/)
- 5.0 (November 2025): `bpy.props` values are no longer reachable via dict access (`scene['cycles']` fails). The legacy Action API (`action.fcurves`, `action.groups`) was removed in favor of channelbags. `scene.node_tree` was removed in favor of `scene.compositing_node_group`. Several compositor nodes were replaced by shader nodes. The File Output node was redone. `GreasePencilv3` was renamed to `GreasePencil` and `bpy.data.grease_pencils_v3` to `bpy.data.grease_pencils`, while the old annotation types (`GPencilStroke` and so on) became `Annotation*`. The engine identifier `BLENDER_EEVEE_NEXT` became `BLENDER_EEVEE`. Render passes were renamed (`Z` to "Depth" and so on). Image/effect strip `end_frame` became `length`. Strip add operators became modal by default (`move_strips`). `context.sequencer_scene` may differ from `context.scene`. BGL was removed. mathutils types are now float32 — [Blender 5.0 Python API release notes](https://developer.blender.org/docs/release_notes/5.0/python_api/); [Digital Production, Blender 5.0](https://digitalproduction.com/2025/11/20/blender-5-0-its-here/)
- 5.1: Python 3.13. VSE strip time properties were renamed (`frame_final_start` to `left_handle`, `frame_start` to `content_start`, with the old names removed in 6.0). New `strip.content_end`. No Grease Pencil or render API changes were listed — [Blender 5.1 Python API notes](https://developer.blender.org/docs/release_notes/5.1/python_api/)
- 5.2 changed the Grease Pencil brush settings type between 5.1 and 5.2 — [Blender 5.2 API change log](https://docs.blender.org/api/5.2/change_log.html)
- The 5.2 GreasePencilDrawing API has `add_strokes()`, `remove_strokes()`, `resize_strokes(type, indices)`, `reorder_strokes()`, `set_types()`, `tag_positions_changed()`, vertex-group helpers and properties `attributes`, `color_attributes`, `curve_offsets`, `strokes` — [Blender 5.2 API: GreasePencilDrawing](https://docs.blender.org/api/current/bpy.types.GreasePencilDrawing.html)

**LLM success rates and failure modes for Blender**
- BlenderRAG (University of Bologna / Ferrari preprint, May 2026): state-of-the-art LLMs produce "frequent syntactic errors" in Blender code. Retrieval of expert-validated examples raised compilation success from 40.8% to 70.0% across four LLMs — [chatpaper summary of BlenderRAG](https://chatpaper.com/chatpaper/paper/274387)
- CodeGen-3D (IEEE Access, 2026), a benchmark for LLM-generated Blender modeling code: single-pass generation is insufficient, and self-refinement loops or domain specialization work better — [SJSU ScholarWorks](https://scholarworks.sjsu.edu/faculty_rsca/6835)
- A practitioner blog attributes many bpy hallucinations to training data predating the current API (5.0 node_tree removal, the Grease Pencil data model). It is a single-author analysis — [StraySpark blog](https://www.strayspark.studio/blog/ai-hallucinating-blender-python-api-bpy-fix)
- Community Claude Code skills exist that pin bpy to 5.x ("blender5-code") or wrap Blender in a JSON-scene CLI (cli-anything-blender, requires Blender 4.2+). These are self-published listings, not evaluated — [agensi.io blender5-code](https://www.agensi.io/skills/blender5-code); [cli-anything-blender](https://skillselion.com/skills/hkuds/cli-anything/cli-anything-blender)
- A reported agent experiment (Simon Willison, via a Spanish-language article) had a coding agent (Codex, not Claude) drive bpy headlessly to a rendered 3D image over several prompts — [ecosistemastartup.com](https://ecosistemastartup.com/?p=104952)

**MoviePy**
- MoviePy 2.0 (November 20, 2024) introduced "major breaking changes" and v1 is unmaintained. A Korean guide warns that copying old v1 code from search results "will likely produce errors" — [MoviePy GitHub README](https://github.com/Zulko/moviepy); [wikidocs guide](https://wikidocs.net/226777); [PyPI moviepy](https://pypi.org/project/moviepy/)

**Synfig, OpenToonz, Spine**
- Synfig Python plugins are Studio-menu scripts that take a .sif path as the first argument and edit the XML. There's no CLI flag to run them, so an agent would edit .sif (XML) directly and then call `synfig` — [Synfig plugins docs](https://synfig.readthedocs.io/en/latest/plugins.html)
- OpenToonz ToonzScript exposes a Scene object (cells, load levels, `scene.save`) — [OpenToonz ToonzScript docs (ja)](https://opentoonz.readthedocs.io/ja/latest/toonzscript.html)
- A Spine project file cannot be loaded without the Spine Editor — [Spine forum](https://it.esotericsoftware.com/forum/d/28095-export-mov-videos-from-spine-project-files-programmatically)

### Inferences
- For Blender, the agent must be told the exact version (pin 5.2 LTS, supported to July 2028) and given a curated cheatsheet: GPv3 drawing/attribute API, `strips` not `sequences`, `left_handle/content_start`, channelbag-based F-curve access (or just `keyframe_insert`), `compositing_node_group`, `BLENDER_EEVEE`, `media_type='VIDEO'` before `file_format='FFMPEG'`. Without this, Haiku-class and local 27B models will likely emit 3.x/4.x code. Grease Pencil v3 is the worst area: most GP scripting examples online are GPv2 (`frame.strokes.new()`, `gpencil_add`).
- High-level, stable bpy calls (object creation, `keyframe_insert`, materials via node trees, camera, lights) changed little and are reliable. Grease Pencil, VSE, compositor, Actions and the File Output node are where LLM code breaks.
- Pinning one Blender build and running every generated script with `--python-exit-code 1` plus a single-frame test render gives the agent a tight error loop. The CodeGen-3D finding (self-refinement beats single pass) supports this.
- The custom pycairo stack has the lowest API-churn risk: pycairo, numpy, OpenCV and ffmpeg CLI are stable and heavily represented in training data. The cost is that the agent writes everything (camera, particles, rigs) itself.
- Synfig .sif and OpenToonz scene files are rare in training data. Expect weak LLM output without examples, and a local 27B model will struggle more.
- Lottie JSON uses terse keys (`ks`, `ip`, `op`, `ty`, keyframe `i/o` tangents). LLMs know the schema but tend to make structural errors in long hand-written files (prior knowledge). Generating it through python-lottie's object model is safer than raw JSON.

### Gaps
- No quantitative study isolating "outdated API" as an error category for bpy (BlenderRAG and CodeGen-3D don't break this out in their abstracts).
- No evaluation of LLMs writing Grease Pencil v3 code specifically.
- No reports found of LLMs writing Synfig .sif or ToonzScript.

## Maintenance status and maturity as of 2026

### Takeaway
Blender is very actively maintained (5.2 LTS released July 14, 2026, supported to July 2028). OpenToonz 1.8.0 (June 2026) ended a three-year gap. Synfig is slow: its last stable is 1.4.5 (May 2024), with dev builds into 2026. python-lottie is a single-maintainer beta, last released May 2025. MoviePy 2.2.1 (May 2025) had no 2026 release found. rLottie is effectively unmaintained, and ThorVG has taken over the Lottie rendering role (1.0 in 2026).

### Cited Findings
- Blender 5.2 LTS: released July 14, 2026, supported until July 2028 — [blender.org 5.2 LTS](https://www.blender.org/releases/5-2/); [endoflife.ai](https://endoflife.ai/blender/5.2)
- Blender 5.0 was released in November 2025 — [Digital Production](https://digitalproduction.com/2025/11/20/blender-5-0-its-here/)
- Synfig: last stable 1.4.5 (May 19, 2024, bugfix). Dev 1.5.4 came out on January 18, 2026 and dev 1.5.5 in March 2026 (sources disagree on March 16 vs 22) — [Synfig stable releases](https://www.synfig.org/category/releases/stable-releases/); [Synfig news](https://www.synfig.org/news/); [Wikipedia Synfig](https://en.wikipedia.org/wiki/Synfig)
- Synfig 1.5.0 added Python import/export plugins — [Synfig 1.5.0 release notes](https://synfig.readthedocs.io/en/latest/releases/development/1.5.0.html)
- OpenToonz 1.8.0, released June 19, 2026, was the first official update in about three years. It adds Assistant Tool improvements, brush and fill tool improvements, stroke replication, screentone, OCA (Open Cel Animation) import/export, and better audio in "Fast Render to MP4" — [Impress Watch](https://forest.watch.impress.co.jp/docs/news/2118799.html); [MajorGeeks](https://www.majorgeeks.com/files/details/opentoonz.html)
- OpenToonz 1.7 (2023) added clipboard image paste and a Preproduction Board, and 1.7.1 was a patch release — [Ubunlog](https://ubunlog.com/en/opentoonz-1-7-has-already-been-released-and-these-are-its-news/)
- python-lottie 0.7.2 (May 1, 2025). Releases were 0.7.0 in Sep 2022, 0.7.1 in Oct 2024 and 0.7.2 in May 2025. Classifier "4 - Beta", one maintainer (Mattia Basaglia), issues on GitLab — [PyPI lottie](https://pypi.org/project/lottie/)
- rLottie "suffered from a lack of maintenance, leading to increased error rates" (Canva case study). ThorVG is actively maintained, all official dotLottie players (Web, iOS, Android) use it, and a ThorVG 1.0 talk was scheduled at COSCUP on August 9, 2026 — [LottieFiles blog](https://lottiefiles.com/blog/working-with-lottie-animations/canva-enhances-ios-rendering-faster-and-efficient-with-thorvg); [LottieFiles docs ThorVG](https://docs.lottiefiles.com/en/runtimes/overview/thorvg); [COSCUP 2026](https://coscup.org/2026/en/session/TMBVKB)
- MoviePy releases: 2.0.0 (Nov 20, 2024), 2.1.0 (Nov 24, 2024), 2.1.2 (Jan 10, 2025), 2.2.0 and 2.2.1 (May 21, 2025). Python 3.9+ — [PyPI moviepy](https://pypi.org/project/moviepy/)
- Spine Runtimes License last updated April 5, 2025 — [Spine Runtimes License](https://raw.github.com/EsotericSoftware/spine-runtimes/master/LICENSE)

### Inferences
- For a tool built in late 2026, Blender 5.2 LTS is the safe pin: two years of fixes and no API breaks within the LTS line. 5.x feature releases (5.3+) will keep breaking things, and 6.0 will remove the deprecated VSE names.
- MoviePy has had no release for about 17 months as of October 2026. That doesn't mean it's abandoned, but it's a risk signal.
- Synfig is mature but stagnant at the stable level. OpenToonz is alive again but its focus is interactive drawing, not scripting.

### Gaps
- No 2026 commit-activity data for MoviePy, python-lottie or Synfig GitHub/GitLab was retrieved.
- Godot's current 4.x version and three.js release status were not checked (prior knowledge: both are very active).

## Audio and narration sync: placing audio tracks, timing from word timestamps, exporting with audio

### Takeaway
Blender's VSE can place sound strips at exact frames from Python and mux audio in the FFmpeg output, so a word-timestamp JSON can drive both keyframes and strip placement inside one script. MoviePy places `AudioFileClip`s at times and writes audio with video. Lottie has no audio. Synfig and OpenToonz audio support is weak or GUI-centric. Godot captures its own audio. The proven approach (Initial Condition) keeps the timeline and audio mix outside the renderer: cue specs resolved from Whisper word timings, a separate mixer, and an ffmpeg mux. That works with any picture engine.

### Cited Findings
- Blender sound strips: `scene.sequence_editor.sequences.new_sound(name, filepath, channel, frame_start)` in 4.0-4.3. From 4.4 the collection is `strips` (the `sequences` names were deprecated and removed in 5.0) — [Blender 4.3 API SequencesTopLevel](https://docs.blender.org/api/4.3/bpy.types.SequencesTopLevel.html); [Blender 4.4 Python API notes](https://developer.blender.org/docs/release_notes/4.4/python_api/)
- In 5.0, `context.sequencer_scene` (the workspace's sequencer scene) may differ from `context.scene`, and strip add operators are modal by default (`move_strips`) — [Blender 5.0 Python API notes](https://developer.blender.org/docs/release_notes/5.0/python_api/)
- In 5.1, strip timing properties were renamed (`left_handle`, `content_start`, new `content_end`) — [Blender 5.1 Python API notes](https://developer.blender.org/docs/release_notes/5.1/python_api/)
- In background mode, Blender's audio is off by default; `-setaudio Default` re-enables it — [Blender 5.2 manual](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- MoviePy 2.x examples chain `with_subclip` and `with_multiply_volume` (the v2 `with_*` API replacing v1 `set_*`) — [MoviePy GitHub README](https://github.com/Zulko/moviepy)
- Godot Movie Maker writes AVI with MJPEG video and uncompressed audio from the running project — [Godot docs: Creating movies](https://docs.godotengine.org/de/4.4/_sources/tutorials/animation/creating_movies.rst.txt)
- OpenToonz 1.8 improved audio handling in "Fast Render to MP4" — [Impress Watch](https://forest.watch.impress.co.jp/docs/news/2118799.html)
- Initial Condition's method: Whisper word timings resolve cue specs such as `"L27:end+0.3"`. Shots are padded around lines. Pin slots keep later shots fixed when a take changes length. Audio is mixed separately (voice, fx, music buses, LUFS master) and muxed with the video stream copied — LESSONS-FROM-INITIAL-CONDITION.md

### Inferences
- Recommended for any engine: keep audio out of the renderer. Render silent picture (PNG/EXR sequence or segment MP4s), build the mix with Python/ffmpeg, then mux. Blender's VSE audio is useful for previewing in the GUI but adds API churn (strip renames in 4.4, 5.0 and 5.1) for no gain in a headless pipeline. Rendering audio from Blender in `-b` also requires remembering `-setaudio`.
- For lip-sync (character work), Blender is the only tool here with a practical path: shape keys or pose-library mouth shapes keyed from phoneme or word timings via `keyframe_insert`. Rhubarb Lip Sync is a common phoneme source (prior knowledge, not re-verified). Spine also supports mouth swaps but needs the editor.
- Word-timestamp-driven keyframing is easy in any code-first tool (bpy, Godot via generated AnimationPlayer tracks, three.js, pycairo). It's awkward in Synfig (.sif XML waypoints) and OpenToonz (xsheet cells).
- Lottie output must always be muxed with audio externally, since the format has no audio track (prior knowledge).

### Gaps
- Whether Synfig's CLI ffmpeg target muxes sound layers was not confirmed.
- No source found for Blender's FFmpeg audio-codec property names in 5.2 (`scene.render.ffmpeg.audio_codec`, prior knowledge).

## Rendering single frames for review, partial re-renders

### Takeaway
All the CLI tools can render a single frame or a range. Blender (`-f 120`, `-f 1,50,120`, `-s/-e`), Synfig (`--time`, `--begin-time/--end-time`) and python-lottie (`--frame`) do this natively, so the stills, contact sheet and segment-re-render loop from Initial Condition carries over. Real-time engines (Godot, three.js) need a custom seek-to-time hook for stills.

### Cited Findings
- Blender `-f` accepts single frames, comma lists without spaces, relative `+/-` frames and `..` ranges. `-s/-e/-j` define ranges and steps, so `-j 48` yields a 2-second contact sheet at 24 fps — [Blender 5.2 manual](https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html)
- Synfig `--time <seconds>` renders a single frame, and `--begin-time/--end-time` bound a range — [Ubuntu manpage synfig](https://manpages.ubuntu.com/manpages/lunar/man1/synfig.1.html)
- python-lottie's `lottie_convert.py` renders a still frame with `--frame` (PNG needs cairosvg/pillow) — [PyPI lottie](https://pypi.org/project/lottie/)
- OpenToonz `tconverter` has frame-range flags — [Morevna: OpenToonz CLI](https://morevnaproject.org/2016/11/27/use-opentoonz-cli)
- HyperFrames' three.js adapter renders from explicit seek events and time values, which is the pattern needed for single-frame review — [HyperFrames three](https://www.vibeindex.ai/skills/heygen-com/hyperframes/three)
- Initial Condition's stills mode (`render.py --stills 4.5:2.0`, shot-relative times) and contact sheets (one frame every 2 s) were "the core feedback loop for the agent, who cannot watch video". Deleting a segment file re-renders just that segment — LESSONS-FROM-INITIAL-CONDITION.md

### Inferences
- Blender has a startup cost per invocation (loading the .blend, compiling Eevee shaders), so stills are best batched in one call (`-f 10,50,90,130`) rather than one process per frame. Rendering segments to image sequences (PNG/EXR) rather than MP4 makes partial re-renders trivial: overwrite frames, then re-encode.
- Eevee's shader compilation on first render can take tens of seconds per new material set (prior knowledge). Caching the shader cache between runs helps the iteration loop.
- In Godot, single-frame stills require the project to accept a "start time" argument and to quit after N frames. That's possible but must be built into the template.

### Gaps
- No measured Blender per-invocation startup overhead or Eevee shader-compile times on the RTX 5080.

## Visual quality ceiling and styles each tool suits

### Takeaway
Blender has by far the highest ceiling and the widest range: photoreal (Cycles), stylized or NPR (Eevee and shader-to-RGB), rigged 3D characters, cut-out (image planes plus armatures), and hand-drawn 2D through Grease Pencil v3 rendered in Eevee. OpenToonz is the best traditional cel/hand-drawn pipeline but is the least scriptable. Synfig suits vector cut-out with bone rigs. Lottie suits flat motion graphics. MoviePy is a compositor, not an animation tool. The pycairo stack suits stylized vector plus painted plates, but character animation and lip-sync are out of reach in practice.

### Cited Findings
- Grease Pencil v3 (4.3+) stores strokes as curve attributes. GP modifiers are now regular modifiers, and geometry nodes can process GP data (for example scaling thickness procedurally, replacing the removed screen-space thickness) — [GP migration to 4.3](https://developer.blender.org/docs/release_notes/4.3/grease_pencil_migration/)
- Blender 5.0 added a Pen tool in GP Edit Mode and improved cyclic-stroke handling — [Digital Production, Blender 5.0](https://digitalproduction.com/2025/11/20/blender-5-0-its-here/)
- OpenToonz 1.8 adds screentone and OCA import/export along with brush, fill and assistant-tool improvements, and it targets traditional drawn animation — [Impress Watch](https://forest.watch.impress.co.jp/docs/news/2118799.html)
- Spine is a skeletal 2D animation editor whose project files require the editor — [Spine CLI docs](https://esotericsoftware.com/spine-command-line-interface); [Spine forum](https://it.esotericsoftware.com/forum/d/28095-export-mov-videos-from-spine-project-files-programmatically)
- Initial Condition's own assessment: the pycairo stack fits "narrated, stylized, vector-plus-plate animation (essays, explainers, poems, manifestos). It doesn't fit character animation, lip-sync, 3D". The author's notes centered on proportion, composition, physical logic (depth, occlusion) and readability — LESSONS-FROM-INITIAL-CONDITION.md

### Inferences
- Several author notes from Initial Condition (depth, occlusion, a knife falling "behind the hand", scaling toward a vanishing point) are things a 3D scene in Blender gives for free. A hybrid (Blender for 3D or depth shots, pycairo/compositing for 2D graphics) is plausible.
- Rigged character animation from code: Blender is the only free option with a high ceiling. An agent can import a rigged character (for example a glTF/FBX with an armature, or a Rigify rig) and key bones from Python. But LLM-authored character motion (posing, weight shifts, acting) tends to look stiff, and complex hand-keyed acting is a weak spot for agents. Procedural loops (breathing, idle sway), simple gestures and camera moves are realistic targets. No source measured this, so it's an inference.
- Hand-drawn look: GPv3 strokes are generated by code, so the "hand-drawn" quality comes from noise or jitter modifiers, line-thickness variation and boiling (re-randomized strokes every 2-3 frames), not real drawings. OpenToonz gives real hand-drawn quality but needs a human artist.
- Painterly or atmospheric: Eevee volumetrics, bloom (now done via the compositor's Glare node since 4.2; prior knowledge) and textured image planes carrying AI-painted plates give a parallax 2.5D look that the pycairo stack approximated by hand.
- Lottie's ceiling is flat vector motion design (no blur-heavy atmospherics, no 3D). It's fine for title cards or overlays rendered separately and composited.
- Godot and three.js can reach strong stylized real-time looks (toon shaders, post-processing) but lack Blender's offline quality features (path tracing, high-quality motion blur, the compositor).

### Gaps
- No public examples found of an LLM agent producing a narrated character animation in Blender end to end, with quality assessments.
- No sources on Synfig quality comparisons in 2025-2026.

## Licensing

### Takeaway
Blender, Synfig, OpenToonz, MoviePy, Godot, three.js and ThorVG are free and open source, with no restrictions on rendered output. python-lottie is AGPLv3, which matters only if it ships inside a networked service. Spine is proprietary: a paid editor license is required, and the runtime license is tied to it.

### Cited Findings
- MoviePy: MIT — [PyPI moviepy](https://pypi.org/project/moviepy/)
- python-lottie: AGPLv3+ — [PyPI lottie](https://pypi.org/project/lottie/)
- ThorVG: MIT — [LottieFiles blog](https://lottiefiles.com/blog/working-with-lottie-animations/introducing-thorvg-powerful-graphic-library-for-lottie-animations)
- Spine Runtimes License (updated April 5, 2025): use of the runtimes requires a Spine Editor license per user, or integration under Section 2 of the Editor license. Staff said Spine Essential is enough unless gross revenue is over $500k in the past 12 months, after which Enterprise is needed (this threshold may be outdated) — [Spine Runtimes License](https://raw.github.com/EsotericSoftware/spine-runtimes/master/LICENSE); [Spine forum](https://esotericsoftware.com/forum/d/18211)
- A third-party npm `spine-exporter` claims CLI export without the Spine editor, but only for Spine 3.8.x, with 4.0 "planned" — [npm spine-exporter](https://npmjs.com/package/spine-exporter)

### Inferences
- Prior knowledge, not re-verified this session: Blender is GPL-2.0-or-later (GPL-3 for the whole binary), and rendered output and .blend content are the user's own. Synfig is GPL-3.0. OpenToonz uses a modified BSD license. Godot and three.js are MIT. pycairo is LGPL-2.1/MPL-1.1. OpenCV 4.5+ is Apache-2.0. numpy is BSD. ffmpeg is LGPL/GPL depending on the build (GPL with libx264).
- For a local personal tool none of these licenses restrict use or output. AGPL (python-lottie) and Spine are the only ones to flag if the tool is later shared or offered as a service.

### Gaps
- License texts for Blender, Synfig, OpenToonz, Godot and three.js were not fetched in this session.

## Compositing raster images and video (AI-generated background plates and clips)

### Takeaway
Blender can use AI plates and clips as textured planes in 3D (true parallax and lighting), as world backgrounds, or as VSE image and movie strips, plus a node compositor. Its compositor and VSE APIs, though, are exactly where 5.0 broke scripts. MoviePy is the simplest Python compositor for layering clips, images and text, but it's CPU-bound and slow per frame. The pycairo/numpy/OpenCV stack composited plates directly with full control. Lottie supports only embedded raster images and no video. Synfig imports images. Godot and three.js use plates as textures.

### Cited Findings
- Blender 5.0 removed `scene.node_tree` in favor of `scene.compositing_node_group` (created via `bpy.data.node_groups.new`). `scene.use_nodes` is deprecated, several compositor nodes were replaced by shader-node equivalents (for example Gamma), the File Output node was reworked, and image/effect strips use `length` instead of `end_frame` — [Blender 5.0 Python API notes](https://developer.blender.org/docs/release_notes/5.0/python_api/)
- In 4.4 the new CPU compositor became the only CPU compositor (the old toggles were removed) — [Blender 4.4 Python API notes](https://developer.blender.org/docs/release_notes/4.4/python_api/)
- The 5.2 changelog includes fixes for GPU compositor crashes and a Denoise node crash — [Blender 5.2 LTS page](https://www.blender.org/releases/5-2/)
- python-lottie can import PNG, GIF, WebP, BMP, TIFF and SVG, and even Blender and Krita files — [PyPI lottie](https://pypi.org/project/lottie/)
- Synfig CLI `--append <file>` merges layers from another file into the composition — [Ubuntu manpage synfig](https://manpages.ubuntu.com/manpages/lunar/man1/synfig.1.html)
- Initial Condition: about 25 Qwen-Image plates (1664x928, cover-fit to 1080p) and about 20 silhouette sources (thresholded and traced), composited with numpy/OpenCV. A memo cache on disk was used for expensive static images — LESSONS-FROM-INITIAL-CONDITION.md

### Inferences
- For AI plates, Blender's strongest move is a 2.5D setup: split plates into depth layers (or use a depth map with displacement) on planes, then move a real camera. That gives parallax, depth-of-field and volumetric light that pycairo had to fake. Wiring materials uses shader nodes (stable API) rather than the compositor (churned API), which lowers LLM error risk.
- AI-generated video clips can be image-sequence or movie textures on planes (`Image` source `MOVIE`) or VSE movie strips. Frame-accurate sync of external clips is simpler done in a final ffmpeg/numpy pass.
- MoviePy v2 is a good glue layer for final assembly (plates, rendered passes, titles, audio) when performance isn't critical. For a 7-minute 1080p film with per-pixel effects, numpy/OpenCV or ffmpeg filtergraphs are faster (prior knowledge; MoviePy runs Python per frame).

### Gaps
- No benchmark of MoviePy v2 compositing throughput at 1080p.
- No sources on Lottie's handling of large embedded raster plates (file size, performance).
