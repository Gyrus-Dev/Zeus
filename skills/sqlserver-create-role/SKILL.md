---
name: sqlserver-create-role
description: Consult SQL Server CREATE ROLE parameter reference before generating any role or permission DDL.
---

Before writing a CREATE ROLE statement:
1. Read `references/parameters.md` to review role creation, membership, and permission syntax.
2. Database roles group permissions for sets of users; use ALTER ROLE ... ADD MEMBER to assign membership.
3. Prefer custom database roles over direct permission grants for maintainability.
4. Use built-in roles (db_datareader, db_datawriter, db_owner) only when their broad scope is appropriate.
5. Server roles (sysadmin, securityadmin, etc.) operate at the server level, not per database.
6. Use GRANT, DENY, REVOKE to manage object-level and schema-level permissions.
7. DENY always takes precedence over GRANT — use carefully.
