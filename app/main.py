import typer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.services.extraction_service import ExtractionService
from app.schemas.extraction import ExtractionOutput
from app.utils.logger import logger
import uvicorn

# --- Setup FastAPI ---
app = FastAPI(title="AI Structured Extraction Tool API")
service = ExtractionService()

class ExtractRequest(BaseModel):
    text: str

@app.post("/extract", response_model=ExtractionOutput)
async def extract_text(request: ExtractRequest):
    """
    Extract structured information via API.
    """
    logger.info(f"Received API request for text: {request.text[:50]}...")
    try:
        result = service.process(request.text)
        return result
    except Exception as e:
        logger.error(f"API extraction failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# --- Setup CLI with Typer ---
cli = typer.Typer()

@cli.command()
def extract(text: str = typer.Argument(..., help="Unstructured text to extract info from")):
    """
    Extract structured information via CLI.
    """
    logger.info(f"Starting CLI extraction for text: {text[:50]}...")
    try:
        result = service.process(text)
        typer.echo(result.model_dump_json(indent=2))
    except Exception as e:
        logger.error(f"CLI extraction failed: {str(e)}")
        typer.echo(f"Error: {str(e)}", err=True)

@cli.command()
def serve(port: int = 8000, host: str = "0.0.0.0"):
    """
    Run the API server.
    """
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    cli()
