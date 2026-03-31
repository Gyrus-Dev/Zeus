# SQL Server CREATE TRIGGER — Parameter Reference

## Full Syntax

### DML Trigger
```sql
CREATE [ OR ALTER ] TRIGGER [ schema_name . ] trigger_name
ON { table | view }
[ WITH <dml_trigger_option> [ ,...n ] ]
{ FOR | AFTER | INSTEAD OF }
{ [ INSERT ] [ , ] [ UPDATE ] [ , ] [ DELETE ] }
[ WITH APPEND ]
[ NOT FOR REPLICATION ]
AS
{ sql_statement [ ; ] [ ,...n ] | EXTERNAL NAME <method specifier> }

<dml_trigger_option> ::=
{
    ENCRYPTION
  | EXECUTE AS { CALLER | SELF | OWNER | 'user_name' }
}
```

### DDL Trigger
```sql
CREATE [ OR ALTER ] TRIGGER trigger_name
ON { ALL SERVER | DATABASE }
[ WITH <ddl_trigger_option> [ ,...n ] ]
{ FOR | AFTER } { event_type | event_group } [ ,...n ]
AS
{ sql_statement [ ; ] [ ,...n ] | EXTERNAL NAME <method specifier> }

<ddl_trigger_option> ::=
{
    ENCRYPTION
  | EXECUTE AS { CALLER | SELF | OWNER | 'user_name' }
}
```

### Logon Trigger
```sql
CREATE [ OR ALTER ] TRIGGER trigger_name
ON ALL SERVER
[ WITH <logon_trigger_option> [ ,...n ] ]
{ FOR | AFTER } LOGON
AS
{ sql_statement [ ; ] [ ,...n ] | EXTERNAL NAME <method specifier> }

<logon_trigger_option> ::=
{
    ENCRYPTION
  | EXECUTE AS { CALLER | SELF | OWNER | 'user_name' }
}
```

## DML Trigger Types

### AFTER Trigger (FOR)
- Fires after the triggering DML statement completes and all constraint checks pass.
- Cannot be created on views.
- Multiple AFTER triggers can exist on the same table/event.
- `FOR` and `AFTER` are synonymous.

```sql
CREATE OR ALTER TRIGGER sales.tr_Order_Insert
ON sales.[Order]
AFTER INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Log new orders
    INSERT INTO audit.OrderLog (OrderId, Action, ActionTime, ActionBy)
    SELECT OrderId, N'INSERT', GETDATE(), SYSTEM_USER
    FROM INSERTED;
END;
GO
```

### INSTEAD OF Trigger
- Fires INSTEAD OF the triggering DML statement.
- Can be created on tables and views.
- Used to make non-updateable views updateable.
- Only one INSTEAD OF trigger per INSERT, UPDATE, or DELETE per table/view.

```sql
CREATE OR ALTER TRIGGER sales.tr_v_Order_InsteadOfInsert
ON sales.v_OrderDetails
INSTEAD OF INSERT
AS
BEGIN
    SET NOCOUNT ON;

    -- Redirect insert to base table
    INSERT INTO sales.[Order] (CustomerId, OrderDate, Status)
    SELECT i.CustomerId, COALESCE(i.OrderDate, GETDATE()), COALESCE(i.Status, N'Pending')
    FROM INSERTED i;
END;
GO
```

## INSERTED and DELETED Pseudo-Tables

Both pseudo-tables have the same column structure as the trigger's base table.

| Operation | INSERTED | DELETED |
|-----------|----------|---------|
| INSERT | New rows | Empty |
| DELETE | Empty | Old rows |
| UPDATE | New row values (after update) | Old row values (before update) |

```sql
CREATE OR ALTER TRIGGER hr.tr_Employee_Update
ON hr.Employee
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    -- Capture salary changes
    INSERT INTO audit.SalaryChange
        (EmployeeId, OldSalary, NewSalary, ChangedAt, ChangedBy)
    SELECT
        d.EmployeeId,
        d.Salary AS OldSalary,
        i.Salary AS NewSalary,
        GETDATE(),
        SYSTEM_USER
    FROM DELETED d
    JOIN INSERTED i ON d.EmployeeId = i.EmployeeId
    WHERE d.Salary <> i.Salary;
END;
GO
```

## UPDATE() and COLUMNS_UPDATED()

### UPDATE(column)
- Returns TRUE if a specific column was included in the UPDATE statement.
- Does NOT indicate whether the value actually changed — only that the column was in the SET list.

```sql
CREATE OR ALTER TRIGGER hr.tr_Employee_SalaryChange
ON hr.Employee
AFTER UPDATE
AS
BEGIN
    SET NOCOUNT ON;

    IF UPDATE(Salary)
    BEGIN
        -- Handle salary change logic
        INSERT INTO audit.SalaryAudit (EmployeeId, OldSalary, NewSalary)
        SELECT d.EmployeeId, d.Salary, i.Salary
        FROM DELETED d
        JOIN INSERTED i ON d.EmployeeId = i.EmployeeId
        WHERE d.Salary <> i.Salary;
    END;
END;
GO
```

### COLUMNS_UPDATED()
- Returns a varbinary bitmask indicating which columns were updated.
- Each bit corresponds to a column by column_id order.
- More granular than UPDATE() but more complex to use.

```sql
-- Check if column 3 or column 5 was updated
IF (COLUMNS_UPDATED() & 0x14) > 0  -- 0x14 = bit 3 (4) + bit 5 (16)
BEGIN
    -- handle update
END;
```

## DDL Trigger Events

### Common Database-Level Events
| Event | Description |
|-------|-------------|
| `CREATE_TABLE` | CREATE TABLE |
| `ALTER_TABLE` | ALTER TABLE |
| `DROP_TABLE` | DROP TABLE |
| `CREATE_VIEW` | CREATE VIEW |
| `ALTER_VIEW` | ALTER VIEW |
| `DROP_VIEW` | DROP VIEW |
| `CREATE_PROCEDURE` | CREATE PROCEDURE |
| `ALTER_PROCEDURE` | ALTER PROCEDURE |
| `DROP_PROCEDURE` | DROP PROCEDURE |
| `CREATE_INDEX` | CREATE INDEX |
| `DROP_INDEX` | DROP INDEX |
| `GRANT_DATABASE` | GRANT on database objects |

### Common Server-Level Events
| Event | Description |
|-------|-------------|
| `CREATE_DATABASE` | CREATE DATABASE |
| `DROP_DATABASE` | DROP DATABASE |
| `ALTER_LOGIN` | ALTER LOGIN |
| `CREATE_LOGIN` | CREATE LOGIN |

### Event Groups
| Group | Covers |
|-------|--------|
| `DDL_TABLE_EVENTS` | CREATE/ALTER/DROP TABLE |
| `DDL_DATABASE_LEVEL_EVENTS` | All database DDL |
| `DDL_SERVER_LEVEL_EVENTS` | All server DDL |

```sql
CREATE OR ALTER TRIGGER tr_PreventTableDrop
ON DATABASE
FOR DROP_TABLE
AS
BEGIN
    PRINT 'Table drops are not allowed during business hours.';
    ROLLBACK;
END;
GO
```

### EVENTDATA() in DDL Triggers
```sql
CREATE OR ALTER TRIGGER tr_AuditDDL
ON DATABASE
FOR DDL_TABLE_EVENTS
AS
BEGIN
    SET NOCOUNT ON;

    DECLARE @EventData XML = EVENTDATA();

    INSERT INTO audit.DDLLog
        (EventType, ObjectName, SchemaName, TSQLCommand, LoginName, EventTime)
    VALUES
    (
        @EventData.value('(/EVENT_INSTANCE/EventType)[1]',   'NVARCHAR(100)'),
        @EventData.value('(/EVENT_INSTANCE/ObjectName)[1]',  'NVARCHAR(256)'),
        @EventData.value('(/EVENT_INSTANCE/SchemaName)[1]',  'NVARCHAR(256)'),
        @EventData.value('(/EVENT_INSTANCE/TSQLCommand)[1]', 'NVARCHAR(MAX)'),
        @EventData.value('(/EVENT_INSTANCE/LoginName)[1]',   'NVARCHAR(256)'),
        GETDATE()
    );
END;
GO
```

## Trigger Management

```sql
-- Disable a trigger
DISABLE TRIGGER sales.tr_Order_Insert ON sales.[Order];

-- Enable a trigger
ENABLE TRIGGER sales.tr_Order_Insert ON sales.[Order];

-- Disable all triggers on a table
DISABLE TRIGGER ALL ON sales.[Order];

-- Enable all triggers on a table
ENABLE TRIGGER ALL ON sales.[Order];

-- Disable a DDL trigger
DISABLE TRIGGER tr_PreventTableDrop ON DATABASE;

-- Drop a trigger
DROP TRIGGER IF EXISTS sales.tr_Order_Insert;
DROP TRIGGER IF EXISTS tr_AuditDDL ON DATABASE;
```

## Conditional Create Pattern

```sql
-- Check sys.triggers for DML triggers
IF EXISTS (
    SELECT 1 FROM sys.triggers
    WHERE name = N'tr_Order_Insert'
      AND parent_id = OBJECT_ID(N'sales.[Order]')
)
    DROP TRIGGER sales.tr_Order_Insert;
GO

CREATE TRIGGER sales.tr_Order_Insert
ON sales.[Order]
AFTER INSERT
AS
...
GO

-- Or use CREATE OR ALTER (SQL Server 2016+):
CREATE OR ALTER TRIGGER sales.tr_Order_Insert
ON sales.[Order]
AFTER INSERT
AS
...
GO
```

## System Views for Inspection

```sql
-- List DML triggers
SELECT t.name, OBJECT_NAME(t.parent_id) AS TableName, t.type_desc,
       t.is_disabled, t.is_instead_of_trigger, t.create_date
FROM sys.triggers t
WHERE t.parent_class = 1  -- Object (table/view) triggers
ORDER BY OBJECT_NAME(t.parent_id), t.name;

-- List DDL triggers
SELECT name, parent_class_desc, type_desc, is_disabled, create_date
FROM sys.triggers
WHERE parent_class = 0  -- Database/server triggers
ORDER BY name;

-- Get trigger definition
SELECT definition
FROM sys.sql_modules
WHERE object_id = OBJECT_ID(N'sales.tr_Order_Insert');

-- List trigger events
SELECT t.name AS TriggerName, te.type_desc AS EventType
FROM sys.triggers t
JOIN sys.trigger_events te ON t.object_id = te.object_id
ORDER BY t.name;
```
