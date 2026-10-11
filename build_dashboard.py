import os
import json
import glob

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
READY_DIR = os.path.join(ROOT_DIR, "out", "ready_to_publish")
CONFIG_DIR = os.path.join(ROOT_DIR, "config")
OUT_HTML = os.path.join(ROOT_DIR, "preview_dashboard.html")

def build_dashboard():
    # Load topics
    topics_file = os.path.join(CONFIG_DIR, "viral_topics_vault.json")
    with open(topics_file, "r", encoding="utf-8") as f:
        topics = json.load(f)

    # Find all produced videos & metadata
    meta_files = glob.glob(os.path.join(READY_DIR, "*_metadata.json"))
    videos_data = []

    for mf in meta_files:
        try:
            with open(mf, "r", encoding="utf-8") as f:
                meta = json.load(f)
            base_slug = os.path.basename(mf).replace("_metadata.json", "")
            mp4_file = os.path.join("out", "ready_to_publish", f"{base_slug}_master.mp4")
            thumb_file = os.path.join("out", "ready_to_publish", f"{base_slug}_thumbnail.jpg")
            if not os.path.exists(os.path.join(ROOT_DIR, thumb_file)):
                thumb_file = os.path.join("out", "ready_to_publish", f"preview_frame_2s.jpg")

            videos_data.append({
                "slug": base_slug,
                "title": meta.get("title", base_slug),
                "hook": meta.get("hook", ""),
                "description": meta.get("description", ""),
                "hashtags": " ".join(meta.get("hashtags", [])),
                "pinned_comment": meta.get("pinned_comment", ""),
                "duration": f"{meta.get('duration_sec', 0):.1f}s",
                "created_at": meta.get("created_at", ""),
                "mp4_rel": mp4_file.replace("\\", "/"),
                "thumb_rel": thumb_file.replace("\\", "/")
            })
        except Exception as e:
            print("Error parsing", mf, e)

    cards_html = []
    for v in videos_data:
        cards_html.append(f"""
        <div class="video-card">
            <div class="media-container">
                <video controls poster="{v['thumb_rel']}" preload="metadata">
                    <source src="{v['mp4_rel']}" type="video/mp4">
                    Your browser does not support video.
                </video>
            </div>
            <div class="card-body">
                <div class="badge-row">
                    <span class="badge brand">[ THE UNTOLD TRUTH ]</span>
                    <span class="badge duration">{v['duration']}</span>
                    <span class="badge time">{v['created_at']}</span>
                </div>
                <h3 class="video-title">{v['title']}</h3>
                <p class="hook-quote">"{v['hook']}"</p>

                <div class="meta-section">
                    <label>Pinned Comment:</label>
                    <div class="code-box">{v['pinned_comment']}</div>
                </div>

                <div class="action-row">
                    <button class="btn btn-primary" onclick="copyText(`{v['title']}`)">📋 Copy Title</button>
                    <button class="btn btn-secondary" onclick="copyText(`{v['description']}`)">📄 Copy Description</button>
                    <button class="btn btn-secondary" onclick="copyText(`{v['hashtags']}`)">🏷️ Copy Tags</button>
                </div>
            </div>
        </div>
        """)

    cards_joined = "\n".join(cards_html) if cards_html else "<p class='empty-state'>No videos produced yet. Run engine.py to produce your first short.</p>"

    queue_items = []
    for t in topics[:6]:
        queue_items.append(f"""
        <div class="queue-item">
            <span class="q-pillar">{t['pillar']}</span>
            <span class="q-title">{t['title']}</span>
            <span class="q-hook">"{t['hook']}"</span>
        </div>
        """)
    queue_joined = "\n".join(queue_items)

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>THE UNTOLD TRUTH | Production Studio Dashboard</title>
    <style>
        :root {{
            --bg-main: #0a0b0e;
            --bg-card: #13151b;
            --bg-elevated: #1a1e27;
            --amber-glow: #F5A623;
            --cyan-accent: #00D2FF;
            --text-main: #f0f2f5;
            --text-muted: #8b92a5;
            --border: #232733;
        }}
        * {{ box-sizing: border-box; margin: 0; padding: 0; }}
        body {{
            background: var(--bg-main);
            color: var(--text-main);
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            padding: 30px 40px;
            line-height: 1.5;
        }}
        header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding-bottom: 25px;
            border-bottom: 1px solid var(--border);
            margin-bottom: 30px;
        }}
        .brand-logo {{
            font-family: "Georgia", serif;
            font-size: 28px;
            font-weight: bold;
            letter-spacing: 3px;
            color: #fff;
        }}
        .brand-logo span {{ color: var(--amber-glow); }}
        .header-stats {{
            display: flex;
            gap: 20px;
        }}
        .stat-badge {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            padding: 10px 18px;
            border-radius: 8px;
            text-align: center;
        }}
        .stat-val {{ font-size: 20px; font-weight: bold; color: var(--amber-glow); }}
        .stat-lbl {{ font-size: 11px; text-transform: uppercase; color: var(--text-muted); letter-spacing: 1px; }}

        .layout-grid {{
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 30px;
        }}
        .section-header {{
            font-size: 18px;
            text-transform: uppercase;
            letter-spacing: 2px;
            color: var(--amber-glow);
            margin-bottom: 20px;
            display: flex;
            align-items: center;
            gap: 10px;
        }}
        .video-card {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            display: flex;
            overflow: hidden;
            margin-bottom: 25px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            transition: transform 0.2s, border-color 0.2s;
        }}
        .video-card:hover {{
            border-color: var(--amber-glow);
            transform: translateY(-2px);
        }}
        .media-container {{
            width: 270px;
            min-width: 270px;
            background: #000;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        .media-container video {{
            width: 100%;
            height: 100%;
            max-height: 480px;
            object-fit: cover;
        }}
        .card-body {{
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            flex-grow: 1;
        }}
        .badge-row {{
            display: flex;
            gap: 8px;
            margin-bottom: 12px;
        }}
        .badge {{
            font-size: 11px;
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }}
        .badge.brand {{ background: rgba(245,166,35,0.15); color: var(--amber-glow); border: 1px solid rgba(245,166,35,0.3); font-family: Georgia, serif; }}
        .badge.duration {{ background: rgba(0,210,255,0.15); color: var(--cyan-accent); }}
        .badge.time {{ background: var(--bg-elevated); color: var(--text-muted); }}

        .video-title {{
            font-size: 20px;
            margin-bottom: 10px;
            color: #fff;
            line-height: 1.3;
        }}
        .hook-quote {{
            font-style: italic;
            color: var(--amber-glow);
            margin-bottom: 15px;
            font-size: 14px;
            border-left: 2px solid var(--amber-glow);
            padding-left: 10px;
        }}
        .meta-section {{
            margin-bottom: 15px;
        }}
        .meta-section label {{
            display: block;
            font-size: 11px;
            color: var(--text-muted);
            text-transform: uppercase;
            margin-bottom: 4px;
        }}
        .code-box {{
            background: var(--bg-main);
            border: 1px solid var(--border);
            padding: 10px;
            border-radius: 6px;
            font-size: 12px;
            color: #ccc;
            user-select: all;
        }}
        .action-row {{
            display: flex;
            gap: 10px;
        }}
        .btn {{
            padding: 8px 14px;
            font-size: 12px;
            font-weight: bold;
            border-radius: 6px;
            cursor: pointer;
            border: 1px solid transparent;
            transition: background 0.2s;
        }}
        .btn-primary {{
            background: var(--amber-glow);
            color: #000;
        }}
        .btn-primary:hover {{ background: #e09419; }}
        .btn-secondary {{
            background: var(--bg-elevated);
            color: var(--text-main);
            border-color: var(--border);
        }}
        .btn-secondary:hover {{ background: #232834; }}

        .sidebar {{
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 24px;
            height: fit-content;
        }}
        .queue-item {{
            padding: 12px 0;
            border-bottom: 1px solid var(--border);
        }}
        .queue-item:last-child {{ border-bottom: none; }}
        .q-pillar {{
            display: inline-block;
            font-size: 10px;
            color: var(--cyan-accent);
            text-transform: uppercase;
            font-weight: bold;
            letter-spacing: 1px;
        }}
        .q-title {{
            display: block;
            font-weight: bold;
            color: #fff;
            margin: 4px 0;
            font-size: 14px;
        }}
        .q-hook {{
            display: block;
            font-size: 12px;
            color: var(--text-muted);
            font-style: italic;
        }}
        .cmd-snippet {{
            margin-top: 20px;
            background: var(--bg-main);
            border: 1px solid var(--border);
            padding: 15px;
            border-radius: 8px;
            font-family: monospace;
            font-size: 12px;
            color: #00D2FF;
        }}
    </style>
</head>
<body>
    <header>
        <div class="brand-logo">[ THE UNTOLD <span>TRUTH</span> ]</div>
        <div class="header-stats">
            <div class="stat-badge">
                <div class="stat-val">{len(videos_data)}</div>
                <div class="stat-lbl">Videos Ready</div>
            </div>
            <div class="stat-badge">
                <div class="stat-val">100</div>
                <div class="stat-lbl">Vault Assets</div>
            </div>
            <div class="stat-badge">
                <div class="stat-val">~52s</div>
                <div class="stat-lbl">Avg Render Time</div>
            </div>
        </div>
    </header>

    <div class="layout-grid">
        <main>
            <div class="section-header">📁 Produced Shorts Library</div>
            {cards_joined}
        </main>

        <aside class="sidebar">
            <div class="section-header">⚡ Next in Topic Queue</div>
            {queue_joined}

            <div class="cmd-snippet">
                # Generate next video:<br>
                python the_untold_truth\\engine.py --auto
            </div>
        </aside>
    </div>

    <script>
        function copyText(txt) {{
            navigator.clipboard.writeText(txt).then(() => {{
                alert("Copied to clipboard!");
            }});
        }}
    </script>
</body>
</html>
"""
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Generated Studio Dashboard: {OUT_HTML}")

if __name__ == "__main__":
    build_dashboard()
