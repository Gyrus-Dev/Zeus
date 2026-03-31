# SQL Server Full-Text Search — Parameter Reference

Full-Text Search (FTS) is SQL Server's equivalent of PostgreSQL text search configuration. It enables linguistic searches on character and binary column data.

## Architecture

```
Full-Text Catalog
└── Full-Text Index (one per table)
    ├── Column (with LANGUAGE)
    ├── Column (with LANGUAGE)
    └── KEY INDEX (unique index on the table)
```

---

## Prerequisites

```sql
-- Check if Full-Text Search feature is installed
SELECT FULLTEXTSERVICEPROPERTY('IsFullTextInstalled');  -- Returns 1 if installed

-- Enable Full-Text Search on the database (usually auto-enabled)
IF NOT EXISTS (
    SELECT 1 FROM sys.fulltext_catalogs WHERE name = N'DefaultFTCatalog'
)
    CREATE FULLTEXT CATALOG DefaultFTCatalog AS DEFAULT;
```

---

## CREATE FULLTEXT CATALOG

### Syntax

```sql
CREATE FULLTEXT CATALOG catalog_name
    [ ON FILEGROUP filegroup ]
    [ IN PATH 'rootpath' ]
    [ WITH ACCENT_SENSITIVITY = { ON | OFF } ]
    [ AS DEFAULT ]
    [ AUTHORIZATION owner_name ]
[ ; ]
```

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `catalog_name` | Unique name for the full-text catalog | Required |
| `ON FILEGROUP` | Filegroup for the catalog files | PRIMARY |
| `IN PATH` | Physical directory path for catalog files | SQL Server default data directory |
| `WITH ACCENT_SENSITIVITY` | Whether accents are significant (`á` ≠ `a`) | Depends on database collation |
| `AS DEFAULT` | Makes this the default catalog for new full-text indexes | No |
| `AUTHORIZATION` | Catalog owner | Current user |

### Examples

```sql
-- Simple catalog
CREATE FULLTEXT CATALOG ProductSearchCatalog
WITH ACCENT_SENSITIVITY = OFF;
GO

-- Default catalog for the database
CREATE FULLTEXT CATALOG MainFTCatalog
WITH ACCENT_SENSITIVITY = ON
AS DEFAULT;
GO

-- Catalog on specific filegroup
CREATE FULLTEXT CATALOG ArchiveFTCatalog
ON FILEGROUP [SECONDARY]
WITH ACCENT_SENSITIVITY = OFF
AUTHORIZATION dbo;
GO
```

---

## CREATE FULLTEXT INDEX

### Syntax

```sql
CREATE FULLTEXT INDEX ON table_name
    [ ( { column_name
            [ TYPE COLUMN type_column_name ]
            [ LANGUAGE language_term ]
            [ STATISTICAL_SEMANTICS ]
        } [ ,...n ] ) ]
    KEY INDEX index_name
    [ ON <catalog_filegroup_option> ]
    [ WITH [ ( ] <with_option> [ ,...n ] [ ) ] ]
[ ; ]

<catalog_filegroup_option> ::=
{
    fulltext_catalog_name
  | ( fulltext_catalog_name, FILEGROUP filegroup_name )
  | ( FILEGROUP filegroup_name, fulltext_catalog_name )
  | ( FILEGROUP filegroup_name )
}

<with_option> ::=
{
    CHANGE_TRACKING [ = ] { MANUAL | AUTO | OFF [, NO POPULATION] }
  | STOPLIST [ = ] { OFF | SYSTEM | stoplist_name }
  | SEARCH PROPERTY LIST [ = ] property_list_name
}
```

### Parameters

#### Column Options
| Parameter | Description |
|-----------|-------------|
| `column_name` | Column to index; must be char/nchar/varchar/nvarchar/text/ntext/xml/varbinary/image type |
| `TYPE COLUMN type_column_name` | Column that holds file type extension (for varbinary/image columns storing documents) |
| `LANGUAGE language_term` | Language for word breaking and stemming; use LCID (e.g., 1033 for English) |
| `STATISTICAL_SEMANTICS` | Enable semantic indexing (extracts key phrases and document similarity) |

#### KEY INDEX
- The unique, single-column, non-nullable index used to identify rows.
- Usually the primary key index.
- Must be on a single column; composite key indexes are not supported.

#### CHANGE_TRACKING Options
| Value | Description |
|-------|-------------|
| `AUTO` | Full-text index updated automatically after DML changes (default) |
| `MANUAL` | Changes tracked but index not updated until `ALTER FULLTEXT INDEX ... START UPDATE POPULATION` |
| `OFF` | Change tracking disabled; full population required manually |
| `OFF, NO POPULATION` | Change tracking off and no initial population (schedule separately) |

#### STOPLIST Options
| Value | Description |
|-------|-------------|
| `SYSTEM` | Use SQL Server's built-in system stop words (default) |
| `OFF` | No stop words used |
| `stoplist_name` | Use a custom stoplist |

### Examples

```sql
-- Full-text index on product name and description
CREATE FULLTEXT INDEX ON catalog.Product
(
    ProductName     LANGUAGE 1033,  -- English (US)
    Description     LANGUAGE 1033,
    Tags            LANGUAGE 1033
)
KEY INDEX PK_Product
ON ProductSearchCatalog
WITH CHANGE_TRACKING AUTO, STOPLIST = SYSTEM;
GO

-- Full-text index on document content (varbinary column)
CREATE FULLTEXT INDEX ON dbo.Document
(
    FileContent TYPE COLUMN FileExtension LANGUAGE 1033,
    Title       LANGUAGE 1033,
    Keywords    LANGUAGE 1033
)
KEY INDEX PK_Document
ON MainFTCatalog
WITH CHANGE_TRACKING AUTO;
GO

-- Multi-language full-text index
CREATE FULLTEXT INDEX ON catalog.ProductLocalized
(
    NameEN  LANGUAGE N'English',
    NameFR  LANGUAGE N'French',
    NameDE  LANGUAGE N'German',
    NameES  LANGUAGE N'Spanish'
)
KEY INDEX PK_ProductLocalized
ON ProductSearchCatalog
WITH CHANGE_TRACKING AUTO;
GO
```

---

## Full-Text Search Predicates

### CONTAINS

Used in WHERE clauses for precise term matching.

```sql
-- Simple word match
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(ProductName, N'laptop');

-- Multiple words (AND)
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(ProductName, N'"laptop" AND "gaming"');

-- Phrase match (exact phrase)
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(Description, N'"high performance"');

-- Prefix match (word starting with)
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(ProductName, N'"lap*"');

-- Proximity search (words near each other)
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(Description, N'NEAR((laptop, gaming), 5)');

-- Inflectional forms (run, runs, running, ran)
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(Description, N'FORMSOF(INFLECTIONAL, run)');

-- Thesaurus forms
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(Description, N'FORMSOF(THESAURUS, laptop)');

-- Weighted terms
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(Description, N'ISABOUT(laptop WEIGHT(.8), notebook WEIGHT(.4))');

-- Search all full-text columns
SELECT ProductId, ProductName
FROM catalog.Product
WHERE CONTAINS(*, N'laptop');
```

### FREETEXT

Used for natural language searches; less precise but more intuitive.

```sql
-- Natural language search
SELECT ProductId, ProductName
FROM catalog.Product
WHERE FREETEXT(Description, N'lightweight laptop for gaming');

-- Search all full-text indexed columns
SELECT ProductId, ProductName
FROM catalog.Product
WHERE FREETEXT(*, N'affordable wireless headphones');
```

---

## Full-Text Search Functions (Ranked Results)

### CONTAINSTABLE

Returns a table with `KEY` (row key) and `RANK` (relevance score 1–1000).

```sql
SELECT p.ProductId, p.ProductName, ft.RANK
FROM CONTAINSTABLE(catalog.Product, ProductName, N'laptop') ft
JOIN catalog.Product p ON ft.[KEY] = p.ProductId
ORDER BY ft.RANK DESC;

-- With TOP N
SELECT p.ProductId, p.ProductName, ft.RANK
FROM CONTAINSTABLE(catalog.Product, *, N'gaming laptop', 10) ft
JOIN catalog.Product p ON ft.[KEY] = p.ProductId
ORDER BY ft.RANK DESC;
```

### FREETEXTTABLE

Returns a table with `KEY` and `RANK` for natural language searches.

```sql
SELECT p.ProductId, p.ProductName, ft.RANK
FROM FREETEXTTABLE(catalog.Product, Description, N'high end gaming laptop') ft
JOIN catalog.Product p ON ft.[KEY] = p.ProductId
ORDER BY ft.RANK DESC;
```

---

## Manage Full-Text Indexes

```sql
-- Trigger full population (rebuild index)
ALTER FULLTEXT INDEX ON catalog.Product START FULL POPULATION;

-- Trigger incremental population (update changed rows)
ALTER FULLTEXT INDEX ON catalog.Product START INCREMENTAL POPULATION;

-- Trigger update population (process tracked changes)
ALTER FULLTEXT INDEX ON catalog.Product START UPDATE POPULATION;

-- Stop population
ALTER FULLTEXT INDEX ON catalog.Product STOP POPULATION;

-- Enable / disable
ALTER FULLTEXT INDEX ON catalog.Product ENABLE;
ALTER FULLTEXT INDEX ON catalog.Product DISABLE;

-- Change change tracking
ALTER FULLTEXT INDEX ON catalog.Product SET CHANGE_TRACKING AUTO;
ALTER FULLTEXT INDEX ON catalog.Product SET CHANGE_TRACKING MANUAL;

-- Drop full-text index
DROP FULLTEXT INDEX ON catalog.Product;

-- Drop full-text catalog (must remove all indexes first)
DROP FULLTEXT CATALOG ProductSearchCatalog;
```

---

## Stoplists

```sql
-- Create a custom stoplist
CREATE FULLTEXT STOPLIST ProductStoplist FROM SYSTEM STOPLIST;

-- Add stop words
ALTER FULLTEXT STOPLIST ProductStoplist
ADD N'the' LANGUAGE N'English';
ALTER FULLTEXT STOPLIST ProductStoplist
ADD N'and' LANGUAGE N'English';

-- Use in index
CREATE FULLTEXT INDEX ON catalog.Product (ProductName LANGUAGE 1033)
KEY INDEX PK_Product
ON ProductSearchCatalog
WITH STOPLIST = ProductStoplist;
```

---

## System Views for Inspection

```sql
-- List full-text catalogs
SELECT name, path, is_default, is_accent_sensitivity_on,
       population_status, item_count
FROM sys.fulltext_catalogs;

-- List full-text indexes
SELECT OBJECT_NAME(fti.object_id) AS TableName,
       fti.change_tracking_state_desc,
       fti.has_crawl_completed,
       fti.crawl_type_desc,
       fti.row_count_in_thousands,
       fti.is_enabled
FROM sys.fulltext_indexes fti;

-- List indexed columns
SELECT OBJECT_NAME(ftic.object_id) AS TableName,
       c.name AS ColumnName,
       ftic.language_id,
       ftic.statistical_semantics
FROM sys.fulltext_index_columns ftic
JOIN sys.columns c ON ftic.object_id = c.object_id
                   AND ftic.column_id = c.column_id
ORDER BY TableName, c.name;

-- Population status
SELECT OBJECT_NAME(fti.object_id) AS TableName,
       fti.crawl_type_desc, fti.crawl_start_date,
       fti.crawl_end_date, fti.incremental_timestamp
FROM sys.fulltext_indexes fti
WHERE fti.has_crawl_completed = 0;

-- Available languages
SELECT lcid, name, alias
FROM sys.fulltext_languages
ORDER BY name;
```
