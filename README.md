# SLM Server

A Small Language Model (SLM) implemented in Python.
Model: [Gemma 4b](https://ai.google.dev/gemma) from [Ollama](https://ollama.com/).
Backend: [Flask](https://flask.palletsprojects.com/en/stable/).

## Requirements
 - Python 3.8 or higher
   - Flask
   - Ollama
   - Requests
 - Ollama
 - Gemma 4b model
 - At least 8GB of RAM

## Installation and Usage
 1. Install the [Ollama](https://ollama.com/download) client
 2. Install Mistral 7B model using the command:
    ```bash
    ollama pull gemma3:4b
    ```
 3. Install required Python packages, either globally or in an virtual environment, using the command:
    ```bash
    pip install -r requirements.txt
    ```
 4. Run the server using the command:
    ```bash
    python server.py
    ```
 5. Open your web browser and navigate to `http://localhost:5000` to access the SLM server.
