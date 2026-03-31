---
name: sqlserver-create-linked-server
description: Consult SQL Server linked server parameter reference before generating any linked server, foreign data wrapper, or remote table DDL.
---

Before writing linked server statements:
1. Read `references/parameters.md` to review sp_addlinkedserver, sp_addlinkedsrvlogin, and query patterns.
2. Linked servers are SQL Server's equivalent of PostgreSQL Foreign Data Wrappers (FDWs).
3. Use sp_addlinkedserver to register the remote server with the appropriate OLE DB provider.
4. Use sp_addlinkedsrvlogin to configure credentials for the linked server connection.
5. Four-part naming ([server].[database].[schema].[table]) is the standard way to reference linked objects.
6. Use OPENQUERY for better performance when the query can be pushed down to the remote server.
7. Choose the correct provider: SQLNCLI/MSOLEDBSQL for SQL Server, MSDAORA for Oracle, MSDASQL for ODBC.
8. Linked server credentials contain sensitive information — never hardcode passwords in source control.
