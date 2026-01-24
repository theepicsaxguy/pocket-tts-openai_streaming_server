# Pocket-TTS OpenAI Streaming Server

This project implements an [OpenAI-compatible API](https://platform.openai.com/docs/api-reference/audio/createSpeech) for the **Pocket-TTS** text-to-speech model. It supports real-time streaming, high-quality voice synthesis, and easy management of custom voices.

Pocket-TTS Github repo: https://github.com/kyutai-labs/pocket-tts

Pocket-TTS Huggingface: https://huggingface.co/kyutai/pocket-tts

## Features

-   **OpenAI API Compatibility**: Drop-in replacement for `tts-1` endpoints.
-   **Streaming Support**: Real-time audio generation with low latency.
-   **Web Interface**: Simple built-in UI to test voices and generation.
-   **Custom Voices**: Easy addition of new voices by dragging and dropping `.wav` files.
-   **Flexible Configuration**: Run via command line or an interactive batch launcher.
-   **Windows EXE included**: If you want to use defaults (host: 0.0.0.0, port: 5002, streaming enabled, local model file and built-in voices) just double click on .exe and you're up and running!

## Prerequisites

-   **Python 3.10+**: Ensure Python is installed and added to your system PATH.

## EXE Installation and Usage (Windows only)

-   Download latest release .zip from https://github.com/teddybear082/pocket-tts-openai_streaming_server/releases
-   Unzip to location on your computer that is not protected, like C://Pocket-TTS-Server/
-   To use all defaults for server (host: 0.0.0.0, port: 5002, streaming enabled, local model file and built-in voices) just double click on .exe and you're up and running!
-   To be able to input custom arguments for any of those, run the run_pocket_tts_server_exe.bat instead and follow the UI prompts.
-   To use the WebUI, navigate to the host and port you set in the .bat file, by default: http://localhost:5002
-   Supports cloning .wav, .mp3. and .flac files. To try out custom cloning, use the WebUI and in the voice list select the last option to upload a custom file and insert the path to the .wav, .mp3, or .flac with the voice you want to clone.

## Python Installation

1.  **Clone or Download** this repository to your local machine.

2.  **Install Dependencies**:
    It is recommended to use a virtual environment.

    ```bash
    # Create virtual environment
    python -m venv venv

    # Activate virtual environment
    # Windows:
    venv\Scripts\activate
    # Linux/Mac:
    source venv/bin/activate

    # Install requirements
    pip install -r requirements.txt
    ```

    *Note: If you do not have `requirements.txt`, you will need at least:*
    ```bash
    pip install flask pocket-tts torch torchaudio
    ```

3.  **Hugging Face Login (If required)**:
    Until a workaround is found, to enable voice cloning of .wavs you will need to insert your hugging face token when prompted in the .bat file.

## Python Usage

### Method 1: Interactive Launcher (Windows)

Double-click `run_pocket_tts_server.bat`. This interactive script handles the setup:

1.  **Hugging Face Login**: It may ask for your HF Token if not already set (leave blank if voice cloning not needed).
2.  **Environment**: Automatically looks for and activates your `venv`.
3.  **Configuration**: detailed prompts allow you to customize the run:
    -   **Host/Port**: Defaults to `0.0.0.0:5002`.
    -   **Model Path**: Press ENTER for the default, or specify a custom path/variant.
    -   **Voices Directory**: Defaults to `voices/` in the script's folder.
    -   **Streaming**: Option to enable streaming by default for all requests.

### Method 2: Command Line

Activate your virtual environment and run:

```bash
python pocket_tts_openai_server.py --host 0.0.0.0 --port 5002 --stream
```

**Arguments:**
-   `--host`: Host IP to bind to (default: `0.0.0.0`).
-   `--port`: Port to listen on (default: `5002`).
-   `--model_path`: Path to a local model file or a specific Hugging Face model variant.
-   `--voices_dir`: Directory to scan for custom voice `.wav` files (default: `voices/` in the project root if created, or as specified).
-   `--stream`: Enable streaming by default for all requests.

## Web Interface

Once the server is running, open your web browser and go to:

> **http://localhost:5002** (or your configured host:port)

From here you can:
-   Select available voices (Built-in or Custom).
-   Type text to generate speech.
-   Listen to the output directly in the browser.

## Custom Voices

You can easily add your own voices to the server.

1.  **Create a folder** for your voices (e.g., `voices/`).
2.  **Add Audio Files**: Place short, clear `.wav` files (3-10 seconds ideal) of the target speaker in this folder.
3.  **Restart/Configure Server**:
    -   If using the **Batch Launcher**, specify the full path to your `voices` folder when prompted.
    -   If using **CLI**, add `--voices_dir "path/to/voices"`.

**Naming**: The filename (e.g., `my_voice.wav`) will become the Voice ID.
-   Example Voice ID: `my_voice.wav`
-   In the Request: `"voice": "my_voice.wav"`

### Built-in Voices
The server comes with mappings for several default Pocket TTS voices:
`alba`, `marius`, `javert`, `jean`, `fantine`, `cosette`, `eponine`, `azelma`.

## API Usage

You can use this server with any OpenAI-compatible client.

**Endpoint**: `POST /v1/audio/speech`

**Example Request (cURL)**:
```bash
curl http://localhost:5002/v1/audio/speech \
  -H "Content-Type: application/json" \
  -d '{
    "model": "tts-1",
    "input": "The quick brown fox jumps over the lazy dog.",
    "voice": "alba"
  }' \
  --output speech.wav
```

**Python (openai-python)**:
```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:5002/v1",
    api_key="not-needed"
)

response = client.audio.speech.create(
    model="tts-1",
    voice="alba",
    input="Hello world! This is a test of Pocket TTS."
)

response.stream_to_file("output.wav")
```
