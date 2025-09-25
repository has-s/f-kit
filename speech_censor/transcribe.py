# transcribe.py
from typing import List
from faster_whisper import WhisperModel

class Word:
    def __init__(self, text: str, start_time: float, end_time: float, censored: bool = False):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.censored = censored

class Segment:
    def __init__(self, words: List['Word']):
        self.words = words
        self.start_time = words[0].start_time if words else 0.0
        self.end_time = words[-1].end_time if words else 0.0

class Transcript:
    def __init__(self, segments: List['Segment'], duration: float):
        self.segments = segments
        self.duration = duration

def transcribe_file(file_path: str, model_size: str = "medium", language: str = None) -> Transcript:
    """
    Transcribe an audio or video file and return a Transcript object containing
    segments and words with timestamps.
    """
    model = WhisperModel(model_size)

    segments_gen, info = model.transcribe(file_path, word_timestamps=True, language=language)

    segments_list: List[Segment] = []

    for seg_idx, segment in enumerate(segments_gen, 1):
        words_list: List[Word] = []

        if segment.words:
            for w_idx, w in enumerate(segment.words, 1):
                word_obj = Word(
                    text=w.word,
                    start_time=w.start,
                    end_time=w.end
                )
                words_list.append(word_obj)

            seg_obj = Segment(words=words_list)
            segments_list.append(seg_obj)

    transcript = Transcript(segments=segments_list, duration=info.duration)
    return transcript

def transcribe_stream(audio_data: bytes, model_size: str = "medium", language: str = None) -> Transcript:
    """
    Transcribe audio from memory (bytes) and return a Transcript object.
    """
    model = WhisperModel(model_size)

    # faster-whisper поддерживает list[str] файлов или BytesIO
    import io
    audio_io = io.BytesIO(audio_data)

    segments_gen, info = model.transcribe(audio_io, word_timestamps=True, language=language)

    segments_list: List[Segment] = []

    for segment in segments_gen:
        words_list: List[Word] = []
        if segment.words:
            for w in segment.words:
                words_list.append(Word(
                    text=w.word,
                    start_time=w.start,
                    end_time=w.end
                ))
            segments_list.append(Segment(words=words_list))

    return Transcript(segments=segments_list, duration=info.duration)