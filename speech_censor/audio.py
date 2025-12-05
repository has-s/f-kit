import numpy as np
from pathlib import Path
from pydub import AudioSegment
import pyloudnorm as pyln
from typing import Union, List, Tuple
from speech_censor.constants import SAMPLE_RATE, SAMPLE_WIDTH, CHANNELS


def extract_audio(input_file: str, output_file: str = None) -> str:
    """
    Extract audio from video or audio file into 16-bit PCM WAV format.

    Parameters
    ----------
    input_file : str
        Path to input audio or video file.
    output_file : str, optional
        Path for the extracted WAV file. If None, adds "_extracted.wav" to input filename.

    Returns
    -------
    str
        Path to the extracted WAV file.

    Raises
    ------
    CalledProcessError
        If ffmpeg extraction fails.
    """
    from subprocess import run

    input_path = Path(input_file)
    if output_file is None:
        output_file = input_path.with_name(input_path.stem + "_extracted.wav")
    else:
        output_file = Path(output_file)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", str(SAMPLE_RATE),
        "-ac", str(CHANNELS),
        str(output_file)
    ]
    run(cmd, check=True)
    return str(output_file)


def _normalize_loudness(waveform: np.ndarray, target_lufs: float, sr: int) -> np.ndarray:
    """
    Normalize waveform loudness to a target LUFS using ITU-R BS.1770 / EBU R128.

    Parameters
    ----------
    waveform : np.ndarray
        Float32 waveform, mono or stereo, values in [-1, 1].
    target_lufs : float
        Desired loudness in LUFS.
    sr : int
        Sample rate in Hz.

    Returns
    -------
    np.ndarray
        Normalized waveform.
    """
    meter = pyln.Meter(sr)
    block_size_samples = int(0.4 * sr)

    if len(waveform) < block_size_samples:
        return waveform

    loudness = meter.integrated_loudness(waveform)
    waveform_norm = pyln.normalize.loudness(waveform, loudness, target_lufs)
    return waveform_norm


def make_beep(duration: float, freq: int = 1000, target_lufs: float = -23.0) -> AudioSegment:
    """
    Generate a stereo sine beep of specified duration, frequency, and loudness.

    Parameters
    ----------
    duration : float
        Length of beep in seconds.
    freq : int
        Frequency in Hz (default 1000).
    target_lufs : float
        Target loudness in LUFS (default -23.0).

    Returns
    -------
    AudioSegment
        Stereo beep AudioSegment.
    """
    num_samples = int(duration * SAMPLE_RATE)
    t = np.arange(num_samples) / SAMPLE_RATE
    waveform = 0.1 * np.sin(2 * np.pi * freq * t).astype(np.float32)
    waveform_norm = _normalize_loudness(waveform, target_lufs, SAMPLE_RATE)
    waveform_int16 = np.int16(waveform_norm * 32767)
    stereo = np.column_stack([waveform_int16] * CHANNELS)
    return AudioSegment(
        stereo.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=SAMPLE_WIDTH,
        channels=CHANNELS
    )


def make_mute(duration: float) -> AudioSegment:
    """
    Generate a silent stereo AudioSegment of given duration.

    Parameters
    ----------
    duration : float
        Length of silence in seconds.

    Returns
    -------
    AudioSegment
        Silent stereo AudioSegment.
    """
    num_samples = int(duration * SAMPLE_RATE)
    silent = np.zeros((num_samples, CHANNELS), dtype=np.int16)
    return AudioSegment(
        silent.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=SAMPLE_WIDTH,
        channels=CHANNELS
    )


def censor_audio(
        input_wav: Union[str, AudioSegment],
        segments: List[Tuple[float, float]],
        mode: str = "beep",
        beep_freq: int = 1000,
        target_lufs: float = -23.0
) -> AudioSegment:
    """
    Replace specified segments in audio with beep or silence, maintaining exact original duration.

    Parameters
    ----------
    input_wav : Union[str, AudioSegment]
        Path to input WAV file or an AudioSegment object.
    segments : List[Tuple[float, float]]
        List of (start_time, end_time) tuples in seconds to censor.
    mode : str
        Replacement mode: "beep" or "mute" (default "beep").
    beep_freq : int
        Frequency of beep in Hz if mode="beep" (default 1000).
    target_lufs : float
        Loudness of beep in LUFS (default -23.0).

    Returns
    -------
    AudioSegment
        Censored AudioSegment with identical duration to input.
    """
    if isinstance(input_wav, AudioSegment):
        audio = input_wav
    else:
        audio = AudioSegment.from_wav(input_wav)

    censored_audio = AudioSegment.empty()
    cursor_ms = 0

    for start_sec, end_sec in sorted(segments, key=lambda x: x[0]):
        start_ms = int(start_sec * 1000)
        end_ms = int(end_sec * 1000)

        if start_ms > cursor_ms:
            censored_audio += audio[cursor_ms:start_ms]

        duration_sec = end_sec - start_sec
        replacement = (
            make_beep(duration_sec, beep_freq, target_lufs) if mode == "beep" else make_mute(duration_sec)
        )
        censored_audio += replacement
        cursor_ms = end_ms

    if cursor_ms < len(audio):
        censored_audio += audio[cursor_ms:]

    if len(censored_audio) > len(audio):
        censored_audio = censored_audio[:len(audio)]
    elif len(censored_audio) < len(audio):
        censored_audio += make_mute((len(audio) - len(censored_audio)) / 1000)

    return censored_audio