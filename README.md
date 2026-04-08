<div align="center">

```
███████╗███████╗██╗   ██╗███████╗
╚══███╔╝██╔════╝██║   ██║██╔════╝
  ███╔╝ █████╗  ██║   ██║███████╗
 ███╔╝  ██╔══╝  ██║   ██║╚════██║
███████╗███████╗╚██████╔╝███████║
╚══════╝╚══════╝ ╚═════╝ ╚══════╝
                    ╰─ by Gyrus Inc ─╯
```

**An open-source, self-hosted agentic framework that turns plain English into SQL Server operations.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](#license)
[![Python](https://img.shields.io/badge/python-3.11.10-blue?logo=python)](https://www.python.org/)
[![Models](https://img.shields.io/badge/models-Claude%20%7C%20Gemini%20%7C%20OpenAI-green)](#model-provider)
[![SQL%20Server](https://img.shields.io/badge/built%20for-SQL%20Server-CC2927?logo=microsoftsqlserver)](https://www.microsoft.com/sql-server)
[![Discord](https://img.shields.io/badge/community-Discord-5865F2?logo=discord&logoColor=white)](https://discord.gg/fErydWMv)

[**Quick Start**](#quick-start) · [**Features**](#spotlight-features) · [**Architecture**](#architecture) · [**Setup**](#setup) · [**Safety**](#safety) · [**Contributing**](#contributing) · [**Discord**](https://discord.gg/fErydWMv) · [**Get in Touch**](#get-in-touch)

If you find Zeus useful, please consider giving it a star - it helps others discover the project!

</div>

---

## What is Zeus?

Zeus is a self-hosted, multi-agent SQL Server control plane built by [Gyrus Inc](https://www.thegyrus.com) that lets you manage your SQL Server environment in plain English.
Learn more at https://www.thegyrus.com

```
"create a new schema for finance reporting"
  → Generates and runs the SQL in dependency order

"show me which indexes are missing on my busiest tables"
  → Inspects SQL Server metadata and DMVs, then summarizes the findings

"why are queries blocking in production?"
  → Pulls live operational data and explains the likely cause
```

Unlike SaaS copilots, Zeus runs in your environment, uses your model provider, and can be customized for your standards and guardrails.

---

## Why Zeus?

Building and governing SQL Server infrastructure usually means switching between manual SQL, admin tools, scripts, and tribal knowledge. Zeus brings that into one governed workflow.

Beyond object creation, Zeus helps across the full lifecycle:
- **Database engineering** (schemas, tables, views, procedures, triggers, indexes, jobs) - so delivery teams can move faster with repeatable SQL Server patterns
- **Administration** (logins, users, roles, grants, database access) - so access and platform setup stay consistent
- **Operations and monitoring** (DMVs, blocking, sessions, connections, performance checks) - so troubleshooting is faster and more explainable
- **Security workflows** (row-level security, column-level permissions, policy-oriented access controls) - so sensitive data access can be governed in a structured way

All from natural language, in minutes.

| | |
|---|---|
| Self-hosted | Zeus runs in your environment. Credentials stay local. Every line of logic is readable and modifiable. |
| Bring your own model | Works with OpenAI, Anthropic Claude, and Google Gemini out of the box. Swap providers with configuration instead of rewiring the system. |
| Purpose-built for SQL Server | Zeus is built around SQL Server objects, DMVs, permissions, administration workflows, and operational inspection. |
| Safe by design | Destructive SQL is restricted, execution is centralized, and the manager validates outcomes before continuing. |
| Inspection-first | Zeus can inspect live infrastructure before planning changes, reducing blind execution and duplicate work. |
| Natural language all the way | Create objects, inspect metadata, investigate operational issues, and review access patterns from plain English. |

> Want to see it in action? [Schedule a demo →](mailto:priyank@thegyrus.com)

---

## Quick Start

```bash
git clone https://github.com/Gyrus-Dev/Zeus.git
cd zeus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env`, fill in your SQL Server credentials and model API key (see [Configure](#configure)), then:

```bash
python -m src.sql_server_ai.objagents.main
```

> Full setup details - model providers, SQL Server connection settings, and runtime options - are in [Setup](#setup) below.

---

## Safety

Zeus enforces two independent safeguards before any query reaches SQL Server.

### Layer 1 - Agent instructions (prompt-level)

Every agent prefers additive or minimally destructive SQL patterns where possible. Agents are instructed to inspect before acting, execute one step at a time, validate each outcome, and avoid unsafe SQL unless a specific workflow explicitly requires it.

### Layer 2 - `execute_query` safety gate (code-level)

A centralized execution tool intercepts every statement before it reaches SQL Server.

- **`DROP`** - blocked outright.
- **`TRUNCATE`** - requires explicit approval.
- **Execution flow** - results are recorded in state so the manager can validate before the next step.

```
User request
     |
     v
Agent generates SQL
     |
     v  execute_query safety gate
     |   |- contains "DROP"?      -> blocked
     |   |- contains "TRUNCATE"?  -> requires approval
     |   `- otherwise              -> passed through
     |
     v
execute_query() -> SQL Server
```

Because Layer 2 is enforced in code, not only in prompts, it gives Zeus a more reliable control point than direct model-to-SQL execution.

---

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                 CLI (Rich + prompt_toolkit)                 │
└──────────────────────────────┬───────────────────────────────┘
                               │ user message
                               v
┌──────────────────────────────────────────────────────────────┐
│                 SQLSERVER_ARCHITECT (Manager)               │
│   Classifies intent · plans work · delegates one step at    │
│   a time · validates results through state                  │
└──────┬──────────┬──────────┬────────────┬────────────┬──────┘
       v          v          v            v            v
   DATA      ADMINISTRATOR  SECURITY   INSPECTOR   ACCOUNT
 ENGINEER                  ENGINEER    PILLAR      MONITOR
       \___________ _________ _________ _________ _________/
                               |
                               v
                         execute_query() -> SQL Server
                               |
                               v
                         session state validation
```

### Agent Pillars

| Pillar | Role |
|---|---|
| **SQLSERVER_ARCHITECT** | Manager - plans, routes, validates |
| **DATA_ENGINEER** | Databases, schemas, tables, indexes, views, procedures, functions, triggers, SQL Server Agent jobs |
| **ADMINISTRATOR** | Logins, users, roles, grants, access configuration |
| **SECURITY_ENGINEER** | Row-level security and column-level permission patterns |
| **INSPECTOR_PILLAR** | Read-only inspection of SQL Server metadata and catalog state |
| **ACCOUNT_MONITOR** | Query stats, blocking, sessions, connections, and operational health |
| **RESEARCH_AGENT** | Documentation and best-practice fallback |

### How It Works

1. **You type** a natural language request.
2. **The Manager** classifies intent and creates an execution plan.
3. **Pillar agents** receive delegated tasks one at a time.
4. **Specialist agents** generate and execute SQL Server statements through the shared execution tool.
5. **After every step**, the manager validates success from session state before continuing.
6. **CLI output** shows execution progress and tool activity.
7. **On exit**, Zeus can preserve the executed query trail for later review.

---

## Spotlight Features

### Natural Language SQL Server Administration

Use plain English to perform common SQL Server administration workflows.

```
"create a login and user for the analytics team"
"set up a new schema for finance"
"grant read access to the reporting role"
```

Zeus routes these requests through SQL Server-specific agents that understand object dependencies, access patterns, and execution order.

---

### Metadata Inspection and Inventory

Zeus can inspect SQL Server infrastructure before taking action.

```
"show me all tables in the sales schema"
"list stored procedures in reporting"
"check whether this index already exists"
```

This supports discovery-first operations and reduces duplicate or unsafe changes.

---

### Operational Monitoring and Troubleshooting

Zeus can answer day-2 operational questions using SQL Server metadata and DMV-style inspection.

```
"why is the database slow right now?"
"show blocking sessions"
"which queries are consuming the most resources?"
```

This makes Zeus useful not just for build workflows, but also for operations and incident investigation.

---

### Access and Security Workflows

Zeus helps with governed access setup and security-related SQL Server patterns.

Examples include:
- users and logins
- roles and grants
- row-level security patterns
- column-level permission handling
- schema-scoped access configuration

---

### Model Flexibility

Zeus supports multiple model-provider configurations.

- Google Gemini
- Anthropic via LiteLLM
- OpenAI via LiteLLM

That means the orchestration layer can remain stable even if your model strategy changes.

---

## SQL Server Objects Supported

<details>
<summary><strong>Data Engineering</strong></summary>

Databases · Schemas · Tables · Indexes · Views · Stored Procedures · Functions · Triggers · SQL Server Agent Jobs

</details>

<details>
<summary><strong>Administration</strong></summary>

Logins · Users · Roles · Grants · Database access configuration

</details>

<details>
<summary><strong>Security</strong></summary>

Row-level security workflows · Column-level permission patterns

</details>

<details>
<summary><strong>Inspection and Monitoring</strong></summary>

System catalog inspection · Information schema discovery · Query stats · Sessions · Connections · Blocking and operational checks

</details>

---

## Setup

### Prerequisites

- Python 3.11.10
- A reachable SQL Server instance
- ODBC Driver 18 for SQL Server
- An API key for your chosen model provider

### Install

```bash
git clone https://github.com/Gyrus-Dev/Zeus.git
cd zeus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Configure

Create a `.env` file in the project root by copying the provided template:

```bash
cp .env.example .env
```

Then fill in your values - refer to `.env.example` for all available variables and their descriptions.

#### SQL Server Connection

| Variable | Required | Description |
|---|---|---|
| `SQLSERVER_HOST` | **Yes** | SQL Server hostname or IP |
| `SQLSERVER_PORT` | **Yes** | SQL Server port |
| `SQLSERVER_USER` | **Yes** | SQL Server username |
| `SQLSERVER_PASSWORD` | **Yes** | SQL Server password |
| `SQLSERVER_DATABASE` | No | Default database |
| `SQLSERVER_DRIVER` | No | ODBC driver name |
| `SQLSERVER_TRUST_SERVER_CERTIFICATE` | No | Trust server certificate for local/dev environments |

#### Application Identity

| Variable | Required | Description |
|---|---|---|
| `APP_USER_NAME` | **Yes** | Display name shown in session state |
| `APP_USER_ID` | **Yes** | Unique user ID for session tracking |
| `APP_NAME` | **Yes** | Application name for session scoping |

#### Model Provider

| Variable | Required | Description |
|---|---|---|
| `MODEL_PROVIDER` | No | `google` (default) · `openai` · `anthropic` |
| `GOOGLE_API_KEY` | If `google` | API key for Gemini models |
| `OPENAI_API_KEY` | If `openai` | API key for OpenAI models |
| `ANTHROPIC_API_KEY` | If `anthropic` | API key for Claude models |
| `MODEL_PRIMARY` | No | Override the primary model |
| `MODEL_THINKING` | No | Override the reasoning model |

## CLI Features

- terminal-first interactive experience
- execution progress visibility
- debug mode for agent payloads and generated code
- centralized SQL execution feedback

## Project Structure

```text
zeus/
├── src/sql_server_ai/
│   ├── objagents/
│   ├── adksession.py
│   ├── adkstate.py
│   └── adkrunner.py
├── skills/
├── .env.example
├── README.md
└── requirements.txt
```

## Tech Stack

- Python 3.11
- Google ADK
- LiteLLM
- Rich
- prompt_toolkit
- pyodbc / SQL Server ODBC driver

## Community

- Join the Discord community: [https://discord.gg/fErydWMv](https://discord.gg/fErydWMv)

## Contributing

Contributions, bug reports, and documentation improvements are welcome.

## Build Your Own Zeus

Zeus is designed to be adaptable. You can customize prompts, skills, guardrails, and routing behavior to match your SQL Server standards and operating model.

## Enterprise

If you want Zeus adapted for your environment, internal standards, or multi-system workflows, reach out to Gyrus.

## Get in Touch

- Website: [https://www.thegyrus.com](https://www.thegyrus.com)
- Email: [priyank@thegyrus.com](mailto:priyank@thegyrus.com)
- Discord: [https://discord.gg/fErydWMv](https://discord.gg/fErydWMv)

## License

This project is licensed under the Apache 2.0 License. See [LICENSE](./LICENSE).
