---
name: sqlserver-create-procedure
description: Consult SQL Server CREATE PROCEDURE parameter reference before generating any stored procedure DDL.
---

Before writing a CREATE PROCEDURE statement:
1. Read `references/parameters.md` to review all available options, parameter syntax, and patterns.
2. Use CREATE OR ALTER PROCEDURE instead of CREATE OR REPLACE PROCEDURE (SQL Server syntax).
3. Always include SET NOCOUNT ON as the first statement in the procedure body to suppress row count messages.
4. Use TRY/CATCH for error handling; include XACT_ABORT ON for transaction safety.
5. Prefix output parameters with OUT or OUTPUT.
6. Default parameter values are specified with = <default> in the parameter declaration.
7. Use EXECUTE AS to control the security context when needed.
8. Procedures can issue COMMIT and ROLLBACK — use transactions for multi-statement operations.
