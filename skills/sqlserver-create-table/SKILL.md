---
name: sqlserver-create-table
description: Consult SQL Server CREATE TABLE parameter reference before generating any CREATE TABLE DDL.
---

Before writing a CREATE TABLE statement:
1. Read `references/parameters.md` to review all available column types, constraints, and table options.
2. Use IDENTITY(seed, increment) for auto-incrementing columns, not SERIAL or AUTOINCREMENT.
3. SQL Server has no CREATE OR REPLACE TABLE and no IF NOT EXISTS; use a conditional check against sys.tables instead.
4. Name all constraints explicitly using the PK_, FK_, UQ_, CK_, DF_ prefixes.
5. Use DATETIME2 instead of DATETIME for new timestamp columns (higher precision, wider range).
6. For computed columns use AS (<expression>) [PERSISTED].
7. For temporal tables, include PERIOD FOR SYSTEM_TIME and WITH (SYSTEM_VERSIONING = ON).
