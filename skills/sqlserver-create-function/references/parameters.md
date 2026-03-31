# SQL Server CREATE FUNCTION — Parameter Reference

## Full Syntax

### Scalar Function
```sql
CREATE [ OR ALTER ] FUNCTION [ schema_name. ] function_name
(
    [ { @parameter_name [ AS ] [ type_schema_name. ] parameter_data_type [ = default ] [ READONLY ] }
      [ ,...n ] ]
)
RETURNS return_data_type
    [ WITH <function_option> [ ,...n ] ]
    [ AS ]
    BEGIN
        function_body
        RETURN scalar_expression
    END
[ ; ]
```

### Inline Table-Valued Function (TVF)
```sql
CREATE [ OR ALTER ] FUNCTION [ schema_name. ] function_name
(
    [ { @parameter_name [ AS ] [ type_schema_name. ] parameter_data_type [ = default ] [ READONLY ] }
      [ ,...n ] ]
)
RETURNS TABLE
    [ WITH <function_option> [ ,...n ] ]
    [ AS ]
    RETURN [ ( ] select_statement [ ) ]
[ ; ]
```

### Multi-Statement Table-Valued Function (MSTVF)
```sql
CREATE [ OR ALTER ] FUNCTION [ schema_name. ] function_name
(
    [ { @parameter_name [ AS ] [ type_schema_name. ] parameter_data_type [ = default ] [ READONLY ] }
      [ ,...n ] ]
)
RETURNS @return_variable TABLE <table_type_definition>
    [ WITH <function_option> [ ,...n ] ]
    [ AS ]
    BEGIN
        function_body
        RETURN
    END
[ ; ]

<table_type_definition> ::=
(
    { <column_definition> <column_constraint>
    | <computed_column_definition>
    | <table_constraint> }
    [ ,...n ]
)
```

### WITH Options
```sql
<function_option> ::=
{
    ENCRYPTION
  | SCHEMABINDING
  | RETURNS NULL ON NULL INPUT | CALLED ON NULL INPUT
  | EXECUTE AS { CALLER | SELF | OWNER | 'user_name' }
  | INLINE = { ON | OFF }
}
```

## Function Types Comparison

| Type | Syntax | Returns | Performance | Use Case |
|------|--------|---------|-------------|----------|
| Scalar | `RETURNS <type>` | Single value | Can be slow when called per-row | Reusable calculations, formatting |
| Inline TVF (ITVF) | `RETURNS TABLE AS RETURN (...)` | Table | Best — inlined like a view | Parameterized views, row filters |
| Multi-statement TVF (MSTVF) | `RETURNS @t TABLE (...) AS BEGIN...END` | Table | Slower — opaque to optimizer | Complex logic requiring multiple statements |

**Prefer Inline TVF over Multi-Statement TVF whenever possible.**

## WITH Options Detail

### SCHEMABINDING
- Binds the function to the schema of referenced objects.
- Prevents modifications to referenced objects (ALTER/DROP of columns or tables).
- Required to create an indexed computed column or indexed view using this function.
- All referenced objects must use two-part names (`schema.object`).

### ENCRYPTION
- Obfuscates the function definition in `sys.sql_modules`.
- Cannot be recovered — keep source DDL in version control.

### RETURNS NULL ON NULL INPUT
- If any input parameter is NULL, the function automatically returns NULL without executing.
- Can improve performance when NULL handling is straightforward.

### CALLED ON NULL INPUT (default)
- Function executes normally even when input parameters are NULL.
- The function body must handle NULL explicitly.

### EXECUTE AS
- Specifies the security context for the function execution.
- Same options as procedures: CALLER (default), SELF, OWNER, or a named user.

### INLINE = ON | OFF
- Controls whether scalar UDFs are inlined into the calling query (SQL Server 2019+).
- `INLINE = ON` (default when eligible): scalar UDF is expanded inline, enabling better optimization.
- `INLINE = OFF`: forces the function to execute as a black box (legacy behavior).

## Scalar Function Example

```sql
CREATE OR ALTER FUNCTION dbo.ufn_format_phone
(
    @PhoneNumber NVARCHAR(20)
)
RETURNS NVARCHAR(20)
WITH SCHEMABINDING
AS
BEGIN
    DECLARE @Cleaned NVARCHAR(20) = '';
    DECLARE @i INT = 1;

    -- Remove non-numeric characters
    WHILE @i <= LEN(@PhoneNumber)
    BEGIN
        IF SUBSTRING(@PhoneNumber, @i, 1) LIKE '[0-9]'
            SET @Cleaned = @Cleaned + SUBSTRING(@PhoneNumber, @i, 1);
        SET @i = @i + 1;
    END;

    RETURN CASE
        WHEN LEN(@Cleaned) = 10
            THEN '(' + SUBSTRING(@Cleaned, 1, 3) + ') ' +
                       SUBSTRING(@Cleaned, 4, 3) + '-' +
                       SUBSTRING(@Cleaned, 7, 4)
        ELSE @PhoneNumber
    END;
END;
GO

-- Usage
SELECT dbo.ufn_format_phone(N'5551234567'); -- Returns (555) 123-4567
```

## Inline Table-Valued Function Example

```sql
CREATE OR ALTER FUNCTION sales.uft_get_customer_orders
(
    @CustomerId INT,
    @StartDate  DATE = NULL,
    @EndDate    DATE = NULL
)
RETURNS TABLE
WITH SCHEMABINDING
AS
RETURN
(
    SELECT
        o.OrderId,
        o.OrderDate,
        o.Status,
        SUM(ol.LineTotal) AS TotalAmount,
        COUNT(ol.OrderLineId) AS LineCount
    FROM sales.[Order] o
    JOIN sales.OrderLine ol ON o.OrderId = ol.OrderId
    WHERE o.CustomerId = @CustomerId
      AND (@StartDate IS NULL OR CAST(o.OrderDate AS DATE) >= @StartDate)
      AND (@EndDate   IS NULL OR CAST(o.OrderDate AS DATE) <= @EndDate)
    GROUP BY o.OrderId, o.OrderDate, o.Status
);
GO

-- Usage (treated like a parameterized view)
SELECT * FROM sales.uft_get_customer_orders(42, '2024-01-01', '2024-12-31');

-- Can be JOINed
SELECT c.CustomerName, co.*
FROM sales.Customer c
CROSS APPLY sales.uft_get_customer_orders(c.CustomerId, '2024-01-01', NULL) co
WHERE c.IsActive = 1;
```

## Multi-Statement Table-Valued Function Example

```sql
CREATE OR ALTER FUNCTION hr.uft_get_employee_hierarchy
(
    @ManagerId INT
)
RETURNS @Result TABLE
(
    EmployeeId   INT          NOT NULL,
    EmployeeName NVARCHAR(200) NOT NULL,
    Level        INT          NOT NULL,
    ManagerId    INT          NULL
)
AS
BEGIN
    -- Use recursive CTE to build hierarchy
    WITH OrgChart AS
    (
        -- Anchor: direct reports of the manager
        SELECT e.EmployeeId, e.Name, 1 AS Level, e.ManagerId
        FROM hr.Employee e
        WHERE e.ManagerId = @ManagerId

        UNION ALL

        -- Recursive: reports of reports
        SELECT e.EmployeeId, e.Name, oc.Level + 1, e.ManagerId
        FROM hr.Employee e
        JOIN OrgChart oc ON e.ManagerId = oc.EmployeeId
    )
    INSERT INTO @Result
    SELECT EmployeeId, Name, Level, ManagerId
    FROM OrgChart;

    RETURN;
END;
GO

-- Usage
SELECT * FROM hr.uft_get_employee_hierarchy(10) ORDER BY Level, EmployeeName;
```

## APPLY Operators with TVFs

```sql
-- CROSS APPLY: returns rows only when TVF returns results
SELECT c.CustomerId, c.CustomerName, co.OrderId, co.TotalAmount
FROM sales.Customer c
CROSS APPLY sales.uft_get_customer_orders(c.CustomerId, NULL, NULL) co;

-- OUTER APPLY: returns all customers, NULL for those with no orders
SELECT c.CustomerId, c.CustomerName, co.OrderId, co.TotalAmount
FROM sales.Customer c
OUTER APPLY sales.uft_get_customer_orders(c.CustomerId, NULL, NULL) co;
```

## Determinism

A function is deterministic if it always returns the same result for the same inputs.

Requirements for a deterministic function:
- Must use `WITH SCHEMABINDING`.
- Must not call non-deterministic built-ins (GETDATE, RAND, NEWID, etc.).
- All referenced functions must also be deterministic.

Deterministic scalar functions can be used in:
- Indexed computed columns.
- Indexed views (via schemabinding).

```sql
-- Check function determinism
SELECT is_deterministic
FROM sys.sql_modules
WHERE object_id = OBJECT_ID(N'dbo.ufn_format_phone');
```

## System Views for Inspection

```sql
-- List all user-defined functions
SELECT s.name AS SchemaName, o.name AS FunctionName, o.type_desc,
       m.is_schema_bound, m.is_inlineable
FROM sys.objects o
JOIN sys.schemas s ON o.schema_id = s.schema_id
JOIN sys.sql_modules m ON o.object_id = m.object_id
WHERE o.type IN ('FN', 'IF', 'TF')  -- FN=scalar, IF=inline TVF, TF=multi-statement TVF
ORDER BY s.name, o.name;

-- Get function definition
SELECT definition
FROM sys.sql_modules
WHERE object_id = OBJECT_ID(N'sales.uft_get_customer_orders');
```
