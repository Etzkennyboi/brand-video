import os
import sys
import json
import time
import re
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(ROOT_DIR, "..")))

from the_untold_truth.engine import MasterEngine
from the_untold_truth.core.visual_selector import VisualSelector

CONTRARIAN_FRAMEWORKS = [
    {
        "hook_pattern": "Never mistake {A} for {B}. It is {C}.",
        "epiphany_theme": "Disillusionment with conventional virtue"
    },
    {
        "hook_pattern": "The moment you start {action}, notice who {reaction}.",
        "epiphany_theme": "Envy and social sabotage from close allies"
    },
    {
        "hook_pattern": "{Concept} is not noble. It is cowardice wearing perfume.",
        "epiphany_theme": "Re-framing passive behavior as self-deception"
    },
    {
        "hook_pattern": "People do not hate {flaw}. They just hate that {envy}.",
        "epiphany_theme": "Systemic hypocrisy and survival instincts"
    },
    {
        "hook_pattern": "If you dropped dead on a Tuesday, your position would be posted by Thursday.",
        "epiphany_theme": "Institutional indifference and replaceable devotion"
    },
    {
        "hook_pattern": "The loudest person in the room is always the most {weakness}.",
        "epiphany_theme": "Strategic silence versus noisy insecurity"
    },
    {
        "hook_pattern": "A comfortable {cage} is the drug employers give you to forget {dream}.",
        "epiphany_theme": "Golden handcuffs and modern economic sedation"
    }
]

class ScriptRanker:
    def __init__(self, catalog_path=None):
        cat_file = catalog_path or os.path.join(ROOT_DIR, "assets", "visual_vault", "catalog.json")
        with open(cat_file, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        self.catalog_keywords = set()
        for item in self.catalog:
            for kw in item.get("keywords", []):
                self.catalog_keywords.add(kw.lower())

    def score_script(self, script_data):
        """
        Scores a candidate script on a 100-point viral retention index:
        1. Hook Tension (30 pts)
        2. Word Economy & Cadence (25 pts)
        3. Cynical Depth & Stakes (25 pts)
        4. Visual Vault Synergy (20 pts)
        """
        beats = script_data.get("beats", [])
        if not beats:
            return 0, {}

        hook = beats[0]["text"]
        full_text = script_data.get("full_script", " ".join(b["text"] for b in beats))
        words = full_text.split()
        word_count = len(words)

        # 1. Hook Tension (30 pts)
        hook_words = len(hook.split())
        hook_score = 0
        # Optimal hook: 7 to 14 words
        if 6 <= hook_words <= 14:
            hook_score += 15
        elif hook_words < 6 or hook_words <= 18:
            hook_score += 10
        else:
            hook_score += 5

        # Curiosity gap / contrarian trigger words
        contrarian_triggers = ["never", "stop", "mistake", "hate", "silence", "knife", "loyalty", "replaced", "clapping", "winning", "salary", "cowardice", "truth", "secret", "trap"]
        matches = sum(1 for tr in contrarian_triggers if tr in hook.lower())
        hook_score += min(15, matches * 5)

        # 2. Word Economy & Cadence (25 pts)
        # Optimal Shorts retention script: 85 to 110 words (~32 to 40 seconds)
        economy_score = 0
        if 85 <= word_count <= 112:
            economy_score += 25
        elif 75 <= word_count < 85 or 112 < word_count <= 125:
            economy_score += 18
        else:
            economy_score += 10

        # 3. Cynical Depth & Psychological Stakes (25 pts)
        depth_score = 0
        depth_markers = ["predator", "leverage", "superiority", "contempt", "citadel", "exploit", "predictability", "replace", "ledger", "severance", "blueprint", "pedestal", "galleon", "sedate", "empire"]
        depth_matches = sum(1 for dm in depth_markers if dm in full_text.lower())
        depth_score = min(25, 10 + depth_matches * 3)

        # 4. Visual Vault Synergy (20 pts)
        vault_score = 0
        visual_matches = 0
        for w in words:
            clean_w = re.sub(r'[^a-zA-Z]', '', w).lower()
            if clean_w in self.catalog_keywords:
                visual_matches += 1
        vault_score = min(20, 8 + visual_matches * 2)

        total_score = hook_score + economy_score + depth_score + vault_score
        breakdown = {
            "hook_tension": hook_score,
            "cadence_economy": economy_score,
            "cynical_depth": depth_score,
            "vault_synergy": vault_score,
            "total": total_score,
            "word_count": word_count
        }
        return total_score, breakdown

class BatchProducer:
    def __init__(self):
        self.ranker = ScriptRanker()
        self.engine = MasterEngine()

    def generate_candidate_scripts(self, theme_prompt, count=7):
        """
        Drafts candidate contrarian scripts based on topic vault or input theme.
        """
        topics_file = os.path.join(ROOT_DIR, "config", "viral_topics_vault.json")
        with open(topics_file, "r", encoding="utf-8") as f:
            vault_topics = json.load(f)

        candidates = []
        for i in range(count):
            topic_item = vault_topics[i % len(vault_topics)]
            script_data = self.engine.director.generate_script(topic_item)
            candidates.append(script_data)
        return candidates

    def run_rank_and_produce(self, theme=None, num_candidates=7, top_k=3, dry_run=False):
        print("\n" + "=" * 75)
        print("🎯 [THE UNTOLD TRUTH] 7-SCRIPT CANDIDATE TOURNAMENT & TOP 3 ENGINE")
        print("=" * 75)
        print(f"[*] Drafting {num_candidates} viral retention candidate scripts...")
        candidates = self.generate_candidate_scripts(theme or "Power and Deception", count=num_candidates)

        scored_candidates = []
        for idx, cand in enumerate(candidates):
            score, breakdown = self.ranker.score_script(cand)
            cand["score"] = score
            cand["breakdown"] = breakdown
            cand["candidate_id"] = idx + 1
            scored_candidates.append(cand)

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        print("\n📊 CANDIDATE TOURNAMENT LEADERBOARD:")
        print("-" * 75)
        print(f"{'Rank':<5} | {'Score':<6} | {'Words':<6} | {'Title':<26} | {'Opening Hook'}")
        print("-" * 75)
        for r, c in enumerate(scored_candidates):
            print(f"#{r+1:<4} | {c['score']}/100 | {c['breakdown']['word_count']:<6} | {c['title'][:25]:<26} | \"{c['beats'][0]['text'][:35]}...\"")

        winners = scored_candidates[:top_k]
        print("\n" + "=" * 75)
        print(f"🏆 TOP {top_k} CHAMPIONS SELECTED FOR AUTOMATED PRODUCTION:")
        for r, w in enumerate(winners):
            print(f"  [{r+1}] {w['title']} (Score: {w['score']}/100) -> Hook: \"{w['beats'][0]['text']}\"")
        print("=" * 75)

        if dry_run:
            print("[Dry Run] Skipped video compositing. Scripts ranked successfully.")
            return winners

        produced_videos = []
        for r, winner in enumerate(winners):
            print(f"\n🎬 RENDERING CHAMPION [{r+1}/{top_k}]: {winner['title']}...")
            try:
                mp4 = self.engine.run(winner)
                produced_videos.append(mp4)
            except Exception as e:
                print(f"❌ Error rendering {winner['title']}: {e}")

        # Refresh dashboard
        try:
            import the_untold_truth.build_dashboard as bd
            bd.build_dashboard()
        except Exception:
            pass

        print("\n" + "=" * 75)
        print(f"✨ BATCH PRODUCTION COMPLETE: {len(produced_videos)}/{top_k} Master Shorts Ready!")
        for v in produced_videos:
            print(f"  📁 {v}")
        print("=" * 75 + "\n")
        return produced_videos

def main():
    parser = argparse.ArgumentParser(description="THE UNTOLD TRUTH Batch Candidate Tournament")
    parser.add_argument("--theme", type=str, default=None, help="Theme prompt")
    parser.add_argument("--candidates", type=int, default=7, help="Number of scripts to draft (default: 7)")
    parser.add_argument("--top", type=int, default=3, help="Number of top scripts to render (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Rank scripts without rendering videos")
    args = parser.parse_args()

    producer = BatchProducer()
    producer.run_rank_and_produce(theme=args.theme, num_candidates=args.candidates, top_k=args.top, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
