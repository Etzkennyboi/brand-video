import os
import sys
import time
import subprocess
import shutil
import re
from concurrent.futures import ThreadPoolExecutor

import platform

IS_WINDOWS = platform.system().lower() == "windows"
WIN_FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'
FFMPEG = shutil.which("ffmpeg") or (WIN_FFMPEG if IS_WINDOWS else "ffmpeg")

ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
parent_dir = os.path.dirname(ROOT_DIR)
vid5_clip = os.path.join(parent_dir, "vid5_ref_clip.wav")
if os.path.exists(vid5_clip):
    DEFAULT_REF_AUDIO = vid5_clip
else:
    DEFAULT_REF_AUDIO = os.path.join(ROOT_DIR, "assets", "ref_voice_vid5.wav")

DEFAULT_REF_TEXT = "The word karma is a word used by losers. People use it when they're too powerless to get justice themselves."

try:
    import dotenv
    dotenv.load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))
    dotenv.load_dotenv(os.path.join(os.getcwd(), ".env"))
except ImportError:
    pass

env_tokens = os.getenv("HF_TOKENS")
if env_tokens:
    DEFAULT_TOKENS = [t.strip() for t in env_tokens.split(",") if t.strip()]
elif os.getenv("HF_TOKEN"):
    DEFAULT_TOKENS = [os.getenv("HF_TOKEN").strip()]
else:
    DEFAULT_TOKENS = []


def sanitize_voice_text(text: str) -> str:
    """
    Cleans and reformats text specifically for F5-TTS cloned voice synthesis:
    - Colons (:) and semicolons (;) break voice cadence because F5-TTS does not
      pause naturally on them. Replaces with a natural comma pause.
    - Hyphens (-), em dashes (—), and en dashes (–) break flow without pausing.
      Replaces with a natural comma pause.
    - Hyphenated compound words (e.g. 'fear-inducer') -> 'fear inducer' for smooth articulation.
    - Ellipses (...) -> converted to comma or period depending on context.
    - Strips quotes, backticks, asterisks, brackets, and markdown formatting that confuse phonemizer.
    - Normalizes punctuation combinations and whitespace.
    """
    if not text:
        return ""
    t = text
    # 1. Colons & Semicolons -> comma pause
    t = re.sub(r':\s*', ', ', t)
    t = re.sub(r';\s*', ', ', t)

    # 2. Em-dashes, en-dashes, and spaced hyphens -> comma pause
    t = re.sub(r'\s*[\u2014\u2013—–]+\s*', ', ', t)
    t = re.sub(r'\s+-\s+', ', ', t)

    # 3. Compound hyphens -> single space for natural pronunciation
    t = re.sub(r'(\w)-(\w)', r'\1 \2', t)

    # 4. Ellipses -> comma if followed by lowercase clause, period otherwise
    t = re.sub(r'\s*\.{2,}\s*(?=[a-z])', ', ', t)
    t = re.sub(r'\s*\.{2,}\s*', '. ', t)

    # 5. Remove quotes, backticks, brackets, formatting symbols
    t = re.sub(r'["\'`*~_\[\]\(\)<>{}]', '', t)

    # 6. Normalize punctuation combinations
    t = re.sub(r',\s*,+', ',', t)
    t = re.sub(r',\s*\.', '.', t)
    t = re.sub(r'\.\s*,', '.', t)
    t = re.sub(r'!\s*,', '!', t)
    t = re.sub(r'\?\s*,', '?', t)

    # 7. Ensure space after punctuation
    t = re.sub(r'([,.!?])(?=[^\s\d])', r'\1 ', t)

    # 8. Collapse whitespace
    t = re.sub(r'\s+', ' ', t).strip()
    return t


class VoiceSynthesizer:
    def __init__(self, speed_factor=1.14, tokens=None, hf_token=None):
        self.speed_factor = speed_factor
        if isinstance(tokens, list) and len(tokens) > 0:
            self.tokens = tokens
        elif hf_token:
            self.tokens = [hf_token]
        else:
            self.tokens = DEFAULT_TOKENS
        
        # Cache active Colab client connection for high-speed reuse
        self._colab_client = None
        self._colab_url = None

    def get_colab_client(self):
        """
        Maintains a persistent client connection to the Colab GPU endpoint,
        eliminating repeated HTTP handshakes.
        """
        colab_url = os.getenv("F5_COLAB_URL") or os.getenv("F5_ENDPOINT")
        if not colab_url:
            return None, None
        
        if self._colab_client is not None and self._colab_url == colab_url:
            return self._colab_client, colab_url

        try:
            from gradio_client import Client
            client = Client(colab_url, httpx_kwargs={"timeout": 120.0})
            self._colab_client = client
            self._colab_url = colab_url
            return self._colab_client, colab_url
        except Exception as e:
            print(f"      [Voice] Error connecting to Colab client ({e})", flush=True)
            return None, colab_url

    def _chunk_text(self, text, max_words=45):
        """
        Splits text into natural sentence chunks (~40-45 words).
        Optimized for Colab T4 GPU to minimize round-trips while maintaining high voice quality.
        """
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
        chunks = []
        curr = []
        curr_len = 0
        for s in sentences:
            w_count = len(s.split())
            if curr and (curr_len + w_count > max_words):
                chunks.append(" ".join(curr))
                curr = [s]
                curr_len = w_count
            else:
                curr.append(s)
                curr_len += w_count
        if curr:
            chunks.append(" ".join(curr))
        return chunks

    def _synthesize_chunk_f5(self, chunk_text, out_chunk_wav, ref_clip, ref_txt, client_instance=None):
        from gradio_client import Client, handle_file
        
        colab_url = os.getenv("F5_COLAB_URL") or os.getenv("F5_ENDPOINT")
        if colab_url:
            client = client_instance
            if client is None:
                client, _ = self.get_colab_client()

            for attempt in range(3):
                try:
                    if client is None:
                        client = Client(colab_url, httpx_kwargs={"timeout": 120.0})
                        self._colab_client = client
                        self._colab_url = colab_url

                    try:
                        res = client.predict(
                            ref_audio_input=handle_file(ref_clip),
                            ref_text_input=ref_txt,
                            gen_text_input=chunk_text,
                            remove_silence=True,
                            randomize_seed=True,
                            seed_input=0,
                            cross_fade_duration_slider=0.15,
                            speed_slider=1.0,
                            api_name="/basic_tts"
                        )
                        wav_path = res[0] if isinstance(res, (tuple, list)) else res
                    except Exception:
                        # Fallback for /predict endpoint
                        res = client.predict(
                            ref_audio=handle_file(ref_clip),
                            ref_text=ref_txt,
                            gen_text=chunk_text,
                            remove_silence=True,
                            api_name="/predict"
                        )
                        wav_path = res[0] if isinstance(res, (tuple, list)) else res

                    shutil.copy2(wav_path, out_chunk_wav)
                    return True
                except Exception as e:
                    print(f"      [Voice] Colab attempt {attempt+1} error ({e})...", flush=True)
                    # Reconnect client on failure
                    client = None
                    self._colab_client = None
                    time.sleep(1.5)

        # Fallback to Hugging Face token pool
        last_err = None
        for idx, tok in enumerate(self.tokens):
            try:
                client = Client("mrfakename/E2-F5-TTS", token=tok, httpx_kwargs={"timeout": 120.0})
                res = client.predict(
                    ref_audio=handle_file(ref_clip),
                    ref_text=ref_txt,
                    gen_text=chunk_text,
                    remove_silence=True,
                    api_name="/predict"
                )
                shutil.copy2(res, out_chunk_wav)
                return True
            except Exception as e:
                last_err = e
                err_str = str(e)
                if "quota" in err_str.lower() or "exceeded" in err_str.lower():
                    print(f"      [Voice] Token #{idx+1} reached hourly quota. Rolling over...", flush=True)
                else:
                    print(f"      [Voice] Token #{idx+1} busy ({e}). Rolling over...", flush=True)
        raise RuntimeError(f"All voice synthesis endpoints exhausted. Last error: {last_err}")

    def synthesize_speech(self, text, output_wav, ref_audio=None, ref_text=None, voice_engine="f5"):
        """
        Main speech synthesis entrypoint. Default and primary engine is F5-TTS voice cloning.
        Uses parallel chunk processing over Colab T4 GPU for maximum throughput.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)

        # Sanitize text to remove colons, hyphens, and syntax that break F5 cadence
        clean_text = sanitize_voice_text(text)

        if voice_engine == "gtts":
            from gtts import gTTS
            tts = gTTS(text=clean_text, lang='en', tld='co.uk', slow=False)
            temp_mp3 = output_wav + ".gtts.mp3"
            tts.save(temp_mp3)
            cmd = [FFMPEG, '-y', '-i', temp_mp3, '-ar', '44100', '-ac', '2', output_wav]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            return output_wav

        # Primary Engine: F5-TTS Voice Cloning
        ref_clip = ref_audio or DEFAULT_REF_AUDIO
        ref_txt = ref_text or DEFAULT_REF_TEXT
        
        # Optimized chunk size (~45 words)
        chunks = self._chunk_text(clean_text, max_words=45)
        temp_dir = os.path.dirname(os.path.abspath(output_wav))
        chunk_wavs = [os.path.join(temp_dir, f"_temp_vchunk_{i:02d}.wav") for i in range(len(chunks))]
        
        client, colab_url = self.get_colab_client()
        print(f"      [Voice] Synthesizing {len(chunks)} chunk(s) via F5-TTS cloned voice ({os.path.basename(ref_clip)})...", flush=True)
        t0 = time.time()

        for c_idx, chunk in enumerate(chunks):
            print(f"      [Voice] Processing chunk {c_idx+1}/{len(chunks)}...", flush=True)
            self._synthesize_chunk_f5(chunk, chunk_wavs[c_idx], ref_clip, ref_txt, client_instance=client)

        # Concatenate chunks into final audio track
        concat_txt = os.path.join(temp_dir, "_temp_vchunks_concat.txt")
        with open(concat_txt, "w", encoding="utf-8") as f_concat:
            for cw in chunk_wavs:
                f_concat.write(f"file '{os.path.abspath(cw)}'\n")

        cmd_concat = [
            FFMPEG, '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_txt,
            '-c', 'pcm_s16le',
            '-ar', '44100',
            '-ac', '2',
            output_wav
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Clean temporary chunks
        for cw in chunk_wavs:
            if os.path.exists(cw):
                os.remove(cw)
        if os.path.exists(concat_txt):
            os.remove(concat_txt)

        print(f"      [Voice] F5 voiceover completed in {time.time()-t0:.2f}s! -> {output_wav}", flush=True)
        return output_wav

    def tighten_cadence(self, input_wav, output_wav, speed_factor=None):
        """
        Trims silence and tightens pacing for high-retention viral delivery.
        """
        factor = speed_factor or self.speed_factor
        af = f"silenceremove=stop_periods=-1:stop_duration=0.22:stop_threshold=-40dB,atempo={factor}"

        cmd_tight = [
            FFMPEG, '-y',
            '-i', input_wav,
            '-af', af,
            '-ar', '44100',
            '-ac', '2',
            output_wav
        ]
        subprocess.run(cmd_tight, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return output_wav

    def synthesize(self, text, out_raw_wav, out_tight_wav, engine="f5", ref_audio=None, ref_text=None):
        self.synthesize_speech(text, out_raw_wav, ref_audio=ref_audio, ref_text=ref_text, voice_engine=engine)
        self.tighten_cadence(out_raw_wav, out_tight_wav, speed_factor=self.speed_factor)
        return out_tight_wav

if __name__ == "__main__":
    v = VoiceSynthesizer()
    print("Default ref voice:", DEFAULT_REF_AUDIO)
    print("Testing F5 synthesizer initialization...")
