import os
import sys
import time
import subprocess
import shutil
import platform
from concurrent.futures import ThreadPoolExecutor

IS_WINDOWS = platform.system().lower() == "windows"
WIN_FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'
FFMPEG = shutil.which("ffmpeg") or (WIN_FFMPEG if IS_WINDOWS else "ffmpeg")

class SinglePassRender:
    def __init__(self, brand_title="THE UNTOLD TRUTH", watermark_text="THE UNTOLD TRUTH"):
        self.brand_title = brand_title
        self.watermark_text = watermark_text

    def render_scene_clip(self, scene_info, out_clip):
        """
        Renders an animated 2.5D camera zoom clip with high-contrast grading.
        """
        dur = scene_info["duration"]
        fps = 30
        frames = int(dur * fps)
        zoom_dir = scene_info.get("zoom_dir", "in")

        if zoom_dir == "in":
            zoom_expr = "min(zoom+0.00045,1.08)"
        else:
            zoom_expr = "max(1.08-on*0.0004,1.0)"

        vf = (
            f"scale=1200:2133:force_original_aspect_ratio=increase,"
            f"crop=1080:1920,"
            f"zoompan=z='{zoom_expr}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={frames}:s=1080x1920:fps={fps},"
            f"vignette=PI/4,"
            f"eq=contrast=1.06:saturation=1.04"
        )

        cmd = [
            FFMPEG, '-y',
            '-loop', '1', '-i', scene_info["image_path"],
            '-vf', vf,
            '-c:v', 'libx264',
            '-preset', 'ultrafast', # Fast parallel clip generation
            '-crf', '19',
            '-pix_fmt', 'yuv420p',
            '-t', str(dur),
            out_clip
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        return out_clip

    def render_full_video(self, scenes, voice_audio, bgm_audio, ass_subtitles, output_mp4, bgm_volume=0.14, total_duration=None):
        return self.build_video(
            scenes=scenes,
            voice_audio=voice_audio,
            bgm_audio=bgm_audio,
            ass_path=ass_subtitles,
            total_duration=total_duration,
            out_master_path=output_mp4,
            bgm_volume=bgm_volume
        )

    def build_video(self, scenes, voice_audio, bgm_audio, ass_path, total_duration, out_master_path, bgm_volume=0.14):

        """
        Assembles all scenes in parallel, merges audio with dynamic ducking,
        and burns subtitles + brand watermark.
        """
        t0 = time.time()
        temp_dir = os.path.dirname(os.path.abspath(out_master_path))
        os.makedirs(temp_dir, exist_ok=True)

        # Step 1: Render scenes in parallel across CPU cores
        print(f"      [Render] Generating {len(scenes)} camera-motion scenes in parallel...", flush=True)
        clip_paths = [os.path.join(temp_dir, f"_temp_scene_{i:02d}.mp4") for i in range(len(scenes))]
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = [
                executor.submit(self.render_scene_clip, scene, clip_paths[i])
                for i, scene in enumerate(scenes)
            ]
            for f in futures:
                f.result()

        # Step 2: Write concat list
        concat_list_file = os.path.join(temp_dir, "_temp_concat.txt")
        with open(concat_list_file, "w", encoding="utf-8") as f_concat:
            for cp in clip_paths:
                f_concat.write(f"file '{os.path.abspath(cp)}'\n")

        # Step 3: Stream-concat to single temp video track
        raw_video_track = os.path.join(temp_dir, "_temp_raw_track.mp4")
        cmd_concat = [
            FFMPEG, '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', concat_list_file,
            '-c', 'copy',
            raw_video_track
        ]
        subprocess.run(cmd_concat, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Step 4: Mix audio with 500% signature BGM boost + broadcast compand + loudnorm limiter
        mixed_audio = os.path.join(temp_dir, "_temp_mixed_audio.wav")
        audio_filter = (
            "[0:a]equalizer=f=120:t=q:w=1.2:g=2.8,"
            "equalizer=f=2800:t=q:w=1.0:g=2.2,"
            "equalizer=f=5500:t=q:w=1.0:g=2.5,"
            "compand=attacks=0.02:decays=0.15:points=-60/-60|-24/-14|-12/-7|0/-2:soft-knee=6:gain=4[v_proc];"
            f"[1:a]lowpass=f=7500,volume={bgm_volume}[bg_proc];"
            "[v_proc][bg_proc]amix=inputs=2:normalize=0:dropout_transition=0[mix];"
            f"[mix]afade=t=out:st={total_duration - 0.6}:d=0.6[faded];"
            "[faded]loudnorm=I=-14.0:TP=-1.0:LRA=7.0[master]"
        )


        cmd_audio = [
            FFMPEG, '-y',
            '-i', voice_audio,
            '-stream_loop', '-1', '-i', bgm_audio,
            '-filter_complex', audio_filter,
            '-map', '[master]',
            '-t', str(total_duration),
            mixed_audio
        ]
        subprocess.run(cmd_audio, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Step 5: Final pass - Burn kinetic ASS subtitles + brand watermark
        print(f"      [Render] Burning '{self.brand_title}' branding and kinetic pop subtitles...", flush=True)
        if IS_WINDOWS and os.path.exists(r"C:\Windows\Fonts\georgiab.ttf"):
            font_opt = "fontfile='C\\:/Windows/Fonts/georgiab.ttf':"
            fontsdir_opt = ":fontsdir=C\\\\:/Windows/Fonts"
        else:
            font_opt = ""
            fontsdir_opt = ""

        safe_ass = ass_path.replace("\\", "/").replace(":", "\\:")
        final_vf = (
            f"drawtext=text='{self.watermark_text}':{font_opt}fontsize=32:fontcolor=white@0.75:"
            f"x=(w-text_w)/2:y=h-240:shadowcolor=black@0.9:shadowx=2:shadowy=2,"
            f"ass='{safe_ass}'{fontsdir_opt}"
        )

        final_cmd = [
            FFMPEG, '-y',
            '-i', raw_video_track,
            '-i', mixed_audio,
            '-vf', final_vf,
            '-c:v', 'libx264',
            '-preset', 'ultrafast', # Ultra-fast production encoding
            '-crf', '18',
            '-pix_fmt', 'yuv420p',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-t', str(total_duration),
            out_master_path
        ]
        subprocess.run(final_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

        # Step 6: Cleanup temporary clips
        for cp in clip_paths:
            if os.path.exists(cp):
                os.remove(cp)
        if os.path.exists(concat_list_file):
            os.remove(concat_list_file)
        if os.path.exists(raw_video_track):
            os.remove(raw_video_track)
        if os.path.exists(mixed_audio):
            os.remove(mixed_audio)

        render_sec = time.time() - t0
        print(f"      [Render] Render completed in {render_sec:.2f}s! -> {out_master_path}", flush=True)
        return out_master_path, render_sec

if __name__ == "__main__":
    print("SinglePassRender module loaded successfully.")
