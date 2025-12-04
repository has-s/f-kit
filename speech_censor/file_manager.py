from pathlib import Path
from typing import List

class FileManager:
    """
    Handles paths and management of files involved in media processing (audio/video).

    This class provides structured access to input files, temporary/intermediate files,
    and output files. It ensures directories exist and provides convenient properties
    for commonly used file paths during processing, such as extracted audio, transcripts,
    censored audio, and subtitles.

    Attributes
    ----------
    input_file : Path
        Path to the original audio or video file to be processed.
    temp_dir : Path
        Directory for temporary or intermediate files created during processing.
    output_dir : Path
        Directory for final output files after processing.
    """

    # Common audio and video extensions supported by FFmpeg
    AUDIO_EXTS = {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".aac"}
    VIDEO_EXTS = {".mp4", ".mov", ".mkv", ".avi", ".webm", ".flv", ".wmv", ".mpg", ".mpeg"}

    def __init__(self, input_file: str, temp_dir: str = "../tests/temp", output_dir: str = "../tests/output"):
        """
        Initialize a FileManager instance with paths for input, temporary, and output files.

        Ensures that the temporary and output directories exist, creating them if necessary.

        Parameters
        ----------
        input_file : str
            Path to the input audio or video file to be processed.
        temp_dir : str, optional
            Path to the temporary directory for intermediate files (default: "../tests/temp").
        output_dir : str, optional
            Path to the output directory for final files (default: "../tests/output").
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
        Path to the WAV file extracted from the input media file.

        Returns
        -------
        Path
            Full path to the extracted WAV file in the temporary directory.
        """
        return self.temp_dir / f"{self.input_file.stem}_extracted.wav"

    @property
    def transcript_original_json(self) -> Path:
        """
        Path to the JSON file storing the original transcript, including any existing censored flags.

        Returns
        -------
        Path
            Full path to the original transcript JSON file in the temporary directory.
        """
        return self.temp_dir / f"{self.input_file.stem}_transcript_original.json"

    @property
    def transcript_edit_json(self) -> Path:
        """
        Path to the JSON file storing the editable censored flags (working version for edits).

        Returns
        -------
        Path
            Full path to the editable transcript JSON file in the temporary directory.
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
        Path to the WAV file after applying audio censoring.

        Returns
        -------
        Path
            Full path to the censored WAV file in the output directory.
        """
        return self.output_dir / f"{self.input_file.stem}_subtitles.srt"

    @property
    def output_media(self) -> Path:
        """
        Path to the SRT file generated from the censored transcript.

        Returns
        -------
        Path
            Full path to the subtitles SRT file in the output directory.
        """
        return self.output_dir / f"{self.input_file.stem}_censored{self.input_file.suffix}"

    # ======== UTILITY METHODS ========

    def list_temp_files(self) -> List[Path]:
        """
        List all temporary and intermediate files associated with this FileManager.

        Includes files such as:
            - Extracted WAV from input media
            - Original transcript JSON
            - Editable transcript JSON

        Returns
        -------
        List[Path]
            List of Path objects representing all temporary/intermediate files.
        """
        return [
            self.extracted_wav,
            self.transcript_original_json,
            self.transcript_edit_json,
        ]

    def clean_temp(self):
        """
        Remove all temporary and intermediate files associated with this FileManager.

        Checks each file returned by `list_temp_files()` and deletes it if it exists.

        Returns
        -------
        None
        """
        for f in self.list_temp_files():
            if f.exists():
                f.unlink()
