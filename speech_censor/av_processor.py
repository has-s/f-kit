#!/usr/bin/env python3
"""
av_processor.py — universal media processing module.

Handles extraction, conversion, and merging of audio/video using ffmpeg.
Designed to integrate with transcription and censoring pipeline.
"""

from __future__ import annotations
from pathlib import Path
from subprocess import run, CalledProcessError
from typing import Optional


class MediaProcessor:
    """
    Universal processor for extracting, converting, and merging audio/video.

    Steps:
        1. extract_to_wav() — extract raw audio from any file.
        2. remux_audio() — export processed WAV into final format (OGG, MP3, etc.).
        3. remux_video() — merge censored audio back into video, if applicable.
    """

    def __init__(self, input_file: str | Path, temp_dir: str | Path, output_dir: str | Path):
        self.input_file = Path(input_file)
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.base = self.input_file.stem
        self.extracted_wav = self.temp_dir / f"{self.base}_extracted.wav"
        self.censored_wav = self.temp_dir / f"{self.base}_censored.wav"

    def _run_ffmpeg(self, args: list[str]):
        """Run ffmpeg with basic error handling."""
        try:
            run(["ffmpeg", "-y", *args], check=True)
        except CalledProcessError as e:
            raise RuntimeError(f"FFmpeg execution failed: {e}") from e

    def extract_to_wav(self, target_sr: int = 48000) -> Path:
        """
        Extracts an audio track from any input file into a 16-bit PCM WAV.

        Parameters:
            target_sr (int): Target sample rate for output WAV.

        Returns:
            Path: Path to the extracted WAV file.
        """
        self._run_ffmpeg([
            "-i", str(self.input_file),
            "-vn",
            "-acodec", "pcm_s16le",
            "-ac", "2",
            "-ar", str(target_sr),
            str(self.extracted_wav)
        ])
        return self.extracted_wav

    def remux_audio(self, output_format: str = "ogg") -> Path:
        """
        Converts censored WAV to the final audio format.

        Parameters:
            output_format (str): Format for the output (ogg, mp3, wav...).

        Returns:
            Path: Path to the exported audio file.
        """
        codec = {
            "ogg": "libvorbis",
            "mp3": "libmp3lame",
            "wav": "pcm_s16le"
        }.get(output_format, "libvorbis")

        out_file = self.output_dir / f"{self.base}_censored.{output_format}"
        self._run_ffmpeg([
            "-i", str(self.censored_wav),
            "-c:a", codec,
            "-q:a", "5",
            str(out_file)
        ])
        return out_file

    def remux_video(self, censored_audio: Path) -> Optional[Path]:
        """
        Merges censored audio with the original video (if video stream exists).

        Parameters:
            censored_audio (Path): Path to censored audio file.

        Returns:
            Optional[Path]: Path to the final MKV file, or None if input is audio-only.
        """
        probe = run([
            "ffprobe", "-v", "error",
            "-select_streams", "v:0",
            "-show_entries", "stream=codec_type",
            "-of", "default=nokey=1:noprint_wrappers=1",
            str(self.input_file)
        ], capture_output=True, text=True)

        has_video = "video" in probe.stdout.strip().lower()
        if not has_video:
            return None

        out_video = self.output_dir / f"{self.base}_censored.mkv"
        self._run_ffmpeg([
            "-i", str(self.input_file),
            "-i", str(censored_audio),
            "-c:v", "copy",
            "-map", "0:v:0",
            "-map", "1:a:0",
            str(out_video)
        ])
        return out_video

    def clean_temp(self):
        """Remove all temporary files created during processing."""
        for f in self.temp_dir.glob(f"{self.base}_*"):
            try:
                f.unlink()
            except Exception:
                pass

    def reset_output(self):
        """Remove all existing output files for this input."""
        for f in self.output_dir.glob(f"{self.base}_censored.*"):
            try:
                f.unlink()
            except Exception:
                pass