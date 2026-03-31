---
name: sqlserver-create-schema
description: Consult SQL Server CREATE SCHEMA parameter reference before generating any CREATE SCHEMA DDL.
---

Before writing a CREATE SCHEMA statement:
1. Read `references/parameters.md` to review all available parameters and syntax.
2. Use AUTHORIZATION to assign ownership when the schema owner differs from the current user.
3. SQL Server has no IF NOT EXISTS for schemas; use a conditional check against sys.schemas instead.
4. Remember that SQL Server schemas are namespace containers — ownership is transferable via ALTER AUTHORIZATION.
5. Grant schema-level permissions with GRANT on SCHEMA:: syntax, not GRANT USAGE.
