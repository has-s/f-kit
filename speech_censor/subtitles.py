from pathlib import Path

def _fmt_ts(t: float):
    ms = int((t - int(t)) * 1000)
    s = int(t) % 60
    m = (int(t) // 60) % 60
    h = int(t) // 3600
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def save_srt(segments, path: Path):
    """Convert segments → SRT."""
    lines = []
    idx = 1

    for seg in segments:
        start = seg.start_time
        end = seg.end_time

        text = " ".join(w.text for w in seg.words)  # у Segment НЕТ .text

        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = t % 60
            return f"{h:02}:{m:02}:{s:06.3f}".replace(".", ",")

        lines.append(str(idx))
        lines.append(f"{fmt(start)} --> {fmt(end)}")
        lines.append(text)
        lines.append("")
        idx += 1

    path.write_text("\n".join(lines), encoding="utf8")