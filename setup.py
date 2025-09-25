from setuptools import setup, find_packages

setup(
    name="speech-censor",
    version="0.1.0",
    description="A Python core for audio censorship using Whisper",
    author="hass",
    packages=find_packages(),
    install_requires=[
        "faster-whisper",
        "pysrt",
        "tqdm",
        "simpleaudio"
    ],
    entry_points={
        "console_scripts": [
            "speech-censor=speech_censor.cli:main",
        ]
    },
    python_requires=">=3.9",
    license="MIT",
)