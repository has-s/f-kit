#!/usr/bin/env python3
from pathlib import Path
import json
from pydub import AudioSegment
from speech_censor.audio import extract_audio, censor_audio
from speech_censor.transcribe import transcribe_file
from speech_censor.censor import CurseBase, censor_words

# Папки
INPUT_VIDEO = Path("../tests/set/video.mov")
TEMP_DIR = Path("../tests/temp")
OUTPUT_DIR = Path("../tests/output")
TEMP_DIR.mkdir(exist_ok=True, parents=True)
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# Файлы
EXTRACTED_WAV = TEMP_DIR / "video_extracted.wav"
CURSE_SEGMENTS_JSON = TEMP_DIR / "curse_segments.json"
CENSORED_WAV = OUTPUT_DIR / "video_censored.wav"

# Настройка словаря матов
curse_base = CurseBase(
    curse_words={"пизд", "бляд", "блят", "бля", "сука", "хуй", "еб", "трах", "шлюх", "муд"},
    whitelist={"колеб"}
)

# --- Шаг 1: извлекаем аудио ---
print("Extracting audio...")
extract_audio(INPUT_VIDEO, EXTRACTED_WAV)

# --- Шаг 2: транскрибируем и ищем маты ---
if CURSE_SEGMENTS_JSON.exists():
    print("Loading existing curse segments...")
    cursed_intervals = json.loads(CURSE_SEGMENTS_JSON.read_text())
else:
    print("Transcribing audio...")
    transcript = transcribe_file(EXTRACTED_WAV, model_size="large-v1", language="ru")
    print("Detecting curse words...")
    _, cursed_words = censor_words(transcript.segments, curse_base)
    cursed_intervals = [(w.start_time, w.end_time) for w in cursed_words]
    # Сохраняем для последующего использования
    CURSE_SEGMENTS_JSON.write_text(json.dumps(cursed_intervals, indent=2))

print(f"Found {len(cursed_intervals)} cursed segments.")

# --- Шаг 3: цензурируем аудио ---
print("Censoring audio...")
# можно передать AudioSegment вместо пути для ускорения обработки
original_audio = AudioSegment.from_wav(EXTRACTED_WAV)
censored_audio = censor_audio(original_audio, cursed_intervals, mode="beep", beep_freq=1000, target_lufs=-23.0)

# Экспорт результата
censored_audio.export(CENSORED_WAV, format="wav")
print(f"Censored audio saved to {CENSORED_WAV}")

# --- Шаг 4: (дополнительно) можно вставить обратно в видео через ffmpeg ---
OUTPUT_VIDEO = OUTPUT_DIR / "video_censored.mov"
from subprocess import run
run([
    "ffmpeg", "-y",
    "-i", str(INPUT_VIDEO),
    "-i", str(CENSORED_WAV),
    "-c:v", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    str(OUTPUT_VIDEO)
], check=True)
print(f"Censored video saved to {OUTPUT_VIDEO}")