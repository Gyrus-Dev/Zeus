# SQL Server CREATE TYPE — Parameter Reference

## Full Syntax

### Alias Type (based on system type)
```sql
CREATE TYPE [ schema_name . ] type_name
FROM base_type
[ ( precision [ , scale ] ) ]
[ NULL | NOT NULL ]
[ ; ]
```

### Table Type
```sql
CREATE TYPE [ schema_name . ] type_name
AS TABLE
(
    { <column_definition>
    | <computed_column_definition>
    | <column_constraint>
    | <table_constraint> }
    [ ,...n ]
)
[ ; ]
```

### CLR Type (requires assembly)
```sql
CREATE TYPE [ schema_name . ] type_name
{ FROM base_type [ ( precision [ , scale ] ) ] [ NULL | NOT NULL ] }
| EXTERNAL NAME assembly_name [ .class_name ]
[ ; ]
```

## Alias Types

An alias type creates a named wrapper around a system type for semantic clarity and consistency.

### Parameters
| Parameter | Description |
|-----------|-------------|
| `type_name` | Unique name for the new type within the schema |
| `base_type` | Any system data type (INT, NVARCHAR, DECIMAL, etc.) |
| `precision` | For DECIMAL/NUMERIC/FLOAT: total digits |
| `scale` | For DECIMAL/NUMERIC: digits after decimal point |
| `NULL \| NOT NULL` | Nullability of the alias type; default depends on `sp_configure 'default nullability'` |

### Alias Type Examples

```sql
-- Semantic type aliases
CREATE TYPE dbo.CustomerName FROM NVARCHAR(200) NOT NULL;
CREATE TYPE dbo.EmailAddress  FROM NVARCHAR(256) NULL;
CREATE TYPE dbo.PhoneNumber   FROM NVARCHAR(20)  NULL;
CREATE TYPE dbo.Money19_4     FROM DECIMAL(19,4) NOT NULL;
CREATE TYPE dbo.Flag          FROM BIT           NOT NULL;
CREATE TYPE dbo.RowVersion    FROM ROWVERSION;

-- Usage in a table
CREATE TABLE sales.Customer
(
    CustomerId   INT                  NOT NULL IDENTITY(1,1),
    CustomerName dbo.CustomerName,    -- Uses alias type
    Email        dbo.EmailAddress,
    Phone        dbo.PhoneNumber,
    CONSTRAINT PK_Customer PRIMARY KEY (CustomerId)
);
```

## Table Types (Table-Valued Parameters)

Table types define structured in-memory table variables primarily used as table-valued parameters (TVPs) in stored procedures and functions.

### Column Definition (within table type)
```sql
<column_definition> ::=
column_name <data_type>
    [ COLLATE collation_name ]
    [ NULL | NOT NULL ]
    [ DEFAULT constant_expression ]
    [ IDENTITY [ ( seed, increment ) ] ]
    [ <column_constraint> ]

<column_constraint> ::=
    [ CONSTRAINT constraint_name ]
    { PRIMARY KEY [ CLUSTERED | NONCLUSTERED ]
    | UNIQUE [ CLUSTERED | NONCLUSTERED ]
    | CHECK ( logical_expression )
    }

<table_constraint> ::=
    [ CONSTRAINT constraint_name ]
    { PRIMARY KEY [ CLUSTERED | NONCLUSTERED ] ( column_name [ ,...n ] )
    | UNIQUE [ CLUSTERED | NONCLUSTERED ] ( column_name [ ,...n ] )
    | CHECK ( logical_expression )
    }
```

### Table Type Examples

```sql
-- Simple ID list (common pattern)
CREATE TYPE dbo.IntIdList AS TABLE
(
    Id INT NOT NULL PRIMARY KEY
);
GO

-- Order line table type for batch insert
CREATE TYPE dbo.OrderLineTableType AS TABLE
(
    ProductId   INT           NOT NULL,
    Quantity    INT           NOT NULL,
    UnitPrice   DECIMAL(18,4) NOT NULL,
    CONSTRAINT PK_OrderLineTableType PRIMARY KEY (ProductId)
);
GO

-- Generic key-value pair
CREATE TYPE dbo.KeyValuePair AS TABLE
(
    [Key]   NVARCHAR(128) NOT NULL,
    [Value] NVARCHAR(MAX) NULL,
    UNIQUE CLUSTERED ([Key])
);
GO
```

### Using Table Types as TVPs

```sql
-- Procedure accepting TVP
CREATE OR ALTER PROCEDURE sales.usp_bulk_insert_orders
    @OrderLines dbo.OrderLineTableType READONLY
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO sales.OrderLine (OrderId, ProductId, Quantity, UnitPrice)
    SELECT 1, ProductId, Quantity, UnitPrice
    FROM @OrderLines;
END;
GO

-- Calling with TVP from T-SQL
DECLARE @Lines dbo.OrderLineTableType;
INSERT INTO @Lines (ProductId, Quantity, UnitPrice)
VALUES (101, 2, 29.99), (205, 1, 49.99), (312, 3, 9.99);

EXEC sales.usp_bulk_insert_orders @OrderLines = @Lines;
```

## Table Type Restrictions

- Table type variables are **always** in-memory (not in tempdb by default, unless temp table is used).
- Must pass as `READONLY` to procedures and functions.
- Cannot be used with `OUTPUT` direction.
- Cannot be altered after creation — must `DROP TYPE` and recreate.
- Cannot create triggers on table type variables.
- Indexes in table types are limited (PRIMARY KEY or UNIQUE only; no non-clustered without a key).

## CLR Types

Require CLR integration to be enabled and a registered assembly:

```sql
-- Enable CLR (if not already enabled)
EXEC sp_configure 'clr enabled', 1;
RECONFIGURE;
GO

-- Register assembly (assembly must be created separately)
CREATE ASSEMBLY HierarchyIdAssembly
FROM 'C:\assemblies\HierarchyId.dll'
WITH PERMISSION_SET = SAFE;
GO

-- Create type from assembly
CREATE TYPE dbo.CustomHierarchyId
EXTERNAL NAME HierarchyIdAssembly.HierarchyIdClass;
GO
```

## Drop Type

```sql
-- Table types cannot be dropped if any table columns or procedure parameters reference them
-- First check for dependencies:
SELECT
    OBJECT_NAME(c.object_id) AS TableName,
    c.name AS ColumnName
FROM sys.columns c
JOIN sys.types t ON c.user_type_id = t.user_type_id
WHERE t.name = N'CustomerName' AND t.schema_id = SCHEMA_ID(N'dbo');

-- Then drop if no dependencies:
DROP TYPE IF EXISTS dbo.OrderLineTableType;
```

## System Views for Inspection

```sql
-- List all user-defined types
SELECT s.name AS SchemaName, t.name AS TypeName,
       t.system_type_id, TYPE_NAME(t.system_type_id) AS BaseType,
       t.is_table_type, t.is_assembly_type, t.is_nullable,
       t.max_length, t.precision, t.scale
FROM sys.types t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.is_user_defined = 1
ORDER BY s.name, t.name;

-- Inspect columns of a table type
SELECT c.name, TYPE_NAME(c.user_type_id) AS DataType,
       c.max_length, c.precision, c.scale, c.is_nullable
FROM sys.columns c
JOIN sys.table_types tt ON c.object_id = tt.type_table_object_id
JOIN sys.types t ON tt.user_type_id = t.user_type_id
WHERE t.name = N'OrderLineTableType'
  AND t.schema_id = SCHEMA_ID(N'dbo')
ORDER BY c.column_id;
```
