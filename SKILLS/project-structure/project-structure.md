---
name: project-structure
description: >
  Designs and recommends scalable, maintainable project folder structures adapted to the
  specific type of project the user is building. Use this skill WHENEVER the user asks about:
  how to organize a project, what folder structure to use, how to structure their codebase,
  project architecture layout, directory organization, how to make a project scalable or
  maintainable, or any request like "how should I structure my X project". Also trigger when
  the user shares code or describes a project and wants to know the best way to organize it.
  Covers all project types: AI/LLM/RAG apps, APIs, CLIs, web apps, ML pipelines, monorepos,
  data science projects, and more. Always produces a concrete folder tree with file-level
  explanations and the reasoning behind each architectural decision.
---

# Project Structure Skill

Produces opinionated, concrete folder structures adapted to the project type, stack, and
team scale — with rationale for every decision so the user understands *why*, not just *what*.

---

## Workflow

### Step 1 — Gather context

Before producing any structure, identify these signals from the conversation. If the user
already described their project, extract as much as possible before asking. Only ask for
what's genuinely missing.

**Required signals:**
- **Project type** — what is this? (LLM/RAG/Agent app, REST API, CLI tool, web app,
  ML training pipeline, data pipeline, monorepo, library/SDK, data science notebook project)
- **Primary language + key frameworks** — Python/FastAPI, TypeScript/Node, Go, etc.
- **Scale target** — solo/small team (clean but lean), team project (CI/CD, testing),
  production/enterprise (full separation of concerns, MLOps, monorepo)

**Useful but optional:**
- Deployment target (Docker, serverless, k8s, local only)
- Whether it needs a frontend
- External integrations (vector DB, message queue, object storage)
- Whether it's a new project or a refactor of something existing

If the user says "make it scalable and maintainable", assume **team project** scale unless
told otherwise.

---

### Step 2 — Select the base template

Pick the closest template below, then adapt it. Never output a generic tree — always
customize file names, layer names, and annotations to the user's actual stack.

---

## Templates

### Template A — LLM / RAG / AI Agent (Python)

Best for: apps built around LLM calls, retrieval-augmented generation, agent loops,
tool-using assistants, chatbots with memory.

**Core principle**: Keep framework code at the edges, pure logic in the center.
The `core/` layer must have zero framework dependencies — no FastAPI, no LangChain,
no DB ORM. This makes it testable in isolation and swappable without rewrites.

```
my-ai-project/
├── .env                        # secrets — never commit
├── .env.example                # template with dummy values — always commit
├── pyproject.toml              # or requirements.txt + requirements-dev.txt
├── Makefile                    # shortcuts: make dev, make test, make ingest
├── README.md
│
├── src/
│   ├── config/
│   │   ├── settings.py         # pydantic BaseSettings — loads from .env automatically
│   │   ├── prompts.py          # all prompt templates as string constants or dataclasses
│   │   └── logging.py          # structured logging setup (loguru or structlog)
│   │
│   ├── core/                   # pure domain logic — NO framework imports here
│   │   ├── llm.py              # LLM client wrapper — swap provider in one file
│   │   ├── embeddings.py       # embedding model abstraction
│   │   ├── retriever.py        # vector store search and ranking logic
│   │   ├── agent.py            # agent loop, tool registry, orchestration
│   │   ├── chains.py           # RAG pipeline / chain composition
│   │   ├── memory.py           # conversation memory / context window management
│   │   └── tools/              # agent tools, one file per tool
│   │       ├── web_search.py
│   │       └── calculator.py
│   │
│   ├── data/                   # everything that touches raw data
│   │   ├── loaders.py          # PDF, web, DB, S3 connectors
│   │   ├── chunkers.py         # text splitting strategies (recursive, semantic, etc.)
│   │   ├── parsers.py          # format-specific parsers (markdown, HTML, docx)
│   │   └── schemas.py          # pydantic models for all data I/O
│   │
│   ├── api/                    # HTTP layer only — thin, delegates to core/
│   │   ├── app.py              # FastAPI app factory
│   │   ├── routes/
│   │   │   ├── chat.py         # /chat endpoint
│   │   │   └── health.py       # /health, /ready
│   │   └── deps.py             # dependency injection, auth, rate limiting
│   │
│   └── utils/                  # stateless helpers
│       ├── token_utils.py      # count tokens, truncate context windows
│       ├── retry.py            # exponential backoff decorator
│       └── cache.py            # simple in-memory or Redis cache wrapper
│
├── tests/                      # mirrors src/ structure exactly
│   ├── conftest.py             # shared fixtures: mock LLM, temp vector store
│   ├── unit/
│   │   ├── test_llm.py
│   │   ├── test_retriever.py
│   │   └── test_chunkers.py
│   └── integration/
│       └── test_pipeline.py    # end-to-end RAG flow with real deps
│
├── scripts/                    # operational one-offs, never imported by app code
│   ├── ingest.py               # index documents into vector store
│   └── eval.py                 # run evals / benchmarks against golden set
│
└── infra/                      # optional: only if deploying
    ├── Dockerfile
    ├── docker-compose.yml
    └── k8s/                    # or terraform/, or deploy.sh
```

**Dependency rule**: `api` → `core` → `config`. Nothing points outward. `utils` is
imported by anyone. `scripts` import from `core` and `data` but are never imported themselves.

---

### Template B — REST API / Backend Service (Python FastAPI or Node/Express)

Best for: standalone microservices, backend APIs, internal tools with an HTTP interface.
Not AI-specific — general-purpose API structure.

**Core principle**: Layered architecture — router → service → repository → model.
Each layer has one job and only calls the layer below it.

```
my-api/
├── .env  /  .env.example
├── pyproject.toml  /  package.json
├── Makefile  /  justfile
├── README.md
│
├── src/
│   ├── config/
│   │   ├── settings.py         # env vars via pydantic BaseSettings
│   │   └── database.py         # DB connection setup (SQLAlchemy / Prisma)
│   │
│   ├── api/
│   │   ├── app.py              # app factory, middleware registration
│   │   ├── routes/             # one file per resource
│   │   │   ├── users.py
│   │   │   └── items.py
│   │   └── middleware/
│   │       ├── auth.py
│   │       └── rate_limit.py
│   │
│   ├── services/               # business logic — no HTTP or DB knowledge
│   │   ├── user_service.py
│   │   └── item_service.py
│   │
│   ├── repositories/           # all DB queries live here
│   │   ├── user_repo.py
│   │   └── item_repo.py
│   │
│   ├── models/                 # DB models (SQLAlchemy ORM / Mongoose / Drizzle)
│   │   ├── user.py
│   │   └── item.py
│   │
│   └── schemas/                # request/response validation (pydantic / zod)
│       ├── user.py
│       └── item.py
│
├── tests/
│   ├── conftest.py             # test DB, auth fixtures
│   ├── unit/
│   └── integration/
│
└── infra/
    └── Dockerfile
```

---

### Template C — ML Training Pipeline (Python, PyTorch / TF)

Best for: model training, fine-tuning, experiment tracking. Reproducibility is the
primary design goal.

**Core principle**: Every experiment must be reproducible from a config file alone.
No magic globals, no hardcoded paths.

```
my-ml-project/
├── configs/                    # one YAML/TOML per experiment
│   ├── base.yaml               # shared defaults
│   └── experiments/
│       └── exp_001.yaml        # overrides base — logged with each run
│
├── data/
│   ├── raw/                    # original, immutable data — never modify
│   ├── processed/              # output of preprocessing scripts
│   └── external/               # third-party datasets
│
├── src/
│   ├── data/
│   │   ├── dataset.py          # torch Dataset / tf.data pipeline
│   │   └── transforms.py       # augmentations, normalization
│   │
│   ├── models/
│   │   ├── base.py             # abstract base model
│   │   └── my_model.py         # concrete architecture
│   │
│   ├── training/
│   │   ├── trainer.py          # training loop
│   │   ├── losses.py
│   │   └── metrics.py
│   │
│   └── utils/
│       ├── seed.py             # fix random seeds for reproducibility
│       └── checkpoints.py
│
├── notebooks/                  # exploration only — not production code
│   └── 01_eda.ipynb
│
├── outputs/                    # gitignored: checkpoints, logs, predictions
│   ├── checkpoints/
│   └── logs/
│
├── scripts/
│   ├── train.py                # entry point: python scripts/train.py --config configs/exp_001.yaml
│   ├── evaluate.py
│   └── export.py               # export to ONNX / TorchScript
│
└── tests/
    └── test_model_shapes.py    # sanity checks: input/output tensor shapes
```

---

### Template D — CLI Tool (Python)

Best for: developer tools, automation scripts, internal utilities distributed as a package.

```
my-cli/
├── pyproject.toml              # [project.scripts] entry point defined here
├── README.md
│
├── src/
│   └── my_cli/
│       ├── __init__.py
│       ├── cli.py              # click / typer command definitions — thin
│       ├── core/               # actual logic, importable as a library too
│       │   └── processor.py
│       ├── config.py           # app configuration
│       └── utils.py
│
└── tests/
    └── test_cli.py             # use click's CliRunner or typer's testing utilities
```

---

### Template E — Data Science / Notebook Project

Best for: exploratory analysis, reporting, Kaggle-style projects. Notebooks are
first-class citizens but kept organized.

```
my-ds-project/
├── data/
│   ├── raw/                    # original data — read only
│   ├── interim/                # intermediate transformations
│   └── final/                  # clean datasets ready for modeling
│
├── notebooks/
│   ├── 01_eda.ipynb            # numbered by workflow stage
│   ├── 02_feature_engineering.ipynb
│   └── 03_modeling.ipynb
│
├── src/
│   └── my_project/             # reusable code extracted from notebooks
│       ├── features.py
│       ├── models.py
│       └── visualization.py
│
├── reports/
│   └── figures/                # exported charts and tables
│
└── environment.yml             # conda env for full reproducibility
```

---

## Step 3 — Customize and annotate

After selecting the template, adapt it to the user's actual stack:

- **Replace generic names** with real ones from the project description.
  (e.g. if the user says "it's a Slack bot", rename `api/routes/chat.py` → `api/routes/slack.py`)
- **Add stack-specific files**: if using Alembic, add `alembic/`. If using LangChain,
  note where it belongs (`core/chains.py`). If Docker Compose, add `docker-compose.yml`.
- **Remove layers that don't apply**: a solo script project doesn't need `infra/`.
  A CLI doesn't need `api/`. Don't add bloat for its own sake.
- **Annotate every non-obvious file** with a one-line comment explaining its job.
  Files like `conftest.py` or `deps.py` confuse junior developers — explain them.

---

## Step 4 — Explain the architecture

After the folder tree, always include a short section titled **"Why this structure"**
covering:

1. **The dependency rule** for this project type — what imports what, and what's forbidden
2. **Where to add X** — preempt the most common "where does this go?" questions:
   - "Where do I add a new LLM provider?" → `core/llm.py`
   - "Where do I add a new endpoint?" → `api/routes/`
   - "Where do I put environment variables?" → `config/settings.py`
3. **What to do on day 1** — the 3-5 files to create first, in order
4. **Common anti-patterns to avoid** — the 2-3 things that kill maintainability
   in this type of project (e.g. fat routes, hardcoded prompts, imports between
   peer layers)

---

## Step 5 — Offer concrete next steps

End with actionable follow-ups the user can ask for:

- "Generate the boilerplate for `core/llm.py`"
- "Show me what `config/settings.py` should look like with pydantic"
- "Create a `Makefile` with the most useful commands for this project"
- "Generate the `pyproject.toml` / `package.json` for this stack"
- "Show me how to wire up the dependency injection in `api/deps.py`"

Offer 2-3 of the most relevant ones based on the project type.

---

## Output format

1. A folder tree using ASCII art (`├──`, `└──`, `│`) with inline comments (`# ...`)
2. A **"Why this structure"** section in prose (not bullets — readable paragraphs)
3. **"Where does X go?"** — 4-6 concrete Q&A pairs for the most common additions
4. **"Anti-patterns to avoid"** — 2-3 short, specific warnings
5. **"Next steps"** — 2-3 follow-up prompts the user can ask

Keep the tree as the centrepiece. The prose sections should be concise and scannable.
Never truncate the tree — output it in full.

---

## Key principles (apply to all templates)

**Separation of concerns**: Each folder has one job. If you can't describe a folder's
purpose in 5 words, it's doing too much.

**Dependencies point inward**: Business logic never imports from HTTP/framework layers.
This is non-negotiable for testability.

**Configuration at the boundary**: All env vars, secrets, and tunable parameters live
in `config/`. Code never reads `os.environ` directly — it always goes through the
settings object.

**Tests mirror source**: `tests/unit/test_llm.py` tests `src/core/llm.py`. This
1:1 mapping makes it trivial to find and maintain tests.

**Scripts are not application code**: Anything that's a one-off operation (ingest,
eval, seed, migrate) goes in `scripts/`. It can import from `src/` but is never
imported by `src/`.

**Start lean, scale by splitting**: Don't add layers preemptively. A solo project
starts with `core/` + `config/` + `tests/`. Add `api/`, `data/`, `infra/` only
when the complexity justifies it.