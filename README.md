# Armenian Voice AI Bank Agent

A real-time Armenian voice AI support agent for bank-related customer queries, built using self-hosted LiveKit and a retrieval-based architecture grounded in official bank website data.

## Objective

The system enables users to interact via voice in Armenian and receive accurate answers strictly limited to:

* Credits
* Deposits
* Branch Locations

All responses are generated using scraped data from Armenian bank websites, ensuring grounded and reliable answers.

## Architecture Overview

```text
Browser (localhost:3000)
        |
        v
LiveKit (localhost:7880)
        |
        v
Agent Worker (Docker)
        |
        v
Knowledge DB (data/knowledge.db)
        |
        v
OpenAI API
```

## Architecture and Design Decisions

### LiveKit (Open Source)

LiveKit is used for real-time voice streaming. It is self-hosted to meet the assignment requirement and provides low-latency communication between client and agent.

### Retrieval-Based Approach

Instead of passing all data into the prompt, the system uses embeddings and semantic search:

* improves scalability
* ensures responses are grounded in source data
* prevents hallucination

### OpenAI Models

OpenAI models are used for:

* natural language understanding and generation
* multilingual capability, including Armenian
* reliable real-time performance

### SQLite

SQLite is used as a lightweight local database to store processed bank data. It is sufficient for this use case and simplifies deployment.

### Docker

Docker Compose is used to orchestrate all services, ensuring reproducibility and consistent environment setup.

## Knowledge Base Pipeline

* Bank websites are defined in `seeds/banks.yaml`
* Pages are scraped and converted into clean text
* Text is split into chunks
* Embeddings are generated
* Data is stored in `data/knowledge.db`
* At runtime, relevant chunks are retrieved and passed to the LLM

## Guardrails

The agent is strictly limited to the following topics:

* Credits
* Deposits
* Branch Locations

The system enforces this by:

* retrieving only relevant chunks
* restricting response scope
* refusing unrelated queries

Example behavior:

If a user asks an unrelated question, the agent responds with a refusal indicating it only supports bank-related topics.

## Armenian Language Support

* Source data is in Armenian
* The LLM processes Armenian input and generates Armenian responses
* The voice pipeline supports Armenian speech interaction

## Setup Instructions

### 1. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -e .
```

### 3. Configure environment

Create `.env` file:

```env
OPENAI_API_KEY=your_key_here
LIVEKIT_URL=ws://localhost:7880
```

Do not use placeholder values.

### 4. Build knowledge base

```bash
python scripts/scrape_and_ingest.py
```

Verify:

```bash
ls -la data
```

Expected:

```text
knowledge.db
```

### 5. Run Docker stack

```bash
docker compose -f deploy/docker-compose.yml down
docker compose -f deploy/docker-compose.yml up -d --build
```

### 6. Verify services

```bash
docker ps -a
```

All services should be running:

* agent-worker
* token-server
* livekit
* redis
* client

### 7. Open application

`http://localhost:3000`

Click "Join" and test voice interaction.

## Critical Concepts

### LiveKit URLs

| Context | URL |
| --- | --- |
| Browser | `ws://localhost:7880` |
| Docker | `ws://livekit:7880` |

These must not be mixed.

### Knowledge Base Requirement

The system requires:

`data/knowledge.db`

If missing, the agent will fail to start.

## API Key Note (Important)

This project requires an OpenAI API key.

The API key used during development may not work due to quota or billing limitations.

To test the project:

* Add your own API key to `.env`:
  `OPENAI_API_KEY=your_key_here`
* Rebuild the system:

```bash
docker compose down
docker compose up -d --build
```

Reviewers are expected to use their own API keys when evaluating the project.

## Seed Data

Defined in:

`seeds/banks.yaml`

Each bank includes:

* credits
* deposits
* branch_locations

The system is designed to scale by adding more banks to this file.

## Troubleshooting

### LiveKit connection error

```text
Cannot connect to localhost:7880
```

Fix:

`LIVEKIT_URL: ws://livekit:7880`

### Missing database

```text
sqlite3.OperationalError: unable to open database file
```

Fix:

```bash
python scripts/scrape_and_ingest.py
```

### Missing dependencies

Add required packages to `pyproject.toml` and reinstall:

```bash
pip install -e .
```

### Invalid OpenAI API key

```text
openai.AuthenticationError
```

Fix:

* ensure valid API key
* ensure billing/quota is available

### Worker exits

Check logs:

```bash
docker logs deploy-agent-worker-1 --tail 100
```

Common causes:

* missing database
* invalid API key
* incorrect LiveKit URL

## Notes

* The knowledge base must be generated before running Docker
* The system depends on external APIs for language processing
* The architecture is designed for scalability across multiple banks

## Status

The system operates correctly when:

* knowledge database exists
* services are running
* LiveKit connection is established
* a valid API key is provided
