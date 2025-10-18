from typing import List
from faster_whisper import WhisperModel

class Word:
    """
    Represents a single word in a transcript with timing and censorship info.

    Attributes:
        text (str): The recognized word text.
        start_time (float): Start time of the word in seconds.
        end_time (float): End time of the word in seconds.
        censored (bool): Flag indicating if the word has been censored. Defaults to False.
    """

    def __init__(self, text: str, start_time: float, end_time: float, censored: bool = False):
        self.text = text
        self.start_time = start_time
        self.end_time = end_time
        self.censored = censored


class Segment:
    """
    Represents a segment of audio containing a sequence of words.

    Attributes:
        words (List[Word]): List of Word objects in the segment.
        start_time (float): Start time of the segment (from first word).
        end_time (float): End time of the segment (from last word).
    """

    def __init__(self, words: List['Word']):
        self.words = words
        self.start_time = words[0].start_time if words else 0.0
        self.end_time = words[-1].end_time if words else 0.0


class Transcript:
    """
    Represents the full transcript of an audio file.

    Attributes:
        segments (List[Segment]): List of segments in the transcript.
        duration (float): Total duration of the audio file in seconds.
    """

    def __init__(self, segments: List['Segment'], duration: float):
        self.segments = segments
        self.duration = duration


def transcribe_file(file_path: str, model_size: str = "medium", language: str = None) -> Transcript:
    """
    Transcribe an audio or video file and return a Transcript object containing
    segments and words with timestamps.

    Args:
        file_path (str): Path to the audio/video file to transcribe.
        model_size (str, optional): Size of the Whisper model ("tiny", "base", "medium", "large"). Defaults to "medium".
        language (str, optional): Language code for transcription (e.g., "ru"). If None, automatic detection is used.

    Returns:
        Transcript: Transcript object containing all segments and words with timestamps.
    """
    model = WhisperModel(model_size)
    segments_gen, info = model.transcribe(file_path, word_timestamps=True, language=language)

    segments_list: List[Segment] = []

    for segment in segments_gen:
        words_list: List[Word] = []
        if segment.words:
            for w in segment.words:
                word_obj = Word(
                    text=w.word,
                    start_time=w.start,
                    end_time=w.end
                )
                words_list.append(word_obj)
            segments_list.append(Segment(words=words_list))

    return Transcript(segments=segments_list, duration=info.duration)


def transcribe_stream(audio_data: bytes, model_size: str = "medium", language: str = None) -> Transcript:
    """
    Transcribe audio from memory (bytes) and return a Transcript object.

    Args:
        audio_data (bytes): Raw audio data to transcribe.
        model_size (str, optional): Size of the Whisper model. Defaults to "medium".
        language (str, optional): Language code for transcription. Defaults to None.

    Returns:
        Transcript: Transcript object containing all segments and words with timestamps.
    """
    import io
    audio_io = io.BytesIO(audio_data)
    model = WhisperModel(model_size)

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