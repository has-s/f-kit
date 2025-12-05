class CurseBase:
    """
    Base class for curse word detection.

    Attributes
    ----------
    curse_words : set[str]
        Set of words considered as curses.
    whitelist : set[str]
        Set of substrings that, if present in a word, prevent it from being treated as a curse.
    """

    def __init__(self, curse_words: set[str], whitelist: set[str] = None):
        """
        Initialize CurseBase with curse words and optional whitelist.

        Parameters
        ----------
        curse_words : set[str]
            Words to treat as curses.
        whitelist : set[str], optional
            Substrings that prevent words from being flagged as curses.
        """
        self.curse_words = curse_words
        self.whitelist = whitelist or set()

    def is_curse(self, word: str) -> bool:
        """
        Check if a word is a curse word.

        The check is case-insensitive and respects the whitelist.

        Parameters
        ----------
        word : str
            Word to check.

        Returns
        -------
        bool
            True if the word is a curse, False if whitelisted or not a curse.
        """
        w_lower = word.lower()
        if any(white in w_lower for white in self.whitelist):
            return False
        return any(c in w_lower for c in self.curse_words)


def censor_words(segments, curse_base: CurseBase):
    """
    Mark curse words in segments with a 'censored' flag.

    The original word text is left unchanged.

    Parameters
    ----------
    segments : list[Segment]
        List of segments containing words.
    curse_base : CurseBase
        Instance containing curse words and whitelist.

    Returns
    -------
    tuple
        - Updated segments with 'censored' flags set.
        - List of Word objects that were marked as cursed, with start and end times.
    """
    cursed_words = []

    for segment in segments:
        for word in segment.words:
            if curse_base.is_curse(word.text):
                word.censored = True
                cursed_words.append(word)

    return segments, cursed_words


def generate_ffmpeg_times(cursed_words):
    """
    Generate time intervals for ffmpeg from a list of cursed words.

    Parameters
    ----------
    cursed_words : list[Word]
        Words marked as censored with start_time and end_time attributes.

    Returns
    -------
    list[tuple[float, float]]
        List of (start_time, end_time) tuples for each censored word.
    """
    ffmpeg_times = []
    for word in cursed_words:
        ffmpeg_times.append((word.start_time, word.end_time))
    return ffmpeg_times
