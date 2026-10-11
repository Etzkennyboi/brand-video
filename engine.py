import os
import sys
import re
import time
import json
import argparse

# Fix Windows console utf-8 encoding
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

from core.script_director import ScriptDirector
from core.visual_selector import VisualSelector
from core.voice_synthesizer import VoiceSynthesizer
from core.subtitle_generator import SubtitleGenerator
from core.single_pass_render import SinglePassRender
from core.thumbnail_generator import ThumbnailGenerator

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
ASSETS_DIR = os.path.join(ROOT_DIR, "assets")
OUT_DIR = os.path.join(ROOT_DIR, "out")
DRAFTS_DIR = os.path.join(OUT_DIR, "drafts")
READY_DIR = os.path.join(OUT_DIR, "ready_to_publish")

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '_', text).strip('_')
    return text[:40]

class MasterEngine:
    def __init__(self, personality="untold_truth"):
        brand_config_path = os.path.join(CONFIG_DIR, "brand_rules.json")
        with open(brand_config_path, "r", encoding="utf-8") as f:
            self.brand = json.load(f)

        self.personality = personality
        brand_label = "SIR ROGERS" if "roger" in personality.lower() else self.brand["brand_name"]
        watermark_text = "SIR ROGERS" if "roger" in personality.lower() else self.brand["watermark"]["text"]

        self.director = ScriptDirector(brand_title=brand_label, personality=personality)
        self.selector = VisualSelector(
            catalog_path=os.path.join(ASSETS_DIR, "visual_vault", "catalog.json"),
            images_dir=os.path.join(ASSETS_DIR, "visual_vault", "images")
        )
        tokens = [t for t in self.brand["audio"].get("hf_tokens", []) if t.startswith("hf_")] or None
        self.voice = VoiceSynthesizer(
            speed_factor=self.brand["audio"]["voice_speed_factor"],
            tokens=tokens
        )
        self.subtitles = SubtitleGenerator(model_size="base")
        self.renderer = SinglePassRender(
            brand_title=brand_label,
            watermark_text=watermark_text
        )
        self.thumb_gen = ThumbnailGenerator(brand_title=brand_label)

    def set_personality(self, personality):
        self.personality = personality
        brand_label = "SIR ROGERS" if "roger" in personality.lower() else self.brand["brand_name"]
        watermark_text = "SIR ROGERS" if "roger" in personality.lower() else self.brand["watermark"]["text"]
        self.director.set_personality(personality)
        self.renderer.brand_title = brand_label
        self.renderer.watermark_text = watermark_text
        self.thumb_gen.brand_title = brand_label

    def run(self, topic_input, voice_engine="auto", ref_audio=None, out_name=None, personality=None):
        if personality:
            self.set_personality(personality)

        brand_display = "SIR ROGERS" if "roger" in self.personality.lower() else "THE UNTOLD TRUTH"

        t_start = time.time()
        print("=" * 75, flush=True)
        print(f"🎬 [{brand_display}] INITIALIZING MASTER PRODUCTION ENGINE", flush=True)
        print("=" * 75, flush=True)

        # 1. Script Generation
        print("\n[1/6] NARRATIVE DIRECTING: Generating 5-beat retention script...", flush=True)
        if isinstance(topic_input, dict) and "beats" in topic_input:
            story = topic_input
        else:
            story = self.director.generate_script(topic_input, personality=self.personality)

        title = story["title"]
        slug = slugify(title if not out_name else out_name)
        print(f"      Personality: {brand_display}", flush=True)
        print(f"      Title:       {title}", flush=True)
        print(f"      Hook:        \"{story['beats'][0]['text']}\"", flush=True)

        # 2. Voiceover Synthesis
        print("\n[2/6] AUDIO SYNTHESIS: Generating tightened narration...", flush=True)
        raw_audio = os.path.join(DRAFTS_DIR, f"{slug}_raw_voice.wav")
        tight_audio = os.path.join(DRAFTS_DIR, f"{slug}_tight_voice.wav")

        ref = ref_audio or os.path.join(ASSETS_DIR, "ref_voice_vid5.wav")
        ref_text = self.brand["audio"]["ref_voice_text"]

        try:
            self.voice.synthesize_speech(
                text=story["full_script"],
                output_wav=raw_audio,
                ref_audio=ref,
                ref_text=ref_text,
                voice_engine=voice_engine
            )
        except Exception as e:
            print(f"  [!] Fallback to gTTS due to: {e}", flush=True)
            self.voice.synthesize_speech(
                text=story["full_script"],
                output_wav=raw_audio,
                voice_engine="gtts"
            )

        self.voice.tighten_cadence(
            input_wav=raw_audio,
            output_wav=tight_audio,
            speed_factor=self.brand["audio"]["voice_speed_factor"]
        )

        # 3. Millisecond Whisper Transcription & Kinetic Subtitle Styling
        print("\n[3/6] SUBTITLES: Transcribing word boundaries & generating ASS captions...", flush=True)
        words_data = self.subtitles.transcribe_words(tight_audio)
        ass_path = os.path.join(DRAFTS_DIR, f"{slug}_captions.ass")
        self.subtitles.generate_ass_file(words_data, ass_path, title=title)

        # 4. Cinematic Visual Matching & Dynamic Beat Alignment
        print("\n[4/6] VISUAL CURATION: Matching 9:16 cinematic visuals from vault...", flush=True)
        matched_cuts = self.selector.match_beats_to_images(story["beats"])
        total_duration = words_data[-1]["end"] + 0.6 if words_data else 40.0
        aligned_scenes = self.selector.align_cuts_to_whisper(matched_cuts, words_data, total_duration)

        # 5. Parallel Motion Render & Single-Pass Compositor
        print("\n[5/6] COMPOSITING: Single-pass hardware render with 500% BGM mix...", flush=True)
        bgm_path = os.path.join(ASSETS_DIR, "bgm", "soundtrack_from_video5.mp3")
        final_mp4 = os.path.join(READY_DIR, f"{slug}_master.mp4")

        self.renderer.render_full_video(
            scenes=aligned_scenes,
            voice_audio=tight_audio,
            bgm_audio=bgm_path,
            ass_subtitles=ass_path,
            output_mp4=final_mp4,
            bgm_volume=self.brand["audio"]["bgm_volume_multiplier"],
            total_duration=total_duration
        )

        # 6. Cover Thumbnail & Metadata Generation
        print("\n[6/6] PUBLISHING SUITE: Generating cover art thumbnail & metadata...", flush=True)
        first_img = aligned_scenes[0]["image_path"] if aligned_scenes else os.path.join(ASSETS_DIR, "visual_vault", "images", "Aging_king_smirking_in_shadows.jpg")
        thumb_path = os.path.join(READY_DIR, f"{slug}_thumbnail.jpg")
        self.thumb_gen.generate_cover(
            background_img=first_img,
            title_text=title,
            output_path=thumb_path,
            brand_subtitle=brand_display
        )

        # Save metadata JSON for publishing
        meta_path = os.path.join(READY_DIR, f"{slug}_metadata.json")
        metadata = {
            "title": f"{title} | {brand_display}",
            "personality": self.personality,
            "description": f"{story['beats'][0]['text']}\n\nProduced autonomously by {brand_display} Studio.\n\n#psychology #mindset #motivation #shorts #viral",
            "hook": story["beats"][0]["text"],
            "full_script": story["full_script"],
            "tags": ["psychology", "viral", "shorts", "power", "truth", "gametheory", "mindset"],
            "video_file": final_mp4,
            "thumbnail_file": thumb_path,
            "duration_sec": total_duration,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(meta_path, "w", encoding="utf-8") as f_meta:
            json.dump(metadata, f_meta, indent=2, ensure_ascii=False)

        total_elapsed = time.time() - t_start
        print("\n" + "=" * 75, flush=True)
        print(f"✨ [{brand_display}] PRODUCTION COMPLETE in {total_elapsed:.1f}s!", flush=True)
        print(f"📁 Video:     {final_mp4}", flush=True)
        print(f"🖼️ Thumbnail: {thumb_path}", flush=True)
        print(f"📄 Metadata:  {meta_path}", flush=True)
        print("=" * 75 + "\n", flush=True)
        return final_mp4

def ask_user_personality():
    print("\n" + "=" * 55)
    print("🎭 CHOOSE SCRIPT PERSONALITY:")
    print("  [1] THE UNTOLD TRUTH (Dark, cynical, philosophical power)")
    print("  [2] SIR ROGERS       (Cheeky, game theory, exploits, loopholes)")
    print("=" * 55)
    choice = input("Enter 1 or 2 (default 1): ").strip()
    if choice == "2":
        return "sir_rogers"
    return "untold_truth"

def main():
    parser = argparse.ArgumentParser(description="Automated Video Production Engine")
    parser.add_argument("--personality", type=str, default=None, choices=["untold_truth", "sir_rogers", "ask"], help="Writer personality")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic to produce")
    parser.add_argument("--auto", action="store_true", help="Pick next viral topic from topics vault")
    parser.add_argument("--voice", type=str, default="auto", choices=["auto", "f5", "gtts"], help="Voice engine")
    parser.add_argument("--ref", type=str, default=None, help="Reference audio for voice cloning")
    args = parser.parse_args()

    chosen_personality = args.personality
    if not chosen_personality or chosen_personality == "ask":
        if sys.stdin.isatty():
            chosen_personality = ask_user_personality()
        else:
            chosen_personality = "untold_truth"

    engine = MasterEngine(personality=chosen_personality)

    if args.auto:
        topics_file = os.path.join(CONFIG_DIR, "viral_topics_vault.json")
        with open(topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        chosen_topic = topics[0]
        print(f"Autonomous Mode: Picked topic '{chosen_topic['title']}'", flush=True)
        engine.run(chosen_topic, voice_engine=args.voice, ref_audio=args.ref)
    elif args.topic:
        engine.run(args.topic, voice_engine=args.voice, ref_audio=args.ref)
    else:
        default_topic = "How Casinos Trick Your Brain" if "roger" in chosen_personality else "The Myth of Loyalty at Work"
        engine.run(default_topic, voice_engine=args.voice, ref_audio=args.ref)

if __name__ == "__main__":
    main()
