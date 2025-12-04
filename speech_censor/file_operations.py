import json
from pathlib import Path
from typing import Optional

from speech_censor.file_manager import FileManager
from speech_censor.transcribe import Transcript, Segment, Word


# ===== TRANSCRIPT OPERATIONS =====

def load_transcript(fm: FileManager) -> Optional[Transcript]:
    """
    Load a transcript from JSON into a Transcript object.

    Loads the original transcript from `transcript_original_json`. Strips leading
    and trailing spaces from each word's text to avoid artifacts in further processing.

    Parameters
    ----------
    fm : FileManager
        FileManager instance with paths to original transcript JSON.

    Returns
    -------
    Optional[Transcript]
        A Transcript object if the JSON file exists, otherwise None.

    Raises
    ------
    TypeError
        If the JSON structure has incorrect types.
    KeyError
        If required keys are missing in the JSON structure.
    json.JSONDecodeError
        If the JSON file is corrupted or invalid.
    """
    if not fm.transcript_original_json.exists():
        return None
    with open(fm.transcript_original_json, "r", encoding="utf-8") as f:
        data = json.load(f)
    validate_transcript_structure(data)
    segments = []
    for seg_data in data['segments']:
        words = [Word(w['text'].strip(), w['start_time'], w['end_time'], w['censored']) for w in seg_data['words']]
        segments.append(Segment(words=words))
    return Transcript(segments=segments, duration=data['duration'])


def save_transcript(fm: FileManager, transcript: Transcript):
    """
    Save a Transcript object to JSON.

    Stores the transcript into `transcript_original_json`. Leading and trailing
    spaces in words are stripped to maintain clean storage format.

    Parameters
    ----------
    fm : FileManager
        FileManager instance with paths to original transcript JSON.
    transcript : Transcript
        Transcript object to save.

    Returns
    -------
    None
    """
    data = {
        "duration": transcript.duration,
        "segments": [
            {
                "start_time": s.start_time,
                "end_time": s.end_time,
                "words": [
                    {"text": w.text.strip(), "start_time": w.start_time, "end_time": w.end_time, "censored": w.censored}
                    for w in s.words
                ]
            }
            for s in transcript.segments
        ]
    }
    with open(fm.transcript_original_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def validate_transcript_structure(data) -> bool:
    """
    Validate the structure of a loaded transcript JSON.

    Expected JSON format:
        {
            'segments': [
                {
                    'words': [
                        {'text': str, 'start_time': float, 'end_time': float, 'censored': bool},
                        ...
                    ],
                    'start_time': float,
                    'end_time': float
                },
                ...
            ],
            'duration': float
        }

    Parameters
    ----------
    data : dict
        JSON object loaded from a transcript file.

    Returns
    -------
    bool
        True if the structure matches the expected transcript format.

    Raises
    ------
    TypeError
        If types of root, segments, or words are incorrect.
    KeyError
        If required keys are missing in transcript, segments, or words.
    """
    if not isinstance(data, dict):
        raise TypeError("Transcript root should be a dictionary.")
    if "segments" not in data or "duration" not in data:
        raise KeyError("Transcript must have 'segments' and 'duration' keys.")
    if not isinstance(data['segments'], list):
        raise TypeError("'segments' must be a list.")
    for i, seg in enumerate(data['segments']):
        if not isinstance(seg, dict):
            raise TypeError(f"Segment {i} must be a dict.")
        if "words" not in seg or "start_time" not in seg or "end_time" not in seg:
            raise KeyError(f"Segment {i} missing required keys.")
        if not isinstance(seg['words'], list):
            raise TypeError(f"Segment {i} 'words' must be a list.")
        for j, w in enumerate(seg['words']):
            if not all(k in w for k in ("text", "start_time", "end_time", "censored")):
                raise KeyError(f"Word {j} in segment {i} missing required keys.")
    return True


# ===== CENSOR FLAGS OPERATIONS =====

def load_original_file(fm: FileManager) -> dict:
    """
    Load censored flags from the original transcript.

    Always loads from `transcript_original_json`. Do not mix calls to
    `load_original_file()` and `load_editable_file()` in the same context,
    as this can lead to confusion and errors when handling censored flags.

    Parameters
    ----------
    fm : FileManager
        FileManager instance with paths to original transcript.

    Returns
    -------
    dict
        Mapping of segment indices and word indices to censored boolean flags.

    Raises
    ------
    FileNotFoundError
        If the original transcript file does not exist.
    """
    import json

    if not fm.transcript_original_json.exists():
        raise FileNotFoundError("Original transcript file not found.")

    with open(fm.transcript_original_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {i: {j: w.get("censored", False) for j, w in enumerate(seg.get("words", []))}
            for i, seg in enumerate(data.get("segments", []))}


def load_editable_file(fm: FileManager) -> dict:
    """
    Load censored flags from the editable transcript.

    Always loads from `transcript_edit_json`. Do not mix calls to
    `load_original_file()` and `load_editable_file()` in the same context,
    as this can lead to confusion and errors when handling censored flags.

    Parameters
    ----------
    fm : FileManager
        FileManager instance with paths to editable transcript.

    Returns
    -------
    dict
        Mapping of segment indices and word indices to censored boolean flags.

    Raises
    ------
    FileNotFoundError
        If the editable transcript file does not exist.
    """
    import json

    if not fm.transcript_edit_json.exists():
        raise FileNotFoundError("Editable transcript file not found.")

    with open(fm.transcript_edit_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    return {i: {j: w.get("censored", False) for j, w in enumerate(seg.get("words", []))}
            for i, seg in enumerate(data.get("segments", []))}


def load_censored_flags(file: Path) -> dict:
    """
    Load censored flags from a JSON file that must match the original transcript.

    Parameters
    ----------
    file : Path
        Path to the JSON file with censored flags.
    fm : FileManager
        FileManager instance providing access to the original transcript.

    Returns
    -------
    dict
        Dictionary mapping segment indices and word indices to censored boolean flags.

    Raises
    ------
    FileNotFoundError
        If the file or the original transcript does not exist.
    ValueError
        If the loaded flags do not match the original transcript structure.
    json.JSONDecodeError
        If the file contains invalid JSON.

    Notes
    -----
    - The loaded file must have the same number of segments and words per segment as the
      original transcript (`transcript_original_json`) to ensure correct application.
    """

    fm = FileManager()  # assumes default initialization or context where input_file/temp_dir is set

    if not fm.transcript_original_json.exists():
        raise FileNotFoundError(f"Original transcript file {fm.transcript_original_json} not found.")
    if not file.exists():
        raise FileNotFoundError(f"Censored flags file {file} not found.")

    with open(fm.transcript_original_json, "r", encoding="utf-8") as f:
        original = json.load(f)

    with open(file, "r", encoding="utf-8") as f:
        flags_data = json.load(f)

    # Validate structure
    if len(flags_data) != len(original.get("segments", [])):
        raise ValueError("Number of segments in censored flags does not match original transcript.")

    for i, seg in enumerate(original.get("segments", [])):
        if i not in flags_data:
            raise ValueError(f"Segment {i} missing in censored flags.")
        if len(flags_data[i]) != len(seg.get("words", [])):
            raise ValueError(f"Segment {i} has {len(flags_data[i])} words in flags, "
                             f"but {len(seg.get('words', []))} in original transcript.")

    return flags_data


def save_censored_flags(fm: FileManager, current_flags: dict):
    """
    Save the current in-memory censored flags to the editable transcript.

    Always saves to `transcript_edit_json`. The original transcript remains
    unchanged. Use this function to persist edits to the working copy of
    censored flags.

    Parameters
    ----------
    fm : FileManager
        FileManager instance with paths to editable transcript.
    current_flags : dict
        Current in-memory censored flags mapping segment and word indices to booleans.
    """
    import json

    with open(fm.transcript_edit_json, "w", encoding="utf-8") as f:
        json.dump(current_flags, f, ensure_ascii=False, indent=2)


def apply_censored_flags(fm: FileManager, current_flags: dict = None):
    """
    Apply censored flags to the original transcript.

    Behavior:
    - Updates only the 'censored' boolean flags in the original transcript.
    - Leaves word text intact.
    - Flags are applied from the provided `current_flags` dictionary if given.
      Otherwise, loads flags from transcript_edit_json.
    - This is the only function that modifies the original transcript.

    Args:
        fm (FileManager): FileManager instance with paths.
        current_flags (dict, optional): Dictionary of flags to apply.
                                        If None, loads from transcript_edit_json.

    Raises:
        FileNotFoundError: If the original transcript or editable flags file does not exist.
    """
    import json

    if not fm.transcript_original_json.exists():
        raise FileNotFoundError("Original transcript file not found.")

    # Determine source of flags
    if current_flags is None:
        if not fm.transcript_edit_json.exists():
            raise FileNotFoundError("Editable flags file not found.")
        with open(fm.transcript_edit_json, "r", encoding="utf-8") as f:
            current_flags = json.load(f)

    with open(fm.transcript_original_json, "r", encoding="utf-8") as f:
        data = json.load(f)

    for seg_idx, words_dict in current_flags.items():
        if int(seg_idx) >= len(data["segments"]):
            continue
        segment = data["segments"][int(seg_idx)]
        for word_idx, censored in words_dict.items():
            if int(word_idx) >= len(segment["words"]):
                continue
            segment["words"][int(word_idx)]["censored"] = censored

    with open(fm.transcript_original_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def reset_censorship(current_flags: dict) -> dict:
    """
    Reset all in-memory censored flags to False.

    Behavior:
    - Does not modify any files.
    - Sets all flags in the provided current_flags dictionary to False.

    Args:
        current_flags (dict): Current in-memory censored flags.

    Returns:
        dict: New dictionary with all flags set to False.
    """
    reset_flags = {}
    for seg_idx, words_dict in current_flags.items():
        reset_flags[seg_idx] = {word_idx: False for word_idx in words_dict}
    return reset_flags


