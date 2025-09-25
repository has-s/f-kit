# __main__.py
from speech_censor.transcribe import transcribe_stream

def main():
    audio_path = "../proto/audio.wav"  # путь к тестовому аудио
    print(f"Loading audio from {audio_path}...")

    # читаем аудио в память
    with open(audio_path, "rb") as f:
        audio_bytes = f.read()

    print("Transcribing audio from memory...")
    transcript = transcribe_stream(audio_bytes, model_size="medium", language="ru")

    print(f"Transcription finished. Duration: {transcript.duration:.1f} sec")
    print(f"Found {len(transcript.segments)} segments.\n")

    # вывод первых двух сегментов
    for seg_idx, seg in enumerate(transcript.segments[:2], 1):
        print(f"Segment {seg_idx} ({seg.start_time:.2f}-{seg.end_time:.2f} sec):")
        for word in seg.words:
            print(f"  {word.text} [{word.start_time:.2f}-{word.end_time:.2f}]")

if __name__ == "__main__":
    main()