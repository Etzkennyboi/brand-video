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

SIR_ROGERS_TOPICS = [
    {"title": "How Casinos Trick Your Brain", "theme": "casino floor layout, chips, and free drink psychology"},
    {"title": "The Martingale Betting Trap", "theme": "doubling bets on red until life savings are wiped out"},
    {"title": "How To Build An Addictive Slot Machine", "theme": "near misses, disguised losses as wins, and high-speed trance"},
    {"title": "The Billionaire Airline Bet", "theme": "Richard Branson and Tony Fernandez cross-dressing F1 wager"},
    {"title": "The Street Trivia Gambling Trap", "theme": "influencer giveaways, coin flips, and US lottery law"},
    {"title": "How Scammers Scammed The Politicians", "theme": "fake EFCC agents blackmailing corrupt government officials"},
    {"title": "The One-Second Delay Hustle", "theme": "stadium live betting latency and AirPod phone calls"}
]

PROF_LAYI_TOPICS = [
    {"title": "Nobody Wants To Accompany Who Is Not Accomplished", "theme": "love does not cost a dime fallacy, London flights, and entourage radius"},
    {"title": "The Mathematician's Dilemma", "theme": "baby formula calculus, minimum wage hard work, and info leverage"},
    {"title": "The Proof Of Knowledge Is Demonstration", "theme": "shoe cobbler junction test, destiny vs destination, and Greek philosophy"},
    {"title": "Why Currency Must Be Current", "theme": "stagnant mattress money, mosquito swamp metaphor, and inflation demotion"},
    {"title": "Matrimony Without Money", "theme": "jollof rice poetry fallacy, emotional breakdown vs breakthrough, and independent economic power"},
    {"title": "The Forty-Three Million Naira Watch", "theme": "dictating another man's time, overthinking vs overdoing, and perceived status"}
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

    def score_script(self, script_data, personality="untold_truth"):
        """
        Scores a candidate script on a 100-point viral retention index:
        1. Hook Tension (30 pts)
        2. Word Economy & Cadence (25 pts)
        3. Psychological Depth & Exploit Value (25 pts)
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
        if 6 <= hook_words <= 18:
            hook_score += 15
        else:
            hook_score += 8

        is_layi = "layi" in personality.lower() or "prof" in personality.lower() or "laya" in personality.lower()
        is_rogers = "roger" in personality.lower()

        if is_layi:
            triggers = ["quiet", "talk", "proof", "demonstration", "nobody", "accomplished", "mathematician", "money", "currency", "mentor", "matrimony", "watch"]
        elif is_rogers:
            triggers = ["you", "problem", "bet", "lost", "job", "fix", "guru", "here", "scam", "fool", "delay", "billionaire"]
        else:
            triggers = ["never", "stop", "mistake", "hate", "silence", "knife", "loyalty", "replaced", "clapping", "winning", "salary", "truth", "secret"]

        matches = sum(1 for tr in triggers if tr in hook.lower())
        hook_score += min(15, matches * 5)

        # 2. Word Economy & Cadence (25 pts)
        economy_score = 0
        if 80 <= word_count <= 118:
            economy_score += 25
        elif 70 <= word_count < 80 or 118 < word_count <= 135:
            economy_score += 18
        else:
            economy_score += 10

        # 3. Psychological Depth & Stakes (25 pts)
        if is_layi:
            depth_markers = ["demonstration", "mentor", "accomplished", "currency", "breakdown", "breakthrough", "intellectual", "arrogance", "matrimony", "value", "formula", "fly", "gncc", "calculus"]
        elif is_rogers:
            depth_markers = ["casino", "chips", "exploit", "near miss", "trance", "vip", "algorithm", "loophole", "freeze", "double", "investigator", "bribe", "congrats"]
        else:
            depth_markers = ["predator", "leverage", "superiority", "contempt", "citadel", "exploit", "predictability", "replace", "ledger", "severance", "pedestal", "galleon", "empire"]

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
            "psychological_depth": depth_score,
            "vault_synergy": vault_score,
            "total": total_score,
            "word_count": word_count
        }
        return total_score, breakdown

class BatchProducer:
    def __init__(self, personality="untold_truth"):
        self.personality = personality
        self.ranker = ScriptRanker()
        self.engine = MasterEngine(personality=personality)

    def generate_candidate_scripts(self, theme_prompt, count=7):
        p_lower = self.personality.lower()
        if "layi" in p_lower or "prof" in p_lower or "laya" in p_lower:
            topic_pool = PROF_LAYI_TOPICS
        elif "roger" in p_lower:
            topic_pool = SIR_ROGERS_TOPICS
        else:
            topics_file = os.path.join(ROOT_DIR, "config", "viral_topics_vault.json")
            with open(topics_file, "r", encoding="utf-8") as f:
                topic_pool = json.load(f)

        candidates = []
        for i in range(count):
            topic_item = topic_pool[i % len(topic_pool)]
            script_data = self.engine.director.generate_script(topic_item, personality=self.personality)
            candidates.append(script_data)
        return candidates

    def run_rank_and_produce(self, theme=None, num_candidates=7, top_k=3, dry_run=False, personality=None):
        if personality:
            self.personality = personality
            self.engine.set_personality(personality)

        p_lower = self.personality.lower()
        if "layi" in p_lower or "prof" in p_lower or "laya" in p_lower:
            brand_display = "PROF LAYI"
        elif "roger" in p_lower:
            brand_display = "SIR ROGERS"
        else:
            brand_display = "THE UNTOLD TRUTH"

        print("\n" + "=" * 75)
        print(f"🎯 [{brand_display}] 7-SCRIPT CANDIDATE TOURNAMENT & TOP {top_k} ENGINE")
        print("=" * 75)
        print(f"[*] Drafting {num_candidates} retention candidate scripts under '{brand_display}' DNA...")
        candidates = self.generate_candidate_scripts(theme or "Exploits and Human Psychology", count=num_candidates)

        scored_candidates = []
        for idx, cand in enumerate(candidates):
            score, breakdown = self.ranker.score_script(cand, personality=self.personality)
            cand["score"] = score
            cand["breakdown"] = breakdown
            cand["candidate_id"] = idx + 1
            scored_candidates.append(cand)

        # Sort descending by score
        scored_candidates.sort(key=lambda x: x["score"], reverse=True)

        print("\n📊 CANDIDATE TOURNAMENT LEADERBOARD:")
        print("-" * 75)
        print(f"{'Rank':<5} | {'Score':<6} | {'Words':<6} | {'Title':<28} | {'Opening Hook'}")
        print("-" * 75)
        for r, c in enumerate(scored_candidates):
            print(f"#{r+1:<4} | {c['score']}/100 | {c['breakdown']['word_count']:<6} | {c['title'][:27]:<28} | \"{c['beats'][0]['text'][:32]}...\"")

        winners = scored_candidates[:top_k]
        print("\n" + "=" * 75)
        print(f"🏆 TOP {top_k} CHAMPIONS SELECTED FOR AUTOMATED PRODUCTION:")
        for r, w in enumerate(winners):
            print(f"  [{r+1}] {w['title']} (Score: {w['score']}/100) -> Hook: \"{w['beats'][0]['text']}\"")
        print("=" * 75)

        if dry_run:
            print(f"\n[Dry Run] Successfully ranked {num_candidates} candidate scripts under {brand_display}. Compositing skipped.")
            return winners

        produced_videos = []
        for r, winner in enumerate(winners):
            print(f"\n🎬 RENDERING CHAMPION [{r+1}/{top_k}]: {winner['title']}...")
            try:
                mp4 = self.engine.run(winner, voice_engine="f5", personality=self.personality)
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
    parser = argparse.ArgumentParser(description="Candidate Tournament & Batch Video Producer")
    parser.add_argument("--personality", type=str, default="untold_truth", choices=["untold_truth", "prof_layi", "sir_rogers"], help="Personality model")
    parser.add_argument("--theme", type=str, default=None, help="Theme prompt")
    parser.add_argument("--candidates", type=int, default=7, help="Number of scripts to draft (default: 7)")
    parser.add_argument("--top", type=int, default=3, help="Number of top scripts to render (default: 3)")
    parser.add_argument("--dry-run", action="store_true", help="Rank scripts without rendering videos")
    args = parser.parse_args()

    producer = BatchProducer(personality=args.personality)
    producer.run_rank_and_produce(theme=args.theme, num_candidates=args.candidates, top_k=args.top, dry_run=args.dry_run)

if __name__ == "__main__":
    main()
