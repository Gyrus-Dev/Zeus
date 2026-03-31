---
name: sqlserver-create-database
description: Consult SQL Server CREATE DATABASE parameter reference before generating any CREATE DATABASE DDL.
---

Before writing a CREATE DATABASE statement:
1. Read `references/parameters.md` to review all available parameters and their defaults.
2. Include only parameters that differ from the default or the user explicitly requested.
3. Use CREATE DATABASE — SQL Server has no IF NOT EXISTS, use a conditional check pattern instead.
4. Set collation explicitly only when the user requests a non-default collation.
5. Filegroups: add only when user requests specific file placement or multiple filegroups.
6. Use CONTAINMENT = PARTIAL only when user requests contained database for portable auth.
