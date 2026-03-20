# News Fact-Checking Service Design Spec

## Overview
A domain-aware multi-agent system designed to verify news articles. It breaks down articles into verifiable claims, gathers evidence through search, cross-references with author history, and provides a final credibility score based on logical reasoning.

## Architecture: Multi-Agent Asynchronous Pipeline
The system uses an **Orchestrator-Worker** pattern. A central `FactCheckCoordinator` manages the lifecycle of a fact-check request, dispatching tasks to specialized agents.

### Core Workflow
1.  **Decomposition**: The article is analyzed to extract individual **Claims**.
2.  **Parallel Evidence Gathering**:
    *   **SearchAgent**: For each claim, parallel search tasks are launched to find supporting or refuting evidence.
    *   **AuthorAgent**: Simultaneously, the **AuthorDatabase** is queried for the author's history and credibility profile.
3.  **Logical Reasoning**: The **InferenceAgent** compares evidence against claims to find contradictions or support.
4.  **Scoring & Synthesis**: The **ScoringAgent** assigns a reliability score (0-100), and a **SummaryAgent** compiles the final report.

## Modules & Components

### 1. Decomposer Agent (`app/agents/decomposer.py`)
*   **Role**: Analyze text and extract verifiable claims.
*   **Input**: Raw article text.
*   **Output**: List of `Claim` objects (statement, context, priority).

### 2. Search/Evidence Agent (`app/agents/search_agent.py`)
*   **Role**: Search external or internal sources for evidence.
*   **Design**: Extensible interface to support multiple search providers (e.g., Tavily, Google, Mock).
*   **Output**: List of `Evidence` objects (source, content, relevance).

### 3. Inference & Scoring Agent (`app/agents/reasoning_agent.py`)
*   **Role**: Fact-check claims against evidence.
*   **Logic**: Performs cross-claim consistency checks and evidence-to-claim alignment.
*   **Output**: `ReasoningResult` (Verdict: Supported/Refuted/Uncertain, Reasoning Details).

### 4. Author History Agent (`app/agents/author_agent.py`)
*   **Role**: Assess author credibility.
*   **Input**: Author name/ID.
*   **Interface**: `AuthorDatabase` abstraction.
*   **Output**: `AuthorProfile` (Trust score, historical accuracy, bias indicators).

### 5. FactCheck Coordinator (`app/services/factcheck_service.py`)
*   **Role**: Orchestration using `asyncio` for high performance.
*   **Responsibility**: Managing the state of the check and handling agent communication.

## Data Model (`app/schemas/factcheck.py`)
```python
class Claim(BaseModel):
    id: str
    text: str
    category: str  # e.g., factual, statistical, temporal

class Evidence(BaseModel):
    claim_id: str
    source_url: str
    content: str
    credibility_score: float

class AuthorProfile(BaseModel):
    author_name: str
    historical_score: int  # 0-100
    total_articles: int
    reliability_assessment: str

class FactCheckReport(BaseModel):
    article_summary: str
    claims_verified: List[dict]  # Claim text -> Verdict & Reasoning
    author_background: AuthorProfile
    total_reliability_score: int
    final_verdict: str
```

## Database Abstraction (`app/db/author_database.py`)
A generic `BaseAuthorDB` class will be implemented to allow switching between a simple JSON file and a production-grade database.

## Scalability & Extensibility
*   **Provider Pattern**: New search engines or LLMs can be added by implementing new agent subclasses.
*   **Asynchronous Processing**: Claims are processed in parallel to minimize latency.
*   **Failure Protection**: If search results are empty, the system provides a "reasoning-only" check based on internal knowledge with a disclaimer.
