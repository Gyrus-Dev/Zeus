---
name: sqlserver-create-trigger
description: Consult SQL Server CREATE TRIGGER parameter reference before generating any DML or DDL trigger DDL.
---

Before writing a CREATE TRIGGER statement:
1. Read `references/parameters.md` to understand DML, DDL, and logon trigger types.
2. Use CREATE OR ALTER TRIGGER instead of CREATE OR REPLACE TRIGGER (SQL Server syntax).
3. DML triggers fire AFTER or INSTEAD OF INSERT, UPDATE, DELETE on a table or view.
4. Use the INSERTED and DELETED pseudo-tables to access before/after row images.
5. Use UPDATE(<column>) or COLUMNS_UPDATED() to check which columns were modified.
6. DDL triggers fire on DATABASE or ALL SERVER scope for DDL events (e.g., CREATE_TABLE).
7. Keep trigger logic minimal; avoid long-running operations inside triggers.
8. Use DISABLE TRIGGER / ENABLE TRIGGER to manage trigger state without dropping it.
