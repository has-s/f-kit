from pathlib import Path
from typing import List

class FileManager:
    """
    Manage input, temporary, and output files for media processing (audio/video).

    Attributes:
        input_file (Path): Original audio or video file.
        temp_dir (Path): Directory for temporary/intermediate files.
        output_dir (Path): Directory for final outputs.

    Properties:
        extracted_wav (Path): WAV file extracted from input media.
        transcript_json (Path): JSON file storing full transcript (segments + words + censored flag).
        cursed_segments_json (Path): JSON file storing intervals of censored words.
        censored_wav (Path): WAV file after audio censoring.
        subtitles_srt (Path): SRT file generated from censored transcript.
        output_media (Path): Final media file with censored audio and optionally subtitles.
    """

    # Common audio and video extensions supported by FFmpeg
    AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac"}
    VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".wmv", ".mpg", ".mpeg"}

    def __init__(self, input_file: str, temp_dir: str = "../tests/temp", output_dir: str = "../tests/output"):
        """
        Initialize FileManager with paths and ensure directories exist.

        :param input_file: Path to input audio or video file.
        :param temp_dir: Path to temporary directory (default: "../tests/temp").
        :param output_dir: Path to output directory (default: "../tests/output").
        """
        self.input_file = Path(input_file)
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    # ======== TEMP FILES ========

    @property
    def extracted_wav(self) -> Path:
        """
        Path to WAV file extracted from input media.

        :return: Path object for extracted WAV.
        """
        return self.temp_dir / f"{self.input_file.stem}_extracted.wav"

    @property
    def transcript_json(self) -> Path:
        """
        Path to JSON file storing full transcript (segments + words + censored flags).

        :return: Path object for transcript JSON.
        """
        return self.temp_dir / f"{self.input_file.stem}_transcript.json"

    @property
    def cursed_segments_json(self) -> Path:
        """
        Path to JSON file storing intervals of censored words.

        :return: Path object for cursed segments JSON.
        """
        return self.temp_dir / f"{self.input_file.stem}_cursed_segments.json"

    # ======== OUTPUT FILES ========

    @property
    def censored_wav(self) -> Path:
        """
        Path to WAV file after applying audio censoring.

        :return: Path object for censored WAV.
        """
        return self.output_dir / f"{self.input_file.stem}_censored.wav"

    @property
    def subtitles_srt(self) -> Path:
        """
        Path to SRT file generated from censored transcript.

        :return: Path object for SRT subtitles.
        """
        return self.output_dir / f"{self.input_file.stem}_subtitles.srt"

    @property
    def output_media(self) -> Path:
        """
        Path to final media file with censored audio and optionally subtitles.
        Extension is kept the same as the input file.

        :return: Path object for final output media.
        """
        return self.output_dir / f"{self.input_file.stem}_censored{self.input_file.suffix}"

    # ======== UTILITY METHODS ========

    def list_temp_files(self) -> List[Path]:
        """
        List all temporary/intermediate files for cleanup or inspection.

        :return: List of Path objects for temporary files.
        """
        return [
            self.extracted_wav,
            self.transcript_json,
            self.cursed_segments_json,
        ]

    def clean_temp(self):
        """
        Delete all temporary/intermediate files if they exist.
        """
        for f in self.list_temp_files():
            if f.exists():
                f.unlink()