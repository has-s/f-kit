import subprocess
import wave
from pathlib import Path
import numpy as np

def extract_audio(input_file: str, output_file: str = None) -> str:
    """
    Extracts audio from any video or audio file supported by ffmpeg.
    Converts to WAV for compatibility with Whisper if needed.

    :param input_file: Path to input video/audio file.
    :param output_file: Path to save extracted audio; if None, same folder + 'audio.wav'.
    :return: Path to extracted audio file.
    """
    input_path = Path(input_file)
    if output_file is None:
        output_file = input_path.parent / "audio.wav"
    else:
        output_file = Path(output_file)

    cmd = [
        "ffmpeg",
        "-y",            # overwrite if exists
        "-i", str(input_path),
        "-vn",           # no video
        "-acodec", "pcm_s16le",  # WAV PCM
        "-ar", "48000",          # sample rate
        "-ac", "2",              # stereo
        str(output_file)
    ]

    subprocess.run(cmd, check=True)
    return str(output_file)

def make_beep(duration=0.2, freq=1000, sample_rate=48000):
    """
    Generate a beep sound as a numpy array (16-bit PCM), no file needed.

    :param duration: length of the beep in seconds
    :param freq: frequency in Hz
    :param sample_rate: samples per second
    :return: numpy array of int16, sample rate
    """
    t = np.linspace(0, duration, int(sample_rate * duration), False)
    tone = 0.5 * np.sin(2 * np.pi * freq * t)
    audio_data = np.int16(tone * 32767)
    return audio_data, sample_rate

def make_mute(duration=0.2, sample_rate=48000):
    """
    Generate a silent audio segment as a numpy array (16-bit PCM).

    :param duration: length of silence in seconds
    :param sample_rate: samples per second
    :return: numpy array of int16, sample rate
    """
    n_samples = int(duration * sample_rate)
    audio_data = np.zeros(n_samples, dtype=np.int16)
    return audio_data, sample_rate

def make_censor_track(
    audio_length: float,
    cursed_intervals: list[tuple[float, float]],
    sample_rate: int = 48000,
    method: str = "beep",
    beep_freq: int = 1000,
    beep_amplitude: float = 0.5
) -> np.ndarray:
    """
    Generate a full-length audio track for censoring.

    :param audio_length: total length of original audio in seconds
    :param cursed_intervals: list of tuples (start_time, end_time)
    :param sample_rate: samples per second
    :param method: "mute" or "beep"
    :param beep_freq: frequency of beep in Hz (if method="beep")
    :param beep_amplitude: amplitude of beep (0..1)
    :return: numpy array of int16 audio samples
    """
    # Initialize track with zeros
    total_samples = int(audio_length * sample_rate)
    track = np.zeros(total_samples, dtype=np.float32)

    for start, end in cursed_intervals:
        start_idx = int(start * sample_rate)
        end_idx = int(end * sample_rate)
        duration = end_idx - start_idx
        if method == "beep":
            t = np.linspace(0, (duration / sample_rate), duration, endpoint=False)
            beep = beep_amplitude * np.sin(2 * np.pi * beep_freq * t)
            track[start_idx:end_idx] = beep
        else:  # mute
            track[start_idx:end_idx] = 0.0

    # Convert to int16
    track_int16 = np.int16(track * 32767)
    return track_int16

def save_censor_track(track: np.ndarray, filename: str, sample_rate: int = 48000):
    """Save generated track as WAV file."""
    with wave.open(filename, "w") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(track.tobytes())

def overlay_censor_track(
        original_audio_file: str,
        censor_track: np.ndarray,
        output_file: str,
        sample_rate: int = 48000
):
    """
    Overlay the generated censor track (beeps or silence) on the original audio.

    :param original_audio_file: path to original WAV
    :param censor_track: numpy array of int16 samples
    :param output_file: path to save final audio
    :param sample_rate: sample rate of audio
    """
    import tempfile

    # Save temporary censor track
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name
        save_censor_track(censor_track, tmp_path, sample_rate)

    # Use ffmpeg to mix original audio with censor track
    cmd = [
        "ffmpeg",
        "-y",
        "-i", original_audio_file,
        "-i", tmp_path,
        "-filter_complex", "[0:a][1:a]amix=inputs=2:dropout_transition=0",
        output_file
    ]
    subprocess.run(cmd, check=True)

    #TODO: Fix audio overlay. Mute before beep.