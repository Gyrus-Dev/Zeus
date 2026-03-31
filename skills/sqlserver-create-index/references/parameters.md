# SQL Server CREATE INDEX — Parameter Reference

## Full Syntax

```sql
CREATE [ UNIQUE ] [ CLUSTERED | NONCLUSTERED ] INDEX index_name
ON <object> ( column [ ASC | DESC ] [ ,...n ] )
[ INCLUDE ( column_name [ ,...n ] ) ]
[ WHERE <filter_predicate> ]
[ WITH ( <relational_index_option> [ ,...n ] ) ]
[ ON { partition_scheme_name ( column_name )
     | filegroup_name
     | default
     }
]
[ FILESTREAM_ON { filestream_filegroup_name | partition_scheme_name | "NULL" } ]
[ ; ]

<relational_index_option> ::=
{
    PAD_INDEX                  = { ON | OFF }
  | FILLFACTOR                 = fillfactor
  | SORT_IN_TEMPDB             = { ON | OFF }
  | IGNORE_DUP_KEY             = { ON | OFF }
  | STATISTICS_NORECOMPUTE     = { ON | OFF }
  | STATISTICS_INCREMENTAL     = { ON | OFF }
  | DROP_EXISTING              = { ON | OFF }
  | ONLINE                     = { ON | OFF }
  | RESUMABLE                  = { ON | OFF }
  | MAX_DURATION               = <time> [MINUTES]
  | ALLOW_ROW_LOCKS            = { ON | OFF }
  | ALLOW_PAGE_LOCKS           = { ON | OFF }
  | OPTIMIZE_FOR_SEQUENTIAL_KEY = { ON | OFF }
  | MAXDOP                     = max_degree_of_parallelism
  | DATA_COMPRESSION           = { NONE | ROW | PAGE } [ ON PARTITIONS ( ... ) ]
  | XML_COMPRESSION            = { ON | OFF } [ ON PARTITIONS ( ... ) ]
}
```

## Index Types

### Clustered Index
- Determines the physical order of data in the table (similar to a primary key heap sort).
- Only **one** clustered index per table.
- The leaf level of the clustered index IS the table data.
- Automatically created for PRIMARY KEY constraints (clustered by default).

```sql
CREATE CLUSTERED INDEX CX_Order_OrderDate
ON sales.[Order] (OrderDate DESC);
```

### Nonclustered Index
- Separate B-tree structure with pointers back to the clustered index or heap.
- Up to **999** nonclustered indexes per table.
- Default when CLUSTERED/NONCLUSTERED not specified.

```sql
CREATE NONCLUSTERED INDEX IX_Customer_Email
ON sales.Customer (Email ASC);
```

### Unique Index
- Enforces uniqueness on the indexed columns.
- A UNIQUE constraint creates a unique nonclustered index internally.

```sql
CREATE UNIQUE NONCLUSTERED INDEX UQ_Customer_Email
ON sales.Customer (Email ASC)
WHERE Email IS NOT NULL;  -- Filtered unique index
```

## Key Parameters

### INCLUDE columns
- Adds non-key columns to the leaf level of the index.
- Allows the index to "cover" a query without widening the key.
- Covered queries retrieve all needed columns from the index without accessing the base table.
- Maximum 1023 include columns.

```sql
CREATE NONCLUSTERED INDEX IX_OrderLine_ProductId
ON sales.OrderLine (ProductId ASC)
INCLUDE (Quantity, UnitPrice, LineTotal);
```

### WHERE (Filtered Index)
- Creates an index over a subset of rows matching the predicate.
- Reduces index size and improves performance for queries on that subset.
- The filter predicate must use simple comparison expressions.

```sql
-- Index only active records
CREATE NONCLUSTERED INDEX IX_Customer_Email_Active
ON sales.Customer (Email ASC)
WHERE IsActive = 1;

-- Index only non-null values
CREATE NONCLUSTERED INDEX IX_Order_ShipDate
ON sales.[Order] (ShipDate ASC)
WHERE ShipDate IS NOT NULL;
```

## WITH Options Detail

| Option | Default | Description |
|--------|---------|-------------|
| `PAD_INDEX` | OFF | Apply FILLFACTOR to intermediate index pages |
| `FILLFACTOR` | 0 (=100%) | % of each leaf page to fill during creation (1–100) |
| `SORT_IN_TEMPDB` | OFF | Store intermediate sort results in tempdb |
| `IGNORE_DUP_KEY` | OFF | Ignore duplicate key errors on INSERT (unique indexes only) |
| `STATISTICS_NORECOMPUTE` | OFF | Disable automatic statistics update for this index |
| `DROP_EXISTING` | OFF | Drop and recreate index if it exists; preserves index position in clustered rebuild |
| `ONLINE` | OFF | Allow concurrent DML during index build (Enterprise edition) |
| `RESUMABLE` | OFF | Allow index build to be paused and resumed |
| `ALLOW_ROW_LOCKS` | ON | Allow row-level locking |
| `ALLOW_PAGE_LOCKS` | ON | Allow page-level locking |
| `MAXDOP` | 0 (auto) | Maximum degree of parallelism for the index operation |
| `DATA_COMPRESSION` | NONE | Row or page compression for the index |
| `OPTIMIZE_FOR_SEQUENTIAL_KEY` | OFF | Optimize for last-page insert contention (IDENTITY columns, sequences) |

### FILLFACTOR Guidance
| Scenario | Recommended FILLFACTOR |
|----------|----------------------|
| Read-mostly table | 90–100 |
| Moderate inserts/updates | 70–90 |
| Heavy inserts (e.g., log tables) | 60–80 |
| Sequential key (IDENTITY) | 100 with OPTIMIZE_FOR_SEQUENTIAL_KEY |

## Columnstore Indexes

### Clustered Columnstore Index
- Replaces the rowstore with a column-oriented storage format.
- Best for data warehouse / analytical workloads.
- Only one per table; table cannot have a clustered rowstore index at the same time.

```sql
CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales
ON dw.FactSales
WITH (DROP_EXISTING = OFF, COMPRESSION_DELAY = 0);
```

### Nonclustered Columnstore Index
- Adds column-oriented storage alongside existing rowstore.
- Best for mixed OLTP/analytics ("operational analytics").

```sql
CREATE NONCLUSTERED COLUMNSTORE INDEX NCCI_OrderLine_Analytics
ON sales.OrderLine (OrderId, ProductId, Quantity, UnitPrice, LineTotal);
```

## Partitioned Index

```sql
CREATE NONCLUSTERED INDEX IX_Order_OrderDate
ON sales.[Order] (OrderDate ASC)
ON ps_OrderDate(OrderDate);  -- partition scheme
```

## Conditional Create Pattern

```sql
-- Check before creating (avoid error on duplicate)
IF NOT EXISTS (
    SELECT 1
    FROM sys.indexes
    WHERE object_id = OBJECT_ID(N'sales.Customer')
      AND name = N'IX_Customer_Email'
)
BEGIN
    CREATE NONCLUSTERED INDEX IX_Customer_Email
    ON sales.Customer (Email ASC)
    WHERE IsActive = 1;
END;
GO

-- Alternatively, use DROP_EXISTING to rebuild:
CREATE NONCLUSTERED INDEX IX_Customer_Email
ON sales.Customer (Email ASC)
WITH (DROP_EXISTING = ON);
GO
```

## Index Rebuild and Reorganize

```sql
-- Rebuild (offline by default, updates statistics)
ALTER INDEX IX_Customer_Email ON sales.Customer REBUILD
WITH (ONLINE = ON, DATA_COMPRESSION = ROW);

-- Reorganize (always online, less thorough than rebuild)
ALTER INDEX IX_Customer_Email ON sales.Customer REORGANIZE;

-- Rebuild all indexes on a table
ALTER INDEX ALL ON sales.Customer REBUILD;

-- Disable an index
ALTER INDEX IX_Customer_Email ON sales.Customer DISABLE;
```

## System Views for Inspection

```sql
-- List all indexes on a table
SELECT i.name, i.type_desc, i.is_unique, i.is_primary_key, i.is_disabled,
       i.fill_factor, i.has_filter, i.filter_definition
FROM sys.indexes i
WHERE i.object_id = OBJECT_ID(N'sales.Customer');

-- List index columns
SELECT i.name AS IndexName, c.name AS ColumnName, ic.is_included_column,
       ic.key_ordinal, ic.is_descending_key
FROM sys.indexes i
JOIN sys.index_columns ic ON i.object_id = ic.object_id AND i.index_id = ic.index_id
JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE i.object_id = OBJECT_ID(N'sales.Customer')
ORDER BY i.name, ic.key_ordinal;

-- Index fragmentation
SELECT i.name, ips.avg_fragmentation_in_percent, ips.page_count
FROM sys.dm_db_index_physical_stats(DB_ID(), OBJECT_ID(N'sales.Customer'), NULL, NULL, 'LIMITED') ips
JOIN sys.indexes i ON ips.object_id = i.object_id AND ips.index_id = i.index_id;
```
