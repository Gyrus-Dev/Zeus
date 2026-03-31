# SQL Server CREATE TABLE — Parameter Reference

## Full Syntax

```sql
CREATE TABLE [ database_name . [ schema_name ] . | schema_name . ] table_name
(
    { <column_definition>
    | <computed_column_definition>
    | <column_set_definition>
    | <table_constraint>
    | <table_index> }
    [ ,...n ]
)
[ ON { partition_scheme_name ( partition_column_name )
       | filegroup
       | "default" }
]
[ TEXTIMAGE_ON { filegroup | "default" } ]
[ FILESTREAM_ON { partition_scheme_name
                 | filegroup
                 | "default" } ]
[ WITH ( <table_option> [ ,...n ] ) ]
[ ; ]
```

## Column Definition Syntax

```sql
<column_definition> ::=
column_name <data_type>
    [ FILESTREAM ]
    [ COLLATE collation_name ]
    [ SPARSE ]
    [ MASKED WITH ( FUNCTION = 'mask_function' ) ]
    [ CONSTRAINT constraint_name ] DEFAULT constant_expression
    [ IDENTITY [ ( seed, increment ) ] [ NOT FOR REPLICATION ] ]
    [ GENERATED ALWAYS AS { ROW | TRANSACTION_ID | SEQUENCE_NUMBER } { START | END } [ HIDDEN ] ]
    [ NOT NULL | NULL ]
    [ ROWGUIDCOL ]
    [ ENCRYPTED WITH ( COLUMN_ENCRYPTION_KEY = key_name , ENCRYPTION_TYPE = { DETERMINISTIC | RANDOMIZED } , ALGORITHM = 'aead_aes_256_cbc_hmac_sha_256' ) ]
    [ <column_constraint> [ ,...n ] ]
    [ <column_index> ]
```

## Data Types

### Exact Numerics
| Type | Storage | Range |
|------|---------|-------|
| `BIT` | 1 bit | 0, 1, NULL |
| `TINYINT` | 1 byte | 0–255 |
| `SMALLINT` | 2 bytes | -32,768–32,767 |
| `INT` | 4 bytes | -2^31–2^31-1 |
| `BIGINT` | 8 bytes | -2^63–2^63-1 |
| `DECIMAL(p,s)` / `NUMERIC(p,s)` | 5–17 bytes | Precision 1–38, scale 0–p |
| `SMALLMONEY` | 4 bytes | ±214,748.3648 |
| `MONEY` | 8 bytes | ±922,337,203,685,477.5807 |

### Approximate Numerics
| Type | Storage | Notes |
|------|---------|-------|
| `FLOAT(n)` | 4 or 8 bytes | n=1–24 → 4 bytes; n=25–53 → 8 bytes |
| `REAL` | 4 bytes | Equivalent to FLOAT(24) |

### Date and Time
| Type | Storage | Accuracy | Range |
|------|---------|----------|-------|
| `DATE` | 3 bytes | 1 day | 0001-01-01–9999-12-31 |
| `TIME(n)` | 3–5 bytes | 100 ns | 00:00:00.0000000–23:59:59.9999999 |
| `DATETIME` | 8 bytes | 3.33 ms | 1753-01-01–9999-12-31 |
| `DATETIME2(n)` | 6–8 bytes | 100 ns | 0001-01-01–9999-12-31 (preferred) |
| `SMALLDATETIME` | 4 bytes | 1 min | 1900-01-01–2079-06-06 |
| `DATETIMEOFFSET(n)` | 8–10 bytes | 100 ns | Includes timezone offset |

**Prefer DATETIME2 over DATETIME for new columns.**

### Character Strings
| Type | Storage | Notes |
|------|---------|-------|
| `CHAR(n)` | n bytes | Fixed-length, 1–8000 bytes, non-Unicode |
| `VARCHAR(n)` | n + 2 bytes | Variable-length, 1–8000 bytes, non-Unicode |
| `VARCHAR(MAX)` | Up to 2 GB | Stored off-row when large |
| `NCHAR(n)` | 2n bytes | Fixed-length Unicode, 1–4000 chars |
| `NVARCHAR(n)` | 2n + 2 bytes | Variable-length Unicode, 1–4000 chars |
| `NVARCHAR(MAX)` | Up to 2 GB | Unicode, stored off-row when large |
| `TEXT` | Up to 2 GB | Deprecated; use VARCHAR(MAX) |
| `NTEXT` | Up to 2 GB | Deprecated; use NVARCHAR(MAX) |

### Binary
| Type | Notes |
|------|-------|
| `BINARY(n)` | Fixed-length binary, 1–8000 bytes |
| `VARBINARY(n)` | Variable-length binary, 1–8000 bytes |
| `VARBINARY(MAX)` | Up to 2 GB |
| `IMAGE` | Deprecated; use VARBINARY(MAX) |

### Other Types
| Type | Notes |
|------|-------|
| `UNIQUEIDENTIFIER` | 16-byte GUID; use NEWID() or NEWSEQUENTIALID() |
| `XML` | Stores XML data; can be typed with XML schema collection |
| `GEOGRAPHY` | Spatial type for geographic coordinates |
| `GEOMETRY` | Spatial type for planar coordinates |
| `HIERARCHYID` | Represents position in a hierarchy tree |
| `SQL_VARIANT` | Stores values of various types; avoid in new designs |
| `ROWVERSION` / `TIMESTAMP` | Auto-updating binary(8) per row change |

## IDENTITY

```sql
-- Syntax
column_name INT IDENTITY(seed, increment)

-- Examples
Id          INT      NOT NULL IDENTITY(1, 1)   -- starts at 1, increments by 1
ProductCode INT      NOT NULL IDENTITY(1000, 5) -- starts at 1000, increments by 5

-- Get last inserted identity value
SELECT SCOPE_IDENTITY();       -- preferred (scope-safe)
SELECT @@IDENTITY;             -- not scope-safe
SELECT IDENT_CURRENT('table'); -- returns last identity regardless of session
```

## NULL / NOT NULL

- Always specify `NULL` or `NOT NULL` explicitly for clarity.
- Default behavior depends on `SET ANSI_NULL_DFLT_ON` (typically ON → nullable).

## DEFAULT Constraints

```sql
-- Inline syntax
ColumnName  DATETIME2 NOT NULL DEFAULT GETDATE()
Status      NVARCHAR(20) NOT NULL DEFAULT N'Active'
IsActive    BIT NOT NULL DEFAULT 1

-- Named constraint syntax (preferred)
ColumnName  DATETIME2 NOT NULL CONSTRAINT DF_TableName_ColumnName DEFAULT GETDATE()
```

## Computed Columns

```sql
-- Virtual computed column (recalculated on access)
FullName AS (FirstName + N' ' + LastName)

-- Persisted computed column (stored on disk, updated on change)
TotalPrice AS (Quantity * UnitPrice) PERSISTED

-- Named computed column
FullName AS (FirstName + N' ' + LastName) PERSISTED
    CONSTRAINT CK_Employee_FullName CHECK (LEN(FullName) <= 200)
```

## Column Constraints

```sql
-- Primary key (inline)
Id INT NOT NULL CONSTRAINT PK_Customer PRIMARY KEY

-- Unique (inline)
Email NVARCHAR(256) NOT NULL CONSTRAINT UQ_Customer_Email UNIQUE

-- Check (inline)
Age INT NOT NULL CONSTRAINT CK_Customer_Age CHECK (Age >= 0 AND Age <= 150)

-- Foreign key (inline)
DepartmentId INT NOT NULL
    CONSTRAINT FK_Employee_Department
    REFERENCES hr.Department(DepartmentId)
    ON DELETE NO ACTION
    ON UPDATE CASCADE
```

## Table Constraints

```sql
-- Composite primary key
CONSTRAINT PK_OrderLine PRIMARY KEY CLUSTERED (OrderId, LineNumber)

-- Composite unique
CONSTRAINT UQ_Product_CodeVersion UNIQUE NONCLUSTERED (ProductCode, Version)

-- Check constraint
CONSTRAINT CK_Order_Dates CHECK (ShipDate IS NULL OR ShipDate >= OrderDate)

-- Foreign key
CONSTRAINT FK_OrderLine_Order
    FOREIGN KEY (OrderId)
    REFERENCES sales.Order(OrderId)
    ON DELETE CASCADE
    ON UPDATE NO ACTION
```

## ON DELETE / ON UPDATE Actions

| Action | Description |
|--------|-------------|
| `NO ACTION` (default) | Error if referenced rows exist |
| `CASCADE` | Propagate delete/update to child rows |
| `SET NULL` | Set FK column to NULL in child rows |
| `SET DEFAULT` | Set FK column to its default value in child rows |

## Filegroup and Storage Options

```sql
-- Place table on specific filegroup
CREATE TABLE sales.Order (...)
ON [SECONDARY];

-- Place LOB data on different filegroup
CREATE TABLE dbo.Document (
    DocId INT NOT NULL,
    Content NVARCHAR(MAX)
)
ON [PRIMARY]
TEXTIMAGE_ON [SECONDARY];
```

## WITH Table Options

```sql
WITH (
    DATA_COMPRESSION = { NONE | ROW | PAGE }
  , FILETABLE_DIRECTORY = 'directory_name'
  , FILETABLE_COLLATE_FILENAME = collation_name
)
```

### DATA_COMPRESSION values
| Value | Description |
|-------|-------------|
| `NONE` | No compression (default) |
| `ROW` | Row-level compression (minimal CPU overhead) |
| `PAGE` | Page-level compression (better ratio, more CPU) |

## Temporal Tables (System-Versioned)

```sql
CREATE TABLE dbo.Employee
(
    EmployeeId   INT           NOT NULL CONSTRAINT PK_Employee PRIMARY KEY,
    Name         NVARCHAR(200) NOT NULL,
    Salary       MONEY         NOT NULL,
    ValidFrom    DATETIME2     GENERATED ALWAYS AS ROW START NOT NULL,
    ValidTo      DATETIME2     GENERATED ALWAYS AS ROW END   NOT NULL,
    PERIOD FOR SYSTEM_TIME (ValidFrom, ValidTo)
)
WITH (SYSTEM_VERSIONING = ON (HISTORY_TABLE = dbo.EmployeeHistory));
GO
```

## Partitioned Tables

```sql
-- Step 1: Create partition function
CREATE PARTITION FUNCTION pf_OrderDate (DATETIME2)
AS RANGE RIGHT FOR VALUES ('2022-01-01', '2023-01-01', '2024-01-01');

-- Step 2: Create partition scheme
CREATE PARTITION SCHEME ps_OrderDate
AS PARTITION pf_OrderDate
TO ([FG2022], [FG2023], [FG2024], [FG2025]);

-- Step 3: Create partitioned table
CREATE TABLE sales.Order
(
    OrderId   INT      NOT NULL,
    OrderDate DATETIME2 NOT NULL,
    ...
    CONSTRAINT PK_Order PRIMARY KEY CLUSTERED (OrderId, OrderDate)
)
ON ps_OrderDate(OrderDate);
```

## Conditional Create Pattern

```sql
IF NOT EXISTS (
    SELECT 1
    FROM sys.tables t
    JOIN sys.schemas s ON t.schema_id = s.schema_id
    WHERE t.name = N'Customer'
      AND s.name = N'sales'
)
BEGIN
    CREATE TABLE sales.Customer
    (
        CustomerId   INT           NOT NULL IDENTITY(1,1),
        CustomerName NVARCHAR(200) NOT NULL,
        Email        NVARCHAR(256) NULL,
        IsActive     BIT           NOT NULL CONSTRAINT DF_Customer_IsActive DEFAULT 1,
        CreatedAt    DATETIME2     NOT NULL CONSTRAINT DF_Customer_CreatedAt DEFAULT GETDATE(),
        CONSTRAINT PK_Customer PRIMARY KEY CLUSTERED (CustomerId),
        CONSTRAINT UQ_Customer_Email UNIQUE NONCLUSTERED (Email)
    );
END;
GO
```

## Complete Example

```sql
CREATE TABLE sales.OrderLine
(
    OrderLineId  INT            NOT NULL IDENTITY(1,1),
    OrderId      INT            NOT NULL,
    ProductId    INT            NOT NULL,
    Quantity     INT            NOT NULL CONSTRAINT CK_OrderLine_Quantity CHECK (Quantity > 0),
    UnitPrice    DECIMAL(18,4)  NOT NULL CONSTRAINT CK_OrderLine_UnitPrice CHECK (UnitPrice >= 0),
    Discount     DECIMAL(5,2)   NOT NULL CONSTRAINT DF_OrderLine_Discount DEFAULT 0.00,
    LineTotal    AS (Quantity * UnitPrice * (1 - Discount / 100)) PERSISTED,
    CreatedAt    DATETIME2      NOT NULL CONSTRAINT DF_OrderLine_CreatedAt DEFAULT GETDATE(),
    UpdatedAt    DATETIME2      NOT NULL CONSTRAINT DF_OrderLine_UpdatedAt DEFAULT GETDATE(),

    CONSTRAINT PK_OrderLine
        PRIMARY KEY CLUSTERED (OrderLineId),

    CONSTRAINT UQ_OrderLine_OrderProduct
        UNIQUE NONCLUSTERED (OrderId, ProductId),

    CONSTRAINT FK_OrderLine_Order
        FOREIGN KEY (OrderId)
        REFERENCES sales.[Order](OrderId)
        ON DELETE CASCADE
        ON UPDATE NO ACTION,

    CONSTRAINT FK_OrderLine_Product
        FOREIGN KEY (ProductId)
        REFERENCES catalog.Product(ProductId)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
)
WITH (DATA_COMPRESSION = ROW);
GO
```

## System Views for Inspection

```sql
-- Check if table exists
SELECT t.name, s.name AS SchemaName, t.create_date
FROM sys.tables t
JOIN sys.schemas s ON t.schema_id = s.schema_id
WHERE t.name = N'OrderLine' AND s.name = N'sales';

-- List all columns
SELECT c.name, tp.name AS DataType, c.max_length, c.precision, c.scale,
       c.is_nullable, c.is_identity, c.default_object_id
FROM sys.columns c
JOIN sys.types tp ON c.user_type_id = tp.user_type_id
WHERE c.object_id = OBJECT_ID(N'sales.OrderLine')
ORDER BY c.column_id;

-- List constraints
SELECT name, type_desc, definition
FROM sys.check_constraints
WHERE parent_object_id = OBJECT_ID(N'sales.OrderLine');
```
