---
name: sqlserver-create-view
description: Consult SQL Server CREATE VIEW parameter reference before generating any CREATE VIEW or indexed view DDL.
---

Before writing a CREATE VIEW statement:
1. Read `references/parameters.md` to review all available view attributes and options.
2. Use CREATE OR ALTER VIEW instead of CREATE OR REPLACE VIEW (SQL Server syntax).
3. Add WITH SCHEMABINDING when creating an indexed (materialized) view — it is required.
4. For indexed views, the first index must be a UNIQUE CLUSTERED INDEX.
5. Use WITH CHECK OPTION to ensure DML through the view satisfies the WHERE clause.
6. Use WITH ENCRYPTION to obfuscate the view definition in system catalogs.
7. Avoid SELECT * in view definitions; enumerate columns explicitly.
