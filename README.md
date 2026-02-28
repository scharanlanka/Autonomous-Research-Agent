# Autonomous Research Agent (ARA)

Autonomous Research Agent (ARA) is a Streamlit-based multi-agent research workflow built with LangGraph. It takes a research prompt, plans the work, searches the web and arXiv, fetches page content, drafts a cited report, critiques and improves that draft, then stores a compact memory of the result in ChromaDB for future runs.

## Features

- LangGraph orchestration with a fixed agent pipeline:
  - Planner
  - Memory retrieval
  - Researcher
  - Summarizer
  - Critic
  - Memory persistence
- Streamlit interface for submitting research tasks and viewing results
- Tavily-powered web search for current web sources
- arXiv search for academic papers
- Web page fetching and text extraction with BeautifulSoup + lxml
- Structured markdown report generation with inline citations
- Critique and revision pass to improve report quality
- PDF export using ReportLab
- Markdown export from the UI
- ChromaDB-backed long-term memory using Azure embeddings
- Debug log view for tracing each step of a run
- Configurable limits for search result counts and page extraction length

## Workflow

1. The planner turns the query into a short research plan.
2. The memory layer retrieves similar prior research notes from ChromaDB.
3. The researcher collects sources from Tavily and arXiv, then fetches web page text.
4. The summarizer writes a markdown research report with citations.
5. The critic reviews the draft and returns an improved final report.
6. A condensed version of the completed report is stored back into memory.

## Tech Stack

- Python 3.13+
- Streamlit
- LangGraph
- Pydantic
- Tavily
- arXiv Python client
- ChromaDB
- Azure-hosted chat model endpoint
- Azure-hosted embedding endpoint
- ReportLab

## Project Structure

```text
.
├── app.py                  # Streamlit UI entrypoint
├── main.py                 # Minimal CLI placeholder
├── ara/
│   ├── graph.py            # LangGraph workflow definition
│   ├── config.py           # Environment variable loading
│   ├── memory.py           # ChromaDB memory store
│   ├── azure_llm.py        # Azure chat model wrapper
│   ├── azure_embeddings.py # Azure embeddings wrapper
│   ├── tavily_search.py    # Tavily search integration
│   ├── agents/
│   │   ├── planner.py
│   │   ├── researcher.py
│   │   ├── summarizer.py
│   │   ├── critic.py
│   │   └── reporter.py
│   └── tools/
│       ├── arxiv_tool.py
│       └── web_fetch.py
├── pyproject.toml
├── requirements.txt
└── Architecture.md
```

## Prerequisites

Before running ARA, you need:

- Python 3.13 or newer
- A Tavily API key
- An Azure chat/completions-compatible endpoint
- An Azure embeddings-compatible endpoint

## Environment Variables

Create a `.env` file in the project root with the following values:

```env
AZURE_LLM_ENDPOINT=
AZURE_LLM_API_KEY=
AZURE_LLM_DEPLOYMENT_NAME=grok-3-mini

AZURE_EMBEDDING_ENDPOINT=
AZURE_EMBEDDING_API_KEY=
AZURE_EMBEDDING_DEPLOYMENT_NAME=text-embedding-3-large

TAVILY_API_KEY=

CHROMA_PERSIST_DIR=./chroma_db
CHROMA_COLLECTION=ara_memory

DDG_MAX_RESULTS=8
ARXIV_MAX_RESULTS=5
FETCH_MAX_CHARS=12000
TAVILY_MAX_RESULTS=8
```

Notes:

- `AZURE_LLM_ENDPOINT` should point to the chat/completions endpoint your deployment exposes.
- `AZURE_EMBEDDING_ENDPOINT` should point to the embeddings endpoint your deployment exposes.
- `CHROMA_PERSIST_DIR` controls where local vector memory is stored on disk.
- `DDG_MAX_RESULTS` exists in config but the current research pipeline uses Tavily for web search, not DuckDuckGo.

## Installation

### Option 1: `uv` (recommended)

```bash
uv sync
```

If you want to run commands inside the managed environment:

```bash
uv run streamlit run app.py
```

### Option 2: `pip`

Create and activate a virtual environment, then install dependencies:

```bash
python3.13 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install tavily-python
```

`requirements.txt` does not currently include `tavily-python`, so install it explicitly if you are using the `pip` path.

## Running the App

Start the Streamlit interface:

```bash
streamlit run app.py
```

If you installed with `uv`, use:

```bash
uv run streamlit run app.py
```

Then open the local Streamlit URL shown in the terminal.

## Using ARA

1. Enter a research prompt in the `Research Task` box.
2. Click `Run Research`.
3. Review the generated plan, logs, and final report.
4. Download the report as Markdown or PDF.

Example prompt:

```text
Research the impact of AI on software engineering jobs from 2023 to 2026. Provide key findings with sources, major risks, and practical recommendations.
```

## Output

Each run can produce:

- A generated research plan
- Retrieved source list from web search and arXiv
- Debug logs for the orchestration flow
- A final markdown report with references
- Downloadable `.md` and `.pdf` report exports
- A stored memory note for future similarity retrieval

## Current Limitations

- The web search path currently uses Tavily only, even though DuckDuckGo-related config exists.
- arXiv results include metadata and summaries, but full paper parsing is not implemented.
- `main.py` is only a placeholder and is not the primary application entrypoint.
- The README setup assumes you already have valid provider endpoints and credentials.

## Troubleshooting

- Missing environment variables:
  - The app raises a runtime error from `ara/config.py` when required values are absent.
- Empty or weak reports:
  - Check the debug logs in the sidebar and verify your LLM endpoint, deployment names, and Tavily key.
- Chroma issues:
  - Ensure `CHROMA_PERSIST_DIR` is writable and consistent across runs.
- Dependency mismatch:
  - If using `pip`, make sure `tavily-python` is installed in addition to `requirements.txt`.

## Architecture

High-level design notes are available in [Architecture.md](/Users/saicharanlanka/Education/Autonomous%20Research%20Agent/Architecture.md).
