                        ┌──────────────────────────────┐
                        │           USER               │
                        │  Browser / Client           │
                        └──────────────┬──────────────┘
                                       │
                                       │ HTTPS
                                       ▼
                        ┌──────────────────────────────┐
                        │        FRONTEND              │
                        │        Next.js App          │
                        │                             │
                        │  - Input UI                │
                        │  - Progress visualization  │
                        │  - Report viewer           │
                        └──────────────┬──────────────┘
                                       │
                                       │ REST API
                                       ▼
                        ┌──────────────────────────────┐
                        │        BACKEND API           │
                        │        FastAPI Server       │
                        │                             │
                        │  - Request validation       │
                        │  - Task creation            │
                        │  - Task management          │
                        │  - Response delivery        │
                        └──────────────┬──────────────┘
                                       │
                                       │ Calls
                                       ▼
                ┌────────────────────────────────────────────┐
                │          AGENT ORCHESTRATION LAYER        │
                │              (LangGraph)                  │
                │                                           │
                │  ┌────────────┐     ┌────────────┐       │
                │  │ Planner    │────▶│ Researcher │       │
                │  │ Agent      │     │ Agent      │       │
                │  └────────────┘     └─────┬──────┘       │
                │                            │              │
                │                     ┌──────▼──────┐       │
                │                     │ Summarizer  │       │
                │                     │ Agent       │       │
                │                     └──────┬──────┘       │
                │                            │              │
                │                     ┌──────▼──────┐       │
                │                     │ Critic      │       │
                │                     │ Agent       │       │
                │                     └─────────────┘       │
                └──────────────┬───────────────────────────┘
                               │
                               │ Uses tools
                               ▼

        ┌─────────────────────────────────────────────────────────┐
        │                    TOOL LAYER                          │
        │                                                        │
        │  ┌──────────────┐   ┌──────────────┐   ┌────────────┐ │
        │  │ Web Search   │   │ arXiv Tool   │   │ Wikipedia  │ │
        │  │ API          │   │              │   │ Tool       │ │
        │  └──────┬───────┘   └──────┬───────┘   └──────┬─────┘ │
        │         │                  │                  │        │
        │         └──────────────────┴──────────────────┘        │
        │                        │                               │
        │                        ▼                               │
        │              ┌──────────────────┐                     │
        │              │  Embedding Model │                     │
        │              │  OpenAI Embeds   │                     │
        │              └────────┬─────────┘                     │
        │                       │                               │
        │                       ▼                               │
        │              ┌──────────────────┐                     │
        │              │ Vector Database  │                     │
        │              │  ChromaDB        │                     │
        │              └──────────────────┘                     │
        └─────────────────────────────────────────────────────────┘


                               │
                               ▼

                     ┌──────────────────────┐
                     │     LLM PROVIDER    │
                     │     OpenAI API      │
                     │                     │
                     │  - Reasoning       │
                     │  - Planning        │
                     │  - Summarization   │
                     └──────────────────────┘



                               │
                               ▼

                     ┌──────────────────────┐
                     │   STORAGE LAYER     │
                     │                     │
                     │ - Research Tasks   │
                     │ - Logs             │
                     │ - Reports          │
                     └──────────────────────┘