# SQL Server CREATE STATISTICS — Parameter Reference

## Full Syntax

```sql
CREATE STATISTICS statistics_name
ON { table_or_indexed_view_name } ( column [ ,...n ] )
[ WHERE <filter_predicate> ]
[ WITH
    [ FULLSCAN
    | SAMPLE number { PERCENT | ROWS }
    | STATS_STREAM = stats_stream ]
    [ [ , ] NORECOMPUTE ]
    [ [ , ] INCREMENTAL = { ON | OFF } ]
    [ [ , ] MAXDOP = max_degree_of_parallelism ]
    [ [ , ] AUTO_DROP = { ON | OFF } ]
]
[ ; ]
```

## Parameters

### statistics_name
- The name of the statistics object.
- Must be unique within the table.
- Convention: `STAT_<table>_<column(s)>` or follow a project naming standard.

### table_or_indexed_view_name
- The table or indexed view on which to create statistics.
- Use schema-qualified names: `schema.table`.

### column [ ,...n ]
- One or more columns on which to compute statistics.
- The first column is most important — SQL Server builds a histogram only on the leading column.
- The statistics object records density (selectivity) across all listed columns.
- Maximum 32 columns per statistics object.

### WHERE filter_predicate
- Creates **filtered statistics** covering only rows that match the predicate.
- Improves cardinality estimates for queries that filter on the same predicate.
- Especially useful for columns with highly skewed distributions or for specific partition ranges.

```sql
CREATE STATISTICS STAT_Order_ShipDate_Shipped
ON sales.[Order] (ShipDate)
WHERE Status = N'Shipped';
```

## WITH Options

### FULLSCAN
- Scans every row in the table to compute statistics.
- Most accurate but slowest for large tables.
- Recommended for small-to-medium tables or when accuracy is critical.

```sql
CREATE STATISTICS STAT_Customer_Region
ON sales.Customer (Region)
WITH FULLSCAN;
```

### SAMPLE number { PERCENT | ROWS }
- Scans only a subset of rows (random sampling).
- `PERCENT`: sample N% of all rows (1–100).
- `ROWS`: sample exactly N rows.
- Faster than FULLSCAN for large tables; less accurate.
- SQL Server uses sampling automatically for auto-statistics; manual statistics can use higher rates.

```sql
-- Sample 20% of rows
CREATE STATISTICS STAT_Order_Amount
ON sales.[Order] (TotalAmount)
WITH SAMPLE 20 PERCENT;

-- Sample 10,000 rows
CREATE STATISTICS STAT_Order_Amount
ON sales.[Order] (TotalAmount)
WITH SAMPLE 10000 ROWS;
```

### NORECOMPUTE
- Disables automatic statistics updates for this statistics object.
- Use only when you want full manual control over statistics maintenance.
- After manual creation with NORECOMPUTE, update manually with `UPDATE STATISTICS`.
- Do NOT use NORECOMPUTE on auto-created statistics (can cause stale stats and poor plans).

```sql
CREATE STATISTICS STAT_Product_Category
ON catalog.Product (CategoryId)
WITH FULLSCAN, NORECOMPUTE;
```

### INCREMENTAL = ON | OFF
- Only applicable to partitioned tables.
- `INCREMENTAL = ON`: Creates per-partition statistics (SQL Server 2014+).
  - When a partition is rebuilt, only that partition's statistics are updated.
  - Requires the table to have a partition function on the statistics column.
- `INCREMENTAL = OFF` (default): Creates global statistics across all partitions.

```sql
CREATE STATISTICS STAT_FactSales_OrderDate
ON dw.FactSales (OrderDate)
WITH FULLSCAN, INCREMENTAL = ON;
```

### MAXDOP = max_degree_of_parallelism
- Limits parallelism for the statistics creation operation (SQL Server 2016 SP2+).
- `0` (default): use server max degree of parallelism setting.
- `1`: single-threaded.

```sql
CREATE STATISTICS STAT_Order_Customer
ON sales.[Order] (CustomerId)
WITH FULLSCAN, MAXDOP = 4;
```

### AUTO_DROP = ON | OFF
- SQL Server 2022+.
- `AUTO_DROP = ON` (default): SQL Server may automatically drop the statistics if they become stale or unused.
- `AUTO_DROP = OFF`: Prevents automatic dropping (use for manually maintained statistics).

## When to Create Manual Statistics

SQL Server creates statistics automatically on:
- All index key columns.
- All columns referenced in query predicates (when `AUTO_CREATE_STATISTICS` is ON).

Create manual statistics when:
- A column is used in a join but not filtered.
- Existing auto-statistics have poor sampling (large table, low sample rate).
- A filtered index exists and you want matching filtered statistics.
- A computed column is referenced in queries.
- Statistics on multiple correlated columns are needed (multi-column statistics).

## Update Statistics

```sql
-- Update specific statistics object
UPDATE STATISTICS sales.[Order] STAT_Order_Amount WITH FULLSCAN;

-- Update all statistics on a table
UPDATE STATISTICS sales.[Order] WITH FULLSCAN;

-- Update all statistics in the database (maintenance job)
EXEC sp_updatestats;
```

## Conditional Create Pattern

```sql
IF NOT EXISTS (
    SELECT 1
    FROM sys.stats
    WHERE object_id = OBJECT_ID(N'sales.Customer')
      AND name = N'STAT_Customer_Region'
)
BEGIN
    CREATE STATISTICS STAT_Customer_Region
    ON sales.Customer (Region)
    WITH FULLSCAN;
END;
GO
```

## Multi-Column Statistics Example

```sql
-- Multi-column statistics for correlated columns
CREATE STATISTICS STAT_Order_CustomerStatus
ON sales.[Order] (CustomerId, Status)
WITH FULLSCAN;
```

## Filtered Statistics Example

```sql
-- Statistics for only active customers (matches a filtered index)
CREATE STATISTICS STAT_Customer_Email_Active
ON sales.Customer (Email, Region)
WHERE IsActive = 1
WITH FULLSCAN;
```

## System Views for Inspection

```sql
-- List all statistics on a table
SELECT s.name AS StatisticsName, s.auto_created, s.user_created,
       s.no_recompute, s.is_incremental, s.has_filter, s.filter_definition,
       sp.last_updated, sp.rows, sp.rows_sampled, sp.modification_counter
FROM sys.stats s
CROSS APPLY sys.dm_db_stats_properties(s.object_id, s.stats_id) sp
WHERE s.object_id = OBJECT_ID(N'sales.Customer')
ORDER BY s.name;

-- List statistics columns
SELECT s.name AS StatisticsName, c.name AS ColumnName, sc.stats_column_id
FROM sys.stats s
JOIN sys.stats_columns sc ON s.object_id = sc.object_id AND s.stats_id = sc.stats_id
JOIN sys.columns c ON sc.object_id = c.object_id AND sc.column_id = c.column_id
WHERE s.object_id = OBJECT_ID(N'sales.Customer')
ORDER BY s.name, sc.stats_column_id;

-- View statistics histogram (DBCC only)
DBCC SHOW_STATISTICS ('sales.Customer', 'STAT_Customer_Region') WITH HISTOGRAM;
```
