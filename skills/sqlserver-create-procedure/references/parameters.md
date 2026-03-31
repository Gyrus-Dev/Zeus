# SQL Server CREATE PROCEDURE — Parameter Reference

## Full Syntax

```sql
CREATE [ OR ALTER ] { PROC | PROCEDURE }
    [ schema_name. ] procedure_name
    [ ; number ]
    [ { @parameter_name [ type_schema_name. ] data_type }
        [ VARYING ]
        [ = default ]
        [ OUT | OUTPUT ]
        [ READONLY ]
    ] [ ,...n ]
[ WITH <procedure_option> [ ,...n ] ]
[ FOR REPLICATION ]
AS
{ [ BEGIN ] statements [ END ] }
[ ; ]

<procedure_option> ::=
{
    ENCRYPTION
  | RECOMPILE
  | EXECUTE AS { CALLER | SELF | OWNER | 'user_name' }
}
```

## Parameters

### OR ALTER
- Creates the procedure if it does not exist; alters it if it does.
- Preserves existing permissions (unlike DROP + CREATE).
- Preferred over `CREATE OR REPLACE` (PostgreSQL syntax — invalid in SQL Server).

### schema_name
- Schema that owns the procedure.
- Default is the current user's default schema (usually `dbo`).

### procedure_name
- Convention: prefix with `usp_` for user stored procedures (e.g., `usp_get_customers`).

### ; number
- Optional integer to group related procedures (legacy feature, rarely used).

### Parameters

```sql
-- Input parameter (default direction)
@CustomerId INT

-- Input with default value
@Status NVARCHAR(20) = N'Active'

-- Output parameter
@NewOrderId INT OUTPUT

-- Readonly parameter (for table-valued parameters)
@OrderLines dbo.OrderLineTableType READONLY

-- VARYING (for cursor output parameters only)
@ResultCursor CURSOR VARYING OUTPUT
```

### WITH Options

| Option | Description |
|--------|-------------|
| `ENCRYPTION` | Obfuscates the procedure definition in `sys.sql_modules`; cannot be recovered |
| `RECOMPILE` | Forces recompilation on every execution (no plan caching); useful for highly variable queries |
| `EXECUTE AS CALLER` | Execute with the caller's security context (default) |
| `EXECUTE AS SELF` | Execute with the procedure creator's context |
| `EXECUTE AS OWNER` | Execute with the schema/procedure owner's context |
| `EXECUTE AS 'user_name'` | Execute with a specific user's context |

### FOR REPLICATION
- Creates the procedure specifically for use by SQL Server replication.
- Can be executed only during replication; cannot be executed manually.

## Body Patterns

### SET NOCOUNT ON
Always include at the start to suppress "n rows affected" messages:
```sql
AS
BEGIN
    SET NOCOUNT ON;
    ...
END
```

### TRY / CATCH Error Handling

```sql
AS
BEGIN
    SET NOCOUNT ON;

    BEGIN TRY
        -- Your statements here
    END TRY
    BEGIN CATCH
        SELECT
            ERROR_NUMBER()    AS ErrorNumber,
            ERROR_MESSAGE()   AS ErrorMessage,
            ERROR_SEVERITY()  AS ErrorSeverity,
            ERROR_STATE()     AS ErrorState,
            ERROR_LINE()      AS ErrorLine,
            ERROR_PROCEDURE() AS ErrorProcedure;

        -- Optional: re-throw
        THROW;
    END CATCH;
END;
```

### Transaction Pattern with XACT_ABORT

```sql
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;  -- Automatically roll back on error

    BEGIN TRANSACTION;
    BEGIN TRY
        -- Statement 1
        INSERT INTO ...;

        -- Statement 2
        UPDATE ...;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;

        THROW;  -- Re-raise the error to the caller
    END CATCH;
END;
```

### Output Parameter Pattern

```sql
CREATE OR ALTER PROCEDURE sales.usp_create_order
    @CustomerId INT,
    @OrderDate  DATETIME2,
    @NewOrderId INT OUTPUT
AS
BEGIN
    SET NOCOUNT ON;

    INSERT INTO sales.[Order] (CustomerId, OrderDate, Status)
    VALUES (@CustomerId, @OrderDate, N'Pending');

    SET @NewOrderId = SCOPE_IDENTITY();
END;
GO

-- Calling the procedure:
DECLARE @CreatedOrderId INT;
EXEC sales.usp_create_order
    @CustomerId = 42,
    @OrderDate  = '2024-01-15',
    @NewOrderId = @CreatedOrderId OUTPUT;
SELECT @CreatedOrderId AS NewOrderId;
```

### Table-Valued Parameter Pattern

```sql
-- Step 1: Create table type
CREATE TYPE dbo.ProductIdList AS TABLE
(
    ProductId INT NOT NULL PRIMARY KEY
);
GO

-- Step 2: Use in procedure
CREATE OR ALTER PROCEDURE catalog.usp_get_products_by_ids
    @ProductIds dbo.ProductIdList READONLY
AS
BEGIN
    SET NOCOUNT ON;

    SELECT p.ProductId, p.ProductName, p.UnitPrice
    FROM catalog.Product p
    JOIN @ProductIds ids ON p.ProductId = ids.ProductId;
END;
GO

-- Calling:
DECLARE @Ids dbo.ProductIdList;
INSERT INTO @Ids VALUES (1), (2), (3);
EXEC catalog.usp_get_products_by_ids @ProductIds = @Ids;
```

## Complete Example

```sql
CREATE OR ALTER PROCEDURE sales.usp_process_order
    @CustomerId  INT,
    @OrderLines  dbo.OrderLineTableType READONLY,
    @ApplyDiscount BIT            = 0,
    @NewOrderId  INT              OUTPUT
AS
BEGIN
    SET NOCOUNT ON;
    SET XACT_ABORT ON;

    -- Validate customer exists
    IF NOT EXISTS (SELECT 1 FROM sales.Customer WHERE CustomerId = @CustomerId AND IsActive = 1)
    BEGIN
        THROW 50001, N'Customer not found or inactive.', 1;
    END;

    BEGIN TRANSACTION;
    BEGIN TRY
        -- Create order header
        INSERT INTO sales.[Order] (CustomerId, OrderDate, Status)
        VALUES (@CustomerId, GETDATE(), N'Pending');

        SET @NewOrderId = SCOPE_IDENTITY();

        -- Insert order lines
        INSERT INTO sales.OrderLine (OrderId, ProductId, Quantity, UnitPrice, Discount)
        SELECT
            @NewOrderId,
            ol.ProductId,
            ol.Quantity,
            p.UnitPrice,
            CASE WHEN @ApplyDiscount = 1 THEN 10.00 ELSE 0.00 END
        FROM @OrderLines ol
        JOIN catalog.Product p ON ol.ProductId = p.ProductId;

        COMMIT TRANSACTION;
    END TRY
    BEGIN CATCH
        IF @@TRANCOUNT > 0
            ROLLBACK TRANSACTION;
        THROW;
    END CATCH;
END;
GO
```

## System Views for Inspection

```sql
-- List all stored procedures
SELECT s.name AS SchemaName, p.name AS ProcedureName, p.create_date, p.modify_date
FROM sys.procedures p
JOIN sys.schemas s ON p.schema_id = s.schema_id
ORDER BY s.name, p.name;

-- Get procedure definition
SELECT definition
FROM sys.sql_modules
WHERE object_id = OBJECT_ID(N'sales.usp_process_order');

-- List parameters
SELECT name, parameter_id, TYPE_NAME(user_type_id) AS DataType,
       max_length, has_default_value, is_output
FROM sys.parameters
WHERE object_id = OBJECT_ID(N'sales.usp_process_order')
ORDER BY parameter_id;
```
