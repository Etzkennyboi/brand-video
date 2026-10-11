import os
import sys
import time
import json
import argparse

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
OUT_DIR = os.path.join(ROOT_DIR, "out")
HISTORY_FILE = os.path.join(OUT_DIR, "produced_history.json")

from engine import MasterEngine

def get_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return []
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def run_daemon(batch_count=1, delay_seconds=0):
    topics_file = os.path.join(CONFIG_DIR, "viral_topics_vault.json")
    with open(topics_file, "r", encoding="utf-8") as f:
        all_topics = json.load(f)

    history = get_history()
    produced_ids = {h["id"] for h in history}

    unproduced = [t for t in all_topics if t["id"] not in produced_ids]
    if not unproduced:
        print("[Daemon] All topics in the vault have already been produced! Resetting history cycle...")
        history = []
        produced_ids = set()
        unproduced = all_topics

    engine = MasterEngine()

    to_produce = unproduced[:batch_count]
    print(f"\n[Autonomous Daemon] Queued {len(to_produce)} video(s) for generation.\n")

    for i, topic in enumerate(to_produce, 1):
        print(f"\n>>> [Daemon Job {i}/{len(to_produce)}] Topic: {topic['title']} ({topic['pillar']})")
        out_path = engine.run(topic)

        history.append({
            "id": topic["id"],
            "title": topic["title"],
            "output_file": out_path,
            "produced_at": time.strftime("%Y-%m-%d %H:%M:%S")
        })
        save_history(history)

        if delay_seconds > 0 and i < len(to_produce):
            print(f"[Daemon] Sleeping {delay_seconds}s before next production...")
            time.sleep(delay_seconds)

    print("\n[Autonomous Daemon] Batch production run complete!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Autonomous Auto-Poster Daemon for THE UNTOLD TRUTH")
    parser.add_argument("--count", type=int, default=1, help="Number of videos to generate in this run")
    parser.add_argument("--interval", type=int, default=0, help="Seconds to sleep between batch generations")
    args = parser.parse_args()

    run_daemon(batch_count=args.count, delay_seconds=args.interval)
