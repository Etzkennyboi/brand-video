import os
import sys
import subprocess
import numpy as np
import re
from faster_whisper import WhisperModel

import shutil
import platform

IS_WINDOWS = platform.system().lower() == "windows"
WIN_FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'
FFMPEG = shutil.which("ffmpeg") or (WIN_FFMPEG if IS_WINDOWS else "ffmpeg")

def format_ass_time(sec):
    h = int(sec // 3600)
    m = int((sec % 3600) // 60)
    s = int(sec % 60)
    cs = int(round((sec - int(sec)) * 100))
    if cs >= 100:
        cs = 99
    return f"{h}:{m:02d}:{s:02d}.{cs:02d}"

class SubtitleGenerator:
    def __init__(self, model_size="tiny.en", device="cpu", compute_type="int8"):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model = None

    def get_model(self):
        if self._model is None:
            try:
                self._model = WhisperModel(self.model_size, device=self.device, compute_type=self.compute_type)
            except Exception as e:
                print(f"      [Subtitle] Whisper on {self.device} failed ({e}), falling back to CPU int8...", flush=True)
                self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
        return self._model

    def extract_words(self, audio_path):
        """
        Extracts accurate word timestamps from audio using Faster-Whisper.
        """
        cmd = [FFMPEG, '-y', '-i', audio_path, '-vn', '-ar', '16000', '-ac', '1', '-f', 's16le', '-']
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, check=True)
        audio_data = np.frombuffer(res.stdout, dtype=np.int16).astype(np.float32) / 32768.0

        try:
            model = self.get_model()
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
        except Exception as e:
            print(f"      [Subtitle] CUDA Whisper execution failed ({e}), switching to CPU Whisper...", flush=True)
            self._model = WhisperModel(self.model_size, device="cpu", compute_type="int8")
            segments, info = self._model.transcribe(audio_data, word_timestamps=True, beam_size=1)
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

    def transcribe_words(self, audio_path):
        words, duration = self.extract_words(audio_path)
        return words

    def generate_ass_file(self, words, out_ass_path, title=""):
        return self.generate_ass(words, title, out_ass_path)

    def generate_ass(self, words, hook_title, out_ass_path, chunk_size=1):
        """
        Generates viral single-word kinetic pop .ass subtitles.
        Exactly ONE word is visible on screen at a time, synchronized to speech.
        """
        os.makedirs(os.path.dirname(os.path.abspath(out_ass_path)), exist_ok=True)

        header = f"""[Script Info]
Title: THE UNTOLD TRUTH Single-Word Kinetic Subtitles
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: SingleWord,Arial,74,&H00FFFFFF,&H0023A6F5,&H00000000,&H90000000,-1,0,0,0,100,100,2,0,1,6,5,5,60,60,960,1
Style: HookBadge,Georgia,32,&H00E0DCD0,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,6,0,1,2,3,8,60,60,180,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
        events = []
        # Upper hook title badge for the first 3.2 seconds
        events.append(f"Dialogue: 0,0:00:00.00,0:00:03.20,HookBadge,,0,0,0,,[ {hook_title.upper()} ]")

        # Single word on screen at a time
        gold_accent_keywords = {
            "MONEY", "POWER", "CURRENCY", "TRUTH", "SHADOW", "LEVERAGE", "SILENCE", "BREAKTHROUGH",
            "PROFIT", "DISCIPLINE", "WEALTH", "LEADER", "KING", "PREDATOR", "SECRET", "FREEDOM",
            "DELUSION", "TRASH", "POISON", "AMBITION", "LIGHTNING", "MASTER", "CERTIFICATE", "PADLOCK"
        }

        for w in words:
            w_start = w['start']
            w_end = w['end']
            clean_word = re.sub(r"[^\w\'-]", "", w['word']).upper()
            if not clean_word:
                continue

            # Check if this word should have golden emphasis
            if clean_word in gold_accent_keywords:
                # Gold color with 118% energetic kinetic bounce
                styled = r"{\c&H0023A6F5\fscx118\fscy118\t(0,60,\fscx100\fscy100)}" + clean_word + r"{\r}"
            else:
                # Crisp white with 112% pop bounce
                styled = r"{\c&H00FFFFFF\fscx112\fscy112\t(0,50,\fscx100\fscy100)}" + clean_word + r"{\r}"

            ev = f"Dialogue: 0,{format_ass_time(w_start)},{format_ass_time(w_end)},SingleWord,,0,0,0,,{styled}"
            events.append(ev)

        with open(out_ass_path, "w", encoding="utf-8") as f:
            f.write(header + "\n".join(events) + "\n")

        print(f"      [Subtitles] Generated 1-word-at-a-time kinetic subtitles ({len(words)} events): {out_ass_path}", flush=True)
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
