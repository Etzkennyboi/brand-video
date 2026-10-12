"""
Colab Native Production Engine for THE UNTOLD TRUTH & PROF LAYI
Produces full master videos in ~40-50s on Colab's T4 GPU.
"""

import os
import sys
import time
import shutil
import subprocess

# Ensure repo root is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from core.script_director import ScriptDirector
from core.visual_selector import VisualSelector
from core.subtitle_generator import SubtitleGenerator
from core.voice_synthesizer import VoiceSynthesizer, sanitize_voice_text
from core.single_pass_render import SinglePassRender
from core.thumbnail_generator import ThumbnailGenerator

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"

class ColabMasterEngine:
    def __init__(self, personality="untold_truth"):
        self.personality = personality
        self.brand_title = "PROF LAYI" if "layi" in personality.lower() else "THE UNTOLD TRUTH"
        
        self.director = ScriptDirector(brand_title=self.brand_title, personality=personality)
        self.selector = VisualSelector(
            catalog_path=os.path.join(BASE_DIR, "assets", "visual_vault", "catalog.json"),
            images_dir=os.path.join(BASE_DIR, "assets", "visual_vault", "images")
        )
        
        # In Colab, we can use CUDA for Whisper
        import torch
        device = "cuda" if torch.cuda.is_available() else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        self.subtitles = SubtitleGenerator(model_size="base", device=device, compute_type=compute_type)
        
        self.voice = VoiceSynthesizer(speed_factor=1.14)
        self.renderer = SinglePassRender(brand_title=self.brand_title, watermark_text=self.brand_title)
        self.thumb_gen = ThumbnailGenerator(brand_title=self.brand_title)

    def produce_video(self, topic_input, personality=None, out_name=None):
        t0 = time.time()
        p = personality or self.personality
        brand_label = "PROF LAYI" if "layi" in p.lower() else "THE UNTOLD TRUTH"

        print("=" * 70, flush=True)
        print(f"🎬 [COLAB T4] PRODUCING MASTER SHORT: {brand_label}", flush=True)
        print("=" * 70, flush=True)

        # 1. Script
        print("\n[1/5] Directing script...", flush=True)
        if isinstance(topic_input, dict) and "beats" in topic_input:
            story = topic_input
        else:
            story = self.director.generate_script(topic_input, personality=p)

        title = story["title"]
        slug = out_name or title.lower().replace(" ", "_")[:35]
        
        out_dir = os.path.join(BASE_DIR, "out", "ready_to_publish")
        drafts_dir = os.path.join(BASE_DIR, "out", "drafts")
        os.makedirs(out_dir, exist_ok=True)
        os.makedirs(drafts_dir, exist_ok=True)

        raw_audio = os.path.join(drafts_dir, f"{slug}_raw.wav")
        tight_audio = os.path.join(drafts_dir, f"{slug}_tight.wav")

        # 2. Voiceover Synthesis
        print("\n[2/5] Voiceover synthesis via Colab T4 GPU...", flush=True)
        ref_clip = os.path.join(BASE_DIR, "assets", "ref_voice_vid5.wav")
        ref_text = "The word karma is a word used by losers. People use it when they're too powerless to get justice themselves."
        
        self.voice.synthesize_speech(
            text=story["full_script"],
            output_wav=raw_audio,
            ref_audio=ref_clip,
            ref_text=ref_text,
            voice_engine="f5"
        )
        self.voice.tighten_cadence(raw_audio, tight_audio, speed_factor=1.14)

        # 3. Subtitles
        print("\n[3/5] Faster-Whisper GPU subtitle extraction...", flush=True)
        words_data = self.subtitles.transcribe_words(tight_audio)
        ass_path = os.path.join(drafts_dir, f"{slug}_captions.ass")
        self.subtitles.generate_ass_file(words_data, ass_path, title=title)

        # 4. Metaphorical Scene Alignment
        print("\n[4/5] Metaphorical image alignment (Option A)...", flush=True)
        total_duration = words_data[-1]["end"] + 0.6 if words_data else 35.0
        aligned_scenes = self.selector.align_and_select_scenes(story["beats"], words_data, total_duration)

        # 5. Linux Single-Pass Render
        print("\n[5/5] Single-pass compositing & subtitle burning...", flush=True)
        final_mp4 = os.path.join(out_dir, f"{slug}_master.mp4")
        bgm_path = os.path.join(BASE_DIR, "assets", "bgm", "soundtrack_from_video5.mp3")
        
        self.renderer.render_full_video(
            scenes=aligned_scenes,
            voice_audio=tight_audio,
            bgm_audio=bgm_path,
            ass_subtitles=ass_path,
            output_mp4=final_mp4,
            bgm_volume=0.14,
            total_duration=total_duration
        )

        # Thumbnail
        thumb_path = os.path.join(out_dir, f"{slug}_thumbnail.jpg")
        first_img = aligned_scenes[0]["image_path"] if aligned_scenes else os.path.join(BASE_DIR, "assets", "visual_vault", "images", "Aging_king_smirking_in_shadows.jpg")
        self.thumb_gen.generate_cover(first_img, title, thumb_path, brand_subtitle=brand_label)

        total_sec = time.time() - t0
        print(f"\n✨ [COLAB T4] VIDEO COMPLETED IN {total_sec:.1f}s -> {final_mp4}", flush=True)
        return final_mp4
