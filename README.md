# Zeus

Zeus is the SQL Server specialist in this repository.

It is a self-hosted, multi-agent system for SQL Server operations in plain
English, including creation, inspection, administration, security, and
monitoring workflows.

## Open Source Status

Zeus is structured so it can be published and used as a standalone project.

This directory includes:

- a project README
- a sanitized `.env.example`
- an Apache 2.0 license
- a project-local security policy

Keep live credentials only in your local `.env` file and never commit them.

## What Zeus Handles

- databases, schemas, tables, indexes, views, functions, procedures, triggers
- SQL Server Agent jobs
- logins, users, roles, and grants
- row-level security and column-level access controls
- read-only inspection through system catalog and information schema views
- performance and operations monitoring through SQL Server DMVs

## Safety

Zeus is designed with execution guardrails:

- `DROP` is blocked outright
- destructive or sensitive operations require explicit approval where supported
- the manager validates each step before proceeding

## Run

```bash
cd zeus
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python -m src.sql_server_ai.objagents.main
```

## Requirements

- Python 3.11+
- SQL Server reachable from the Zeus runtime
- ODBC Driver 18 for SQL Server
- one supported model provider: Google, Anthropic, or OpenAI

## Configuration

Set your SQL Server connection details and model provider in `.env`.

Use `.env.example` as the starting point.

Key configuration groups:

- SQL Server connection
- app identity
- model provider selection
- optional OpenTelemetry settings
- optional debug and skill flags

## Supported Model Providers

Zeus supports:

- Google Gemini
- Anthropic via LiteLLM
- OpenAI via LiteLLM

You can switch providers through environment variables without changing the
agent hierarchy.

## Skills

Zeus includes SQL Server-specific skills for common object types and patterns,
including:

- databases
- schemas
- tables
- indexes
- views
- procedures
- functions
- triggers
- users and roles
- naming conventions

These skills help encode domain guidance and improve repeatability for common
SQL Server workflows.

## Security and Publishing Notes

Before publishing Zeus publicly:

- confirm `zeus/.env` is not committed
- rotate any credentials that may have been used in local testing
- review git history for accidental secret exposure
- verify sample prompts and screenshots do not expose internal data

Zeus does not currently ship a standalone A2A server entrypoint in this
directory. The primary supported open-source runtime here is the interactive
CLI entrypoint shown above.

## Role in the Ecosystem

Zeus can be used on its own for SQL Server administration, or through `LEO`
when a workflow spans SQL Server, Confluent, and Snowflake.
