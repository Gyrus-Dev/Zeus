# SQL Server Linked Servers — Parameter Reference

Linked servers are SQL Server's equivalent of PostgreSQL Foreign Data Wrappers (FDWs). They allow distributed queries across SQL Server instances and other data sources.

## Architecture

```
SQL Server Instance
└── Linked Server Definition (sp_addlinkedserver)
    └── Login Mapping (sp_addlinkedsrvlogin)
        └── Remote Server / Data Source
```

---

## sp_addlinkedserver

### Syntax

```sql
EXEC sp_addlinkedserver
    @server     = N'linked_server_name',    -- Required: local alias for the linked server
    @srvproduct = N'product_name',           -- Required: OLE DB data source name (can be empty string)
    @provider   = N'provider_name',          -- OLE DB provider ProgID
    @datasrc    = N'data_source',            -- Data source (server\instance, file path, DSN, etc.)
    @location   = N'location',              -- Optional: location passed to provider
    @provstr    = N'provider_string',        -- Optional: provider connection string
    @catalog    = N'catalog'                -- Optional: default catalog/database
;
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `@server` | Local alias used to reference the linked server in queries |
| `@srvproduct` | Product name of the OLE DB data source; use `N''` (empty) for SQL Server |
| `@provider` | OLE DB provider ProgID (see provider table below) |
| `@datasrc` | Server name, instance, file path, or DSN depending on provider |
| `@location` | Provider-specific location string (rarely needed) |
| `@provstr` | Full OLE DB connection string (alternative to @datasrc) |
| `@catalog` | Default database/catalog on the remote server |

### OLE DB Providers

| Provider | Use Case | @srvproduct |
|----------|----------|-------------|
| `MSOLEDBSQL` | SQL Server 2012+ (recommended) | `N''` |
| `SQLNCLI` | SQL Server (legacy SQL Native Client) | `N''` |
| `SQLNCLI11` | SQL Server 2012 (SQL Native Client 11) | `N''` |
| `Microsoft.ACE.OLEDB.12.0` | Excel / Access | `N'Jet 4.0'` or `N'ACE'` |
| `MSDAORA` | Oracle via OLE DB | `N'Oracle'` |
| `MSDASQL` | Any ODBC data source | `N'ODBC'` |
| `DB2OLEDB` | IBM DB2 | `N'DB2'` |

---

## sp_addlinkedsrvlogin

### Syntax

```sql
EXEC sp_addlinkedsrvlogin
    @rmtsrvname  = N'linked_server_name',   -- Linked server alias
    @useself     = N'false',                 -- TRUE = use caller's credentials (Windows auth only)
    @locallogin  = NULL,                     -- Local login to map (NULL = all logins)
    @rmtuser     = N'remote_username',       -- Remote login/username
    @rmtpassword = N'remote_password'        -- Remote password
;
```

### Parameters

| Parameter | Description |
|-----------|-------------|
| `@rmtsrvname` | The linked server name (must match `@server` in sp_addlinkedserver) |
| `@useself` | `TRUE`: impersonate local Windows identity; `FALSE`: use explicit credentials |
| `@locallogin` | Local SQL login to map; `NULL` maps all logins not explicitly mapped |
| `@rmtuser` | Remote username (when `@useself = FALSE`) |
| `@rmtpassword` | Remote password (stored encrypted in `sys.linked_logins`) |

---

## Examples

### SQL Server to SQL Server (Recommended)

```sql
-- Add linked server
EXEC sp_addlinkedserver
    @server     = N'RemoteSalesDB',
    @srvproduct = N'',
    @provider   = N'MSOLEDBSQL',
    @datasrc    = N'RemoteServer\SQLINSTANCE';
GO

-- Map logins (use Windows passthrough when possible)
EXEC sp_addlinkedsrvlogin
    @rmtsrvname  = N'RemoteSalesDB',
    @useself     = N'true';  -- Windows authentication passthrough
GO

-- Or with explicit SQL credentials:
EXEC sp_addlinkedsrvlogin
    @rmtsrvname  = N'RemoteSalesDB',
    @useself     = N'false',
    @locallogin  = NULL,         -- applies to all local logins
    @rmtuser     = N'ReadOnlyUser',
    @rmtpassword = N'R3m0te#Pass';
GO
```

### SQL Server to Oracle

```sql
EXEC sp_addlinkedserver
    @server     = N'OracleSales',
    @srvproduct = N'Oracle',
    @provider   = N'MSDAORA',
    @datasrc    = N'ORASERVER';  -- Oracle TNS name
GO

EXEC sp_addlinkedsrvlogin
    @rmtsrvname  = N'OracleSales',
    @useself     = N'false',
    @rmtuser     = N'oracle_user',
    @rmtpassword = N'OraP@ss!123';
GO
```

### SQL Server via ODBC DSN

```sql
EXEC sp_addlinkedserver
    @server     = N'MySQLSource',
    @srvproduct = N'ODBC',
    @provider   = N'MSDASQL',
    @datasrc    = N'MyODBCDSNName';  -- System DSN configured on the server
GO
```

### SQL Server with Provider String

```sql
EXEC sp_addlinkedserver
    @server   = N'AzureSQL',
    @srvproduct = N'',
    @provider = N'MSOLEDBSQL',
    @datasrc  = N'',
    @provstr  = N'Server=myserver.database.windows.net;Initial Catalog=MyDB;User Id=myuser;Password=mypass;';
GO
```

---

## Querying Linked Servers

### Four-Part Naming

```sql
-- [linked_server].[database].[schema].[table]
SELECT *
FROM [RemoteSalesDB].[SalesDB].[sales].[Customer];

-- Cross-server JOIN
SELECT
    lc.CustomerId,
    lc.CustomerName,
    lo.OrderId,
    lo.TotalAmount
FROM [RemoteSalesDB].[SalesDB].[sales].[Customer] lc
JOIN sales.[Order] lo ON lc.CustomerId = lo.CustomerId
WHERE lc.IsActive = 1;
```

### OPENQUERY (Passthrough Query)

```sql
-- More efficient: query executed on remote server, only results returned
SELECT *
FROM OPENQUERY([RemoteSalesDB],
    'SELECT CustomerId, CustomerName, Email
     FROM sales.Customer
     WHERE IsActive = 1
     AND Region = ''North''');

-- OPENQUERY with parameterized query (using dynamic SQL)
DECLARE @RemoteSQL NVARCHAR(MAX);
SET @RemoteSQL = 'SELECT * FROM sales.Customer WHERE Region = ''West''';

SELECT *
FROM OPENQUERY([RemoteSalesDB], 'SELECT * FROM sales.Customer WHERE Region = ''West''');
```

### OPENROWSET (Ad-hoc, no pre-defined linked server)

```sql
-- Requires Ad Hoc Distributed Queries to be enabled:
EXEC sp_configure 'Ad Hoc Distributed Queries', 1;
RECONFIGURE;
GO

SELECT *
FROM OPENROWSET(
    'MSOLEDBSQL',
    'Server=RemoteServer\INSTANCE;Trusted_Connection=yes;',
    'SELECT * FROM SalesDB.sales.Customer'
);
```

---

## Linked Server Options (sp_serveroption)

```sql
-- Allow RPC calls (for executing remote stored procedures)
EXEC sp_serveroption @server = N'RemoteSalesDB', @optname = N'rpc', @optvalue = N'true';
EXEC sp_serveroption @server = N'RemoteSalesDB', @optname = N'rpc out', @optvalue = N'true';

-- Disable distributed transactions requirement
EXEC sp_serveroption @server = N'RemoteSalesDB', @optname = N'remote proc transaction promotion', @optvalue = N'false';

-- Enable collation compatibility
EXEC sp_serveroption @server = N'RemoteSalesDB', @optname = N'collation compatible', @optvalue = N'true';

-- Use custom collation
EXEC sp_serveroption @server = N'RemoteSalesDB', @optname = N'use remote collation', @optvalue = N'false';
```

---

## Execute Remote Stored Procedure

```sql
-- With RPC enabled on the linked server:
EXEC [RemoteSalesDB].SalesDB.sales.usp_process_order
    @CustomerId = 42,
    @OrderDate  = '2024-01-15';
```

---

## Remove Linked Server

```sql
-- Remove login mapping first
EXEC sp_droplinkedsrvlogin
    @rmtsrvname = N'RemoteSalesDB',
    @locallogin = NULL;
GO

-- Drop the linked server
EXEC sp_dropserver
    @server     = N'RemoteSalesDB',
    @droplogins = N'droplogins';  -- drops all login mappings too
GO
```

---

## System Views for Inspection

```sql
-- List all linked servers
SELECT name, product, provider, data_source, catalog,
       is_rpc_out_enabled, is_remote_login_enabled, modify_date
FROM sys.servers
WHERE is_linked = 1;

-- List login mappings
SELECT s.name AS LinkedServer, ll.uses_self_credential,
       ll.remote_name AS RemoteUser
FROM sys.linked_logins ll
JOIN sys.servers s ON ll.server_id = s.server_id;

-- Test connectivity
EXEC sp_testlinkedserver N'RemoteSalesDB';
```
