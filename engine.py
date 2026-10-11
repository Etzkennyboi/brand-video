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
    def __init__(self):
        brand_config_path = os.path.join(CONFIG_DIR, "brand_rules.json")
        with open(brand_config_path, "r", encoding="utf-8") as f:
            self.brand = json.load(f)

        self.director = ScriptDirector(brand_title=self.brand["brand_name"])
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
            brand_title=self.brand["brand_name"],
            watermark_text=self.brand["watermark"]["text"]
        )
        self.thumb_gen = ThumbnailGenerator(brand_title=self.brand["brand_name"])

    def run(self, topic_input, voice_engine="auto", ref_audio=None, out_name=None):
        t_start = time.time()
        print("=" * 75, flush=True)
        print(f"🎬 [THE UNTOLD TRUTH] INITIALIZING MASTER PRODUCTION ENGINE", flush=True)
        print("=" * 75, flush=True)

        # 1. Script Generation
        print("\n[1/6] NARRATIVE DIRECTING: Generating 5-beat retention script...", flush=True)
        story = self.director.generate_script(topic_input)
        title = story["title"]
        slug = slugify(title if not out_name else out_name)
        print(f"      Title: {title}", flush=True)
        print(f"      Hook:  \"{story['beats'][0]['text']}\"", flush=True)

        # 2. Voiceover Synthesis
        print("\n[2/6] AUDIO SYNTHESIS: Generating tightened narration...", flush=True)
        raw_audio = os.path.join(DRAFTS_DIR, f"{slug}_raw_voice.wav")
        tight_audio = os.path.join(DRAFTS_DIR, f"{slug}_tight_voice.wav")

        # Synthesize fresh with signature Video 5 cloned voice (F5-TTS)
        ref_path = ref_audio or os.path.join(ROOT_DIR, self.brand["audio"]["ref_voice_audio"])
        ref_txt = self.brand["audio"]["ref_voice_text"]
        self.voice.synthesize(
            story["full_script"],
            raw_audio,
            tight_audio,
            engine="f5",
            ref_audio=ref_path,
            ref_text=ref_txt
        )

        # 3. Subtitle Alignment & Timing
        print("\n[3/6] SPEECH ALIGNMENT: Extracting word timestamps with Faster-Whisper...", flush=True)
        words, total_duration = self.subtitles.extract_words(tight_audio)
        print(f"      Narration Duration: {total_duration:.2f}s ({len(words)} words)", flush=True)

        # 4. Visual Scene Selection & Exact Whisper Boundary Synchronization
        print("\n[4/6] SMART VAULT MATCHING: Synchronizing scenes with Whisper word boundaries...", flush=True)
        scenes = self.selector.align_and_select_scenes(story["beats"], words, total_duration)

        for s in scenes:
            print(f"      Scene {s['scene_index']}: [{s['start']:05.2f}s - {s['end']:05.2f}s] ({s['duration']}s, {s['zoom_dir']}) -> {os.path.basename(s['image_path'])}", flush=True)
            print(f"               Matching: \"{s['text_segment'][:55]}...\"", flush=True)

        # 5. Kinetic Subtitles Generation
        print("\n[5/6] SUBTITLES: Formatting amber kinetic pop ASS subtitles...", flush=True)
        ass_path = os.path.join(DRAFTS_DIR, f"{slug}_subtitles.ass")
        self.subtitles.generate_ass(words, title, ass_path, chunk_size=self.brand["subtitles"]["chunk_size"])

        # 6. Single-Pass High-Speed Render (with 500% BGM Boost)
        print(f"\n[6/6] COMPOSITING: Single-pass parallel rendering ({self.brand['audio'].get('bgm_boost_label', '500%')} BGM boost)...", flush=True)
        bgm_rel = self.brand["audio"]["default_bgm"]
        if bgm_rel.startswith("the_untold_truth/"):
            bgm_rel = bgm_rel.replace("the_untold_truth/", "", 1)
        bgm_path = os.path.join(ROOT_DIR, bgm_rel)
        if not os.path.exists(bgm_path):
            bgm_path = os.path.abspath(os.path.join(ROOT_DIR, "..", "soundtrack_from_video5.mp3"))
        final_mp4 = os.path.join(READY_DIR, f"{slug}_master.mp4")

        self.renderer.build_video(
            scenes=scenes,
            voice_audio=tight_audio,
            bgm_audio=bgm_path,
            ass_path=ass_path,
            total_duration=total_duration,
            out_master_path=final_mp4,
            bgm_volume=self.brand["audio"].get("bgm_volume_multiplier", 3.75)
        )

        # 7. Cover Thumbnail Generation
        print("\n[7/7] COVER THUMBNAIL: Generating high-CTR cover...", flush=True)
        thumb_path = os.path.join(READY_DIR, f"{slug}_thumbnail.jpg")
        try:
            self.thumb_gen.generate_thumbnail(scenes[0]["image_path"], title, story["beats"][0]["text"], thumb_path)
        except Exception as e:
            print(f"      [Thumbnail] Warning: Thumbnail generation skipped ({e})", flush=True)
            thumb_path = None

        # 8. Metadata Packaging
        meta_path = os.path.join(READY_DIR, f"{slug}_metadata.json")
        metadata = {
            "brand": self.brand["brand_name"],
            "title": f"{title} | The Harsh Reality They Never Tell You #shorts",
            "hook": story["beats"][0]["text"],
            "description": (
                f"{story['beats'][0]['text']}\n\n"
                f"{story['full_script']}\n\n"
                f"Subscribe to @TheUntoldTruth for daily unfiltered psychology, harsh truths, and cynical wisdom.\n\n"
                f"#TheUntoldTruth #DarkPsychology #Stoicism #HardTruths #Mindset #LifeLessons #Shorts"
            ),
            "hashtags": ["#TheUntoldTruth", "#DarkPsychology", "#Stoicism", "#CynicalTruth", "#LifeLessons", "#Shorts", "#Viral"],
            "pinned_comment": f"What is a truth you learned too late in life? Drop it below. 👇",
            "thumbnail": thumb_path,
            "duration_sec": total_duration,
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        with open(meta_path, "w", encoding="utf-8") as f_meta:
            json.dump(metadata, f_meta, indent=2, ensure_ascii=False)

        total_elapsed = time.time() - t_start
        print("\n" + "=" * 75, flush=True)
        print(f"✨ PRODUCTION COMPLETE in {total_elapsed:.1f}s!", flush=True)
        print(f"📁 Video:     {final_mp4}", flush=True)
        print(f"🖼️ Thumbnail: {thumb_path}", flush=True)
        print(f"📄 Metadata:  {meta_path}", flush=True)
        print("=" * 75 + "\n", flush=True)
        return final_mp4

def main():
    parser = argparse.ArgumentParser(description="THE UNTOLD TRUTH Video Production Engine")
    parser.add_argument("--topic", type=str, default=None, help="Custom topic to produce")
    parser.add_argument("--auto", action="store_true", help="Pick next viral topic from topics vault")
    parser.add_argument("--voice", type=str, default="auto", choices=["auto", "f5", "gtts"], help="Voice engine")
    parser.add_argument("--ref", type=str, default=None, help="Reference audio for voice cloning")
    args = parser.parse_args()

    engine = MasterEngine()

    if args.auto:
        topics_file = os.path.join(CONFIG_DIR, "viral_topics_vault.json")
        with open(topics_file, "r", encoding="utf-8") as f:
            topics = json.load(f)
        chosen_topic = topics[0] # Pick first or cycle
        print(f"Autonomous Mode: Picked topic '{chosen_topic['title']}'", flush=True)
        engine.run(chosen_topic, voice_engine=args.voice, ref_audio=args.ref)
    elif args.topic:
        engine.run(args.topic, voice_engine=args.voice, ref_audio=args.ref)
    else:
        # Default test topic
        default_topic = "The Myth of Loyalty at Work"
        engine.run(default_topic, voice_engine=args.voice, ref_audio=args.ref)

if __name__ == "__main__":
    main()
