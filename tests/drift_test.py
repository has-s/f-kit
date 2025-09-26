import pytest
from speech_censor.audio import make_mute, censor_audio

# Practical thresholds
MAX_DRIFT_SEC = 0.005      # 5 ms allowed
MAX_DRIFT_PERCENT = 0.05   # 0.05% allowed

@pytest.mark.parametrize(
    "track_length,num_beeps,beep_duration",
    [
        (10.0, 50, 0.01),
        (30.0, 100, 0.05),
        (60.0, 200, 0.2),
        (300.0, 500, 0.01),
    ]
)
def test_audio_drift_realistic(track_length, num_beeps, beep_duration):
    """
    Realistic audio drift test: inserts beeps or silent segments and reports actual drift.
    Ensures that the total track length after censoring remains within acceptable limits.
    """
    interval = beep_duration  # minimal interval between beeps

    # create silent base track
    base_audio = make_mute(track_length)

    # generate segments for beeps
    segments = []
    current_time = 0.0
    for _ in range(num_beeps):
        if current_time + beep_duration > track_length:
            break
        segments.append((current_time, current_time + beep_duration))
        current_time += interval

    # insert beeps
    audio = censor_audio(base_audio, segments, mode="beep", beep_freq=1000)

    # calculate drift
    expected_len_ms = len(base_audio)
    actual_len_ms = len(audio)
    diff_ms = actual_len_ms - expected_len_ms
    drift_sec = diff_ms / 1000.0
    drift_percent = drift_sec / track_length * 100

    print(f"\nTrack length: {track_length}s, num beeps: {len(segments)}, beep duration: {beep_duration}s")
    print(f"Expected length: {expected_len_ms/1000:.6f}s")
    print(f"Actual length:   {actual_len_ms/1000:.6f}s")
    print(f"Difference:      {drift_sec:.6f}s")
    print(f"Drift percentage: {drift_percent:.6f}%")

    # check drift within practical thresholds
    assert abs(drift_sec) <= MAX_DRIFT_SEC, f"Drift too high: {drift_sec:.6f}s"
    assert abs(drift_percent) <= MAX_DRIFT_PERCENT, f"Drift percent too high: {drift_percent:.6f}%"