# SQL Server CREATE ROLE — Parameter Reference

## Full Syntax

### Database Role
```sql
CREATE ROLE role_name
    [ AUTHORIZATION owner_name ]
[ ; ]
```

### Server Role (SQL Server 2012+)
```sql
CREATE SERVER ROLE role_name
    [ AUTHORIZATION server_principal_name ]
[ ; ]
```

## Parameters

### role_name
- Name of the new role.
- Must be unique within the database (for database roles) or server (for server roles).
- Convention: use descriptive names reflecting permissions (e.g., `SalesReader`, `HRDataWriter`).

### AUTHORIZATION owner_name
- The database principal or server principal that owns the role.
- If omitted, the creating user owns the role.

---

## Database Roles

### Create and Manage

```sql
-- Create a custom database role
CREATE ROLE SalesReader AUTHORIZATION dbo;
CREATE ROLE SalesWriter AUTHORIZATION dbo;
CREATE ROLE ReportViewer AUTHORIZATION dbo;

-- Add members
ALTER ROLE SalesReader ADD MEMBER ReportUser1;
ALTER ROLE SalesReader ADD MEMBER ReportUser2;
ALTER ROLE SalesWriter ADD MEMBER AppServiceUser;

-- Remove a member
ALTER ROLE SalesReader DROP MEMBER ReportUser1;

-- Drop a role (members must be removed first)
DROP ROLE IF EXISTS ReportViewer;
```

### Grant Permissions to a Role

```sql
-- Schema-level permissions
GRANT SELECT ON SCHEMA::sales TO SalesReader;
GRANT INSERT, UPDATE, DELETE ON SCHEMA::sales TO SalesWriter;
GRANT EXECUTE ON SCHEMA::sales TO SalesWriter;

-- Object-level permissions
GRANT SELECT ON sales.Customer TO SalesReader;
GRANT INSERT ON sales.[Order] TO SalesWriter;
GRANT EXECUTE ON sales.usp_process_order TO SalesWriter;

-- Database-level permissions
GRANT CREATE TABLE TO SchemaOwnerRole;
GRANT CREATE VIEW TO SchemaOwnerRole;
GRANT CREATE PROCEDURE TO SchemaOwnerRole;

-- View definitions
GRANT VIEW DEFINITION TO MetadataReader;
```

### DENY and REVOKE

```sql
-- DENY overrides GRANT (even if user is in a GRANT role)
DENY SELECT ON finance.SalaryDetail TO HRReadOnly;

-- REVOKE removes a previously GRANTED or DENIED permission
REVOKE SELECT ON sales.Customer FROM SalesReader;
REVOKE INSERT ON sales.[Order] FROM SalesWriter;
```

### Role Nesting (Role as member of another Role)

```sql
-- Grant SalesWriter all permissions that SalesReader has, plus write
ALTER ROLE SalesWriter ADD MEMBER SalesReader;  -- SalesWriter inherits SalesReader permissions
```

---

## Built-in Database Roles

| Role | Permissions |
|------|-------------|
| `db_owner` | Full control over the database |
| `db_securityadmin` | Manage role memberships and permissions |
| `db_accessadmin` | Add or remove access for Windows logins and SQL logins |
| `db_backupoperator` | Back up the database |
| `db_ddladmin` | Run any DDL command in the database |
| `db_datawriter` | INSERT, UPDATE, DELETE on all user tables |
| `db_datareader` | SELECT on all user tables |
| `db_denydatawriter` | DENY INSERT, UPDATE, DELETE on all user tables |
| `db_denydatareader` | DENY SELECT on all user tables |
| `public` | Default role; all users are members; minimal permissions only |

```sql
-- Assign a user to a built-in role
ALTER ROLE db_datareader ADD MEMBER AppReadOnlyUser;
ALTER ROLE db_datawriter ADD MEMBER AppServiceUser;
ALTER ROLE db_owner      ADD MEMBER DBAdminUser;
```

---

## Server Roles

Server roles operate at the SQL Server instance level (not per-database).

### Built-in Fixed Server Roles

| Role | Permissions |
|------|-------------|
| `sysadmin` | Full control over the server |
| `serveradmin` | Configure server-wide settings |
| `securityadmin` | Manage logins and permissions |
| `processadmin` | Kill processes |
| `setupadmin` | Manage linked servers |
| `bulkadmin` | Execute BULK INSERT |
| `diskadmin` | Manage disk files |
| `dbcreator` | Create, alter, restore databases |
| `public` | Default for all logins |

```sql
-- Add a login to a fixed server role
ALTER SERVER ROLE sysadmin ADD MEMBER AdminLogin;
ALTER SERVER ROLE dbcreator ADD MEMBER DevLead;
ALTER SERVER ROLE bulkadmin ADD MEMBER ETLServiceLogin;
```

### Custom Server Roles (SQL Server 2012+)

```sql
-- Create a custom server role
CREATE SERVER ROLE DatabaseMonitor AUTHORIZATION sysadmin;

-- Grant server-level permissions to the role
GRANT VIEW SERVER STATE TO DatabaseMonitor;
GRANT VIEW ANY DATABASE TO DatabaseMonitor;
GRANT VIEW ANY DEFINITION TO DatabaseMonitor;

-- Add login to custom server role
ALTER SERVER ROLE DatabaseMonitor ADD MEMBER MonitoringLogin;
```

---

## Application Roles

Application roles are database-level roles with a password; they replace the user's permissions when activated.

```sql
-- Create application role
CREATE APPLICATION ROLE SalesAppRole
WITH PASSWORD = N'AppR0le#Secret',
     DEFAULT_SCHEMA = sales;

-- Grant permissions to app role
GRANT SELECT, INSERT, UPDATE ON SCHEMA::sales TO SalesAppRole;

-- Activating from application code (T-SQL example)
EXEC sp_setapprole 'SalesAppRole', 'AppR0le#Secret';
-- After activation, user has only SalesAppRole permissions for the session
```

---

## Complete Permission Setup Example

```sql
USE SalesDB;
GO

-- Create roles
CREATE ROLE SalesReader    AUTHORIZATION dbo;
CREATE ROLE SalesWriter    AUTHORIZATION dbo;
CREATE ROLE SalesManager   AUTHORIZATION dbo;
GO

-- Grant schema-level permissions
GRANT SELECT                     ON SCHEMA::sales TO SalesReader;
GRANT SELECT, INSERT, UPDATE      ON SCHEMA::sales TO SalesWriter;
GRANT SELECT, INSERT, UPDATE, DELETE ON SCHEMA::sales TO SalesManager;
GRANT EXECUTE                    ON SCHEMA::sales TO SalesWriter;
GRANT EXECUTE                    ON SCHEMA::sales TO SalesManager;
GO

-- Nest roles
ALTER ROLE SalesWriter ADD MEMBER SalesReader;
ALTER ROLE SalesManager ADD MEMBER SalesWriter;
GO

-- Assign users to roles
ALTER ROLE SalesReader  ADD MEMBER ReportUser;
ALTER ROLE SalesWriter  ADD MEMBER AppServiceUser;
ALTER ROLE SalesManager ADD MEMBER SalesLeadUser;
GO
```

---

## System Views for Inspection

```sql
-- List all database roles
SELECT name, type_desc, is_fixed_role, principal_id
FROM sys.database_principals
WHERE type = 'R'
ORDER BY name;

-- List role members
SELECT r.name AS RoleName, m.name AS MemberName, m.type_desc
FROM sys.database_role_members rm
JOIN sys.database_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.database_principals m ON rm.member_principal_id = m.principal_id
ORDER BY r.name, m.name;

-- List all permissions for a role
SELECT dp.class_desc, OBJECT_NAME(dp.major_id) AS ObjectName,
       dp.permission_name, dp.state_desc
FROM sys.database_permissions dp
JOIN sys.database_principals p ON dp.grantee_principal_id = p.principal_id
WHERE p.name = N'SalesReader'
ORDER BY dp.class_desc, OBJECT_NAME(dp.major_id);

-- List custom server roles
SELECT name, type_desc, is_fixed_role, create_date
FROM sys.server_principals
WHERE type = 'R' AND is_fixed_role = 0;

-- List server role members
SELECT r.name AS RoleName, m.name AS MemberName
FROM sys.server_role_members rm
JOIN sys.server_principals r ON rm.role_principal_id = r.principal_id
JOIN sys.server_principals m ON rm.member_principal_id = m.principal_id
ORDER BY r.name, m.name;
```
