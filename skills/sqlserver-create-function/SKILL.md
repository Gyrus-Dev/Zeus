---
name: sqlserver-create-function
description: Consult SQL Server CREATE FUNCTION parameter reference before generating any UDF DDL.
---

Before writing a CREATE FUNCTION statement:
1. Read `references/parameters.md` to understand the three function types: scalar, inline TVF, and multi-statement TVF.
2. Use CREATE OR ALTER FUNCTION instead of CREATE OR REPLACE FUNCTION (SQL Server syntax).
3. Scalar functions return a single value; use RETURNS <type> and RETURN <expr>.
4. Inline table-valued functions (TVF) use RETURNS TABLE AS RETURN (<select>) — they are the most performant TVF type.
5. Multi-statement TVFs declare the return table variable and populate it with INSERT statements.
6. Add WITH SCHEMABINDING when the function references database objects to prevent unintentional schema changes.
7. Functions cannot issue COMMIT, ROLLBACK, or use non-deterministic functions without marking them accordingly.
8. DETERMINISTIC functions with SCHEMABINDING can be used in indexed computed columns and indexed views.
