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
from rich.panel import Panel
from rich.table import Table
from rich.status import Status
from rich.syntax import Syntax

console = Console()

@cli.command(name="fact-check")
def fact_check_cli(input_data: str = typer.Argument(..., help="URL or text to fact-check")):
    """
    Perform full fact-check via CLI with detailed stage results.
    """
    logger.info(f"Starting CLI fact-check for: {input_data[:50]}...")

    async def run_check():
        with Status("[bold blue]🚀 啟動查核引擎...", console=console, spinner="dots") as status:
            def update_progress(msg: str, data=None):
                status.update(f"[bold blue]{msg}")
                if data:
                    # Temporarily stop status to print intermediate result
                    status.stop()
                    
                    if "text" in str(data) and "title" in str(data): # Extraction Result
                        console.print(Panel(
                            f"[bold]標題:[/bold] {data['title']}\n"
                            f"[bold]作者:[/bold] {data['author']}\n"
                            f"[bold]日期:[/bold] {data['date']}\n"
                            f"[bold]內容摘要:[/bold] {data['text'][:200]}...",
                            title="📄 階段 1: 內容提取成果", border_style="cyan"
                        ))
                    elif isinstance(data, list) and len(data) > 0 and hasattr(data[0], 'text'): # Claims
                        table = Table(title="🧠 階段 2: 拆解聲明列表", show_header=True, header_style="bold magenta")
                        table.add_column("ID", style="dim")
                        table.add_column("聲明內容")
                        table.add_column("類型")
                        for claim in data:
                            table.add_row(claim.id, claim.text, claim.category)
                        console.print(table)
                    elif isinstance(data, dict) and "evidences" in data: # Evidences & Author
                        table = Table(title="🌐 階段 3: 蒐證與作者分析", show_header=True, header_style="bold yellow")
                        table.add_column("來源", style="blue")
                        table.add_column("證據摘要")
                        for ev in data["evidences"][:5]: # Show top 5
                            table.add_row(ev.source_url, ev.content[:100] + "...")
                        console.print(table)
                        
                        auth = data["author"]
                        console.print(Panel(
                            f"[bold]作者:[/bold] {auth.author_name}\n"
                            f"[bold]歷史評分:[/bold] {auth.historical_score}\n"
                            f"[bold]評語:[/bold] {auth.reliability_assessment}",
                            title="👤 階段 3: 作者背景分析", border_style="yellow"
                        ))
                    
                    status.start()
            
            try:
                result = await factcheck_service.fact_check(input_data, progress_callback=update_progress)
                console.print("\n[bold green]🏁 查核流程圓滿完成！[/bold green]")
                
                # Final report syntax highlighting
                json_str = result.model_dump_json(indent=2)
                syntax = Syntax(json_str, "json", theme="monokai", line_numbers=True)
                console.print(Panel(syntax, title="📊 最終查核報告 (Fact-Check Report)", border_style="green"))
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
