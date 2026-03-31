---
name: sqlserver-data-analyst
description: Business rules and domain knowledge for natural language to SQL translation against SQL Server databases.
---

Before generating any analytical SQL query:
1. Read `references/business-rules.md` to review metric definitions, canonical date columns, and domain-specific rules.
2. Apply the correct metric definition when the user references a business term (e.g., "revenue", "active customers").
3. Use SQL Server-specific syntax: TOP N instead of LIMIT, ISNULL()/COALESCE() for null handling, FORMAT() for date formatting.
4. Use explicit JOIN syntax — never comma-separated FROM clause table lists.
5. Apply window functions with ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...) as appropriate.
6. For date arithmetic, use DATEADD() and DATEDIFF() rather than interval arithmetic.
