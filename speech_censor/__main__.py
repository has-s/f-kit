from pathlib import Path
from speech_censor.file_manager import FileManager

def main():
    input_path = Path("../tests/set/video.mov")

    fm = FileManager(input_file=str(input_path))

    if not fm.input_file.exists():
        raise FileNotFoundError(f"Input file not found: {fm.input_file}")

    print("input:", fm.input_file)
    print("temp dir:", fm.temp_dir)
    print("output dir:", fm.output_dir)

    print("extracted_wav:", fm.extracted_wav)
    print("transcript_json:", fm.transcript_json)
    print("cursed_segments_json:", fm.cursed_segments_json)
    print("censored_wav:", fm.censored_wav)
    print("subtitles_srt:", fm.subtitles_srt)
    print("output_media:", fm.output_media)
    print("generic output wav:", fm.output_dir / f"{fm.input_file.stem}_processed.wav")
    print("generic output mkv:", fm.output_dir / f"{fm.input_file.stem}_processed.mkv")

if __name__ == "__main__":
    main()