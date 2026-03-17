# AI Structured Extraction Tool (MVP)

An MVP for extracting structured information from unstructured text using Large Language Models.

## Features
- **Structured JSON Output**: Extracts summary, key entities, action items, deadlines, and risks.
- **Multi-Interface**: Supports both Command Line (CLI) and REST API.
- **Extensible Architecture**: 4-layered design (Input, Extraction, Schema, Application).

## Architecture
1. **Input Layer**: CLI (Typer) and API (FastAPI).
2. **Extraction Layer**: LLM-based (using `instructor` and `openai`).
3. **Schema / Validation Layer**: Pydantic models for format enforcement.
4. **Application Layer**: Orchestrates the extraction flow.

## Getting Started

### Prerequisites
- Python 3.10+
- OpenAI API Key

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

### Usage

#### CLI
To extract information from text via CLI:
```bash
python app/main.py extract "Project X is due on June 1st. Alice needs to finish the design. There is a risk of budget overrun."
```

#### API
To start the API server:
```bash
python app/main.py serve
```
Then send a POST request:
```bash
curl -X POST http://localhost:8000/extract \
     -H "Content-Type: application/json" \
     -d '{"text": "Project X is due on June 1st. Alice needs to finish the design."}'
```

## Future Enhancements
- Support for multiple LLM providers via `litellm`.
- Batch processing support.
- Custom schema definitions via API.
- Rule-based or hybrid extraction methods.
