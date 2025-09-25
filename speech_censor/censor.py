def censor_words(segments, curse_bases: set, whitelist: set = None):
    """
    Обходит сегменты, заменяет цензурируемые слова на [CENSORED].
    Возвращает обновленные сегменты и список таймингов для звукового бипа.
    """
    ...

def generate_ffmpeg_times(cursed_words):
    """
    Из списка найденных матов формирует временные интервалы для ffmpeg.
    """
    ...