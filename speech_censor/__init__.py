from .transcribe import transcribe_file, transcribe_stream
from .censor import censor_words, generate_ffmpeg_times
from .audio import extract_audio
from .utils import play_sound

__all__ = [
    "transcribe_file",       # транскрибирует файл на сегменты и слова
    "transcribe_stream",     # транскрибирует аудио из памяти/потока
    "censor_words",          # заменяет слова на [CENSORED] и возвращает тайминги
    "generate_ffmpeg_times", # формирует интервалы для ffmpeg по найденным матам
    "extract_audio",         # извлекает аудио из видео/аудио файлов
    "play_sound"             # проигрывает короткий звук (например, сигнал окончания)
]