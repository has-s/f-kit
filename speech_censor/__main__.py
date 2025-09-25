from speech_censor.transcribe import transcribe_file
from speech_censor.censor import CurseBase, censor_words
from speech_censor.audio import make_censor_track, overlay_censor_track
import os

def test_censor_pipeline():
    input_audio = "../proto/audio.wav"
    output_audio_beep = "../tests/output_beep.wav"
    os.makedirs(os.path.dirname(output_audio_beep), exist_ok=True)

    # 1. Transcribe the audio
    print("Transcribing audio...")
    transcript = transcribe_file(input_audio, model_size="medium", language="ru")

    # 2. Setup curse detector
    curse_base = CurseBase(
        curse_words={"пизд", "бляд", "блят", "бля", "сука", "хуй", "еб", "трах", "шлюх", "муд"},
        whitelist={"колеб"}
    )

    # 3. Apply censor
    print("Censoring words...")
    segments, cursed_words = censor_words(transcript.segments, curse_base)

    # 4. Extract intervals for beep
    cursed_intervals = [(w.start_time, w.end_time) for w in cursed_words]
    if not cursed_intervals:
        print("No curse words found, skipping audio censoring.")
        return

    # 5. Generate censor track (numpy array)
    audio_length = transcript.duration
    censor_track = make_censor_track(
        audio_length=audio_length,
        cursed_intervals=cursed_intervals,
        method="beep",
        beep_freq=1000
    )

    # 6. Overlay censor track on original audio
    print("Overlaying censor track...")
    overlay_censor_track(
        original_audio_file=input_audio,
        censor_track=censor_track,
        output_file=output_audio_beep
    )

    assert os.path.exists(output_audio_beep), "Beep output file was not created"
    print("Censor pipeline test passed!")

if __name__ == "__main__":
    test_censor_pipeline()