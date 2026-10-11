import os
import json
import random
import re

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_CATALOG = os.path.join(ROOT_DIR, "assets", "visual_vault", "catalog.json")
DEFAULT_IMAGES = os.path.join(ROOT_DIR, "assets", "visual_vault", "images")

class VisualSelector:
    def __init__(self, catalog_path=None, images_dir=None):
        self.catalog_path = catalog_path or DEFAULT_CATALOG
        self.images_dir = images_dir or DEFAULT_IMAGES
        with open(self.catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)


    def _clean_word(self, w):
        return re.sub(r'[^a-zA-Z0-9]', '', w).lower()

    def align_and_select_scenes(self, beats, words, total_duration):
        """
        1. Slices speech into temporal scene segments based on exact Whisper word timestamps.
        2. Splits longer beats (>5.5s) at sentence boundaries for optimal retention & synchronization.
        3. Semantically matches each scene's spoken text to the best visual in the vault.
        """
        if not words or total_duration <= 0:
            return self.select_scenes_for_beats(beats)

        # 1. Clean whisper words
        whisper_cleaned = [self._clean_word(w['word']) for w in words]
        w_cursor = 0

        scene_segments = []

        # Find word boundaries for each beat
        for b_idx, beat in enumerate(beats):
            beat_text = beat.get("text", "")
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', beat_text) if s.strip()]
            if not sentences:
                sentences = [beat_text]

            # If beat has multiple sentences and is likely long, create sub-scenes
            for s_idx, sentence in enumerate(sentences):
                s_words = [self._clean_word(w) for w in sentence.split() if self._clean_word(w)]
                if not s_words:
                    continue

                start_time = words[w_cursor]['start'] if w_cursor < len(words) else 0.0

                # Target the last words of this sentence
                target_last = s_words[-1]
                target_penultimate = s_words[-2] if len(s_words) > 1 else ""

                # Search forward for match
                match_end = min(w_cursor + len(s_words) - 1, len(words) - 1)
                search_start = w_cursor + max(1, len(s_words) - 4)
                search_end = min(w_cursor + len(s_words) + 5, len(words))

                for test_idx in range(search_start, search_end):
                    if whisper_cleaned[test_idx] == target_last:
                        if target_penultimate and test_idx > 0 and whisper_cleaned[test_idx - 1] == target_penultimate:
                            match_end = test_idx
                            break
                        match_end = test_idx

                end_time = words[match_end]['end'] if match_end < len(words) else total_duration
                w_cursor = match_end + 1

                label = f"{beat.get('name', f'Beat {b_idx+1}')}"
                if len(sentences) > 1:
                    label += f" (Part {s_idx+1})"

                scene_segments.append({
                    "beat_index": b_idx + 1,
                    "beat_name": label,
                    "text": sentence,
                    "keywords": beat.get("keywords", []),
                    "start": round(start_time, 2),
                    "end": round(end_time, 2),
                    "duration": round(end_time - start_time, 2)
                })

        # Ensure seamless continuity and final timing
        if scene_segments:
            scene_segments[0]["start"] = 0.0
            for i in range(len(scene_segments) - 1):
                boundary = round((scene_segments[i]["end"] + scene_segments[i+1]["start"]) / 2, 2)
                scene_segments[i]["end"] = boundary
                scene_segments[i]["duration"] = round(scene_segments[i]["end"] - scene_segments[i]["start"], 2)
                scene_segments[i+1]["start"] = boundary
            scene_segments[-1]["end"] = round(total_duration, 2)
            scene_segments[-1]["duration"] = round(scene_segments[-1]["end"] - scene_segments[-1]["start"], 2)

            # Consolidate micro-scenes (< 2.2s) into adjacent scenes, keeping scenes between 2.8s and 5.2s
            merged = []
            for seg in scene_segments:
                if not merged:
                    merged.append(seg)
                else:
                    last = merged[-1]
                    if (seg["duration"] < 2.4 or last["duration"] < 2.5) and (last["duration"] + seg["duration"] <= 5.5):
                        last["text"] += " " + seg["text"]
                        last["end"] = seg["end"]
                        last["duration"] = round(last["end"] - last["start"], 2)
                        last["keywords"].extend(seg.get("keywords", []))
                    else:
                        merged.append(seg)
            scene_segments = merged


        # 2. Semantic visual matching for each scene segment
        used_ids = set()
        used_images = set()
        scenes = []
        all_disk_images = set(os.listdir(self.images_dir))

        CONCEPT_MAP = {
            "casino": ["banker", "coins", "gold", "scales", "deed"],
            "slot": ["coins", "gold", "machinery", "anvil", "scales"],
            "machine": ["blacksmith", "steel", "architect", "scales"],
            "chips": ["coins", "gold", "silver", "balance"],
            "chip": ["coins", "gold", "silver"],
            "bet": ["coins", "hands", "exchange", "scales"],
            "betting": ["coins", "hands", "exchange", "scales"],
            "roulette": ["scales", "balance", "coins", "clock"],
            "loss": ["ruins", "tomb", "beggar", "mud"],
            "lose": ["ruins", "tomb", "beggar", "mud"],
            "win": ["crown", "throne", "gold", "celebrate"],
            "winning": ["crown", "throne", "gold"],
            "trance": ["mirrors", "shadows", "candlelight"],
            "vip": ["banquet", "wine", "goblet", "aristocrat"],
            "drink": ["wine", "goblet", "banquet"],
            "drinks": ["wine", "goblet", "banquet"],
            "money": ["gold", "banker", "coins", "silver", "deed"],
            "dollars": ["gold", "banker", "coins"],
            "cents": ["coins", "silver", "palm"],
            "politician": ["politician", "oligarch", "bishops", "courtier"],
            "politicians": ["politician", "oligarch", "bishops", "courtier"],
            "scam": ["courtier", "mask", "whispering", "bribe"],
            "scammer": ["courtier", "mask", "whispering"],
            "scammers": ["courtier", "mask", "whispering"],
            "billionaire": ["oligarch", "banquet", "crown", "gold"],
            "airline": ["carriage", "traveler", "road"],
            "delay": ["clock", "window", "candlelight"],
            "sports": ["gladiator", "warrior", "arena"],
            "applaud": ["clapping", "audience", "crowd"],
            "applause": ["clapping", "audience", "crowd"],
            "clapping": ["clapping", "audience"],
            "noise": ["crowd", "quarreling", "protest"],
            "loud": ["quarreling", "crowd", "banquet"],
            "observe": ["shadows", "balcony", "watching", "beggar"],
            "observing": ["shadows", "balcony", "watching"],
            "corner": ["shadows", "smirking"],
            "power": ["king", "throne", "crown"],
            "silence": ["shadows", "solitary", "cloaked", "walking", "rain"],
            "silent": ["shadows", "cloaked", "solitary"],
            "blueprint": ["architect", "parchment", "map", "war"],
            "plan": ["commanders", "war_map", "architect"],
            "enemies": ["commanders", "war_map", "guard", "armor"],
            "strategist": ["commanders", "war_map", "architect"],
            "moves": ["commanders", "balance", "scales"],
            "weapon": ["blacksmith", "steel", "sword", "guard"],
            "surprise": ["mask", "carnival", "guard"],
            "gold": ["gold", "banker", "coins", "bishops"],
            "salary": ["gold", "deed", "key", "banker"],
            "corrupt": ["bishops", "gold", "scales", "mob"],
            "corruption": ["bishops", "gold", "scales", "mob"],
            "justice": ["scales", "balance", "court"],
            "crime": ["scales", "balance", "mob", "guard"],
            "loyal": ["bound", "armor", "guard"],
            "loyalty": ["bound", "armor", "guard"],
            "replaced": ["grave", "key", "deed", "ruins"],
            "grave": ["shadows", "solitary", "ruins"]
        }


        for i, seg in enumerate(scene_segments):
            seg_text = seg["text"].lower()
            seg_words = set(self._clean_word(w) for w in seg_text.split())

            # Gather target concept tokens
            target_tokens = set(seg.get("keywords", []))
            target_tokens.update(seg_words)
            for w in seg_words:
                if w in CONCEPT_MAP:
                    target_tokens.update(CONCEPT_MAP[w])

            best_entry = None
            best_score = -100

            for entry in self.catalog:
                img_file = entry.get("image_file")
                if entry["id"] in used_ids or img_file in used_images:
                    continue

                score = 0
                img_name_lower = (img_file or "").lower()
                title_lower = entry["title"].lower()

                # Score image filename matches
                for tok in target_tokens:
                    tok_l = tok.lower()
                    if tok_l in img_name_lower:
                        score += 10
                    if tok_l in title_lower:
                        score += 6
                    for kw in entry.get("keywords", []):
                        if tok_l in kw.lower():
                            score += 4

                # Hook or initial scene preference
                if i == 0 and "king" in img_name_lower:
                    score += 5

                if score > best_score:
                    best_score = score
                    best_entry = entry

            if not best_entry:
                available = [e for e in self.catalog if e["id"] not in used_ids and e.get("image_file") not in used_images]
                best_entry = random.choice(available) if available else self.catalog[0]

            used_ids.add(best_entry["id"])
            img_file = best_entry.get("image_file")
            if not img_file or not os.path.exists(os.path.join(self.images_dir, img_file)) or img_file in used_images:
                remaining_disk = list(all_disk_images - used_images)
                img_file = random.choice(remaining_disk) if remaining_disk else (os.listdir(self.images_dir)[0])

            used_images.add(img_file)
            full_img_path = os.path.join(self.images_dir, img_file)

            zoom_dir = "in" if i % 2 == 0 else "out"

            scenes.append({
                "scene_index": i + 1,
                "beat_name": seg["beat_name"],
                "title": best_entry["title"],
                "start": seg["start"],
                "end": seg["end"],
                "duration": seg["duration"],
                "image_path": full_img_path,
                "zoom_dir": zoom_dir,
                "text_segment": seg["text"]
            })

        return scenes

    def select_scenes_for_beats(self, beats):
        """
        Fallback when word timestamps are not provided.
        """
        used_ids = set()
        used_images = set()
        scenes = []
        all_disk_images = set(os.listdir(self.images_dir))

        for i, beat in enumerate(beats):
            beat_keywords = [k.lower() for k in beat.get("keywords", [])]
            beat_text = beat.get("text", "").lower()

            best_entry = None
            best_score = -1

            for entry in self.catalog:
                img_file = entry.get("image_file")
                if entry["id"] in used_ids or img_file in used_images:
                    continue

                score = 0
                for kw in entry["keywords"]:
                    if kw.lower() in beat_keywords or kw.lower() in beat_text:
                        score += 3
                for word in entry["title"].lower().split():
                    if word in beat_keywords or word in beat_text:
                        score += 2

                if score > best_score:
                    best_score = score
                    best_entry = entry

            if not best_entry:
                available = [e for e in self.catalog if e["id"] not in used_ids and e.get("image_file") not in used_images]
                best_entry = random.choice(available) if available else self.catalog[0]

            used_ids.add(best_entry["id"])
            img_file = best_entry.get("image_file")
            if not img_file or not os.path.exists(os.path.join(self.images_dir, img_file)) or img_file in used_images:
                remaining_disk = list(all_disk_images - used_images)
                img_file = random.choice(remaining_disk) if remaining_disk else (os.listdir(self.images_dir)[0])

            used_images.add(img_file)
            full_img_path = os.path.join(self.images_dir, img_file)

            zoom_dir = "in" if i % 2 == 0 else "out"

            scenes.append({
                "scene_index": i + 1,
                "beat_name": beat.get("name", f"Scene {i+1}"),
                "title": best_entry["title"],
                "image_path": full_img_path,
                "zoom_dir": zoom_dir,
                "text_segment": beat["text"]
            })

        return scenes
