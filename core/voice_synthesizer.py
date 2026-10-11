import os
import sys
import time
import subprocess
import shutil
import re

FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'

DEFAULT_REF_AUDIO = os.path.abspath(r"the_untold_truth/assets/ref_voice_vid5.wav")
if not os.path.exists(DEFAULT_REF_AUDIO):
    DEFAULT_REF_AUDIO = os.path.abspath(r"vid5_ref_clip.wav")

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


class VoiceSynthesizer:
    def __init__(self, speed_factor=1.14, tokens=None, hf_token=None):
        self.speed_factor = speed_factor
        if isinstance(tokens, list) and len(tokens) > 0:
            self.tokens = tokens
        elif hf_token:
            self.tokens = [hf_token]
        else:
            self.tokens = DEFAULT_TOKENS

    def _chunk_text(self, text, max_words=26):
        """
        Splits text into ~20-25 word natural sentence chunks.
        Prevents F5-TTS autoregressive prefix-bleeding and ZeroGPU timeout errors.
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

    def _synthesize_chunk_f5(self, chunk_text, out_chunk_wav, ref_clip, ref_txt):
        """
        Synthesizes a single chunk with F5-TTS, trying tokens in pool.
        """
        from gradio_client import Client, handle_file
        
        last_err = None
        for idx, tok in enumerate(self.tokens):
            try:
                masked_tok = f"{tok[:7]}...{tok[-4:]}"
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
                err_str = str(e)
                last_err = e
                if "quota" in err_str.lower() or "exceeded" in err_str.lower():
                    print(f"      [Voice] Token #{idx+1} reached hourly quota. Rolling over...", flush=True)
                else:
                    print(f"      [Voice] Token #{idx+1} busy ({e}). Rolling over...", flush=True)
        raise RuntimeError(f"All tokens in pool exhausted. Last error: {last_err}")

    def synthesize(self, text, out_raw_wav, out_tight_wav, engine="f5", ref_audio=None, ref_text=None):
        """
        Synthesizes speech using the signature Video 5 cloned voice (F5-TTS).
        Uses sentence chunking to prevent hallucinations, looping, and GPU quota timeouts.
        """
        os.makedirs(os.path.dirname(os.path.abspath(out_raw_wav)), exist_ok=True)
        os.makedirs(os.path.dirname(os.path.abspath(out_tight_wav)), exist_ok=True)

        ref_clip = ref_audio or DEFAULT_REF_AUDIO
        ref_txt = ref_text or DEFAULT_REF_TEXT

        t0 = time.time()
        chunks = self._chunk_text(text)
        print(f"      [Voice] Synthesizing Video 5 voice in {len(chunks)} clean chunks (Token Pool: {len(self.tokens)})...", flush=True)

        temp_dir = os.path.dirname(os.path.abspath(out_raw_wav))
        chunk_wavs = []

        for c_idx, chunk in enumerate(chunks):
            chunk_file = os.path.join(temp_dir, f"_temp_vchunk_{c_idx:02d}.wav")
            print(f"      [Voice] Chunk {c_idx+1}/{len(chunks)} ({len(chunk.split())} words): \"{chunk[:45]}...\"", flush=True)
            self._synthesize_chunk_f5(chunk, chunk_file, ref_clip, ref_txt)
            chunk_wavs.append(chunk_file)

        # Concatenate chunks with clean audio stream
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
            out_raw_wav
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Clean up temporary chunk WAVs
        for cw in chunk_wavs:
            if os.path.exists(cw):
                try:
                    os.remove(cw)
                except Exception:
                    pass
        if os.path.exists(concat_txt):
            try:
                os.remove(concat_txt)
            except Exception:
                pass

        print(f"      [Voice] Cloned speech generated in {time.time()-t0:.2f}s! Applying signature 1.14x tightening...", flush=True)

        # Apply signature 1.14x viral tightening & silenceremove
        af = f"silenceremove=stop_periods=-1:stop_duration=0.28:stop_threshold=-42dB,atempo={self.speed_factor}"
        cmd_tight = [
            FFMPEG, '-y',
            '-i', out_raw_wav,
            '-af', af,
            '-ar', '44100',
            '-ac', '2',
            out_tight_wav
        ]
        subprocess.run(cmd_tight, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"      [Voice] Tightened master voice ready: {out_tight_wav}", flush=True)
        return out_tight_wav

if __name__ == "__main__":
    v = VoiceSynthesizer()
    v.synthesize("Notice who stopped clapping when you started winning. People love supporting you when you are struggling.", "test_raw.wav", "test_tight.wav")
