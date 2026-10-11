import os
import subprocess

FFMPEG = r'C:\Users\User\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-9.0.1-full_build\bin\ffmpeg.EXE'

class ThumbnailGenerator:
    def __init__(self, brand_title="THE UNTOLD TRUTH"):
        self.brand_title = brand_title

    def generate_cover(self, background_img, title_text, output_path, brand_subtitle=None):
        if brand_subtitle:
            self.brand_title = brand_subtitle
        return self.generate_thumbnail(
            base_image=background_img,
            hook_title=title_text,
            hook_text=title_text,
            out_thumbnail_path=output_path
        )

    def generate_thumbnail(self, base_image, hook_title, hook_text, out_thumbnail_path):

        """
        Creates a high-CTR YouTube/TikTok cover thumbnail with dark vignette and bold curiosity hook.
        """
        os.makedirs(os.path.dirname(os.path.abspath(out_thumbnail_path)), exist_ok=True)

        # Break hook text into 2 punchy lines (max 4-5 words each)
        words = hook_text.upper().replace('"', '').replace('.', '').replace(',', '').split()
        if len(words) > 8:
            words = words[:8]

        mid = len(words) // 2
        line1 = " ".join(words[:mid]) if mid > 0 else hook_title.upper()
        line2 = " ".join(words[mid:]) if mid > 0 else ""

        def esc(t):
            return t.replace("'", "").replace(":", "\\:").replace("%", "\\%")

        safe_brand = esc(f"[ {self.brand_title} ]")
        safe_line1 = esc(line1)
        safe_line2 = esc(line2)

        vf = (
            "scale=1200:2133:force_original_aspect_ratio=increase,"
            "crop=1080:1920,"
            "vignette=PI/3,"
            "eq=contrast=1.12:saturation=1.06,"
            "drawbox=y=ih*0.34:color=black@0.72:width=iw:height=420:t=fill,"
            f"drawtext=text='{safe_brand}':fontfile='C\\:/Windows/Fonts/georgiab.ttf':fontsize=36:fontcolor=0xF5A623:x=(w-text_w)/2:y=h*0.37,"
            f"drawtext=text='{safe_line1}':fontfile='C\\:/Windows/Fonts/georgiab.ttf':fontsize=52:fontcolor=white:x=(w-text_w)/2:y=h*0.43:shadowcolor=black@0.9:shadowx=3:shadowy=3"
        )

        if safe_line2:
            vf += f",drawtext=text='{safe_line2}':fontfile='C\\:/Windows/Fonts/georgiab.ttf':fontsize=52:fontcolor=0x23A6F5:x=(w-text_w)/2:y=h*0.50:shadowcolor=black@0.9:shadowx=3:shadowy=3"

        cmd = [
            FFMPEG, '-y',
            '-loop', '1',
            '-i', base_image,
            '-vf', vf,
            '-frames:v', '1',
            '-q:v', '2',
            out_thumbnail_path
        ]
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)
        print(f"      [Thumbnail] Generated high-CTR cover: {out_thumbnail_path}", flush=True)
        return out_thumbnail_path

if __name__ == "__main__":
    tg = ThumbnailGenerator()
    test_img = "the_untold_truth/assets/visual_vault/images/Aging_king_smirking_in_shadows.jpg"
    tg.generate_thumbnail(test_img, "THE LOYALTY TRAP", "Being loyal to a company gets you replaced", "the_untold_truth/out/ready_to_publish/the_loyalty_trap_thumbnail.jpg")
