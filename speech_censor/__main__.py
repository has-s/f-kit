from pathlib import Path
from typing import Set, List

'''
# ---- For IDE testing ----
import sys

        sys.argv = [
            "main.py",
            "/Users/hass/Documents/Code/f-kit/tests/set/video.mov",
            "--curse_words_file", "/Users/hass/Documents/Code/f-kit/tests/set/curse_words.txt",
            "--mode", "beep"
        ]
'''

import argparse
from speech_censor import (
    FileManager, CurseBase, export_to_format, transcribe_audio, save_transcript, load_transcript,
    censor_words, generate_ffmpeg_times, censor_audio, save_srt, merge_media
)

# ---- Load words from a file safely ----
def load_words_from_file(path) -> Set[str]:
    if not path:
        return set()
    p = Path(path)
    if not p.exists():
        return set()
    return {line.strip() for line in p.read_text(encoding="utf-8").splitlines() if line.strip()}

# ---- Confirm overwrite for multiple files ----
def confirm_overwrite(paths: List[Path], force: bool) -> bool:
    existing = [p for p in paths if p.exists()]
    if existing:
        for p in existing:
            print(f"Found existing file: {p}")
        if force:
            return True
        ans = input("Overwrite all existing files? [y/N]: ").strip().lower()
        return ans in ("y", "yes")
    return True

# ---- CLI arguments ----
parser = argparse.ArgumentParser(description="Audio/video censorship tool.")
parser.add_argument("input_file", type=str, help="Path to input media file.")
parser.add_argument("--curse_words", nargs="*", default=[], help="List of curse words.")
parser.add_argument("--whitelist", nargs="*", default=[], help="List of whitelisted words/substrings.")
parser.add_argument("--curse_words_file", type=str, help="Path to file with curse words (one per line).")
parser.add_argument("--whitelist_file", type=str, help="Path to file with whitelisted words/substrings.")
parser.add_argument("--mode", choices=["beep", "mute"], default="beep", help="Censor mode.")
parser.add_argument("--beep_freq", type=int, default=1000, help="Frequency for beep (Hz).")
parser.add_argument("--target_lufs", type=float, default=-23.0, help="Target loudness for audio normalization.")
parser.add_argument("--model", choices=["tiny", "base", "medium", "large"], default="medium", help="Whisper model size.")
parser.add_argument("--lang", default=None, help="Language for transcription, e.g., 'en'.")
parser.add_argument("--force", action="store_true", help="Force overwrite of existing files without prompting.")
parser.add_argument("--force_extract", action="store_true", help="Force re-extraction of audio and re-transcription.")
args = parser.parse_args()

# ---- File manager ----
fm = FileManager(args.input_file)

# ---- Combine CLI and file-based word lists ----
curse_words = set(args.curse_words) | load_words_from_file(args.curse_words_file)
whitelist = set(args.whitelist) | load_words_from_file(args.whitelist_file)
curse_base = CurseBase(curse_words, whitelist)

# ---- Extract audio ----
if args.force_extract or not fm.extracted_wav.is_file():
    print(f"Extracting audio to {fm.extracted_wav}...")
    export_to_format(str(fm.input_file), str(fm.extracted_wav))
else:
    print(f"Using existing WAV: {fm.extracted_wav}")

# ---- Transcribe audio ----
if args.force_extract or not fm.transcript_original_json.exists():
    print("Transcribing audio...")
    transcript = transcribe_audio(str(fm.extracted_wav), model_size=args.model, language=args.lang)
else:
    print("Loading existing transcript...")
    transcript = load_transcript(fm)

# ---- Apply censorship ----
print("Applying censorship...")
segments, cursed_words = censor_words(transcript.segments, curse_base)
intervals = generate_ffmpeg_times(cursed_words)

censored_audio = censor_audio(
    input_wav=str(fm.extracted_wav),
    segments=intervals,
    mode=args.mode,
    beep_freq=args.beep_freq,
    target_lufs=args.target_lufs
)

# ---- Files to save ----
files_to_save = [fm.censored_wav, fm.subtitles_srt, fm.transcript_edit_json, fm.output_media]

# ---- Confirm overwrite and save ----
if confirm_overwrite(files_to_save, args.force):
    censored_audio.export(str(fm.censored_wav), format="wav")
    save_srt(transcript.segments, fm.subtitles_srt)
    save_transcript(fm, transcript)
    merge_media(str(fm.input_file), str(fm.censored_wav), str(fm.output_media))
    print("All files saved.")

# ---- Summary ----
print("Processing complete.")

#TODO: Переписать эту сcaнuнy