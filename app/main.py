import typer
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import asyncio
from app.services.extraction_service import ExtractionService
from app.services.factcheck_service import FactCheckCoordinator
from app.db.author_database import AuthorDatabase
from app.schemas.extraction import ExtractionOutput
from app.schemas.factcheck import FactCheckReport
from app.utils.logger import logger

# --- Setup FastAPI ---
app = FastAPI(title="AI Structured Extraction Tool API")
service = ExtractionService()
author_db = AuthorDatabase()
factcheck_service = FactCheckCoordinator(author_db=author_db)

class ExtractRequest(BaseModel):
    text: str

class FactCheckRequest(BaseModel):
    input_data: str

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

@app.post("/fact-check", response_model=FactCheckReport)
async def fact_check_api(request: FactCheckRequest):
    """
    Perform full fact-check via API.
    """
    logger.info(f"Received API fact-check request for: {request.input_data[:50]}...")
    try:
        result = await factcheck_service.fact_check(request.input_data)
        return result
    except Exception as e:
        logger.error(f"API fact-check failed: {str(e)}")
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

from rich.console import Console
from rich.status import Status
from rich.syntax import Syntax

console = Console()

@cli.command(name="fact-check")
def fact_check_cli(input_data: str = typer.Argument(..., help="URL or text to fact-check")):
    """
    Perform full fact-check via CLI with progress display.
    """
    logger.info(f"Starting CLI fact-check for: {input_data[:50]}...")

    async def run_check():
        with Status("[bold blue]🚀 啟動查核引擎...", console=console, spinner="dots") as status:
            def update_progress(msg: str):
                status.update(f"[bold blue]{msg}")
            
            try:
                result = await factcheck_service.fact_check(input_data, progress_callback=update_progress)
                console.print("\n[bold green]✅ 查核完成！[/bold green]")
                
                # Use syntax highlighting for the JSON output
                json_str = result.model_dump_json(indent=2)
                syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
                console.print(syntax)
            except Exception as e:
                logger.error(f"CLI fact-check failed: {str(e)}")
                console.print(f"\n[bold red]❌ 錯誤: {str(e)}[/bold red]")

    asyncio.run(run_check())


@cli.command()
def serve(port: int = 8000, host: str = "0.0.0.0"):
    """
    Run the API server.
    """
    logger.info(f"Starting API server on {host}:{port}")
    uvicorn.run(app, host=host, port=port)

if __name__ == "__main__":
    cli()
