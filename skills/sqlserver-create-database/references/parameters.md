# SQL Server CREATE DATABASE — Parameter Reference

## Full Syntax

```sql
CREATE DATABASE database_name
[ CONTAINMENT = { NONE | PARTIAL } ]
[ ON
    [ PRIMARY ] <filespec> [ ,...n ]
    [ , <filegroup> [ ,...n ] ]
    [ LOG ON <filespec> [ ,...n ] ]
]
[ COLLATE collation_name ]
[ WITH <option> [ ,...n ] ]
[ ; ]

<filespec> ::=
(
    NAME = logical_file_name,
    FILENAME = { 'os_file_name' | 'filestream_path' }
    [ , SIZE = size [ KB | MB | GB | TB ] ]
    [ , MAXSIZE = { max_size [ KB | MB | GB | TB ] | UNLIMITED } ]
    [ , FILEGROWTH = growth_increment [ KB | MB | GB | TB | % ] ]
)

<filegroup> ::=
FILEGROUP filegroup_name
    [ CONTAINS FILESTREAM ]
    [ DEFAULT ]
    <filespec> [ ,...n ]

<option> ::=
{
    TRUSTWORTHY { ON | OFF }
  | DB_CHAINING { ON | OFF }
  | HONOR_BROKER_PRIORITY { ON | OFF }
  | PERSISTENT_LOG_BUFFER = ON ( DIRECTORY_NAME = 'directory_name' )
}
```

## Parameters

### database_name
- The name of the new database. Must be unique within a SQL Server instance.
- Maximum 128 characters.
- Cannot be a system database name (master, model, msdb, tempdb).

### CONTAINMENT
- **NONE** (default): Traditional non-contained database. Users must have a server login.
- **PARTIAL**: Contained database. Allows users with passwords stored in the database (portable authentication). Requires `sp_configure 'contained database authentication', 1`.

### ON / PRIMARY
- Specifies the data files (MDF/NDF) for the primary filegroup.
- `PRIMARY` keyword is optional; if omitted, the first listed file becomes the primary file.
- If ON is omitted entirely, SQL Server creates a single data file in the model database location.

### LOG ON
- Specifies the transaction log files (LDF).
- If omitted, SQL Server creates a single log file sized at 25% of total data file size (minimum 512 KB).

### filespec Parameters
| Parameter | Description | Default |
|-----------|-------------|---------|
| `NAME` | Logical name for the file (used in T-SQL references) | Required |
| `FILENAME` | Physical OS path including file name | Required |
| `SIZE` | Initial file size | 8 MB for data, 8 MB for log (inherits from model) |
| `MAXSIZE` | Maximum file size; UNLIMITED means bounded only by disk | UNLIMITED |
| `FILEGROWTH` | Auto-growth increment; 0 disables auto-growth | 64 MB for data, 64 MB for log |

### COLLATE
- Sets the database default collation.
- If omitted, inherits from the SQL Server instance collation.
- Example: `COLLATE Latin1_General_CI_AS`
- Common collations:
  - `SQL_Latin1_General_CP1_CI_AS` — SQL Server default (case-insensitive, accent-sensitive)
  - `Latin1_General_CI_AS` — Windows collation, case-insensitive
  - `Latin1_General_CS_AS` — case-sensitive, accent-sensitive
  - `Latin1_General_BIN2` — binary comparison

### WITH options
| Option | Description | Default |
|--------|-------------|---------|
| `TRUSTWORTHY ON\|OFF` | Allows modules to access resources outside the database using an impersonation context | OFF |
| `DB_CHAINING ON\|OFF` | Allows cross-database ownership chaining | OFF |
| `HONOR_BROKER_PRIORITY ON\|OFF` | Honors conversation priority values for Service Broker | OFF |

## Conditional Create Pattern

SQL Server has no `IF NOT EXISTS` clause on CREATE DATABASE. Use:

```sql
IF NOT EXISTS (
    SELECT name
    FROM sys.databases
    WHERE name = N'MyDatabase'
)
BEGIN
    CREATE DATABASE MyDatabase;
END;
GO
```

## Minimal Example

```sql
CREATE DATABASE SalesDB;
```

## Full Example with Filegroups

```sql
CREATE DATABASE SalesDB
ON PRIMARY
(
    NAME = N'SalesDB_Primary',
    FILENAME = N'C:\SQLData\SalesDB.mdf',
    SIZE = 256MB,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 64MB
),
FILEGROUP SalesDB_Data
(
    NAME = N'SalesDB_Data',
    FILENAME = N'C:\SQLData\SalesDB_Data.ndf',
    SIZE = 512MB,
    MAXSIZE = UNLIMITED,
    FILEGROWTH = 128MB
)
LOG ON
(
    NAME = N'SalesDB_Log',
    FILENAME = N'C:\SQLLogs\SalesDB.ldf',
    SIZE = 128MB,
    MAXSIZE = 2GB,
    FILEGROWTH = 64MB
)
COLLATE Latin1_General_CI_AS
WITH TRUSTWORTHY OFF, DB_CHAINING OFF;
GO
```

## Contained Database Example

```sql
-- Enable contained database authentication at server level first:
EXEC sp_configure 'contained database authentication', 1;
RECONFIGURE;
GO

CREATE DATABASE PortableDB
CONTAINMENT = PARTIAL
ON PRIMARY
(
    NAME = N'PortableDB',
    FILENAME = N'C:\SQLData\PortableDB.mdf',
    SIZE = 64MB,
    FILEGROWTH = 32MB
)
LOG ON
(
    NAME = N'PortableDB_Log',
    FILENAME = N'C:\SQLLogs\PortableDB.ldf',
    SIZE = 16MB,
    FILEGROWTH = 16MB
);
GO
```

## Post-Creation Configuration

Common database options set via ALTER DATABASE:
```sql
-- Set recovery model
ALTER DATABASE SalesDB SET RECOVERY FULL;

-- Enable snapshot isolation
ALTER DATABASE SalesDB SET ALLOW_SNAPSHOT_ISOLATION ON;
ALTER DATABASE SalesDB SET READ_COMMITTED_SNAPSHOT ON;

-- Set compatibility level
ALTER DATABASE SalesDB SET COMPATIBILITY_LEVEL = 160; -- SQL Server 2022
```

## System Views for Inspection

```sql
-- List all databases
SELECT name, database_id, collation_name, recovery_model_desc, containment_desc
FROM sys.databases;

-- List database files
SELECT name, physical_name, size, max_size, growth, type_desc
FROM sys.master_files
WHERE database_id = DB_ID('SalesDB');
```
