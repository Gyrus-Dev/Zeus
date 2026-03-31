---
name: sqlserver-create-user
description: Consult SQL Server CREATE USER and CREATE LOGIN parameter reference before generating any security principal DDL.
---

Before writing a CREATE USER or CREATE LOGIN statement:
1. Read `references/parameters.md` to understand the login/user two-tier model.
2. Logins are server-scoped principals; users are database-scoped principals mapped from logins.
3. Use CREATE LOGIN for SQL Server authentication or Windows authentication principals.
4. Use CREATE USER ... FOR LOGIN to map a database user to an existing login.
5. Use CREATE USER ... WITH PASSWORD for contained database users (no login required).
6. Use CREATE USER ... WITHOUT LOGIN for service accounts or application roles.
7. Always set DEFAULT_DATABASE on logins to avoid connecting to master by default.
8. Avoid hardcoding passwords in scripts; use parameterized deployment or Secrets Manager.
