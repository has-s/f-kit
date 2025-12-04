from pathlib import Path
from typing import List, Optional
from subprocess import run


# ======== UTILS ========
def export_to_format(input_wav: str, output_file: str, codec: Optional[str] = None,
                     extra_args: Optional[List[str]] = None):
    """
    Export a WAV file to another audio format using FFmpeg.

    Parameters
    ----------
    input_wav : str
        Path to the source WAV file.
    output_file : str
        Path where the converted audio will be saved.
    codec : str, optional
        Audio codec to use (e.g., ``"libvorbis"``, ``"aac"``).
        If omitted, FFmpeg chooses a default codec based on the output container.
    extra_args : list of str, optional
        Additional FFmpeg arguments appended to the command, e.g. bitrate or filters.

    Notes
    -----
    The function overwrites the output file if it exists. FFmpeg must be installed
    and available in the system PATH.
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

    This function replaces the audio track in a video file or
    outputs the processed audio directly if the source is an audio-only file.

    Parameters
    ----------
    input_media : str
        Path to the original media file (audio or video).
    input_audio : str
        Path to the processed audio track that should replace the original one.
    output_file : str
        Path where the merged media will be saved.

    Notes
    -----
    - Audio-only sources are copied with ``-c:a copy`` to preserve quality.
    - Video sources retain their video stream unchanged (``-c:v copy``).
    - The output file is overwritten if it exists.
    """
    input_path = Path(input_media)
    audio_exts = {
        ".mp3", ".wav", ".ogg", ".flac", ".m4a", ".aac", ".opus", ".wma", ".alac"
    }

    if input_path.suffix.lower() in audio_exts:
        run(["ffmpeg", "-y", "-i", input_audio, "-c:a", "copy", output_file], check=True)
    else:
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
    """
    Placeholder for program completion beep.

    Originally intended to signal the end of a long-running process.
    This function is left unimplemented and serves as a stub.

    Notes
    -----
    Does not play audio segments or previews.

    Humor
    -----
    Beep.
    """
    ...
