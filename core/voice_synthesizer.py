import os
import sys
import time
import subprocess
import shutil
import re
import json
import urllib.request

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
    def __init__(self, speed_factor=1.14, tokens=None, hf_token=None, deepgram_api_key=None):
        self.speed_factor = speed_factor
        if isinstance(tokens, list) and len(tokens) > 0:
            self.tokens = tokens
        elif hf_token:
            self.tokens = [hf_token]
        else:
            self.tokens = DEFAULT_TOKENS
        self.deepgram_key = deepgram_api_key or os.getenv("DEEPGRAM_API_KEY")

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

    def synthesize_deepgram(self, text, output_wav, model="aura-angus-en"):
        """
        Synthesizes high-fidelity speech in milliseconds using Deepgram Aura TTS API.
        Models: aura-angus-en (Charismatic Irish/British male - Sir Rogers), aura-arcas-en, aura-orpheus-en
        """

        key = self.deepgram_key or os.getenv("DEEPGRAM_API_KEY")
        if not key:
            raise ValueError("DEEPGRAM_API_KEY not configured in .env or arguments.")

        os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)
        url = f"https://api.deepgram.com/v1/speak?model={model}"
        headers = {
            "Authorization": f"Token {key}",
            "Content-Type": "application/json"
        }
        payload = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=payload, headers=headers)

        temp_audio = output_wav + ".temp.mp3"
        t0 = time.time()
        print(f"      [Deepgram] Synthesizing speech with model '{model}'...", flush=True)
        with urllib.request.urlopen(req) as resp:
            with open(temp_audio, "wb") as f:
                f.write(resp.read())

        # Convert to 44.1kHz 16-bit stereo WAV
        cmd = [
            FFMPEG, '-y',
            '-i', temp_audio,
            '-ar', '44100',
            '-ac', '2',
            output_wav
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        if os.path.exists(temp_audio):
            try:
                os.remove(temp_audio)
            except Exception:
                pass

        print(f"      [Deepgram] Audio generated in {time.time()-t0:.2f}s! Master WAV: {output_wav}", flush=True)
        return output_wav

    def _synthesize_chunk_f5(self, chunk_text, out_chunk_wav, ref_clip, ref_txt):
        from gradio_client import Client, handle_file
        
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
        raise RuntimeError(f"All tokens in pool exhausted. Last error: {last_err}")

    def synthesize_speech(self, text, output_wav, ref_audio=None, ref_text=None, voice_engine="auto", deepgram_model="aura-helios-en"):
        """
        Unified speech synthesis entrypoint.
        Engine choices: 'deepgram', 'f5', 'gtts', or 'auto' (prefers deepgram if key present, else f5).
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_wav)), exist_ok=True)

        if voice_engine == "deepgram" or (voice_engine == "auto" and (self.deepgram_key or os.getenv("DEEPGRAM_API_KEY"))):
            return self.synthesize_deepgram(text, output_wav, model=deepgram_model)
        elif voice_engine == "gtts":
            from gtts import gTTS
            tts = gTTS(text=text, lang='en', tld='co.uk', slow=False)
            temp_mp3 = output_wav + ".gtts.mp3"
            tts.save(temp_mp3)
            cmd = [FFMPEG, '-y', '-i', temp_mp3, '-ar', '44100', '-ac', '2', output_wav]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            if os.path.exists(temp_mp3):
                os.remove(temp_mp3)
            return output_wav
        else:
            # F5-TTS
            ref_clip = ref_audio or DEFAULT_REF_AUDIO
            ref_txt = ref_text or DEFAULT_REF_TEXT
            chunks = self._chunk_text(text)
            temp_dir = os.path.dirname(os.path.abspath(output_wav))
            chunk_wavs = []
            for c_idx, chunk in enumerate(chunks):
                cf = os.path.join(temp_dir, f"_temp_vchunk_{c_idx:02d}.wav")
                self._synthesize_chunk_f5(chunk, cf, ref_clip, ref_txt)
                chunk_wavs.append(cf)

            concat_txt = os.path.join(temp_dir, "_temp_vchunks_concat.txt")
            with open(concat_txt, "w", encoding="utf-8") as f_concat:
                for cw in chunk_wavs:
                    f_concat.write(f"file '{os.path.abspath(cw)}'\n")

            cmd_concat = [FFMPEG, '-y', '-f', 'concat', '-safe', '0', '-i', concat_txt, '-c', 'pcm_s16le', '-ar', '44100', '-ac', '2', output_wav]
            subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            for cw in chunk_wavs:
                if os.path.exists(cw):
                    os.remove(cw)
            if os.path.exists(concat_txt):
                os.remove(concat_txt)
            return output_wav

    def tighten_cadence(self, input_wav, output_wav, speed_factor=None, is_deepgram=False):
        """
        Applies cadence refinement. For Deepgram, preserves natural comedic pauses and clear pitch.
        """
        if is_deepgram:
            # Deepgram voices have human pacing out of the box. Do NOT strip pauses!
            cmd_clean = [
                FFMPEG, '-y',
                '-i', input_wav,
                '-ar', '44100',
                '-ac', '2',
                output_wav
            ]
            subprocess.run(cmd_clean, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
            return output_wav

        factor = speed_factor or self.speed_factor
        af = f"silenceremove=stop_periods=-1:stop_duration=0.28:stop_threshold=-42dB,atempo={factor}"
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


    def synthesize(self, text, out_raw_wav, out_tight_wav, engine="auto", ref_audio=None, ref_text=None, deepgram_model="aura-helios-en"):
        self.synthesize_speech(text, out_raw_wav, ref_audio=ref_audio, ref_text=ref_text, voice_engine=engine, deepgram_model=deepgram_model)
        self.tighten_cadence(out_raw_wav, out_tight_wav, speed_factor=self.speed_factor)
        return out_tight_wav

if __name__ == "__main__":
    v = VoiceSynthesizer()
    v.synthesize("You are a casino owner, and you have a problem. People do not like losing their money to you.", "out/test_dg_raw.wav", "out/test_dg_tight.wav", engine="deepgram")
    print("Test successful!")
