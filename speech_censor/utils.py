# utils.py
from pathlib import Path
from typing import List, Optional
from subprocess import run

class FileManager:
    """
    Manage input, output, and intermediate files for media processing.

    Attributes:
        input_file (Path): Original audio/video file.
        temp_dir (Path): Directory for temporary/intermediate files.
        output_dir (Path): Directory for final outputs.

    Properties:
        extracted_wav: WAV file extracted from input.
        transcript_txt: Full transcript text file.
        cursed_segments_json: JSON with cursed word intervals.
        censored_wav: WAV file after censoring.
    """

    def __init__(self, input_file: str, temp_dir: str = "../tests/temp", output_dir: str = "../tests/output"):
        self.input_file = Path(input_file)
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ======== TEMP FILES ========
    @property
    def extracted_wav(self) -> Path:
        """Temporary WAV extracted from input media."""
        return self.temp_dir / f"{self.input_file.stem}_extracted.wav"

    @property
    def transcript_txt(self) -> Path:
        """Full transcript text file."""
        return self.temp_dir / f"{self.input_file.stem}_transcript.txt"

    @property
    def cursed_segments_json(self) -> Path:
        """JSON file storing intervals of censored words."""
        return self.temp_dir / f"{self.input_file.stem}_cursed_segments.json"

    @property
    def censored_wav(self) -> Path:
        """Temporary WAV file after censoring."""
        return self.temp_dir / f"{self.input_file.stem}_censored.wav"

    # ======== OUTPUT FILES ========
    def get_output_path(self, suffix: str) -> Path:
        """
        Return a final output file path with the given suffix.

        Args:
            suffix (str): File extension with dot (e.g., ".ogg", ".mkv").

        Returns:
            Path: Full path in output directory.
        """
        return self.output_dir / f"{self.input_file.stem}_processed{suffix}"

    # ======== UTILITY METHODS ========
    def list_temp_files(self) -> List[Path]:
        """Return a list of all temporary/intermediate files."""
        return [self.extracted_wav, self.cursed_segments_json, self.censored_wav, self.transcript_txt]

    def clean_temp(self):
        """Delete all temporary/intermediate files."""
        for f in self.list_temp_files():
            if f.exists():
                f.unlink()


# ======== MEDIA UTILITIES ========

def export_to_format(input_wav: str, output_file: str, codec: Optional[str] = None, extra_args: Optional[List[str]] = None):
    """
    Export WAV to any format using ffmpeg.

    Args:
        input_wav (str): Path to WAV file.
        output_file (str): Desired output file path.
        codec (Optional[str]): Audio codec to use (e.g., "libvorbis", "aac").
        extra_args (Optional[List[str]]): Additional ffmpeg command line arguments.
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

    If input_media is audio-only, simply replace/copy audio into output_file.
    Otherwise, replace audio track in video container.

    Args:
        input_media (str): Original media path (audio or video).
        input_audio (str): Processed audio path.
        output_file (str): Final output media path.
    """
    input_path = Path(input_media)
    audio_exts = {".mp3", ".wav", ".ogg", ".flac", ".m4a"}

    if input_path.suffix.lower() in audio_exts:
        # audio-only -> just copy audio into target format
        run(["ffmpeg", "-y", "-i", input_audio, "-c:a", "copy", output_file], check=True)
    else:
        # video -> replace audio track
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
    ...