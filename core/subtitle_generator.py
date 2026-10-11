import os
import sys
import subprocess
import numpy as np
from faster_whisper import WhisperModel

FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

class SubtitleGenerator:
    def __init__(self, model_size="base", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def extract_words(self, audio_path):
        """
        Extracts accurate word timestamps from audio using Faster-Whisper.
        """
        cmd = [FFMPEG, '-y', '-i', audio_path, '-vn', '-ar', '16000', '-ac', '1', '-f', 's16le', '-']
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        audio_data = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

        model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
        segments, info = model.transcribe(audio_data, word_timestamps=True, beam_size=1)

        words = []
        for seg in segments:
            if seg.words:
                for w in seg.words:
                    cleaned = w.word.strip()
                    if cleaned:
                        words.append({
                            "word": cleaned,
                            "start": w.start,
                            "end": w.end
                        })
        return words, info.duration

    def generate_ass(self, words, hook_title, out_ass_path, chunk_size=3):
        """
        Generates kinetic pop .ass subtitles with brand styling.
        """
        os.makedirs(os.path.dirname(os.path.abspath(out_ass_path)), exist_ok=True)

        header = f"""[Script Info]
Title: THE UNTOLD TRUTH Kinetic Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Caption,Arial,58,&H00FFFFFF,&H0023A6F5,&H00000000,&H90000000,-1,0,0,0,100,100,1,0,1,5,6,5,70,70,950,1
Style: HookBadge,Georgia,32,&H00E0DCD0,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,6,0,1,2,3,8,60,60,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        # Upper hook title for the first 3.5 seconds
        events.append(f"Dialogue: 0,0:00:00.00,0:00:03.50,HookBadge,,0,0,0,,[ {hook_title.upper()} ]")

        # Group words into chunks
        chunks = [words[i:i + chunk_size] for i in range(0, len(words), chunk_size)]

        for chunk in chunks:
            for active_idx, target_word in enumerate(chunk):
                w_start = target_word['start']
                w_end = target_word['end']

                styled_words = []
                for idx, item in enumerate(chunk):
                    w_text = item['word'].upper()
                    if idx == active_idx:
                        # Highlighted active word: Amber glow + 114% scale bounce
                        styled_words.append(r"{\c&H0023A6F5\fscx114\fscy114}" + w_text + r"{\r}")
                    else:
                        styled_words.append(r"{\c&H00FFFFFF}" + w_text + r"{\r}")

                line_text = " ".join(styled_words)
                ev = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},Caption,,0,0,0,,{line_text}"
                events.append(ev)

        with open(out_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")

        print(f"      [Subtitles] Generated kinetic ASS subtitles ({len(words)} words): {out_ass_path}", flush=True)
        return out_ass_path

if __name__ == "__main__":
    sub = SubtitleGenerator()
    dummy = [
        {"word": "Being", "start": 0.0, "end": 0.3},
        {"word": "loyal", "start": 0.3, "end": 0.7},
        {"word": "to", "start": 0.7, "end": 0.9},
        {"word": "a", "start": 0.9, "end": 1.1},
        {"word": "company", "start": 1.1, "end": 1.6}
    ]
    sub.generate_ass(dummy, "THE LOYALTY TRAP", "test_sub.ass")
