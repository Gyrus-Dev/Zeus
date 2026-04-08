<div align="center">

```
███████╗███████╗██╗   ██╗███████╗
╚══███╔╝██╔════╝██║   ██║██╔════╝
  ███╔╝ █████╗  ██║   ██║███████╗
 ███╔╝  ██╔══╝  ██║   ██║╚════██║
███████╗███████╗╚██████╔╝███████║
╚══════╝╚══════╝ ╚═════╝ ╚══════╝
             ╰─ SQL Server AI Assistant ─╯
```

**An open-source, self-hosted agentic framework that turns plain English into SQL Server operations.**

[![License](https://img.shields.io/badge/license-Apache%202.0-blue)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.11+-blue?logo=python)](https://www.python.org/)
[![Models](https://img.shields.io/badge/models-Claude%20%7C%20Gemini%20%7C%20OpenAI-green)](#model-provider)
[![SQL%20Server](https://img.shields.io/badge/built%20for-SQL%20Server-CC2927?logo=microsoftsqlserver)](https://www.microsoft.com/sql-server)

[**Quick Start**](#quick-start) · [**Safety**](#safety) · [**Architecture**](#architecture) · [**Setup**](#setup) · [**Skills**](#skills) · [**Security**](#security) · [**Discord**](https://discord.gg/fErydWMv)

</div>

---

## What Is Zeus?

Zeus is a self-hosted, multi-agent SQL Server assistant that helps you manage
SQL Server infrastructure in plain English.

It is designed for:

- database and schema creation
- table, index, view, function, procedure, and trigger workflows
- SQL Server Agent job setup
- users, roles, and grants
- row-level security and column-level permission patterns
- read-only inspection through system catalog and information schema views
- performance and operational monitoring through SQL Server DMVs

Unlike SaaS copilots, Zeus runs in your environment, uses your model provider,
and can be customized for your standards and guardrails.

## Why Zeus?

Building and governing SQL Server infrastructure usually means switching between
manual SQL, admin tools, scripts, and tribal knowledge.

Zeus brings that into one governed workflow:

- natural-language requests
- manager-driven planning
- one-step-at-a-time execution
- validation after each step
- centralized execution safety
- SQL Server-specific routing and inspection

This makes Zeus useful for both greenfield setup and day-2 operations.

| | |
|---|---|
| Self-hosted | Zeus runs in your environment. Credentials stay local. |
| Bring your own model | Supports Google, Anthropic, and OpenAI-based model configurations. |
| SQL Server specific | Built around SQL Server objects, DMVs, permissions, and administration workflows. |
| Safe by design | `DROP` is blocked outright and destructive operations are tightly controlled. |
| Inspection-first | Zeus can inspect existing infrastructure before planning changes. |
| Extensible | Skills and prompts can be adapted for your naming conventions and operating standards. |

---

## Quick Start

```bash
cd zeus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.sql_server_ai.objagents.main
```

## Safety

Zeus enforces both prompt-level and code-level safety controls.

### Layer 1: Agent Instructions

The manager and specialists are instructed to:

- inspect before acting where appropriate
- execute one step at a time
- validate outcomes after every delegated step
- avoid unsafe or destructive SQL patterns

### Layer 2: Execution Safety Gate

Zeus centralizes SQL execution through a shared tool.

Key guardrails include:

- `DROP` is blocked outright
- `TRUNCATE` requires explicit approval
- the manager validates session state before moving to the next step

This gives Zeus a more controlled operating model than direct model-to-SQL
execution.

---

## Architecture

Zeus uses a manager-led multi-agent hierarchy.

```text
User
  -> Zeus CLI
  -> SQLSERVER_ARCHITECT
  -> Pillar agent
  -> Specialist agent
  -> execute_query
  -> SQL Server
  -> Session state validation
  -> Final response
```

### Pillars

Zeus routes work across these main pillars:

- `DATA_ENGINEER`
  Databases, schemas, tables, indexes, views, procedures, functions, triggers, jobs
- `ADMINISTRATOR`
  Logins, users, roles, grants
- `SECURITY_ENGINEER`
  Row-level security and column-level permissions
- `INSPECTOR_PILLAR`
  Read-only inspection of SQL Server objects
- `ACCOUNT_MONITOR`
  Query stats, connections, blocking, and other operational monitoring
- `RESEARCH_AGENT`
  Documentation and best-practice lookup

### Execution Model

The manager:

1. classifies the request
2. inspects existing infrastructure where needed
3. creates a high-level execution plan
4. delegates one task at a time
5. validates success from session state before continuing

This is one of Zeus’s core control-plane behaviors.

---

## Setup

### Requirements

- Python 3.11+
- SQL Server reachable from the Zeus runtime
- ODBC Driver 18 for SQL Server
- a supported model provider

### Configure

Use [`.env.example`](./.env.example) as the starting point.

Main configuration groups:

- SQL Server connection
- app identity
- model provider
- optional observability
- debug and feature flags

### SQL Server Connection

Configure:

- `SQLSERVER_HOST`
- `SQLSERVER_PORT`
- `SQLSERVER_USER`
- `SQLSERVER_PASSWORD`
- `SQLSERVER_DATABASE`
- `SQLSERVER_DRIVER`
- `SQLSERVER_TRUST_SERVER_CERTIFICATE`

### App Identity

Configure:

- `APP_USER_NAME`
- `APP_USER_ID`
- `APP_NAME`

---

## Model Provider

Zeus supports multiple model-provider configurations.

Supported today:

- Google Gemini
- Anthropic via LiteLLM
- OpenAI via LiteLLM

This means you can change model strategy without changing the Zeus agent
hierarchy.

---

## Skills

Zeus includes SQL Server-specific skills to improve repeatability and enforce
domain guidance.

Examples include:

- `sqlserver-create-database`
- `sqlserver-create-schema`
- `sqlserver-create-table`
- `sqlserver-create-index`
- `sqlserver-create-view`
- `sqlserver-create-function`
- `sqlserver-create-procedure`
- `sqlserver-create-trigger`
- `sqlserver-create-user`
- `sqlserver-create-role`
- `sqlserver-naming-conventions`

These skills act as structured guidance for common object types and enterprise
standards.

---

## Open Source Notes

Zeus is set up to be publishable as a standalone open-source project.

This directory includes:

- a project README
- a sanitized `.env.example`
- an Apache 2.0 license
- a project-local security policy

Before publishing or sharing Zeus:

- keep live credentials only in local `.env`
- do not commit `zeus/.env`
- review git history for accidental secret exposure
- review screenshots, prompts, and docs for internal names or data

Zeus currently exposes its main open-source experience through the CLI entrypoint
shown above.

---

## Security

See [SECURITY.md](./SECURITY.md) for vulnerability reporting and release-safety guidance.

## Role In The Ecosystem

Zeus can run as a standalone SQL Server assistant, or it can be coordinated by
`LEO` in cross-platform workflows that also involve Snowflake and Confluent.
