from faster_whisper import WhisperModel
import pysrt
from tqdm import tqdm
import simpleaudio as sa
import subprocess

VIDEO_FILE = "video.mov"
MODEL_SIZE = "medium"
CURSE_BASES = {
    "пизд",
    "бляд", "блят", "бля",
    "сука",
    "хуй",
    "еб",
    "трах",
    "шлюх",
    "муд",
}
WHITELIST = {"колеб"}

OUTPUT_SRT = "video.srt"
AUDIO_FILE = "audio.wav"
CENSORED_AUDIO_FILE = "audio_censored.wav"
OUTPUT_VIDEO = "video_censored.mkv"

def mute_curses_audio(audio_file, found_curses, output_file=CENSORED_AUDIO_FILE):
    ffmpeg_times = [(w["start_time"], w["end_time"]) for w in found_curses]

    filters = []
    for start, end in ffmpeg_times:
        filters.append(f"volume=enable='between(t,{start},{end})':volume=0")

    filter_str = ",".join(filters)
    cmd = [
        "ffmpeg",
        "-y",  # перезаписывать файл без запроса
        "-i", audio_file,
        "-af", filter_str,
        output_file
    ]
    subprocess.run(cmd)

# --- Транскрипция и поиск матов ---
model = WhisperModel(MODEL_SIZE)

print("Запуск транскрипции...")
segments_gen, info = model.transcribe(VIDEO_FILE, word_timestamps=True)

pbar = tqdm(total=info.duration, unit="sec", desc="Транскрибируем")
segments = []
for segment in segments_gen:
    segments.append(segment)
    pbar.update(segment.end - (pbar.n if pbar.n < segment.end else pbar.n))
pbar.close()

print(f"Транскрипция завершена. Найдено {len(segments)} сегментов. "
      f"Длительность видео: {info.duration:.1f} сек")

subs = pysrt.SubRipFile()
index = 1
found_curses = []

with tqdm(total=info.duration, unit="sec", desc="Обработка видео") as pbar:
    for seg_idx, segment in enumerate(segments, 1):
        words = segment.words
        if not words:
            continue

        start_time = words[0].start
        end_time = words[-1].end
        text = []

        print(f"\nСегмент {seg_idx}/{len(segments)} ({len(words)} слов, {end_time - start_time:.1f} сек)")

        for w_idx, word in enumerate(words, 1):
            w_orig = word.word
            w_lower = w_orig.lower()
            censored = False

            for c in CURSE_BASES:
                if c in w_lower and not any(white in w_lower for white in WHITELIST):
                    w_orig = "[CENSORED]"
                    censored = True
                    found_curses.append({
                        "segment_index": seg_idx,
                        "word_index": w_idx,
                        "start_time": word.start,
                        "end_time": word.end,
                        "word": word.word
                    })
                    break

            text.append(w_orig)
            print(f"  Слово {w_idx}/{len(words)}: {word.word} -> {w_orig}")

        subs.append(pysrt.SubRipItem(
            index=index,
            start=pysrt.SubRipTime(seconds=start_time),
            end=pysrt.SubRipTime(seconds=end_time),
            text=" ".join(text)
        ))
        index += 1
        pbar.update(end_time - (pbar.n if pbar.n < end_time else pbar.n))

subs.save(OUTPUT_SRT, encoding='utf-8')
print(f"\nСубтитры с цензурой сохранены в {OUTPUT_SRT}.")

print("\nНайденные маты с таймингами:")
for f in found_curses:
    print(f)

# --- Сигнал окончания транскрипции ---
wave_obj = sa.WaveObject.from_wave_file("pop.wav")
play_obj = wave_obj.play()
play_obj.wait_done()

# --- Вырезаем аудио из видео ---
subprocess.run(["ffmpeg", "-y", "-i", VIDEO_FILE, "-q:a", "0", "-map", "a", AUDIO_FILE])

# --- Заглушаем маты ---
mute_curses_audio(AUDIO_FILE, found_curses)

# --- Собираем видео с цензурированным аудио ---
subprocess.run([
    "ffmpeg", "-y",
    "-i", VIDEO_FILE,
    "-i", CENSORED_AUDIO_FILE,
    "-c:v", "copy",
    "-map", "0:v:0",
    "-map", "1:a:0",
    OUTPUT_VIDEO
])
print(f"\nВидео с заглушенным матом сохранено в {OUTPUT_VIDEO}.")