---
name: sqlserver-create-sequence
description: Consult SQL Server CREATE SEQUENCE parameter reference before generating any sequence DDL.
---

Before writing a CREATE SEQUENCE statement:
1. Read `references/parameters.md` to review all sequence options and usage patterns.
2. SQL Server sequences use NEXT VALUE FOR schema.sequence_name to retrieve the next value.
3. Unlike IDENTITY, sequences are independent objects and can be used across multiple tables.
4. Use AS <integer_type> to specify the data type (default is BIGINT).
5. Specify CACHE to improve performance by pre-allocating sequence values in memory.
6. Use NO CYCLE unless wrap-around behavior is explicitly required.
7. To use a sequence as a column default: DEFAULT (NEXT VALUE FOR schema.seq_name).
8. Check sys.sequences before creating to avoid conflicts.
