# Agentic Analytics Platform (Flask Edition)

A professional, presentation-ready web dashboard and local LLM Query Agent built with Flask and Ollama.

## Setup Instructions

1. **Install Prerequisites**: Ensure you have Python 3.10+ installed.
   
2. **Install Library Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install and Setup Ollama**:
   - Download Ollama from [https://ollama.com/download](https://ollama.com/download)
   - After installation, start the Ollama server and pull your model:
   ```bash
   ollama run llama3
   ```

4. **Verify Data Configuration**:
   - Ensure the main repository structure is maintained. The datasets are read strictly from your `/data/` root as matched.
   - `config.yaml` points by default to `../data` and `../data/txt`.

5. **Run the Flask App**:
   ```bash
   python app.py
   ```
   *The system reads and loads all CSV files and text matches into pure memory once on startup. This might take a few seconds.*

6. **Open Dashboard**:
   Open a browser and navigate to `http://127.0.0.1:5000`

## Architecture Highlights
- **No Upload functionality**: Completely immutable local analytic tool.
- **Flask Blueprints**: All API streams (Chart.js and Ollama endpoints) are centralized via pure endpoints.
- **Chart.js + Bootstrap 5**: Used for client-side rendering with dark-theme compliance. No `matplotlib` image generation required.
- **`ingest.py`**: Central singleton holding `pd.DataFrame` datasets. Fallback to `latin-1` ensuring data parity across varying export formats!