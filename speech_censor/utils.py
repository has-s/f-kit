from pathlib import Path
from typing import List, Optional
from subprocess import run

# ======== UTILS ========
def export_to_format(input_wav: str, output_file: str, codec: Optional[str] = None, extra_args: Optional[List[str]] = None):
    """
    Export WAV to any format using FFmpeg.

    Args:
        input_wav (str): Path to WAV file.
        output_file (str): Desired output file path.
        codec (Optional[str]): Audio codec to use (e.g., "libvorbis", "aac").
        extra_args (Optional[List[str]]): Additional FFmpeg command line arguments.
    """
    cmd = ["ffmpeg", "-y", "-i", input_wav]
    if codec:
        cmd += ["-c:a", codec]
    if extra_args:
        cmd += extra_args
    cmd.append(output_file)
    run(cmd, check=True)


def merge_media(input_media: str, input_audio: str, output_file: str):
    """
    Merge processed audio into original media.

    - If input_media is audio-only, replace/copy audio into output_file.
    - If input_media is video, replace audio track but keep video intact.

    Args:
        input_media (str): Original media path (audio or video).
        input_audio (str): Processed audio path.
        output_file (str): Final output media path.
    """
    input_path = Path(input_media)
    audio_exts = {
        ".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".opus", ".wma", ".alac"
    }

    if input_path.suffix.lower() in audio_exts:
        # Audio-only -> copy audio
        run(["ffmpeg", "-y", "-i", input_audio, "-c:a", "copy", output_file], check=True)
    else:
        # Video -> replace audio track
        run([
            "ffmpeg", "-y",
            "-i", input_media,
            "-i", input_audio,
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            output_file
        ], check=True)


def play_sound():
    """Stub for audio playback utility."""
    ...