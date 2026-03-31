# Business Rules for SQL Server Data Analyst

## Metric Definitions

- **Revenue**: `SUM(Amount) WHERE Status = 'Completed'`
- **Active Customers**: `COUNT(DISTINCT CustomerId) WHERE IsActive = 1`
- **Average Order Value (AOV)**: `SUM(TotalAmount) / COUNT(OrderId)` for completed orders
- **Gross Margin**: `(Revenue - COGS) / Revenue * 100`
- **Churn Rate**: customers active last period but not this period / customers active last period

---

## Canonical Date Columns

- Use `DATETIME2` columns for all time-series analysis (higher precision than DATETIME).
- Created/updated timestamps: `CreatedAt`, `UpdatedAt` (DATETIME2).
- Business date (no time): `OrderDate`, `ShipDate`, `DueDate` (DATE type).
- **"Today"**: `CAST(GETDATE() AS DATE)`
- **"This month"**: `DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)` through `EOMONTH(GETDATE())`
- **"Last month"**: `DATEADD(MONTH, -1, GETDATE())`
- **"Last year"**: `DATEADD(YEAR, -1, GETDATE())`
- **"Year to date"**: `DATEADD(YEAR, DATEDIFF(YEAR, 0, GETDATE()), 0)` through today

---

## Common Date Calculations

```sql
-- Start of current month
DATEADD(MONTH, DATEDIFF(MONTH, 0, GETDATE()), 0)

-- End of current month
EOMONTH(GETDATE())

-- Start of current year
DATEADD(YEAR, DATEDIFF(YEAR, 0, GETDATE()), 0)

-- Days between two dates
DATEDIFF(DAY, StartDate, EndDate)

-- Months between two dates
DATEDIFF(MONTH, StartDate, EndDate)

-- Add N days
DATEADD(DAY, N, DateColumn)

-- Truncate to day (remove time component)
CAST(DateTimeColumn AS DATE)

-- Truncate to month
DATEADD(MONTH, DATEDIFF(MONTH, 0, DateColumn), 0)

-- Format as string
FORMAT(DateColumn, 'yyyy-MM-dd')
FORMAT(DateColumn, 'MMM yyyy')   -- e.g., Jan 2024
```

---

## SQL Server Specific Syntax Rules

### Row Limiting
- Use `TOP N` instead of `LIMIT N` (SQL Server / T-SQL):
```sql
SELECT TOP 10 * FROM sales.Customer ORDER BY CreatedAt DESC;
SELECT TOP (10) PERCENT * FROM sales.Customer ORDER BY CreatedAt DESC;
```

### NULL Handling
- Use `ISNULL(column, default_value)` for single-column NULL replacement:
```sql
ISNULL(ShipDate, GETDATE())
ISNULL(Notes, N'No notes')
```
- Use `COALESCE(col1, col2, default)` for multiple expressions:
```sql
COALESCE(MobilePhone, HomePhone, WorkPhone, N'No phone')
```
- Check for NULL: `column IS NULL`, `column IS NOT NULL` (never `= NULL`).

### String Operations
- Concatenation: use `+` operator or `CONCAT()` function:
```sql
FirstName + N' ' + LastName
CONCAT(FirstName, N' ', LastName)  -- Preferred: handles NULLs gracefully
```
- String length: `LEN(column)` (excludes trailing spaces) or `DATALENGTH(column)` (bytes).
- Uppercase / lowercase: `UPPER(column)`, `LOWER(column)`.
- Trim: `LTRIM(column)`, `RTRIM(column)`, `TRIM(column)` (SQL Server 2017+).
- Substring: `SUBSTRING(column, start, length)` (1-based index).

### Date Formatting
```sql
FORMAT(DateColumn, 'yyyy-MM-dd')          -- ISO: 2024-01-15
FORMAT(DateColumn, 'dd/MM/yyyy')          -- UK: 15/01/2024
FORMAT(DateColumn, 'MM/dd/yyyy')          -- US: 01/15/2024
FORMAT(DateColumn, 'yyyy-MM-dd HH:mm:ss') -- Full timestamp
CONVERT(NVARCHAR, DateColumn, 120)        -- ISO: 2024-01-15 13:45:00 (faster than FORMAT)
```

### Type Casting
```sql
CAST(column AS INT)
CAST(column AS DECIMAL(18,2))
CAST(column AS NVARCHAR(50))
CONVERT(INT, column)           -- SQL Server style (equivalent to CAST for most cases)
TRY_CAST(column AS INT)        -- Returns NULL if conversion fails (safe)
TRY_CONVERT(INT, column)       -- Returns NULL if conversion fails (safe)
```

---

## Common JOIN Patterns

- **Always use explicit JOIN syntax** — never comma-separated FROM clause.
- Prefer `INNER JOIN` for fact tables where all rows are expected to match.
- Prefer `LEFT JOIN` for optional dimensions where some rows may not have matches.
- Use `EXISTS` instead of `IN` for large subquery result sets (better performance).

```sql
-- Correct: explicit JOIN
SELECT o.OrderId, c.CustomerName
FROM sales.[Order] o
INNER JOIN sales.Customer c ON o.CustomerId = c.CustomerId;

-- Correct: LEFT JOIN for optional dimension
SELECT p.ProductId, p.ProductName, r.ReviewText
FROM catalog.Product p
LEFT JOIN catalog.ProductReview r ON p.ProductId = r.ProductId;

-- EXISTS instead of IN (preferred for performance)
SELECT CustomerId, CustomerName
FROM sales.Customer c
WHERE EXISTS (
    SELECT 1 FROM sales.[Order] o WHERE o.CustomerId = c.CustomerId
);
```

---

## Window Functions

```sql
-- Row number within partition
ROW_NUMBER() OVER (PARTITION BY CustomerId ORDER BY OrderDate DESC) AS RowNum

-- Rank (ties get same rank, gaps after)
RANK() OVER (PARTITION BY Region ORDER BY TotalRevenue DESC) AS RegionRank

-- Dense rank (ties get same rank, no gaps)
DENSE_RANK() OVER (ORDER BY TotalRevenue DESC) AS RevenueRank

-- Running total
SUM(Amount) OVER (PARTITION BY CustomerId ORDER BY OrderDate ROWS UNBOUNDED PRECEDING) AS RunningTotal

-- Moving average (last 7 days)
AVG(DailySales) OVER (ORDER BY OrderDate ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS MovingAvg7

-- Lag / Lead
LAG(TotalAmount, 1, 0) OVER (PARTITION BY CustomerId ORDER BY OrderDate) AS PrevOrderAmount
LEAD(TotalAmount, 1, 0) OVER (PARTITION BY CustomerId ORDER BY OrderDate) AS NextOrderAmount

-- First / Last value in partition
FIRST_VALUE(OrderDate) OVER (PARTITION BY CustomerId ORDER BY OrderDate) AS FirstOrderDate
LAST_VALUE(OrderDate) OVER (PARTITION BY CustomerId ORDER BY OrderDate
    ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING) AS LastOrderDate

-- Percent rank
PERCENT_RANK() OVER (ORDER BY TotalRevenue) AS PctRank

-- NTILE (quartiles)
NTILE(4) OVER (ORDER BY TotalRevenue) AS Quartile
```

---

## Aggregation Patterns

```sql
-- Standard aggregates
COUNT(*)                      -- Count all rows including NULLs
COUNT(column)                 -- Count non-NULL values
COUNT(DISTINCT column)        -- Count distinct non-NULL values
SUM(column)                   -- Sum (NULL safe: NULLs ignored)
AVG(column)                   -- Average (NULLs ignored)
MIN(column)
MAX(column)

-- Conditional aggregation
SUM(CASE WHEN Status = 'Completed' THEN Amount ELSE 0 END) AS CompletedRevenue
COUNT(CASE WHEN IsActive = 1 THEN 1 END) AS ActiveCount
AVG(CASE WHEN Region = 'West' THEN Score END) AS WestAvgScore

-- STRING_AGG (SQL Server 2017+, equivalent to GROUP_CONCAT / string_agg)
STRING_AGG(ProductName, ', ') WITHIN GROUP (ORDER BY ProductName) AS ProductList
```

---

## Common Table Expressions (CTEs)

```sql
-- Simple CTE
WITH OrderTotals AS (
    SELECT
        CustomerId,
        COUNT(OrderId)   AS OrderCount,
        SUM(TotalAmount) AS TotalSpent
    FROM sales.[Order]
    WHERE Status = N'Completed'
    GROUP BY CustomerId
)
SELECT
    c.CustomerName,
    ot.OrderCount,
    ot.TotalSpent
FROM sales.Customer c
JOIN OrderTotals ot ON c.CustomerId = ot.CustomerId
ORDER BY ot.TotalSpent DESC;

-- Recursive CTE (hierarchy)
WITH OrgChart AS (
    SELECT EmployeeId, Name, ManagerId, 0 AS Level
    FROM hr.Employee
    WHERE ManagerId IS NULL  -- Root

    UNION ALL

    SELECT e.EmployeeId, e.Name, e.ManagerId, oc.Level + 1
    FROM hr.Employee e
    JOIN OrgChart oc ON e.ManagerId = oc.EmployeeId
)
SELECT * FROM OrgChart ORDER BY Level, Name;
```

---

## Pivot and Unpivot

```sql
-- PIVOT: rows to columns
SELECT *
FROM (
    SELECT Region, Status, TotalAmount
    FROM sales.[Order]
) AS SourceTable
PIVOT (
    SUM(TotalAmount)
    FOR Status IN ([Pending], [Processing], [Completed], [Cancelled])
) AS PivotTable;

-- Dynamic PIVOT (when columns are not known at design time)
DECLARE @Cols NVARCHAR(MAX);
SELECT @Cols = STRING_AGG(QUOTENAME(Status), ',') FROM (SELECT DISTINCT Status FROM sales.[Order]) t;

DECLARE @SQL NVARCHAR(MAX) = N'
SELECT * FROM (SELECT Region, Status, TotalAmount FROM sales.[Order]) src
PIVOT (SUM(TotalAmount) FOR Status IN (' + @Cols + N')) pvt';

EXEC sp_executesql @SQL;
```

---

## Performance Guidelines

- Avoid `SELECT *` in production queries; enumerate needed columns.
- Avoid functions on indexed columns in WHERE clauses (prevents index seeks):
  ```sql
  -- Bad (table scan):
  WHERE YEAR(OrderDate) = 2024

  -- Good (index seek):
  WHERE OrderDate >= '2024-01-01' AND OrderDate < '2025-01-01'
  ```
- Use `EXISTS` instead of `COUNT(*) > 0` for existence checks.
- Use `TOP 1` with `ORDER BY` instead of `MIN`/`MAX` subqueries when you need the full row.
- Avoid `NOLOCK` hint unless acceptable to read dirty data.
- For large result sets, prefer `OFFSET ... FETCH NEXT` for pagination:
  ```sql
  SELECT * FROM sales.Customer
  ORDER BY CustomerId
  OFFSET 100 ROWS FETCH NEXT 50 ROWS ONLY;
  ```
