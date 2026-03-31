---
name: sqlserver-naming-conventions
description: Enforce SQL Server naming conventions before generating any DDL statement.
---

Before generating any DDL:
1. Read `references/rules.md` to review all SQL Server naming conventions.
2. Apply the naming conventions to all objects in the generated DDL.
3. If the user's request uses a naming style that conflicts with the conventions, apply the correct convention and note the change.
4. All constraint names must be explicit — never rely on system-generated constraint names.
5. Schema names should always be included in fully qualified object references.
