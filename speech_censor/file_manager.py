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
    def transcript_original_json(self) -> Path:
        """
        Path to JSON file storing the original transcript, including any existing censored flags.

        :return: Path object for the original transcript JSON.
        """
        return self.temp_dir / f"{self.input_file.stem}_transcript_original.json"

    @property
    def transcript_edit_json(self) -> Path:
        """
        Path to JSON file storing the editable censored flags (working version for edits).

        :return: Path object for the editable transcript JSON.
        """
        return self.temp_dir / f"{self.input_file.stem}_transcript_edit.json"

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
            self.transcript_original_json,
            self.transcript_edit_json,
        ]

    def clean_temp(self):
        """
        Delete all temporary/intermediate files if they exist.
        """
        for f in self.list_temp_files():
            if f.exists():
                f.unlink()

# -----------------------------------------------------------------------------
# Example: Full cycle of working with _censored.json flags
# (for manual review, applying, or resetting flags)
# -----------------------------------------------------------------------------
#
# from speech_censor.file_operations import (
#     load_censored_flags,
#     save_censored_flags,
#     apply_censored_flags,
#     reset_censorship
# )
#
# # 1) Load existing censorship flags
# censored_dict = load_censored_flags(fm)
# print("Loaded censored flags:", censored_dict)
#
# # 2) Save new flags (e.g., after automated check or user review)
# censored_dict = {}  # create a new dictionary
# for i, seg in enumerate(segments):
#     for j, word in enumerate(seg.words):
#         if word.censored:
#             censored_dict.setdefault(str(i), {})[str(j)] = True
# save_censored_flags(fm, censored_dict)
# print(f"Censored flags saved to {fm.transcript_censored_json}")
#
# # 3) Apply flags to the main transcript
# apply_censored_flags(fm)
# print("Censored flags applied to main transcript.")
#
# # 4) Reset all flags (e.g., after testing or review)
# reset_censorship(fm)
# print("All censorship flags reset.")
#
# -----------------------------------------------------------------------------
# This mini-example demonstrates how to manually control censorship flags:
# - save them separately
# - review and apply them when needed
# - reset them after testing
# -----------------------------------------------------------------------------