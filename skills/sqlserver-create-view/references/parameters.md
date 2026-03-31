# SQL Server CREATE VIEW — Parameter Reference

## Full Syntax

```sql
CREATE [ OR ALTER ] VIEW [ schema_name . ] view_name
    [ ( column [ ,...n ] ) ]
    [ WITH <view_attribute> [ ,...n ] ]
AS
    select_statement
[ WITH CHECK OPTION ]
[ ; ]

<view_attribute> ::=
{
    ENCRYPTION
  | SCHEMABINDING
  | VIEW_METADATA
}
```

## Parameters

### OR ALTER
- If the view exists, alters it; if it does not exist, creates it.
- Equivalent to dropping and recreating, but preserves existing permissions.
- Preferred over `CREATE OR REPLACE` (PostgreSQL syntax — not valid in SQL Server).

### column
- Optional list of column aliases for the result set.
- Required when: two or more columns would have the same name, a column is a computed expression without an alias, or a column is derived from a built-in function or aggregate.

### WITH ENCRYPTION
- Obfuscates the text of the CREATE VIEW statement in `sys.sql_modules` and `sys.syscomments`.
- The original text cannot be recovered after encryption — keep the source DDL in source control.
- Prevents use of `sp_helptext` to view the definition.

### WITH SCHEMABINDING
- Binds the view to the schema of the underlying objects.
- Prevents modifications to underlying tables that would affect the view (ALTER or DROP of referenced columns/tables).
- **Required** for creating an indexed (materialized) view.
- All objects must be referenced using two-part names (`schema.object`).
- Cannot use `SELECT *`, `COUNT(*)`, or non-schema-bound functions.

### WITH VIEW_METADATA
- Causes SQL Server to return metadata about the view (not the underlying tables) to DB-Library, ODBC, and OLE DB APIs for browse-mode queries.
- Allows the view to be used for positioned updates when the SELECT is updateable.

### WITH CHECK OPTION
- Ensures all data modifications through the view satisfy the WHERE clause of the SELECT statement.
- INSERT or UPDATE that would make the row invisible through the view are rejected.
- Only applies to updateable views.

## Standard View Example

```sql
CREATE OR ALTER VIEW sales.v_ActiveCustomers
AS
    SELECT
        c.CustomerId,
        c.CustomerName,
        c.Email,
        c.CreatedAt
    FROM sales.Customer c
    WHERE c.IsActive = 1;
GO
```

## View with Column Aliases

```sql
CREATE OR ALTER VIEW sales.v_OrderSummary
    (OrderId, CustomerName, TotalAmount, OrderDate)
AS
    SELECT
        o.OrderId,
        c.CustomerName,
        SUM(ol.LineTotal),
        o.OrderDate
    FROM sales.[Order] o
    JOIN sales.Customer c  ON o.CustomerId = c.CustomerId
    JOIN sales.OrderLine ol ON o.OrderId = ol.OrderId
    GROUP BY o.OrderId, c.CustomerName, o.OrderDate;
GO
```

## View with SCHEMABINDING

```sql
CREATE OR ALTER VIEW sales.v_ProductRevenue
WITH SCHEMABINDING
AS
    SELECT
        p.ProductId,
        p.ProductName,
        SUM(ol.Quantity * ol.UnitPrice) AS TotalRevenue,
        COUNT_BIG(*)                    AS LineCount
    FROM catalog.Product p
    JOIN sales.OrderLine ol ON p.ProductId = ol.ProductId
    GROUP BY p.ProductId, p.ProductName;
GO
```

## Indexed (Materialized) View

An indexed view requires:
1. `WITH SCHEMABINDING`
2. A `UNIQUE CLUSTERED INDEX` as the first index

```sql
-- Step 1: Create the view with SCHEMABINDING
CREATE OR ALTER VIEW sales.v_DailyRevenue
WITH SCHEMABINDING
AS
    SELECT
        CAST(o.OrderDate AS DATE)   AS OrderDay,
        o.CustomerId,
        SUM(ol.LineTotal)           AS DailyTotal,
        COUNT_BIG(*)                AS LineCount
    FROM sales.[Order] o
    JOIN sales.OrderLine ol ON o.OrderId = ol.OrderId
    GROUP BY CAST(o.OrderDate AS DATE), o.CustomerId;
GO

-- Step 2: Create the unique clustered index (materializes the view)
CREATE UNIQUE CLUSTERED INDEX CX_v_DailyRevenue
ON sales.v_DailyRevenue (OrderDay, CustomerId);
GO

-- Optional: Add non-clustered indexes
CREATE NONCLUSTERED INDEX IX_v_DailyRevenue_Customer
ON sales.v_DailyRevenue (CustomerId);
GO
```

### Indexed View Restrictions
- Cannot use `SELECT *`, `DISTINCT`, `TOP`, `UNION`, `EXCEPT`, `INTERSECT`, `ORDER BY`.
- Cannot reference other views, non-deterministic functions, or `OUTER JOIN` (with some exceptions).
- Aggregate functions allowed: `SUM`, `COUNT_BIG`, `MIN`, `MAX`, `AVG` (AVG must be paired with COUNT_BIG).
- Must use `COUNT_BIG(*)` instead of `COUNT(*)`.
- Subqueries not allowed in the view body.

## View with CHECK OPTION

```sql
CREATE OR ALTER VIEW sales.v_ActiveCustomerPortal
AS
    SELECT CustomerId, CustomerName, Email, IsActive
    FROM sales.Customer
    WHERE IsActive = 1
WITH CHECK OPTION;
GO

-- This will fail because IsActive = 0 violates the WHERE clause:
-- UPDATE sales.v_ActiveCustomerPortal SET IsActive = 0 WHERE CustomerId = 1;
```

## View with ENCRYPTION

```sql
CREATE OR ALTER VIEW finance.v_SalaryBand
WITH ENCRYPTION
AS
    SELECT
        EmployeeId,
        CASE
            WHEN Salary < 50000  THEN 'Band A'
            WHEN Salary < 100000 THEN 'Band B'
            ELSE 'Band C'
        END AS SalaryBand
    FROM hr.Employee;
GO
```

## Updateable Views

A view is updateable when:
- It references only one base table.
- It does not use `GROUP BY`, `HAVING`, `DISTINCT`, `TOP`, or `UNION`.
- It does not include computed columns in the update target.
- The user has the appropriate permissions on the base table.

## Conditional Create Pattern

SQL Server's `CREATE OR ALTER VIEW` handles idempotency. For older compatibility:

```sql
IF OBJECT_ID(N'sales.v_ActiveCustomers', 'V') IS NOT NULL
    DROP VIEW sales.v_ActiveCustomers;
GO

CREATE VIEW sales.v_ActiveCustomers
AS
    SELECT CustomerId, CustomerName
    FROM sales.Customer
    WHERE IsActive = 1;
GO
```

## System Views for Inspection

```sql
-- List all views in the database
SELECT s.name AS SchemaName, v.name AS ViewName, v.create_date, v.modify_date,
       m.is_schema_bound, m.uses_ansi_nulls
FROM sys.views v
JOIN sys.schemas s ON v.schema_id = s.schema_id
JOIN sys.sql_modules m ON v.object_id = m.object_id
ORDER BY s.name, v.name;

-- Get view definition (if not encrypted)
SELECT definition
FROM sys.sql_modules
WHERE object_id = OBJECT_ID(N'sales.v_ActiveCustomers');

-- Or use built-in function
SELECT OBJECT_DEFINITION(OBJECT_ID(N'sales.v_ActiveCustomers'));

-- List indexed views
SELECT v.name, i.name AS IndexName, i.type_desc
FROM sys.views v
JOIN sys.indexes i ON v.object_id = i.object_id
WHERE i.index_id > 0;
```
