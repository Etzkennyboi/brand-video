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
from core.voice_synthesizer import sanitize_voice_text
from core.single_pass_render import SinglePassRender
from core.thumbnail_generator import ThumbnailGenerator

FFMPEG = shutil.which("ffmpeg") or "ffmpeg"


class ColabVoiceSynthesizer:
    def __init__(self, speed_factor=1.14):
        self.speed_factor = speed_factor
        self.f5_api = None

    def get_model(self):
        if self.f5_api is None:
            try:
                from f5_tts.api import F5TTS
                print("      [Colab T4] Initializing F5-TTS on CUDA GPU...", flush=True)
                import torch
                dev = "cuda" if torch.cuda.is_available() else "cpu"
                self.f5_api = F5TTS(device=dev)
                print("      [Colab T4] F5-TTS initialized successfully!", flush=True)
            except Exception as e:
                print(f"      [Colab T4] F5TTS API init note: {e}", flush=True)
                self.f5_api = False
        return self.f5_api

    def synthesize_speech(self, text, output_wav, ref_audio, ref_text):
        clean_text = sanitize_voice_text(text)
        os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)

        # 1. Native F5TTS API on CUDA
        model = self.get_model()
        if model:
            try:
                print("      [Colab T4] Synthesizing speech with F5-TTS in GPU VRAM...", flush=True)
                t0 = time.time()
                model.infer(
                    ref_file=ref_audio,
                    ref_text=ref_text,
                    gen_text=clean_text,
                    file_wave=output_wav
                )
                print(f"      [Colab T4] Voiceover generated in {time.time()-t0:.2f}s! -> {output_wav}", flush=True)
                return output_wav
            except Exception as e:
                print(f"      [Colab T4] Native infer error: {e}. Trying CLI...", flush=True)

        # 2. Try f5-tts CLI
        try:
            print("      [Colab T4] Trying f5-tts_infer-cli...", flush=True)
            cmd = [
                "f5-tts_infer-cli",
                "--model", "F5-TTS",
                "--ref_audio", ref_audio,
                "--ref_text", ref_text,
                "--gen_text", clean_text,
                "--output_file", output_wav
            ]
            subprocess.run(cmd, check=True)
            return output_wav
        except Exception as e:
            print(f"      [Colab T4] CLI fallback note: {e}. Trying local gradio...", flush=True)

        # 3. Try local Gradio 7860 if running
        try:
            from gradio_client import Client, handle_file
            c = Client("http://127.0.0.1:7860/", httpx_kwargs={"timeout": 60.0})
            res = c.predict(
                ref_audio_input=handle_file(ref_audio),
                ref_text_input=ref_text,
                gen_text_input=clean_text,
                remove_silence=True,
                randomize_seed=True,
                seed_input=0,
                cross_fade_duration_slider=0.15,
                speed_slider=1.0,
                api_name="/basic_tts"
            )
            wav_path = res[0] if isinstance(res, (tuple, list)) else res
            shutil.copy2(wav_path, output_wav)
            return output_wav
        except Exception:
            pass

        # 4. Reliable safety fallback: gTTS
        print("      [Colab T4] Falling back to high-speed backup voice...", flush=True)
        from gtts import gTTS
        tts = gTTS(text=clean_text, lang='en', tld='co.uk', slow=False)
        temp_mp3 = output_wav + ".gtts.mp3"
        tts.save(temp_mp3)
        cmd = [FFMPEG, '-y', '-i', temp_mp3, '-ar', '44100', '-ac', '2', output_wav]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(temp_mp3):
            os.remove(temp_mp3)
        return output_wav

    def tighten_cadence(self, input_wav, output_wav, speed_factor=1.14):
        af = f"silenceremove=stop_periods=-1:stop_duration=0.22:stop_threshold=-40dB,atempo={speed_factor}"
        cmd = [
            FFMPEG, '-y',
            '-i', input_wav,
            '-af', af,
            '-ar', '44100',
            '-ac', '2',
            output_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_wav


class ColabMasterEngine:
    def __init__(self, personality="untold_truth"):
        self.personality = personality
        self.brand_title = "PROF LAYI" if "layi" in personality.lower() else "THE UNTOLD TRUTH"
        
        self.director = ScriptDirector(brand_title=self.brand_title, personality=personality)
        self.selector = VisualSelector(
            catalog_path=os.path.join(BASE_DIR, "assets", "visual_vault", "catalog.json"),
            images_dir=os.path.join(BASE_DIR, "assets", "visual_vault", "images")
        )
        
        # Use CUDA for Whisper on Colab
        try:
            import torch
            device = "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            device = "cpu"

        compute_type = "float16" if device == "cuda" else "int8"
        self.subtitles = SubtitleGenerator(model_size="base", device=device, compute_type=compute_type)
        self.voice = ColabVoiceSynthesizer(speed_factor=1.14)
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
        print("\n[2/5] Synthesizing voiceover via Colab GPU...", flush=True)
        ref_clip = os.path.join(BASE_DIR, "assets", "ref_voice_vid5.wav")
        ref_text = "The word karma is a word used by losers. People use it when they're too powerless to get justice themselves."
        
        self.voice.synthesize_speech(
            text=story["full_script"],
            output_wav=raw_audio,
            ref_audio=ref_clip,
            ref_text=ref_text
        )
        self.voice.tighten_cadence(raw_audio, tight_audio, speed_factor=1.14)

        # 3. Subtitles (CUDA)
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
        try:
            self.thumb_gen.generate_cover(first_img, title, thumb_path, brand_subtitle=brand_label)
        except Exception as e:
            print(f"      [Thumbnail] Note: {e}", flush=True)

        total_sec = time.time() - t0
        print(f"\n✨ [COLAB T4] VIDEO COMPLETED IN {total_sec:.1f}s -> {final_mp4}", flush=True)
        return final_mp4
