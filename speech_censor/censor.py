class CurseBase:
    def __init__(self, curse_words: set[str], whitelist: set[str] = None):
        self.curse_words = curse_words
        self.whitelist = whitelist or set()

    def is_curse(self, word: str) -> bool:
        """Check if the word is a curse word, taking the whitelist into account."""
        w_lower = word.lower()
        if any(white in w_lower for white in self.whitelist):
            return False
        return any(c in w_lower for c in self.curse_words)

def censor_words(segments, curse_base: CurseBase, replacement: str = "[CENSORED]"):
    """
    Iterate over segments, replace curse words with a replacement string.
    Returns updated segments and a list of words with their start/end times for beeping.

    :param segments: list of Segment objects
    :param curse_base: CurseBase instance with curse words and whitelist
    :param replacement: string to replace censored words (default: "[CENSORED]")
    """
    cursed_words = []

    for segment in segments:
        for word in segment.words:
            if curse_base.is_curse(word.text):
                word.censored = True
                cursed_words.append(word)
                word.text = replacement

    return segments, cursed_words


def generate_ffmpeg_times(cursed_words):
    """
    From a list of censored Word objects, generate time intervals suitable for ffmpeg.

    :param cursed_words: list of Word objects with start_time and end_time
    :return: list of tuples [(start_time, end_time), ...]
    """
    ffmpeg_times = []
    for word in cursed_words:
        ffmpeg_times.append((word.start_time, word.end_time))
    return ffmpeg_times