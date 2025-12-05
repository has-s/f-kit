from .audio import make_beep, make_mute, extract_audio, censor_audio, _normalize_loudness
from .av_processor import MediaProcessor
from .censor import CurseBase, censor_words, generate_ffmpeg_times
from .constants import SAMPLE_RATE, CHANNELS, SAMPLE_WIDTH, BEEP_FREQ_DEFAULT
from .file_manager import FileManager
from .file_operations import (
    load_transcript,
    save_transcript,
    validate_transcript_structure,
    load_original_file,
    load_editable_file,
    load_censored_flags,
    save_censored_flags,
    apply_censored_flags,
    reset_censorship
)
from .subtitles import save_srt
from .transcribe import Word, Segment, Transcript, transcribe_audio
from .utils import export_to_format, merge_media, play_sound

__all__ = [
    # audio
    "make_beep", "make_mute", "extract_audio", "censor_audio", "_normalize_loudness",
    # av_processor
    "MediaProcessor",
    # censor
    "CurseBase", "censor_words", "generate_ffmpeg_times",
    # constants
    "SAMPLE_RATE", "CHANNELS", "SAMPLE_WIDTH", "BEEP_FREQ_DEFAULT",
    # file_manager
    "FileManager",
    # file_operations
    "load_transcript", "save_transcript", "validate_transcript_structure",
    "load_original_file", "load_editable_file", "load_censored_flags",
    "save_censored_flags", "apply_censored_flags", "reset_censorship",
    # subtitles
    "save_srt",
    # transcribe
    "Word", "Segment", "Transcript", "transcribe_audio",
    # utils
    "export_to_format", "merge_media", "play_sound",
]

#TODO: Cleanup functions for feature uses
