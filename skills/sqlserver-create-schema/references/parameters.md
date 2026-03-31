# SQL Server CREATE SCHEMA — Parameter Reference

## Full Syntax

```sql
CREATE SCHEMA schema_name
    [ AUTHORIZATION owner_name ]
    [ <schema_element> [ ,...n ] ]
[ ; ]

<schema_element> ::=
{
    table_definition
  | view_definition
  | grant_statement
  | revoke_statement
  | deny_statement
}
```

## Parameters

### schema_name
- The name of the schema to create.
- Must be unique within the database.
- Convention: use lowercase (e.g., `sales`, `hr`, `dbo`, `audit`).

### AUTHORIZATION owner_name
- Specifies the database principal (user or role) that will own the schema.
- If omitted, the current user owns the schema.
- The owner does not need to exist when creating the schema, but should exist before the schema is used.
- Ownership can be transferred later: `ALTER AUTHORIZATION ON SCHEMA::schema_name TO new_owner;`

### schema_element
- Optional inline DDL statements to create objects within the schema at creation time.
- Rarely used in practice; objects are typically created separately with schema-qualified names.

## Conditional Create Pattern

SQL Server has no `IF NOT EXISTS` clause on CREATE SCHEMA. Use:

```sql
IF NOT EXISTS (
    SELECT 1
    FROM sys.schemas
    WHERE name = N'sales'
)
BEGIN
    EXEC('CREATE SCHEMA sales AUTHORIZATION dbo');
END;
GO
```

Note: CREATE SCHEMA must be the only statement in a batch when used in dynamic SQL (EXEC).

## Grant Schema-Level Permissions

SQL Server uses `GRANT <permission> ON SCHEMA::` syntax (not `GRANT USAGE`):

```sql
-- Allow a role to SELECT from all objects in the schema
GRANT SELECT ON SCHEMA::sales TO ReadOnlyRole;

-- Allow a role to insert, update, delete
GRANT INSERT, UPDATE, DELETE ON SCHEMA::sales TO DataWriterRole;

-- Allow a role to execute all procedures in the schema
GRANT EXECUTE ON SCHEMA::sales TO AppRole;

-- Grant ALTER on the schema (equivalent to schema ownership for DDL)
GRANT ALTER ON SCHEMA::sales TO SchemaOwnerRole;
```

## Transfer Schema Ownership

```sql
ALTER AUTHORIZATION ON SCHEMA::sales TO new_owner_user;
```

## Examples

### Minimal Example
```sql
CREATE SCHEMA sales;
GO
```

### With Authorization
```sql
CREATE SCHEMA hr AUTHORIZATION HRManagerUser;
GO
```

### Conditional with Authorization
```sql
IF NOT EXISTS (SELECT 1 FROM sys.schemas WHERE name = N'hr')
    EXEC('CREATE SCHEMA hr AUTHORIZATION dbo');
GO
```

### Create Objects in a Schema
```sql
-- Objects are created with schema-qualified names:
CREATE TABLE sales.Customer
(
    CustomerId   INT           NOT NULL IDENTITY(1,1),
    CustomerName NVARCHAR(200) NOT NULL,
    CONSTRAINT PK_Customer PRIMARY KEY (CustomerId)
);
GO

CREATE VIEW sales.v_ActiveCustomers
AS
    SELECT CustomerId, CustomerName
    FROM sales.Customer
    WHERE IsActive = 1;
GO
```

## Notes on SQL Server Schemas

- SQL Server schemas are **namespace containers**, not filesystem directories.
- Unlike PostgreSQL, SQL Server schemas belong to a single database.
- The default schema for a user can be set: `ALTER USER myuser WITH DEFAULT_SCHEMA = sales;`
- `dbo` (database owner) schema exists in every database and is the default schema.
- Built-in schemas: `dbo`, `guest`, `sys`, `INFORMATION_SCHEMA`.

## System Views for Inspection

```sql
-- List all schemas in the current database
SELECT schema_id, name, principal_id
FROM sys.schemas
ORDER BY name;

-- List all objects in a specific schema
SELECT o.name, o.type_desc
FROM sys.objects o
JOIN sys.schemas s ON o.schema_id = s.schema_id
WHERE s.name = N'sales'
ORDER BY o.type_desc, o.name;

-- Find schema owner
SELECT s.name AS SchemaName, p.name AS OwnerName
FROM sys.schemas s
JOIN sys.database_principals p ON s.principal_id = p.principal_id;
```
