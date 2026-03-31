---
name: sqlserver-create-statistics
description: Consult SQL Server CREATE STATISTICS parameter reference before generating any statistics object DDL.
---

Before writing a CREATE STATISTICS statement:
1. Read `references/parameters.md` to review all statistics options and sampling methods.
2. SQL Server automatically creates statistics on indexed columns; manual statistics are for unindexed columns.
3. Use FULLSCAN for the most accurate statistics at the cost of time; SAMPLE N PERCENT for large tables.
4. Filtered statistics (WHERE clause) are useful for skewed data distributions or partitioned views.
5. Use NORECOMPUTE only when you want to manage statistics updates manually.
6. INCREMENTAL statistics are supported for partitioned tables when INCREMENTAL = ON.
7. Check sys.stats before creating to avoid duplicates.
