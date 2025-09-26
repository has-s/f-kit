import numpy as np
from pathlib import Path
from pydub import AudioSegment
import pyloudnorm as pyln
from typing import Union, List, Tuple
from speech_censor.constants import SAMPLE_RATE, SAMPLE_WIDTH, CHANNELS

def extract_audio(input_file: str, output_file: str = None) -> str:
    from subprocess import run

    input_path = Path(input_file)
    if output_file is None:
        # новый файл с `_extracted` в имени
        output_file = input_path.with_name(input_path.stem + "_extracted.wav")
    else:
        output_file = Path(output_file)

    cmd = [
        "ffmpeg", "-y",
        "-i", str(input_path),
        "-vn",
        "-acodec", "pcm_s16le",
        "-ar", "48000",
        "-ac", "2",
        str(output_file)
    ]
    run(cmd, check=True)
    return str(output_file)

def _normalize_loudness(waveform: np.ndarray, target_lufs: float, sr: int) -> np.ndarray:
    """
    Normalize waveform to target LUFS using ITU-R BS.1770 / EBU R128.
    waveform: np.ndarray float32, mono or stereo in range [-1, 1]
    sr: sample rate
    """
    meter = pyln.Meter(sr)  # BS.1770 meter
    block_size_samples = int(0.4 * sr)  # 400 ms default block size

    # если сигнал слишком короткий для метра, возвращаем без нормализации
    if len(waveform) < block_size_samples:
        return waveform

    loudness = meter.integrated_loudness(waveform)
    waveform_norm = pyln.normalize.loudness(waveform, loudness, target_lufs)
    return waveform_norm


def make_beep(duration: float, freq: int = 1000, target_lufs: float = -23.0) -> AudioSegment:
    """
    Generate a sine beep with sample-accurate duration, normalized to LUFS.

    Parameters:
        duration (float): Length of the beep in seconds.
        freq (int): Frequency of the sine wave in Hz (default 1000 Hz).
        target_lufs (float): Target loudness in LUFS (default -23 LUFS, EBU R128 standard).

    Returns:
        AudioSegment: Stereo AudioSegment of the sine beep.
    """
    num_samples = int(duration * SAMPLE_RATE)
    t = np.arange(num_samples) / SAMPLE_RATE

    # Generate sine waveform float32 in [-1, 1]
    waveform = 0.1 * np.sin(2 * np.pi * freq * t).astype(np.float32)

    # Normalize loudness
    waveform_norm = _normalize_loudness(waveform, target_lufs, SAMPLE_RATE)

    # Scale to int16
    waveform_int16 = np.int16(waveform_norm * 32767)

    # Create stereo by duplicating the waveform across channels
    stereo = np.column_stack([waveform_int16] * CHANNELS)

    # Convert to AudioSegment
    return AudioSegment(
        stereo.tobytes(),
        frame_rate=SAMPLE_RATE,
        sample_width=SAMPLE_WIDTH,
        channels=CHANNELS
    )


def make_mute(duration: float) -> AudioSegment:
    """
    Generate a silent audio segment with sample-accurate duration.

    Parameters:
        duration (float): Length of the silence in seconds.

    Returns:
        AudioSegment: Stereo AudioSegment of silence.
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
    Replace segments in WAV or AudioSegment with beep or silence with sample-accurate duration.

    :param input_wav: path to input WAV or AudioSegment
    :param segments: list of (start_time, end_time) in seconds
    :param mode: "beep" or "mute"
    :param beep_freq: frequency for beep if mode="beep"
    :param target_lufs: loudness of beep in LUFS (default -23.0, EBU R128)
    :return: AudioSegment with censored segments
    """
    # load audio if input is a path
    if isinstance(input_wav, AudioSegment):
        audio = input_wav
    else:
        audio = AudioSegment.from_wav(input_wav)

    for start, end in segments:
        duration = end - start
        replacement = (
            make_beep(duration, beep_freq, target_lufs)
            if mode == "beep" else make_mute(duration)
        )

        start_ms = int(start * 1000)
        end_ms = int(end * 1000)

        audio = audio[:start_ms] + replacement + audio[end_ms:]

    # ensure final length matches original within 1 sample
    original_len_samples = len(audio.get_array_of_samples()) // CHANNELS
    expected_len_samples = int(audio.frame_count())
    diff_samples = original_len_samples - expected_len_samples
    if diff_samples != 0:
        if diff_samples > 0:
            audio = audio[:-diff_samples]
        else:
            audio += make_mute(-diff_samples / SAMPLE_RATE)

    return audio