---
name: sqlserver-create-fulltext
description: Consult SQL Server Full-Text Search parameter reference before generating any full-text catalog, index, or search DDL.
---

Before writing full-text search statements:
1. Read `references/parameters.md` to review catalog, index creation, and search predicate syntax.
2. Full-Text Search is SQL Server's equivalent of PostgreSQL text search configuration.
3. A FULLTEXT CATALOG must exist before creating a FULLTEXT INDEX.
4. Each full-text index requires a unique, single-column, non-nullable key index (usually the primary key).
5. Use CHANGE_TRACKING AUTO to keep the full-text index synchronized automatically.
6. Use CONTAINS for precise term matching; use FREETEXT for natural-language search.
7. CONTAINSTABLE and FREETEXTTABLE return ranked result sets for relevance scoring.
8. Specify LANGUAGE for each column to use the appropriate word breaker and stemmer.
