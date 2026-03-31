---
name: sqlserver-create-index
description: Consult SQL Server CREATE INDEX parameter reference before generating any CREATE INDEX DDL.
---

Before writing a CREATE INDEX statement:
1. Read `references/parameters.md` to review all index types, options, and WITH clauses.
2. Each table can have only one CLUSTERED index; all others are NONCLUSTERED.
3. Use INCLUDE columns to cover queries without adding to the key columns.
4. Use WHERE clause for a filtered index to index only a subset of rows.
5. Consider ONLINE = ON for production index creation to minimize blocking.
6. Use DROP_EXISTING = ON when rebuilding an existing index to avoid dropping and recreating.
7. Columnstore indexes are separate from rowstore indexes; use CREATE COLUMNSTORE INDEX syntax.
8. Use a conditional check against sys.indexes before creating to avoid errors.
