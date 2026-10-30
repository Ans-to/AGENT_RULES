# Installation and verification record

Environment: Linux x86-64, Python 3.11, Node 22, 2 CPU cores, about 3.8 GB RAM; no GPU, Docker, system FFmpeg or system Chrome. Large tool/model installations are deliberately kept in `.cache/` and `.venv/` and must be recreated when starting in a new environment. The project itself, installed agent instructions and generated assets are in this repository. At the time of the initial report, nothing had been committed or pushed; publishing was subsequently authorized.

## Cinematic Director — MIT

Upstream: https://github.com/cajias/agentic-video-skills (checked commit `204cefd`; upstream Director skill license MIT). Its documentation describes Claude Code marketplace commands `/plugin marketplace add cajias/agentic-video-skills` and `/plugin install director@agentic-video-skills`; the actual current marketplace name is `cinematic-director`, not `director`. This environment is not Claude Code and does not expose that plugin manager. Instead the skill and its references were installed in project-local `.agents/skills/cinematic-director/` and loaded explicitly for this task:

```sh
git clone --depth 1 https://github.com/cajias/agentic-video-skills.git .cache/setup/director
mkdir -p .agents/skills
cp -a .cache/setup/director/plugins/cinematic-director/skills/cinematic-director .agents/skills/
python .cache/setup/director/tests/validate_structure.py
```

Result: marketplace validator passed (4 plugins, 4 skills, 16 eval definitions); skill front matter, references and shot template are readable. This is a project-local, explicitly loaded skill, not a claim of native Arena plugin registration. Its direction, continuity and shot-planning procedures informed `SPEC.md`. The validator checks structure, not artistic quality.

## Chatterbox — MIT; attempted, blocked by model access

Upstream: https://github.com/resemble-ai/chatterbox (checked `5de7a54`). Documentation specifies `pip install chatterbox-tts` or source `pip install -e .`; dependencies include torch/torchaudio 2.6.0 for Python 3.11, librosa, transformers, conformer and others. Turbo/Nano use reference conditioning or a built-in voice if provided by the model snapshot. Nano supports CPU; source recommends 8 cores for its quoted speed. The machine has 2 cores, no CUDA GPU, and 3.8 GB RAM.

Before the workspace runtime was recreated, the following documented installation and actual test were attempted:

```sh
python -m venv .venv-agent-tools
.venv-agent-tools/bin/python -m pip install chatterbox-tts
# The PyPI 0.1.7 package lacked the documented nano argument, so use current source:
git clone --depth 1 https://github.com/resemble-ai/chatterbox.git .skill-review/chatterbox
cd .skill-review/chatterbox
../../.venv-agent-tools/bin/python -m pip install -e .
# ChatterboxTurboTTS.from_pretrained(device='cpu', nano=True), then generate(...)
```

Package and source installation succeeded in that earlier runtime; source supported `nano=True`. Actual generation failed before inference because the Hugging Face model snapshot could not be fetched (`ConnectError: TLS/SSL connection has been closed (EOF)` / `LocalEntryNotFoundError`); no weights were cached. That virtual environment was not preserved by the workspace snapshot and Chatterbox is not installed in the current runtime. It was **not** used for this video, and its audio quality was not assessed.

## Verified alternative: Kokoro ONNX — MIT runtime, Apache-2.0 model and voice

Kokoro runs on CPU, fits the machine, and its open weights and packaged voice vectors were obtainable from the allowed npm registry. We installed it in an isolated Python environment (its NumPy 2 dependency conflicts with Chatterbox's NumPy 1 requirement):

```sh
python -m venv .venv
.venv/bin/python -m pip install kokoro-onnx soundfile
npm install --prefix .cache/tools --ignore-scripts --no-save kokoro-local-runtime@0.1.0 kokoro-q8-shards@1.0.0
mkdir -p .cache/model
cat .cache/tools/node_modules/kokoro-q8-shards/kokoro-q8.part{0,1,2,3,4,5}.bin > .cache/model/model_quantized.onnx
sha256sum .cache/model/model_quantized.onnx
```

The 92 MB quantized model's SHA-256 was `fbae9257e1e05ffc727e951ef9b9c98418e6d79f1c9b6b13bd59f5c9028a1478`, matching the package's published checksum. The `.bin` voice comes from `kokoro-local-runtime`, which documents Apache-2.0 voice assets; the runtime code is MIT/Apache-2.0. Python uses ONNX Runtime, NumPy, phonemizer and bundled eSpeak NG. `video/scripts/synthesize.py` converts the 510×256 `am_michael` voice tensor to an NPZ and generates speech using actual ONNX inference. Tests generated a 7.66-second `af_heart` sample and an 8.75-second `am_michael` sample; the user explicitly selected Michael. No independent automated claim about naturalness is made.

## HyperFrames — Apache-2.0

Upstream: https://github.com/heygen-com/hyperframes (checked `4e2a1c2`). Node 22+ and FFmpeg are required. Documented `npx --yes hyperframes skills update` was attempted and failed because the GitHub manifest could not be reached; no success was reported. The four documented core skills were copied from the checked-out upstream source to `.agents/skills/` and read explicitly (not native plugin registration). The CLI is `hyperframes@0.8.216`:

```sh
git clone --depth 1 https://github.com/heygen-com/hyperframes.git .cache/setup/hyperframes
for s in hyperframes hyperframes-cli hyperframes-registry media-use; do cp -a .cache/setup/hyperframes/skills/$s .agents/skills/$s; done
npm install --prefix .cache/tools --ignore-scripts --no-save hyperframes@0.8.216 gsap@3.14.2 @sparticuz/chromium@153.0.0 @ffprobe-installer/linux-x64@5.2.0 kokoro-local-runtime@0.1.0 kokoro-q8-shards@1.0.0
.venv/bin/python -m pip install imageio-ffmpeg
```

The normal `hyperframes browser ensure` failed because the Chrome download host was unreachable. The npm-packaged Chromium plus its bundled Linux libraries was extracted and tested instead; `HYPERFRAMES_BROWSER_PATH=/tmp/chromium`, `LD_LIBRARY_PATH=/tmp/al2023/lib`. The npm static ffprobe and imageio-ffmpeg's FFmpeg 7.0.2 were placed on `PATH`; bundled binary licensing is GPL and accompanying package licensing/attribution should be reviewed if redistributing binaries. GSAP is bundled locally so no CDN request is needed. A real 2-second 1080p smoke MP4 was rendered and `hyperframes check` passed after replacing its blocked GSAP CDN with the local copy. The final project also passed HyperFrames check with warnings described in the audit.

## Video Analysis Skill — MIT

Upstream: https://github.com/bydfi-official/video-analysis-skill (checked `b270269`). The README's prompt-install procedure says to copy SKILL.md, references, scripts, agents, requirements, Dockerfile and README without `.git` or artifacts. We did so to `.agents/skills/video-analysis/`, then used the documented requirements install and doctor:

```sh
git clone --depth 1 https://github.com/bydfi-official/video-analysis-skill.git .cache/setup/auditor
mkdir -p .agents/skills/video-analysis
tar --exclude=.git --exclude=__pycache__ --exclude='*.pyc' --exclude=artifacts --exclude=.venv -cf - -C .cache/setup/auditor . | tar -xf - -C .agents/skills/video-analysis
.venv/bin/python -m pip install -r .agents/skills/video-analysis/requirements.txt
PATH="$PWD/.cache/bin:$PATH" .venv/bin/python .agents/skills/video-analysis/scripts/doctor.py --profile base --repair-plan
```

Base doctor: ready. An actual synthetic 2-second clip analysis passed and produced metadata, four sampled frames, a contact sheet and quality gates. Full doctor identifies missing OCR binary, ASR model and Docker; faster-whisper was installed during the earlier runtime but its model was unavailable because Hugging Face was blocked. OCR/ASR were not used; the final audit therefore cannot independently transcribe or verify exact spoken words.

## rendercheck — MIT

Upstream: https://github.com/rogermsc/rendercheck (checked `f104a91`). Python >=3.10; deterministic checks use ffmpeg/ffprobe with no Python runtime dependencies. Documented install and real demo:

```sh
.venv/bin/python -m pip install rendercheck
PATH="$PWD/.cache/bin:$PATH" .venv/bin/rendercheck demo
```

Result: `rendercheck` 0.4.1 installed; demo synthesized ten defective files and correctly reported example failures (`audit/rendercheck-demo.txt`). Final test command and measurements are in `AUDIT.md`. The tool performs signal and metadata checks, not a human listening test or a factual transcript review.
