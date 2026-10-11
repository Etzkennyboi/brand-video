# 🎬 THE UNTOLD TRUTH — Autonomous Video Production Studio

> **An automated production engine that writes, voices, paces, animates, and renders viral 9:16 vertical shorts in under 60 seconds.**

---

## ⚡ Highlights

- **Signature Cloned Voice**: Synthesizes speech using the signature **Video 5** cloned voice (F5-TTS) conditioned on verbatim reference audio and accelerated to `1.14x` viral cadence.
- **Pure 500% Boosted Soundtrack**: Integrates `soundtrack_from_video5.mp3` with EBU R128 dynamic loudness limiting and warmth compand EQ.
- **Millisecond Speech Synchronization**: Aligns scene cuts and amber kinetic pop captions to exact word boundaries using Faster-Whisper.
- **7-Script Tournament Engine**: Automatically drafts 7 contrarian psychological scripts, scores them on a 100-point viral retention index, and produces the top 3 champions.
- **High-CTR Cover Thumbnails**: Generates dark-vignette cover art with custom typography and brand badges.
- **Multi-Token Rollover Pool**: Automatically rotates between Hugging Face API tokens to eliminate ZeroGPU quota downtime.
- **Local Studio Dashboard**: Live web preview dashboard to inspect videos, thumbnails, and copy ready-to-publish metadata with one click.

---

## 📂 Repository Structure

```
the_untold_truth/
├── assets/
│   ├── bgm/
│   │   └── soundtrack_from_video5.mp3       # 500% boosted master piano score
│   ├── visual_vault/                        # 100 9:16 cinematic visuals + catalog.json
│   └── ref_voice_vid5.wav                   # Master reference audio clip
├── config/
│   ├── brand_rules.json                     # Branding tokens, subtitles, & audio rules
│   └── viral_topics_vault.json              # Curated psychological/contrarian topics
├── core/
│   ├── script_director.py                   # 5-beat retention narrative director
│   ├── voice_synthesizer.py                 # F5-TTS cloner with multi-token rollover
│   ├── subtitle_generator.py                # Amber kinetic pop ASS subtitle engine
│   ├── visual_selector.py                   # Whisper boundary alignment & semantic matching
│   ├── single_pass_render.py                # Parallel camera motion & single-pass compositor
│   └── thumbnail_generator.py               # Auto-generating cover thumbnails
├── out/
│   ├── ready_to_publish/                    # Master MP4s, cover JPGs, and metadata JSONs
│   └── drafts/                              # [Gitignored] Intermediate render files
├── engine.py                                # Single video production engine
├── batch_producer.py                        # 7-script candidate tournament & batch renderer
├── build_dashboard.py                       # Local HTML studio builder
├── preview_dashboard.html                   # Dark-mode dashboard preview
└── .env.example                             # Environment token template
```

---

## 🚀 Quick Start

### 1. Requirements
- Python 3.10+
- FFmpeg (added to PATH or specified in `config/brand_rules.json`)

### 2. Environment Setup
Copy `.env.example` to `.env` and add your Hugging Face tokens:
```bash
cp .env.example .env
```
Edit `.env`:
```ini
HF_TOKENS=hf_token1,hf_token2,hf_token3
```

### 3. Generate a Single Video
```bash
# Auto mode (cycles through topics vault):
python the_untold_truth/engine.py --auto

# Custom topic:
python the_untold_truth/engine.py --topic "The Myth of Loyalty at Work"
```

### 4. Run the 7-Script Tournament (Top 3 Production)
```bash
# Preview the ranking leaderboard without rendering:
python the_untold_truth/batch_producer.py --dry-run

# Draft 7 scripts, rank, and render top 3 videos:
python the_untold_truth/batch_producer.py --candidates 7 --top 3
```

### 5. View Dashboard
Open `the_untold_truth/preview_dashboard.html` in any web browser to preview rendered videos, copy YouTube/TikTok titles, descriptions, and hashtags.

---

## ⚖️ License
Proprietary — Built for **THE UNTOLD TRUTH** media brand.
