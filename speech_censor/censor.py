from rapidfuzz import fuzz

class CurseBase:
    """
    Represents a base set of curse words and provides methods to detect them.

    Attributes:
        curse_words (set[str]): Set of base curse substrings.
        whitelist (set[str]): Set of substrings that should not be considered curses.
        fuzzy_threshold (int): Minimum similarity (0-100) for fuzzy matching to detect modified curse words.
    """

    def __init__(self, curse_words: set[str], whitelist: set[str] = None, fuzzy_threshold: int = 80):
        """
        Initialize CurseBase.

        Args:
            curse_words (set[str]): Base curse words to detect.
            whitelist (set[str], optional): Words/substrings to ignore. Defaults to None.
            fuzzy_threshold (int, optional): Similarity threshold for fuzzy matching. Defaults to 80.
        """
        self.curse_words = curse_words
        self.whitelist = whitelist or set()
        self.fuzzy_threshold = fuzzy_threshold

    def is_curse(self, word: str) -> bool:
        """
        Determine if a given word is a curse word.

        The check includes:
        - Exact substring match against curse_words
        - Fuzzy matching using RapidFuzz partial_ratio
        - Ignoring any words that contain a substring from whitelist

        Args:
            word (str): Word to check.

        Returns:
            bool: True if word is a curse, False otherwise.
        """
        w_lower = word.lower()
        if any(white in w_lower for white in self.whitelist):
            return False
        if any(c in w_lower for c in self.curse_words):
            return True
        for curse in self.curse_words:
            if fuzz.partial_ratio(curse, w_lower) >= self.fuzzy_threshold:
                return True
        return False


def censor_words(
    segments,
    curse_base: CurseBase,
    replacement: str = "[CENSORED]",
    window_size: int = 1,
    strict_window_censor: bool = True
):
    """
    Censor curse words in segments using fuzzy matching and an optional sliding window.

    Args:
        segments (list): List of Segment objects containing words with timestamps.
        curse_base (CurseBase): Instance of CurseBase containing curse words and whitelist.
        replacement (str, optional): String to replace censored words with. Defaults to "[CENSORED]".
        window_size (int, optional): Maximum number of consecutive words to combine when checking for merged curse words. Defaults to 1.
        strict_window_censor (bool, optional):
            If True, only words that truly contain a curse substring are replaced in the window.
            If False, all words in the detected window are replaced. Defaults to True.

    Returns:
        tuple: (updated_segments, cursed_words)
            - updated_segments (list): List of Segment objects with censored words replaced.
            - cursed_words (list): List of Word objects that were detected as curses.
    """
    cursed_words = []

    for segment in segments:
        words = segment.words
        n = len(words)

        # First, check each word individually
        for w in words:
            if curse_base.is_curse(w.text):
                w.censored = True
                w.text = replacement
                cursed_words.append(w)

        # Sliding window for merged words
        for size in range(2, window_size + 1):
            for i in range(n - size + 1):
                window_words = words[i:i + size]
                joined_text = "".join([w.text for w in window_words])
                if curse_base.is_curse(joined_text):
                    if strict_window_censor:
                        # Replace only words that really contain curse substring
                        for w in window_words:
                            if curse_base.is_curse(w.text) and not w.censored:
                                w.censored = True
                                w.text = replacement
                                cursed_words.append(w)
                    else:
                        # Replace all words in the window
                        for w in window_words:
                            if not w.censored:
                                w.censored = True
                                w.text = replacement
                                cursed_words.append(w)

    return segments, cursed_words


def generate_ffmpeg_times(cursed_words):
    """
    Generate a list of time intervals suitable for ffmpeg from censored words.

    Args:
        cursed_words (list): List of Word objects that were censored.

    Returns:
        list: List of tuples [(start_time, end_time), ...] for each censored word.
    """
    return [(w.start_time, w.end_time) for w in cursed_words]