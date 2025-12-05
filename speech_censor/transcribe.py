from typing import List, Union
from faster_whisper import WhisperModel
import io


class Word:
    """
    Represents a single word in a transcript with timing and censorship info.

    Attributes
    ----------
    text : str
        Recognized word text.
    start_time : float
        Start time of the word in seconds.
    end_time : float
        End time of the word in seconds.
    censored : bool
        Flag indicating whether the word has been censored. Defaults to False.
    """
    def __init__(self, text: str, start_time: float, end_time: float, censored: bool = False):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.censored = censored


class Segment:
    """
    Represents a segment of audio containing a sequence of words.

    Attributes
    ----------
    words : List[Word]
        List of Word objects in the segment.
    start_time : float
        Start time of the segment (from first word). Defaults to 0 if no words.
    end_time : float
        End time of the segment (from last word). Defaults to 0 if no words.
    """
    def __init__(self, words: List[Word]):
        self.words = words
        self.start_time = words[0].start_time if words else 0.0
        self.end_time = words[-1].end_time if words else 0.0


class Transcript:
    """
    Represents the full transcript of an audio file.

    Attributes
    ----------
    segments : List[Segment]
        List of segments in the transcript.
    duration : float
        Total duration of the audio file in seconds.
    """
    def __init__(self, segments: List[Segment], duration: float):
        self.segments = segments
        self.duration = duration


def transcribe_audio(source: Union[str, bytes], model_size: str = "medium", language: str = None) -> Transcript:
    """
    Transcribe audio from a file path or raw bytes and return a structured Transcript object.

    Parameters
    ----------
    source : str | bytes
        Path to an audio/video file, or raw audio data as bytes.
    model_size : str, optional
        Size of the Whisper model to use ("tiny", "base", "medium", "large"). Defaults to "medium".
    language : str, optional
        Language code for transcription (e.g., "ru"). If None, automatic language detection is used.

    Returns
    -------
    Transcript
        Transcript object containing all segments and words with precise timestamps.

    Notes
    -----
    - Words are represented as Word objects, each with `text`, `start_time`, `end_time`, and `censored` attributes.
    - Segments are grouped sequences of words with `start_time` and `end_time` derived from the first and last words.
    """
    model = WhisperModel(model_size)

    if isinstance(source, bytes):
        source = io.BytesIO(source)

    segments_gen, info = model.transcribe(source, word_timestamps=True, language=language)
    segments_list: List[Segment] = []

    for segment in segments_gen:
        if not segment.words:
            continue
        words_list = [Word(w.word, w.start, w.end) for w in segment.words]
        segments_list.append(Segment(words_list))

    return Transcript(segments=segments_list, duration=info.duration)
