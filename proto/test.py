from faster_whisper import WhisperModel
import pysrt
from tqdm import tqdm

VIDEO_FILE = "video.mov"
MODEL_SIZE = "medium"
OUTPUT_SRT = "words_test.srt"

model = WhisperModel(MODEL_SIZE)
segments_gen, info = model.transcribe(VIDEO_FILE, word_timestamps=False)

segments = list(segments_gen)
subs = pysrt.SubRipFile()
index = 1

word_list = []  # для проверки матерных слов

for seg_idx, segment in enumerate(segments, 1):
    words = segment.words
    if not words:
        continue

    start_time = words[0].start
    end_time = words[-1].end

    # создаем текст без пробелов
    text = "".join([w.word for w in words])

    # сохраняем все слова с таймингами
    for w_idx, word in enumerate(words, 1):
        word_list.append({
            "segment_index": seg_idx,
            "word_index": w_idx,
            "start_time": word.start,
            "end_time": word.end,
            "word": word.word
        })

    subs.append(pysrt.SubRipItem(
        index=index,
        start=pysrt.SubRipTime(seconds=start_time),
        end=pysrt.SubRipTime(seconds=end_time),
        text=text
    ))
    index += 1

subs.save(OUTPUT_SRT, encoding='utf-8')
print(f"Тестовые субтитры сохранены в {OUTPUT_SRT}")
print(f"Найдено {len(word_list)} слов")