from pathlib import Path
from typing import List

def _fmt_ts(t: float) -> str:
    """
    Format a timestamp in seconds into SRT timecode format: HH:MM:SS,mmm.

    Parameters
    ----------
    t : float
        Time in seconds.

    Returns
    -------
    str
        Formatted SRT timestamp.
    """
    ms = int((t - int(t)) * 1000)
    s = int(t) % 60
    m = (int(t) // 60) % 60
    h = int(t) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


def save_srt(segments: List, path: Path, censor_fmt: str = "**{word}**"):
    """
    Save a list of Segment objects as an SRT subtitle file.

    Censored words can be replaced with either a static string or a dynamic pattern.

    Parameters
    ----------
    segments : List[Segment]
        List of transcript segments to convert.
    path : Path
        Path to the output SRT file.
    censor_fmt : str, optional
        Formatting for censored words. Can be:
        - Static string: "[CENSORED]", "***", etc.
        - Dynamic pattern containing "{word}": "**{word}**", "[BEEP:{word}]", etc.
          "{word}" is replaced with the original word text. Defaults to "**{word}**".

    Notes
    -----
    - Each segment generates a numbered SRT entry.
    - Words marked as `censored` are replaced according to `censor_fmt`.
    - Non-censored words remain unchanged.
    """
    lines = []

    for idx, seg in enumerate(segments, start=1):
        if not seg.words:
            continue

        start = seg.words[0].start_time
        end = seg.words[-1].end_time

        def encode_word(w):
            if not w.censored:
                return w.text
            if "{word}" in censor_fmt:
                return censor_fmt.replace("{word}", w.text)
            return censor_fmt

        text = " ".join(encode_word(w) for w in seg.words)

        lines.append(str(idx))
        lines.append(f"{_fmt_ts(start)} --> {_fmt_ts(end)}")
        lines.append(text)
        lines.append("")

    path.write_text("\n".join(lines), encoding="utf-8")
