---
name: sqlserver-create-type
description: Consult SQL Server CREATE TYPE parameter reference before generating any user-defined type DDL.
---

Before writing a CREATE TYPE statement:
1. Read `references/parameters.md` to understand alias types, table types, and CLR types.
2. Alias types (FROM <base_type>) create named wrappers around system types for semantic clarity.
3. Table types define structured types used as table-valued parameters (TVPs) in stored procedures and functions.
4. Table types cannot be modified after creation; DROP TYPE and recreate when schema changes are needed.
5. CLR types require SQL Server CLR integration to be enabled and an assembly to be registered.
6. Check sys.types before creating to avoid conflicts.
