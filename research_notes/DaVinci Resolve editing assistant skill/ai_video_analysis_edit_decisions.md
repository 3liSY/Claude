# AI Video Analysis and Automated Edit Decisions: Pipeline, Tools, and Open-Source Building Blocks (as of Oct 2026)

Scope: how to turn a voice-over talking video (hands and cubes, or gameplay, never a face) into text and images Claude can reason about, and how commercial and research systems turn that into edit decisions (cuts, B-roll, punch-in zooms, SFX). Target machine: Windows 11, RTX 4060 Laptop 8 GB VRAM, 16 GB RAM, Claude Code local. Speech: Syrian (Levantine) Arabic with English cubing terms ("F2L", "PLL"). The user already runs faster-whisper large-v3 (float16, word_timestamps=True).

Method note: arxiv.org, huggingface.co, cohere.com, autocut.com and dev.to could not be fetched directly in this session (DNS failure). Facts from those sites come from search-result summaries of them. GitHub READMEs and files were read directly. Vendor claims are marked as vendor claims.

---

## 1. Transcription with word timestamps (Arabic, dialect, code-switching, forced alignment, VRAM)

### Takeaway
Keep faster-whisper large-v3 as the base transcriber. It fits 8 GB, it is the user's existing tool, and no newer open model has been shown to beat it on *timestamped* Levantine Arabic. Newer Arabic-specialised models are more accurate on text but give no word timestamps: Cohere Transcribe Arabic (Jul 2026, Apache-2.0) and NVIDIA's Arabic Conformer-CTC both lead the Arabic leaderboard but only output text, and Qwen3-ASR's aligner excludes Arabic. So word timing for Arabic still depends on Whisper's own timestamps or on CTC forced alignment: WhisperX's default Arabic wav2vec2, or MMS-based ctc-forced-aligner. Plain Whisper handles code-switched Arabic/English badly. Dialect WER is high (roughly 25–60% depending on dataset), so the skill should treat the transcript as approximate and anchor decisions to word timestamps, not to exact wording.

### Cited Findings
**faster-whisper (the user's current tool)**
- GPU needs cuBLAS for CUDA 12 and cuDNN 9. On Windows, Purfview's whisper-standalone-win archive supplies the cuBLAS/cuDNN DLLs to put on PATH. Install is `pip install faster-whisper` (Python ≥3.9). — [SYSTRAN/faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- README benchmark (large-v2, RTX 3070 Ti 8 GB, beam 5) on the README's reference audio:
  - fp16: 1m03s, 4,525 MB VRAM
  - fp16 with `batch_size=8`: 17s, 6,090 MB
  - int8: 59s, 2,926 MB
  - int8 batched: 16s, 4,500 MB
  - openai/whisper fp16 for comparison: 2m23s, 4,708 MB
  — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- `word_timestamps=True` gives `segment.words` with start/end/word. `vad_filter=True` uses Silero VAD. By default VAD removes only silences longer than 2 s, tunable via `vad_parameters=dict(min_silence_duration_ms=500)`. VAD is on by default in batched mode. The README loads `"turbo"` and supports distil-large-v3 (English-oriented example). — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- Speed on an RTX 4060 8 GB (vendor/blog numbers, they conflict):
  - FP16 large-v3: RTF 0.16–0.18 (5.6–6.2× real-time). INT8 is about 30–33% faster (RTF 0.12). — [GigaGPU 4060 benchmark](https://gigagpu.com/whisper-large-v3-on-rtx-4060-benchmark/)
  - A Japanese benchmark lists RTF 0.25. — [jisaku.com](https://jisaku.com/posts/ai-bench-faster-whisper-speed-2026)
  - One GigaGPU page claims 46×, which is an outlier and inconsistent with the rest. — [GigaGPU](https://gigagpu.com/?p=9057)

**Whisper large-v3 vs large-v3-turbo**
- Turbo keeps the large-v3 encoder and cuts the decoder from 32 layers to 4 (1.54B → 809M parameters). — [novascribe/vexascribe guide](https://vexascribe.com/whisper-large-v3-vs-turbo)
- Turbo is reported as worse on low-resource languages, and the guides recommend large-v3 for those. Vendor-blog multilingual average WER: ~12.5% (v3) vs ~14.0% (turbo). — [vexascribe](https://vexascribe.com/whisper-large-v3-vs-turbo)
- Zero-shot turbo on dialects (community model card, not peer-reviewed):
  - ~10.4% WER on MSA (FLEURS), but 65.0% on Egyptian and 61.1% on Gulf (Casablanca).
  - 0.590 WER / 0.278 CER on a 932-clip multi-dialect set.
  — [oddadmix model cards via search](https://huggingface.co/oddadmix/whisper-large-v3-turbo-arabic-dialectal)

**Arabic benchmark: Open Universal Arabic ASR Leaderboard**
- Paper: arXiv 2412.13788 (Wang, Alhmoud, Alqurishi, 2024). Test sets cover MSA, Egyptian, Gulf, Levantine and Maghrebi.
- In the original paper, NVIDIA Conformer-CTC-large-Arabic with a 4-gram LM ranked first: 25.71% average WER, 10.02% CER.
— [arXiv 2412.13788](https://arxiv.org/pdf/2412.13788)
- **Cohere Transcribe Arabic** (released 7 Jul 2026):
  - Open weights, Apache-2.0. Average WER on the leaderboard 25.87, reported ahead of OmniASR-LLM-7B and Whisper Large V3. — [HF blog](https://huggingface.co/blog/CohereLabs/cohere-transcribe-arabic-07-2026-release); [Cohere blog](https://cohere.com/blog/transcribe-arabic)
  - Per-set WER: SADA (Saudi) 37.47, Common Voice 5.82, Casablanca (Maghrebi) 49.71.
  - Sources disagree on snapshot dates (23.06.26 vs 07.07.26) and on who leads. — [search summary of leaderboard/Cohere tables](https://benchmarklist.com/benchmarks/open_universal_arabic_asr/)
- Cohere Transcribe Arabic has **no word timestamps or diarization** per Friendli's model page. Cohere docs list text-only output. Cohere markets Arabic-English code-switching, but Friendli reports "inconsistent performance on code-switched audio" and no automatic language detection. — [Friendli model page](https://friendli.ai/models/CohereLabs/cohere-transcribe-arabic-07-2026); [Cohere docs](https://docs.cohere.com/docs/transcribe-arabic)

**Levantine and Syrian-specific signals**
- Arab Voices (arXiv 2601.13319, ACL 2026 Findings) benchmarks 14 systems including Whisper-large-v3 on Levantine (apc) and Khaleeji. Levantine WER ranges from ~51.8 down to ~23.5 across systems, and MSA from ~38.9 to ~10.2. The snippet did not show which system got which number. — [Arab Voices](https://arxiv.org/pdf/2601.13319)
- Bulbul dataset (arXiv 2608.21950) reports Whisper V3 WER of ~58.9 for Syria, versus ~34.9 Jordan, ~29.6 Palestine and ~26.0 KSA (accented MSA/CA speech). — [Bulbul](https://arxiv.org/pdf/2608.21950)
- Whisper Large v3 reached 66% WER on Levantine children's speech, 4.1× its FLEURS WER. — [Arabic Little STT, arXiv 2510.23319](https://arxiv.org/pdf/2510.23319)
- Community fine-tune "whisperLevantine" (Whisper Medium, ~2,200 h, mostly Israeli Levantine) self-reports 14% WER on its own test set. — [HebArabNlpProject/whisperLevantine](https://huggingface.co/HebArabNlpProject/whisperLevantine/blame/main/README.md)

**Code-switching (Arabic plus English terms like "F2L", "PLL")**
- Casablanca paper: whisper-large-v3 produced **no code-switched words** in any decoding setting on code-switched input, and sometimes translated instead of transcribing. — [Casablanca, arXiv 2410.04527](https://arxiv.org/pdf/2410.04527)
- A fine-tuned model card says base Whisper drops English technical terms or writes them in Arabic script (e.g. "embedding"). Its fine-tune keeps Latin script (self-reported). Other code-switch fine-tunes exist, e.g. MohamedRashad/Arabic-Whisper-CodeSwitching-Edition (built on large-v2). — [Seif-Eldeen-Sameh/whisper-medium-arabic-codeswitched](https://friendli.ai/models/Seif-Eldeen-Sameh/whisper-medium-arabic-codeswitched); [MohamedRashad model](https://huggingface.co/MohamedRashad/Arabic-Whisper-CodeSwitching-Edition)
- No source tested `initial_prompt` for Arabic-English code-switching. Prompt changes did shift the language balance in Chinese-English studies. — [arXiv 2412.16507](https://arxiv.org/pdf/2412.16507)

**Other 2025–2026 ASR options**
- **Qwen3-ASR** (0.6B/1.7B) transcribes Arabic. **Qwen3-ForcedAligner-0.6B** supports only 11 languages (zh, en, yue, fr, de, it, ja, ko, pt, ru, es) and **not Arabic**. — [QwenLM/Qwen3-ASR](https://github.com/QwenLM/Qwen3-ASR); [arXiv 2601.21337](https://arxiv.org/pdf/2601.21337v2)
- **NVIDIA:**
  - Canary-1b-v2 and Parakeet-tdt-0.6b-v3 (Aug 2025) cover 25 European languages and **not Arabic**.
  - Parakeet-tdt-0.6b-v2 word timestamps are English-only.
  - Arabic (ar-AR) appears only in the Riva/NIM Parakeet RNNT multilingual model, and a Mar 2026 forum thread reports Arabic issues with it.
  - NeMo Forced Aligner gives word timestamps for other models.
  — [NVIDIA Riva support matrix](https://docs.nvidia.com/nim/riva/asr/1.5.0/support-matrix.html); [NVIDIA blog](https://developer.nvidia.com/blog/nvidia-speech-ai-models-deliver-industry-leading-accuracy-and-performance)

**WhisperX**
- Uses faster-whisper plus wav2vec2 alignment. Large-v2 at beam 5 needs under 8 GB VRAM.
- Whisper's native timestamps are utterance-level and "can be inaccurate by several seconds".
- On Windows, install the CUDA toolkit 12.8 first, then `pip install whisperx`. `whisperx[fast]` adds numba.
- Diarization needs an HF token and acceptance of pyannote `speaker-diarization-community-1`.
- Overlapping speech is handled poorly. A bigger alignment model "not that helpful".
— [m-bain/whisperX README](https://github.com/m-bain/whisperX)
- WhisperX's default Arabic alignment model is **`jonatasgrosman/wav2vec2-large-xlsr-53-arabic`** (`DEFAULT_ALIGN_MODELS_HF["ar"]`). In the current code, characters outside the model vocabulary (digits, symbols, foreign script such as Latin "F2L") map to a wildcard column rather than being dropped. The README still says digits/currency get no timing, which reflects older behaviour. — [whisperx/alignment.py](https://raw.githubusercontent.com/m-bain/whisperX/main/whisperx/alignment.py)

**Other aligners**
- **ctc-forced-aligner** (MahmoudAshraf97):
  - Default model `MahmoudAshraf/mms-300m-1130-forced-aligner`, covering 1,130 languages including Arabic (`--language ara`).
  - Needs `--romanize` with the default model. The Arabic example uses the native-script `jonatasgrosman/wav2vec2-large-xlsr-53-arabic` instead.
  - Claims "at least 5× less memory" than the TorchAudio API.
  - Output is JSON segments at sentence, word or char level.
  - BSD-2 code, but **the default model is CC-BY-NC 4.0**.
  - Install: `pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git` plus ffmpeg.
  — [ctc-forced-aligner README](https://github.com/MahmoudAshraf97/ctc-forced-aligner)
- **Montreal Forced Aligner:** `arabic_mfa` dictionary v2.0.0 (2022) with a matching Arabic MFA acoustic model. The docs advise adding reduced pronunciation variants for spontaneous speech. — [MFA Arabic dictionary docs](https://mfa-models.readthedocs.io/en/latest/dictionary/Arabic/Arabic%20MFA%20dictionary%20v2_0_0.html)
- **stable-ts** (jianfch):
  - **Archived and read-only since 30 May 2026**, with development "indefinitely paused".
  - Features: timestamp stabilisation, silence suppression with Silero, `align()` / `align_words()` for aligning known text, `refine()`, and backends for faster-whisper `[fw]` and HF `[hf]`.
  - Install: `pip install -U stable-ts[fw]`.
  — [jianfch/stable-ts](https://github.com/jianfch/stable-ts)
- **Diarization:** pyannote `speaker-diarization-community-1` has better DER than legacy 3.1 (e.g. AMI-IHM 17.0 vs 18.8) and runs ~31 s per hour of audio on an H100. It needs an HF token. — [pyannote-audio README](https://github.com/pyannote/pyannote-audio)

### Inferences
- **Single speaker.** The channel is voice-over only, so diarization (pyannote) adds nothing and need not be installed.
- **Best-fit stack:**
  1. Keep faster-whisper large-v3 fp16 (or int8_float16 for headroom), `language="ar"`, `word_timestamps=True`, with VAD.
  2. Optionally re-time words with WhisperX's Arabic wav2vec2 aligner, or ctc-forced-aligner with the same jonatasgrosman model, to tighten word edges for cut snapping.
  3. The base model in step 1 should be large-v3. Turbo is weaker on low-resource and dialect speech.
- **Code-switched terms.** Expect "F2L", "PLL" and "OLL" to come out as Arabic-script transliterations, as translations, or dropped. Practical mitigations, all untested and needing validation on his audio:
  - A custom-vocabulary post-pass where Claude maps Arabic-script spellings (e.g. "اف تو ال") back to Latin terms.
  - An `initial_prompt`/hotwords string with a mixed Arabic + Latin cubing glossary (faster-whisper supports `initial_prompt` and `hotwords`; not verified in this research).
  - Treating the transcript as approximate for keyword-triggered B-roll.
- **What matters for edit timing.** Word timestamps matter more than WER. A 25–60% WER on dialect still yields usable word boundaries for cuts and zooms, and Claude can infer meaning from noisy Syrian-Arabic text plus frames.
- **Cohere Transcribe Arabic** (parameter count not verified here) could be used as a second-opinion text transcript, with its text forced-aligned through ctc-forced-aligner. That is two models and more VRAM juggling. It is optional and not a default.

### Gaps
- No direct measurement of faster-whisper or WhisperX **word-timestamp error (ms)** on Levantine Arabic was found. Validate on 2–3 minutes of hand-checked audio.
- No direct per-system Levantine WER for Whisper large-v3 vs Cohere vs Conformer-CTC was obtained (leaderboard page and HF not fetchable).
- Cohere Transcribe Arabic parameter count and VRAM were not confirmed.
- WhisperX's latest version number and pinned torch version were not shown on the README.
- The `initial_prompt` effect on Arabic-English code-switching is untested in the literature found.

---

## 2. Silence, filler and retake detection

### Takeaway
Silence cutting is a solved, threshold-based problem: dB or RMS threshold plus padding (auto-editor, TimeBolt, Silero VAD). Auto-editor (now a Nim binary, v31.7.2, Oct 2026) exports directly to a Resolve timeline. Filler and retake detection in commercial tools (Gling, AutoCut Repeat, Descript, Selects, TimeBolt UMCHECK) is transcript-driven, but none publish their algorithm. Claude can do retake detection itself from a word-timestamped transcript by finding near-duplicate sentences and keeping the last or most fluent one.

### Cited Findings
**auto-editor (WyattBlue)**
- Repository language is now **Nim**. Latest releases:
  - 31.7.2 (3 Oct 2026)
  - 31.7.0 (2 Oct 2026), moved to ffmpeg 9.0.2 and **bundled whisper.cpp 1.9.4**
  - 31.6.0 (6 Sep 2026)
  — [auto-editor releases](https://github.com/WyattBlue/auto-editor/releases); [README](https://github.com/WyattBlue/auto-editor)
- Edit methods:
  - `audio:threshold=0.04` (default, or dB form such as `audio:-19dB`)
  - `motion:threshold=0.02`
  - Methods can be combined, e.g. `"(or audio:0.03 motion:0.06)"`
  - `--margin` default 0.2 s, can be asymmetric (`0.3s,1.5sec`)
  - `--export resolve`, `premiere`, `final-cut-pro`, `shotcut`, `kdenlive`, `clip-sequence`
  - Preview with `--when-active cut --when-inactive nil`
  — [auto-editor README](https://github.com/WyattBlue/auto-editor)
- **Silero VAD:** a 30+ ms chunk takes under 1 ms on one CPU thread, trained on 6,000+ languages, 8/16 kHz. `pip install silero-vad`, needs torch ≥1.12, ONNX optional. MIT licence, though the badge text is ambiguous. — [snakers4/silero-vad](https://github.com/snakers4/silero-vad)
- **TimeBolt:**
  - "Filter Below Sound Level" dB threshold. Making it more negative (e.g. -35 → -45 dB) captures more speech.
  - On-device waveform analysis at 0.01 s precision, with XML export to Premiere, FCP, Resolve and Camtasia.
  - UMCHECK filler detection is described as three layers (waveform + transcription + custom phrase matching) at $0.03/min. The "100% accuracy" claim is a vendor claim.
  — [TimeBolt Notion docs](https://timebolt.notion.site/Silence-Detection-67e267311a104d7dbb391073c5960d8e); [thegtmdirectory](https://thegtmdirectory.com/tools/timebolt)
- **Recut:** a competitor page says it supports FCPXML but has no UMCHECK equivalent. Unverified. — [Cutsio blog](https://cutsio.com/blog/best-timebolt-alternative-for-silence-removal)
- **Gling:**
  - Cuts silences, fillers and "repeated or failed recording attempts" (bad takes).
  - Suggested cuts go to a review UI before export. Exports XML to Premiere, FCP and Resolve, with transcript-based editing.
  - Reviewers report lower filler accuracy on heavy accents.
  - The method for matching repeated takes is **not publicly documented**.
  — [devtoollab](https://devtoollab.com/ai-tools/gling); [choppingblock.ai](https://www.choppingblock.ai/companies/gling); [softwarereviews](https://www.softwarereviews.com/products/gling)
- **AutoCut Repeat** (Premiere and Resolve plugin):
  - Needs the audio language set for transcription, then the user reviews the detected repeats.
  - Repeat 2.0 (Mar 2026) added a **"Reference Script"** to improve detection.
  - Third-party reviews note false positives.
  — [AutoCut Repeat help](https://autocut.com/help-center/autocut-repeat/introducing); [AutoCut March 2026 blog](https://www.autocut.com/en/blogs/autocut-march-updates/); [Dataconomy](https://dataconomy.com/tools/autocut/)
- **Selects by Cutback** identifies repeated takes, chooses among them and outputs a rough cut for Premiere, FCP and Resolve. "Up to 60%" prep-time saving is a vendor figure. — [MarTech Series](https://martechseries.com/video/cutback-launches-selects-an-ai-pre-editing-tool-for-professional-video-production-teams/)
- **Descript Underlord** removes fillers and silences in one pass and flags bad takes for review (third-party review). — [Sonix review](https://sonix.ai/resources/es/descript-review-pricing/)
- **DaVinci Resolve 20 AI IntelliScript** builds a timeline from a script by matching transcribed clip audio to the script text and picking the best takes. — [CineD](https://cined.com/davinci-resolve-20-released-with-handful-of-ai-assisted-features)
- **video-use cut heuristics** (open-source Claude Code skill):
  - Silences ≥400 ms are the cleanest cut points. 150–400 ms is a phrase boundary that needs visual check. Under 150 ms is unsafe.
  - Never cut inside a word: snap to word boundaries. Pad edges 30–200 ms (launch example 50 ms before, 80 ms after).
  - Add 30 ms audio fades at every cut.
  - Phrase packing breaks on ≥0.5 s silence.
  — [browser-use/video-use SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)

### Inferences
- **Retake detection Claude can run.** Have Claude compare consecutive sentences in the word-timestamped transcript, using normalised Arabic text similarity plus restart cues ("لا لا", "خليني عيد", "يعني", a long pause, then the same opening words). Default to keeping the **last** complete take, as AutoCut Repeat and Selects effectively do. A cheap pre-filter is a fuzzy string ratio over the first N words. This mirrors the "Reference Script" idea: if the user has a script, align to it.
- **Fillers.** Arabic fillers ("يعني", "اممم", "إيه", "هيك") are not in English filler lists. Whisper often omits or normalises fillers, so the video-use rule "verbatim ASR, no normalized fillers" matters. Silero VAD gaps inside segments are a backup signal for "umm" that Whisper dropped.
- **Use motion as well as audio for this channel.** Hands-only cubing footage has silent stretches that are not dead air (e.g. a silent solve). auto-editor's `motion` method, combined with audio (`or audio motion`), avoids cutting silent-but-active solve footage.

### Gaps
- No public algorithm description for Gling, FireCut, Recut or AutoCut Repeat retake matching (text similarity vs audio).
- auto-editor's Windows install route (exe vs pip) was not confirmed from the release assets. Releases list 9 assets but names were not visible. The `auto-editor.com/installing` page was not fetched.

---

## 3. Visual analysis so the LLM "sees" footage

### Takeaway
The standard pattern is:
1. Detect shots (PySceneDetect or ffmpeg `select='gt(scene,X)'`).
2. Sample keyframes at intervals and at shot boundaries.
3. Tile them into **timestamped contact sheets** sized to Claude's vision limits (≤1568 px long edge, ~1.15 MP, ~1,600 tokens per image, ≤20 images per request on stricter surfaces).
4. Have Claude reason over sheet plus transcript.
5. Fetch close-ups only at ambiguous decision points (the video-use approach).

For "search my clips for 'cube exploding'", build a local CLIP/SigLIP 2 frame-embedding index. Optionally add short text captions per B-roll clip from a small local VLM (Qwen3-VL 2B/4B) so Claude can search by text.

### Cited Findings
**Shot detection and contact sheets**
- **PySceneDetect v0.7.2 (11 Oct 2026):**
  - ContentDetector, AdaptiveDetector and ThresholdDetector.
  - `scenedetect -i video.mp4 save-images` and `split-video` (needs ffmpeg or mkvmerge).
  - `pip install scenedetect --upgrade`. Windows MSI installer and portable ZIP are available.
  — [Breakthrough/PySceneDetect](https://github.com/Breakthrough/PySceneDetect)
- **ffmpeg contact sheets:**
  - Sample at a fixed interval, scale, then `tile` (e.g. 10 s interval, 320 px width, 4×3). Order matters: sample, scale, tile. — [techearl](https://techearl.com/ffmpeg-contact-sheet-preview)
  - Scene-based sampling: `select='gt(scene,0.4)',scale=320:-1,tile=5x4`. A higher threshold gives fewer frames. — [videobeaux docs](https://git.terata.org/eessppeelllloo/videobeaux/src/branch/python/docs/programs/utilities/thumbs.md)
  - Use `drawtext` to burn timestamps onto each tile so the model can map tile to time. — [baeldung](https://www.baeldung.com/linux/generate-video-thumbnails-gallery)
- **Claude vision limits:**
  - Images with a long edge over 1568 px, or over ~1,600 tokens, are downscaled. ~1.15 MP is optimal.
  - Cost is ⌈w/28⌉×⌈h/28⌉ visual tokens. 1092×1092 and 784×1568 cost ~1,600 tokens each on Sonnet 4.6.
  - Images under 200 px on an edge degrade quality.
  - For many-image requests, keep each image ≤2000 px per side or use ≤20 images.
  - Opus 4.7 guidance allows 2576 px long edge and 3.75 MP.
  — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision); [Claude computer-use best practices](https://claude.com/blog/best-practices-for-computer-and-browser-use-with-claude)
- **video-use's text-first approach:**
  - The LLM's primary view is a ~12 KB `takes_packed.md` with lines like `[002.52-005.36] S0 <text>`, phrases split on ≥0.5 s silence.
  - A `timeline_view` tool renders a PNG (filmstrip + waveform + word labels) for any time range. It is called **only at decision points**: ambiguous pauses, retake comparisons, cut checks.
  - The same tool runs on the rendered output for self-evaluation.
  — [browser-use/video-use README](https://github.com/browser-use/video-use); [SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)
- **LAVE (IUI 2024)** makes footage LLM-readable by generating **language descriptions of each clip**, then lets an agent plan edits over those descriptions. — [LAVE project page](https://www.dgp.toronto.edu/~bryanw/lave/); [arXiv 2402.10294](https://arxiv.org/abs/2402.10294v1)

**Semantic search over the user's own B-roll**
- **Semantic Eye:** optical-flow motion filter, then CLIP ViT-L-14 on non-static frames, for natural-language search in footage. — [GughanS/semantic-eye](https://github.com/GughanS/semantic-eye)
- **CLIFS:** older proof of concept for free-text search in video, with a Django UI. — [sourcepulse CLIFS](https://www.sourcepulse.org/projects/2336495)
- OpenVINO MobileCLIP video-search notebook. Common pattern: embed sampled frames (e.g. 768-d CLIP vectors) and index them in LanceDB. — [OpenVINO notebook](https://docs.openvino.ai/2025/notebooks/mobileclip-video-search-with-output.html); [search summary](https://aws.amazon.com/blogs/machine-learning/implement-semantic-video-search-using-open-source-large-vision-models-on-amazon-sagemaker-and-amazon-opensearch-serverless/)
- **SigLIP 2:**
  - Sizes: Base, Large (303M), So400m (400M, the recommended balance), Giant (1B).
  - Loads in open_clip via `hf-hub:timm/ViT-B-16-SigLIP2`; needs open-clip-torch ≥2.31.0 and timm ≥1.0.15.
  - Scores are sigmoid, not softmax.
  — [Voxel51 SigLIP2 docs](https://docs.voxel51.com/plugins/plugins_ecosystem/siglip2.html); [HF ViT-B-16-SigLIP2](https://huggingface.co/MyAlbum/ViT-B-16-SigLIP2); [Transformers docs](https://huggingface.co/docs/transformers/main/model_doc/siglip2)
  - Caveat: a TREC 2025 AVS team found SigLIP2 features "did not work at all" on V3C1 in early tests and used CLIP instead. — [TREC paper](https://trec.nist.gov/pubs/trec34/papers/ccilab.avs.pdf)
- **Local VLM captioning:**
  - Ollama has `qwen3-vl:4b` and `qwen3-vl:8b`. The family is marketed for spatial and video understanding. — [Ollama qwen3-vl](https://registry.ollama.ai/library/qwen3-vl)
  - Guides put 8 GB as the minimum for the family and suggest 2B/4B for 8 GB laptops and captioning. — [codersera](https://codersera.com/blog/qwen3-vl-4b-vs-qwen3-vl-8b-benchmarks-vram-guide/)
  - llama.cpp GGUF support since 30 Oct 2025. — [Unsloth docs](https://docs.unsloth.ai/models/qwen3-vl)
- **Commercial equivalents:** Premiere's Media Intelligence (natural-language clip search, GA Apr 2025) and Resolve 21's IntelliSearch are the same idea built in. — [Business Wire/Adobe](https://www.businesswire.com/news/home/20250402472642/en); [PetaPixel Resolve 21](https://petapixel.com/2026/06/03/davinci-resolve-21-officially-released-with-new-photo-editing-ai-tools/)
- **Motion signal:** auto-editor's `motion:threshold` measures the fraction of changed pixels. — [auto-editor README](https://github.com/WyattBlue/auto-editor)

### Inferences
- **Contact sheets for this channel.**
  - A 4×4 grid of 384×216 tiles is 1536×864, about 55×31 = ~1,700 tokens. A 10–20 min video at one frame per 3–5 s is 120–400 frames, or ~8–25 sheets: roughly 15–40k tokens. That is affordable for Claude Code.
  - Use a denser grid (1 fps) only around candidate edit points.
- **What to burn into each tile.** Hands-and-cube footage looks very similar frame to frame. Burned-in timestamps and a per-tile motion score are needed so Claude can tell "scramble / inspection / solve / explanation" phases apart.
- **Gameplay.** Scene cuts and HUD changes are better signals. Add OCR of HUD or score text if needed, e.g. PaddleOCR/EasyOCR (not researched here).
- **Hosting the B-roll index.**
  - **SigLIP 2 So400m or ViT-B/16 SigLIP2 (or OpenCLIP ViT-L/14)** fits easily in 8 GB at batch inference. Parameter counts above suggest roughly 1–2 GB fp16 for So400m; not measured.
  - Embed 1 frame per 1–2 s of each B-roll clip, store in a numpy/LanceDB/FAISS file, and query with English text. The text encoders are English-centric, so Claude should translate Arabic transcript keywords into English queries.
  - Test CLIP vs SigLIP on his own clips given the TREC caveat.
- **Captions per clip.** A one-off pass of Qwen3-VL-4B (Ollama, Q4) over each B-roll clip's 3–6 keyframes produces text captions ("cube explodes into pieces on desk") that Claude can grep. That is cheaper than sending all B-roll frames to Claude.

### Gaps
- No measured VRAM or throughput for SigLIP2 or Qwen3-VL-4B on an RTX 4060 Laptop.
- No benchmark of contact-sheet grid density vs Claude's temporal accuracy was found.
- PySceneDetect speed figures are only at scenedetect.com/benchmarks (not fetched).
- No source specifically on OCR for gameplay HUDs.

---

## 4. How commercial tools pick B-roll, cuts, zooms and SFX (signals and rules)

### Takeaway
Across vendors, B-roll is **transcript-driven**: keywords, entities and sentiment per sentence, with clips placed where the matching words are spoken. A user-facing **frequency/density slider** and **min/max clip duration** control how much. Zooms are driven by **audio analysis or "key moments" in speech**, with settings for zoom amount, % of video zoomed and min/max zoom length. SFX are mostly paired with transitions or B-roll insertions rather than independently detected. No vendor publishes its algorithm; the most concrete public spec is AutoCut's settings list. One major ecosystem change matters for this user: **Resolve 21.1 (Sep 2026) added a built-in MCP server for Claude/Claude Code, but only in Studio, and moved Python scripting to Studio-only.**

### Cited Findings
**AutoCut** (Premiere and Resolve plugin)
- **AutoZoom** analyses timeline audio and places zooms as editable adjustment layers. Settings: anchor point, min/max zoom amount, share of video zoomed, min/max zoom duration. — [AutoCut AutoZoom page via search](https://autocut.com/en/autozoom)
- **AutoB-Roll** analyses dialogue, suggests stock clips, and lets the user search further. Settings: min/max B-roll duration, which controls count and transitions. It downloads and inserts after review and supports 80+ languages. — [AutoCut AutoBRoll](https://autocut.com/en/autobroll)
- Feature list: AutoCaptions, Silences, Podcast, Zoom, Repeat, Resize, B-Roll, Profanity Filter, Viral clips, Chapters. No auto-SFX found. — [AutoCut features](https://autocut.com/help-center/autocut-overview/autocut-features)
- **AutoResize** keeps the subject in frame. — [AutoCut AutoResize](https://autocut.com/en/autoresize)

**FireCut** (Premiere 2022+, Windows/macOS)
- Zooms are placed at AI-detected "key moments" in speech to fake a multicam feel from one 4K shot.
- B-roll is suggested from Storyblocks with the licence included.
- Also does chapter detection with divider clips, silence/filler cutting and captions. No SFX feature confirmed.
— [FireCut zoom blog](https://firecut.ai/blog/effectively-adding-dynamic-zooms-to-your-video-with-firecut/); [FireCut B-roll](https://firecut.ai/features/b-roll); [FireCut Premiere](https://firecut.ai/premiere-pro)

**Submagic**
- "Magic B-roll" reads the transcript and inserts stock or user-uploaded clips, with a slider for how often B-roll appears. Manual add is the "+" on a subtitle line, so B-roll is anchored to caption lines.
- "99% accuracy" is a marketing claim.
— [Submagic B-roll feature](https://submagic.co/features/b-roll); [Submagic help](https://care.submagic.co/en/article/how-to-add-b-rolls-on-submagic-1kk7vj0)
- Auto zooms are "synchronized to your transcript", with 6 styles. "Magic Transitions" are transitions between B-rolls with animated emojis **with sound**. — [Submagic auto zooms](https://submagic.co/features/auto-zooms); [Submagic integrations](https://www.submagic.co/integrations)

**OpusClip**
- Virality score 0–99 built from **hook, flow, value, trend**. ClipAnything checks relevance to the user's prompt. — [OpusClip help: virality score](https://help.opus.pro/docs/article/virality-score)
- It is marketed as multimodal (dialogue, visuals, sentiment). Reviewers say the free tier clips by words only. A third party reports the model was trained on engagement data from ~6M users (company claim). — [castmagic review](https://www.castmagic.io/software-reviews/opus-clip); [techsy](https://techsy.io/en/blog/opusclip-vs-vizard)

**Captions.ai, InVideo, Pictory**
- **Captions.ai "AI Edit":** chat-prompted. Generates custom (generative) B-roll, SFX, transitions and dynamic zooms on "specific moments". — [Captions edit-with-AI](https://captions.ai/features/edit-with-ai)
- **InVideo:** analyses **keywords and sentiment of each sentence** and places clips at the moment the matching words are spoken. Later marketing claims context/intent/narrative analysis. — [InVideo blog](https://info.invideo.io/blog/automatic-b-roll-selection-video-script-invideo)
- **Pictory:** splits text into scenes and keyword-matches stock to each scene. Reviewers call it overly literal, e.g. email "open rates" → people opening physical mail. — [fast.io Pictory review](https://fast.io/resources/pictory-ai-review-2026/); [marcandrews comparison](https://marcandrews.com/invideo-vs-pictory-2026-which-ai-video-tool-wins/)

**Descript Underlord**
- "Bespoke B-roll" and transcript-based B-roll placement suggestions.
- Jan 2026 update made **Claude Sonnet 4.5 the default model** (Opus 4.6 for enterprise). — [Claude customer story: Descript](https://claude.com/es/customers/descript)
- A third party says Descript's API entered open beta in 2026 with MCP. Unverified. — [Sonix review](https://sonix.ai/resources/es/descript-review-pricing/)

**Eddie AI and Selects**
- **Eddie AI:** runs locally as a Resolve workspace script or as a panel in other NLEs. Logs footage, finds soundbites and assembles a rough cut from Resolve bins including multicam. 2.0 added A/B-roll logging. — [CineD Eddie Resolve extension](https://www.cined.com/eddie-ai-extension-for-davinci-resolve-released-virtual-editing-assistant/); [RedShark NAB 2026](https://www.redsharknews.com/eddie-ai-nab-2026-ai-video-editing-rough-cut)
- **Selects (Cutback):** repeated-take detection plus rough cut. Pricing from $16/mo. — [MarTech Series](https://martechseries.com/video/cutback-launches-selects-an-ai-pre-editing-tool-for-professional-video-production-teams/)

**DaVinci Resolve**
- **Resolve 20** (2025): AI IntelliScript, AI Animated Subtitles (word-synced) and AI Audio Assistant (auto mix). — [CineD Resolve 20](https://cined.com/davinci-resolve-20-released-with-handful-of-ai-assisted-features)
- **Resolve 21** (final ~Jun 2026): IntelliSearch (find clips), CineFocus, Photo page, Krokodove Fusion tools. — [PetaPixel](https://petapixel.com/2026/06/03/davinci-resolve-21-officially-released-with-new-photo-editing-ai-tools/); [Newsshooter](https://www.newsshooter.com/2026/06/02/davinci-resolve-21-final-release/)
- **Resolve 21.1** (Sep 2026):
  - Built-in **MCP server in Resolve Studio**, set up via File > Setup AI Assistants. Works with Claude, Claude Code and Codex. Blackmagic's examples include highlight edits from long-form video, removing unwanted clips and batch rendering. — [Digital Production](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/); [YMCinema](https://ymcinema.com/2026/09/17/davinci-resolve-21-1-mcp-ai-assistants-control-edit/)
  - **Python scripting now requires Studio.** Blackmagic says the Python API was used to unlock Studio features in free. Puget Systems says scripting was "entirely removed" from free 21.1 with no simple workaround, and recommends staying on 21.0. — [Blackmagic 21 readme](https://www.blackmagicdesign.com/support/content/readme/59dd4eef1f4941c29fb8dc48b33f5c87); [Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)
  - A third-party MCP project says Lua scripts still run from Workspace > Scripts on free 21.1. Whether Python runs in the free Console is unconfirmed. — [mcpservers.org Lua MCP](https://mcpservers.org/servers/saadk408/davinci-resolve-lua-mcp); [search summary](https://www.typingmind.com/mcp/samuelgursky-davinci-resolve-mcp)

**Adobe Premiere Pro**
- Generative Extend (GA Apr 2025, Firefly), Media Intelligence search and caption translation (27 languages). No auto-B-roll feature found. — [Business Wire](https://www.businesswire.com/news/home/20250402472642/en); [OWC blog](https://www.owc.com/blog/adobe-powers-up-premiere-pro-with-several-new-ai-features-and-workflow-enhancements)

**Research baseline: B-Script** (Adobe Research/CHI 2019)
- Transcript-based B-roll editor with a recommender trained on expert-annotated data, recommending **both B-roll position and content**.
- Study with 110 participants: B-roll insertion was easier and faster in the transcript interface, and videos were rated more engaging with recommendations.
— [arXiv 1902.11216](https://arxiv.org/abs/1902.11216); [Adobe Research](https://research.adobe.com/publication/b-script-transcript-based-b-roll-video-editing-with-recommendations/)

### Inferences
- **Signals and rules to copy.** These are derived from the documented settings above. The numbers are proposed defaults, not vendor-published.
  - **B-roll triggers.** Concrete nouns, entities or "show-able" phrases in a sentence (e.g. "cube explodes", "world record", "PLL algorithm") trigger B-roll. Topic or section changes trigger a title card or chapter divider.
  - **B-roll placement.** Start at the trigger word's start time minus 0.1–0.3 s. Last 2–5 s, clamped by min/max duration, and never across a sentence boundary into an unrelated topic.
  - **Density cap.** At most one B-roll per N seconds, which mirrors the density sliders.
  - **Zooms.** Punch-ins (110–130%) on emphasis: a loudness/onset peak within a sentence, or an emphatic or key-term word. Reset on the next sentence or cut. Cap zoomed share of runtime (AutoCut exposes this as "% of video zoomed"), with min/max zoom length.
  - **SFX.** Whoosh on B-roll entry and exit or a transition. Pop or ding on on-screen text and emoji. Hit on a punch-in. This matches Submagic's coupling of transitions with sound.
- **Face-based features don't apply.** He never shows his face, so face-tracking reframing (AutoResize, FireCut's speaker punch-in) is not useful. Zoom anchor points should target the motion centroid (hands and cube), which can be estimated from frame differencing.
- **Resolve 21.1 forks the integration path.**
  - **Studio 21.1:** Claude Code can drive Resolve through Blackmagic's MCP.
  - **Free 21.1:** Python scripting is gone. The skill should emit **importable timeline files** (FCPXML/EDL/OTIO, or auto-editor's `--export resolve`) plus marker lists, or stay on Free 21.0.
  - This should be confirmed with the parallel Resolve-API research.

### Gaps
- No vendor documents the exact signal weights or thresholds for zoom or B-roll timing. AutoCut's and Submagic's pages could not be read in full here (domain not fetchable).
- No patents found describing these products' B-roll or zoom logic (not searched in depth).
- Auto-SFX placement logic is undocumented for every vendor checked. Vizard and Gling B-roll logic were not found.
- The exact Resolve version installed by the user (Free vs Studio, 21.0 vs 21.1) is unknown.

---

## 5. LLM-based edit-decision research and open-source projects (and their output schemas)

### Takeaway
Research and open-source systems converge on one pattern:
1. Convert footage to text: transcript with timestamps, plus language descriptions of clips.
2. Have the LLM emit a **structured JSON edit plan**: ranges with start/end, source, rationale/justification, and narrative function, or a sequence of tool calls on a timeline.
3. Render deterministically, often with a critic or self-evaluation loop.

The closest ready-made template for a Claude skill is **browser-use/video-use** (MIT, Claude Code-compatible). Its EDL fields and "hard rules" are directly reusable, but it uses cloud ElevenLabs Scribe, which should be swapped for local faster-whisper.

### Cited Findings
**browser-use/video-use** (open source, MIT, released ~Jul 2026)
- **Pipeline:** Transcribe → Pack → LLM reasons → EDL → Render (ffmpeg) → Self-eval, with up to 3 fix rounds. Works with Claude Code, Codex and other shell agents.
- **Transcription:** ElevenLabs Scribe (word timestamps, speakers, audio events), so it needs an API key.
- **Other features:** filler removal, auto colour grade, burned subtitles, animation overlays via HyperFrames/Remotion/Manim/PIL.
— [video-use README](https://github.com/browser-use/video-use)
- Reported stars: 10k–15k+ (snapshots conflict). — [remio](https://www.remio.ai/post/browser-use-releases-open-source-ai-video-editing-skill-video-use); [themenonlab](https://themenonlab.blog/blog/video-use-ai-video-editing-claude-code-agents)
- **EDL schema** (top level):
  - `version`, `sources`, `ranges`, `grade`, `overlays`, `subtitles`, `total_duration_s`
  - Each **range**: `{source, start, end, beat, quote, reason}`, e.g. `{"source": "C0103", "start": 2.42, "end": 6.85, ...}`
  - **overlays**: `file`, `start_in_output`, `duration`
- **12 hard rules**:
  - Subtitles last.
  - Per-segment extract then lossless concat.
  - 30 ms audio fades.
  - `setpts=PTS-STARTPTS+T/TB` for overlays.
  - Never cut inside a word. Pad 30–200 ms.
  - Word-level verbatim ASR.
  - Cache transcripts.
  - **Get user approval of the plain-English strategy before cutting.**
  - Outputs go to `<videos_dir>/edit/`.
- **Overlay timing:** start early by the reveal duration so the landing frame hits the "payoff word". Hold ≥1 s.
- **Self-eval:**
  - `timeline_view` on the output at every cut ±1.5 s.
  - Check duration with `ffprobe`.
  - Measure loudness with `ffmpeg -af ebur128=peak=true`. Report the numbers "since the agent can't listen".
— [video-use SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)

**Research systems**
- **LAVE** (Wang et al., IUI 2024, arXiv 2402.10294):
  - An LLM agent plans and executes edits over auto-generated clip descriptions: semantic retrieval, storyboarding, trimming.
  - Trim output is JSON: `"segment": ["start", "end", "rationale"]` (frame IDs plus rationale).
  - User study with 8 participants.
  — [LAVE project](https://www.dgp.toronto.edu/~bryanw/lave/); [arXiv HTML](https://arxiv.org/html/2402.10294v1)
- **ExpressEdit** (Tilekbay et al., KAIST/Yale, IUI '24, arXiv 2403.17693):
  - Natural language plus sketching. An LLM and vision models parse **temporal, spatial and operational references** in commands.
  - 10 participants, SUS 75.7. Users wanted smoother transitions and audio polish.
  — [arXiv 2403.17693](https://arxiv.org/abs/2403.17693v1)
- **EditDuet** (arXiv 2509.10761, 2025):
  - Editor and Critic LLM agents for **B-roll over A-roll** timelines.
  - The Editor (Llama3.1-8B) uses tool calls `search_collection`, add/remove/move/switch clip, `DONE`. The Critic gives natural-language feedback or triggers render.
  - One review calls the headline result statistically shaky.
  — [arXiv 2509.10761](https://arxiv.org/html/2509.10761v1); [Pith review](https://pith.science/paper/2509.10761)
- **Prompt-Driven Agentic Video Editing System** (arXiv 2509.16811): selected clips are serialised into a **JSON edit plan with time ranges, visual justifications, narrative function and linked voice-over segments**, for deterministic rendering and auditability. — [arXiv 2509.16811](https://arxiv.org/abs/2509.16811)
- **RankCut** (IUI '26): three-stage LLM ranking pipeline that selects time-aligned extractive transcript spans, with a marker-based review UI. — [RankCut](https://wtmbib.informatik.uni-hamburg.de/Basilic/publis/991/)
- **Text-to-Edit** (arXiv 2501.05884): MLLM-driven end-to-end ad video creation. Only the title and abstract were seen. — [arXiv 2501.05884](https://arxiv.org/html/2501.05884)

**Other agent skills**
- **skills.sh "generate-edit-decision-list"** produces a validated `edl.json` (cut points, transitions, captions) from a script or timestamped transcript. — [skills.sh](https://www.skills.sh/gooseworks-ai/gooseworks-ads-skills/generate-edit-decision-list)

### Inferences
- **Recommended skill output schema** (a superset of video-use and the agentic-editing JSON plan): JSON with
  - `cuts[]`: `{start, end, reason, confidence}`
  - `broll[]`: `{at, duration, clip_path or search_query, trigger_word, reason}`
  - `zooms[]`: `{start, end, scale, anchor_xy, ease, reason}`
  - `sfx[]`: `{at, file or category, gain_db, reason}`
  - `titles[]` and `markers[]`
  - Every item carries a `quote` (the Arabic words at that time) and a `reason`, so the user can audit them.
  - Render this to a human-readable list ("01:23.4 → B-roll X ...") **and** to Resolve-importable form (FCPXML/EDL, or Resolve markers via MCP/Lua).
- **Adopt video-use's "propose plain-English strategy, wait for approval" rule.** It matches the user's no-surprises security posture.

### Gaps
- Could not read full papers (arXiv not fetchable). Quantitative results for EditDuet and the agentic-editing paper, and whether either handles zooms or SFX, are unverified.
- No research found specifically on **automatic SFX placement** or **zoom/punch-in placement** by LLMs.
- No Arabic-language LLM editing study found.

---

## 6. Audio-based emphasis detection (zooms/SFX) and beat detection (music sync)

### Takeaway
Commercial auto-zoom tools say they "analyse the audio" but publish no algorithm. A simple local approach is enough:
- Compute short-time loudness/RMS and onset strength (librosa).
- Find local peaks relative to a rolling baseline within each sentence.
- Snap each peak to the nearest word start from the transcript, and let Claude pick which peaks matter semantically.
- For music, use **Beat This!** (ISMIR 2024, MIT) or librosa's `beat_track` to get beat and downbeat times for cut sync.

### Cited Findings
- **AutoCut AutoZoom** "analyses the audio" of the timeline to decide zoom positions. — [AutoCut AutoZoom](https://autocut.com/en/autozoom)
- **FireCut** zooms on "key moments" detected in speech. — [FireCut blog](https://firecut.ai/blog/effectively-adding-dynamic-zooms-to-your-video-with-firecut/)
- **Submagic** zooms are "synchronized to your transcript". — [Submagic auto zooms](https://submagic.co/features/auto-zooms)
- **librosa `beat_track`** (v0.11.0) is a dynamic-programming beat tracker: onset strength → tempo estimate from onset autocorrelation → peaks consistent with that tempo. It accepts a precomputed `onset_envelope`. — [librosa docs 0.11.0](https://librosa.org/doc/0.11.0/generated/librosa.beat.beat_track.html)
- **Beat This!** (Foscarin, Schlüter, Widmer, ISMIR 2024, arXiv 2407.21658):
  - Beat and downbeat tracking without DBN post-processing.
  - Models: `final0–2` (~78 MB each) and `small0–2` (~8.1 MB).
  - GPU by default with CPU fallback; `--float16` option.
  - Install: `pip install tqdm einops soxr rotary-embedding-torch` then `pip install beat-this`. Needs PyTorch ≥2.0, plus ffmpeg for non-WAV.
  - CLI: `beat_this file -o out.beats`. Python: `File2Beats`. MIT licence.
  — [CPJKU/beat_this](https://github.com/CPJKU/beat_this)
- **video-use** measures loudness with ffmpeg's `ebur128` filter and per-section RMS, and reports numbers because the agent cannot listen. — [video-use SKILL.md](https://raw.githubusercontent.com/browser-use/video-use/main/SKILL.md)

### Inferences
- **Emphasis heuristic.** None of the vendors publish one, so this is a proposal.
  1. Compute RMS in dBFS at 10 ms hop. Optionally use pyloudnorm short-term LUFS (not researched here).
  2. Compute a 3–5 s rolling median per sentence.
  3. Flag words whose peak exceeds the rolling median by ≥6 dB, or by the 90th percentile of the onset envelope, and that are preceded by a ≥250 ms pause ("dramatic pause then punch").
  4. Merge flags closer than ~4 s and cap zoom frequency.
  5. Claude then filters candidates by meaning, e.g. "the record time", "the trick", "watch this".
- **Gameplay channel.** Loudness peaks will often be game audio (explosions), not voice. Run emphasis detection on a **voice-only stem**, either a separate mic track if he records one or a separated stem. Demucs/UVR-style separation was not researched here.
- **Music sync.** Snap B-roll and section cuts to the nearest downbeat within ±150 ms of the speech-derived cut point. Never move a speech cut inside a word.

### Gaps
- No vendor or paper documents the thresholds commercial auto-zoom tools use.
- pyloudnorm, librosa RMS-peak recipes and Demucs were not verified in this research. They are standard tools but not sourced here.
- Beat This! vs madmom accuracy numbers are in the paper's Table 2 (not fetched).

---

## 7. Recommended practical local pipeline for Win11 + RTX 4060 8 GB, with install list and processing times

### Takeaway
A fully local pipeline fits this laptop if GPU models run **sequentially**, never two at once in 8 GB:
1. ASR: faster-whisper large-v3.
2. Optional Arabic CTC re-alignment.
3. Silence/motion analysis: auto-editor or Silero.
4. Shot detection plus timestamped contact sheets: PySceneDetect or ffmpeg.
5. Audio emphasis peaks: librosa.
6. A one-off CLIP/SigLIP index of the B-roll library.
7. Claude reads transcript + sheets + candidates, proposes a plain-English plan, then emits a JSON EDL that becomes a timestamped instruction list and a Resolve-importable timeline.

Expected wall-clock for a 10–20 min video is about 5–12 minutes of preprocessing, excluding first-time B-roll indexing. These are estimates from the benchmarks above, not measured on this machine.

### Cited Findings (component facts used for the estimate)
- **faster-whisper large-v3 on RTX 4060 8 GB:** RTF ~0.16–0.25 FP16, ~0.12 INT8. — [GigaGPU](https://gigagpu.com/whisper-large-v3-on-rtx-4060-benchmark/); [jisaku](https://jisaku.com/posts/ai-bench-faster-whisper-speed-2026)
- **faster-whisper VRAM** (large-v2 class): fp16 ~4.5 GB non-batched, ~6.1 GB at batch 8; int8 ~2.9 GB. Needs CUDA 12 cuBLAS + cuDNN 9; Windows DLLs via Purfview archive. — [faster-whisper README](https://github.com/SYSTRAN/faster-whisper)
- **WhisperX:** <8 GB for large-v2 at beam 5. CUDA toolkit 12.8 on Windows. — [whisperX README](https://github.com/m-bain/whisperX)
- **Silero VAD:** <1 ms per 30 ms chunk on CPU. — [silero-vad](https://github.com/snakers4/silero-vad)
- **pyannote community-1:** ~31 s per hour of audio on H100. Not needed for a single speaker. — [pyannote-audio](https://github.com/pyannote/pyannote-audio)
- **PySceneDetect 0.7.2:** pip or Windows MSI/portable ZIP. — [PySceneDetect](https://github.com/Breakthrough/PySceneDetect)
- **auto-editor 31.7.x:** bundles ffmpeg 9.0.2 and whisper.cpp. Exports a Resolve timeline. — [auto-editor releases](https://github.com/WyattBlue/auto-editor/releases)
- **Claude image budget:** ≤1568 px long edge, ~1,600 tokens per image, ≤20 images per request on stricter surfaces. — [Claude vision docs](https://platform.claude.com/docs/en/build-with-claude/vision)
- **Resolve:**
  - Studio 21.1 has a native MCP server for Claude Code. — [Digital Production](https://digitalproduction.com/2026/09/08/resolve-21-1-adds-mcp-and-finally-gets-presets/)
  - Free 21.1 lost Python scripting. — [Puget Systems](https://www.pugetsystems.com/blog/2026/09/10/how-davinci-resolve-free-v21-1-scripting-changes-affect-puget-bench/)

### Inferences

**Pipeline**

| Stage | Tool | Est. time (15 min video) | GPU? |
|---|---|---|---|
| 0. Extract 16 kHz mono WAV + proxy | ffmpeg | <30 s | no |
| 1. ASR + word timestamps | faster-whisper large-v3 fp16 (already installed), `language="ar"`, `word_timestamps=True`, `vad_filter=True` | ~2.5–4 min (RTF 0.16–0.25) | yes, ~4.5–6 GB |
| 1b. Optional re-alignment | WhisperX align (`jonatasgrosman/wav2vec2-large-xlsr-53-arabic`) or ctc-forced-aligner | ~0.5–1.5 min (guess) | yes, ~1–2 GB (guess) |
| 1c. Term fix-up | Claude post-pass with cubing glossary (Arabic-script → "F2L/PLL/OLL") | n/a | no |
| 2. Silence/motion map | auto-editor `--edit "(or audio:0.04 motion:0.02)"`; export a cut list, or `--export resolve` | ~0.5–2 min (guess) | no |
| 3. Shots + contact sheets | PySceneDetect `detect-adaptive` + ffmpeg `fps=1/3,scale=384:-1,drawtext(pts),tile=4x4` → ~8–20 sheets ≤1536 px | ~1–2 min (guess) | no |
| 4. Emphasis candidates | librosa RMS/onset peaks snapped to word starts; ffmpeg `ebur128` summary | <30 s | no |
| 5. B-roll library index (one-off, then incremental) | open_clip SigLIP2 ViT-B/16 or So400m, frames every 1–2 s → `.npy` / LanceDB; optional Qwen3-VL-4B captions via Ollama | depends on library size (minutes per hour of B-roll, guess) | yes |
| 6. Claude reasoning | Read `transcript_packed.md` (video-use style `[mm:ss.s-mm:ss.s] text`), sheets, candidate lists; propose a plain-English plan; on approval emit JSON EDL | n/a | no |
| 7. Output | Human list ("01:23.4 → B-roll `cube_explode_02.mp4` 3.0 s; 01:30.0 punch-in 120% anchor hands; 01:31.0 whoosh") + FCPXML/EDL/markers or Resolve Studio MCP | n/a | no |

**Total preprocessing:** ~5–12 min per 10–20 min video. Faster with int8 or batched faster-whisper (int8 batched ~4.5 GB).

**Fitting 8 GB and 16 GB RAM**
- Run GPU stages one at a time and free models between stages (`del model; torch.cuda.empty_cache()`, or separate processes).
- Do not keep Ollama's VLM loaded while Whisper runs.
- 16 GB system RAM is enough if proxies are used and frames are streamed rather than all decoded into memory.

**Install list** (for the user's approval; he already has faster-whisper, its CUDA libs, and presumably ffmpeg)
- **Required:**
  - ffmpeg (if not already on PATH)
  - `pip install scenedetect` (or Windows MSI)
  - `pip install librosa soundfile`
  - `pip install numpy pillow`, if not present (contact sheets)
- **Strongly useful:**
  - **auto-editor** (standalone binary from GitHub releases, or pip; route unconfirmed)
  - `pip install silero-vad`, only if not relying on faster-whisper's built-in VAD
- **For B-roll search:**
  - `pip install open-clip-torch>=2.31 timm>=1.0.15` (torch already present via faster-whisper? faster-whisper uses CTranslate2, **not** torch, so torch+CUDA may be a new ~2–3 GB install)
  - Optional: `pip install lancedb` or `faiss-cpu`
- **Optional alignment:** `pip install whisperx` (pulls torch, pyannote; CUDA 12.8 toolkit on Windows) **or** `pip install git+https://github.com/MahmoudAshraf97/ctc-forced-aligner.git`. The latter's default MMS model is non-commercial (CC-BY-NC), which matters for a monetised channel, so use the jonatasgrosman Arabic model instead.
- **Optional captions:** Ollama + `ollama pull qwen3-vl:4b`.
- **Optional music sync:** `pip install beat-this` plus its deps (`tqdm einops soxr rotary-embedding-torch`), needs torch ≥2.0.
- **Not needed:** pyannote/diarization (single speaker); stable-ts (archived May 2026).

**Resolve hand-off**
- **If he runs Studio 21.1:** the skill can use Blackmagic's MCP.
- **If he runs Free 21.1:** Python is blocked, so output importable files (EDL/FCPXML/auto-editor Resolve export) and marker CSVs. Lua scripting may still work but is unverified.

### Gaps
- None of the stage timings except ASR were benchmarked. Stages 1b, 2, 3 and 5 are rough guesses that should be measured on his laptop. Laptop 4060s also run at lower power limits than desktop cards.
- Whether faster-whisper `hotwords`/`initial_prompt` fixes Latin-script cubing terms in Arabic speech is untested.
- auto-editor's Windows install method and whether its bundled whisper.cpp adds a transcript-based edit mode were not confirmed.
- Exact torch/CUDA wheel versions compatible with both open_clip and WhisperX on Windows in Oct 2026 were not checked.
