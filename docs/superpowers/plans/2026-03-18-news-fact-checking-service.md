# News Fact-Checking Service Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a domain-aware, multi-agent asynchronous news verification system that accepts URLs or raw text.

**Architecture:** An Orchestrator-Worker pattern using `asyncio`. It decomposes articles into claims, gathers evidence in parallel (Search + Author history), performs logical reasoning, and outputs a reliability score.

**Tech Stack:** Python, Pydantic, HTTPX, BeautifulSoup4 (for content extraction), OpenAI/Gemini (via instructor), Pytest.

---

### Task 1: Data Models and Schema

**Files:**
- Create: `app/schemas/factcheck.py`

- [ ] **Step 1: Define the fact-checking data structures.**
  Implement `Claim`, `Evidence`, `AuthorProfile`, and `FactCheckReport` as Pydantic models.
  ```python
  from pydantic import BaseModel, Field
  from typing import List, Optional, Dict, Any

  class Claim(BaseModel):
      id: str
      text: str
      category: str = Field(..., description="e.g., factual, statistical, temporal")
      context: Optional[str] = None

  class Evidence(BaseModel):
      claim_id: str
      source_url: str
      title: str
      content: str
      credibility_score: float = 1.0

  class AuthorProfile(BaseModel):
      author_name: str
      historical_score: int = 50
      total_articles: int = 0
      reliability_assessment: str = "Unknown"
      trust_level: str = "Neutral"

  class FactCheckReport(BaseModel):
      article_title: Optional[str] = None
      article_summary: str
      claims_verified: List[Dict[str, Any]]
      author_background: AuthorProfile
      total_reliability_score: int
      final_verdict: str
  ```

- [ ] **Step 2: Commit schemas.**
  ```bash
  git add app/schemas/factcheck.py
  git commit -m "feat: define fact-check data models"
  ```

### Task 2: Content Extraction Layer

**Files:**
- Create: `app/utils/content_extractor.py`
- Test: `tests/test_content_extractor.py`

- [ ] **Step 1: Implement `ContentExtractor`.**
  Handle URL fetching vs. raw text. Use `httpx` for requests and `BeautifulSoup` for basic cleaning.
  ```python
  import httpx
  from bs4 import BeautifulSoup

  class ContentExtractor:
      async def extract(self, input_data: str) -> Dict[str, str]:
          if input_data.startswith("http"):
              async with httpx.AsyncClient() as client:
                  resp = await client.get(input_data, follow_redirects=True)
                  soup = BeautifulSoup(resp.text, 'html.parser')
                  # Simple cleaning: remove script/style
                  for s in soup(['script', 'style']): s.decompose()
                  text = soup.get_text(separator=' ', strip=True)
                  title = soup.title.string if soup.title else "Untitled"
                  return {"text": text, "title": title, "type": "url"}
          return {"text": input_data, "title": "Raw Text", "type": "text"}
  ```

- [ ] **Step 2: Commit utility.**
  ```bash
  git add app/utils/content_extractor.py
  git commit -m "feat: implement ContentExtractor for URL and text support"
  ```

### Task 3: Decomposer Agent

**Files:**
- Create: `app/agents/decomposer.py`
- Test: `tests/test_decomposer.py`

- [ ] **Step 1: Implement `DecomposerAgent`.**
  Use LLM to split text into verifiable claims.
  ```python
  from app.schemas.factcheck import Claim
  # Inherit or use LLMExtractor logic to return List[Claim]
  ```

- [ ] **Step 2: Commit agent.**
  ```bash
  git add app/agents/decomposer.py
  git commit -m "feat: implement DecomposerAgent for claim extraction"
  ```

### Task 4: Evidence & Author Agents (Parallel Workers)

**Files:**
- Create: `app/agents/search_agent.py`
- Create: `app/agents/author_agent.py`
- Create: `app/db/author_database.py`

- [ ] **Step 1: Implement `SearchAgent` with Mock/Tavily interface.**
  Allow searching for evidence for a given `Claim`.

- [ ] **Step 2: Implement `AuthorAgent` and `AuthorDatabase` (Mock).**
  Create a simple JSON-based mock database for author history.

- [ ] **Step 3: Commit parallel workers.**
  ```bash
  git add app/agents/search_agent.py app/agents/author_agent.py app/db/author_database.py
  git commit -m "feat: implement search and author profile agents"
  ```

### Task 5: Reasoning & Scoring Agent

**Files:**
- Create: `app/agents/reasoning_agent.py`

- [ ] **Step 1: Implement `ReasoningAgent`.**
  Logic: Compare `Claim` + `Evidence` -> `Verdict`.
  Calculate final score based on claim verdicts and author background.

- [ ] **Step 2: Commit reasoning agent.**
  ```bash
  git add app/agents/reasoning_agent.py
  git commit -m "feat: implement reasoning and scoring logic"
  ```

### Task 6: FactCheck Coordinator (Orchestration)

**Files:**
- Create: `app/services/factcheck_service.py`
- Modify: `app/main.py`

- [ ] **Step 1: Implement `FactCheckCoordinator`.**
  Use `asyncio.gather` to run Search and Author tasks in parallel.
  Chain: Extract -> Decompose -> (Search/Author) -> Reasoning -> Final Report.

- [ ] **Step 2: Update API and CLI.**
  Add `/fact-check` endpoint and `fact-check` CLI command.

- [ ] **Step 3: Commit orchestrator.**
  ```bash
  git add app/services/factcheck_service.py app/main.py
  git commit -m "feat: orchestrate full fact-check pipeline"
  ```

### Task 7: Integration Testing

- [ ] **Step 1: Create `tests/test_factcheck_integration.py`.**
  Test with both real URLs and raw text.
- [ ] **Step 2: Verify full pipeline.**
