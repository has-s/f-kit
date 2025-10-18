# utils.py
from pathlib import Path
from typing import List

def play_sound(sound_file: str):
    """
    Play a sound file (blocking).

    Parameters:
        sound_file (str): Path to the audio file.
    """
    import simpleaudio as sa
    wave_obj = sa.WaveObject.from_wave_file(sound_file)
    play_obj = wave_obj.play()
    play_obj.wait_done()


class FileManager:
    """
    Manage input, output, and intermediate files for audio/video processing.

    Attributes:
        input_file (Path): Original audio/video file.
        temp_dir (Path): Directory for temporary/intermediate files.
        output_dir (Path): Directory for final outputs.

    Properties:
        extracted_wav: WAV file extracted from input.
        transcript_txt: Full transcript text file.
        cursed_segments_json: JSON with cursed word intervals.
        censored_wav: WAV file after censoring.
        output_audio_ogg: Final censored audio in OGG format.
        output_video: Final censored video file (MKV if video, OGG if audio-only).
    """

    def __init__(self, input_file: str, temp_dir: str = "../tests/temp", output_dir: str = "../tests/output"):
        self.input_file = Path(input_file)
        self.temp_dir = Path(temp_dir)
        self.output_dir = Path(output_dir)

        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    @property
    def extracted_wav(self) -> Path:
        """Temporary WAV extracted from input."""
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

    @property
    def output_audio_ogg(self) -> Path:
        """Final censored audio file in OGG format."""
        return self.output_dir / f"{self.input_file.stem}_censored.ogg"

    @property
    def output_video(self) -> Path:
        """Final censored video file. MKV if input has video, OGG if audio-only."""
        return self.output_dir / f"{self.input_file.stem}_censored.mkv"

    def list_temp_files(self) -> List[Path]:
        """Return a list of all temporary/intermediate files."""
        return [self.extracted_wav, self.cursed_segments_json, self.censored_wav, self.transcript_txt]

    def list_output_files(self) -> List[Path]:
        """Return a list of all final output files."""
        return [self.output_audio_ogg, self.output_video]

    def clean_temp(self):
        """Delete all temporary/intermediate files."""
        for f in self.list_temp_files():
            if f.exists():
                f.unlink()