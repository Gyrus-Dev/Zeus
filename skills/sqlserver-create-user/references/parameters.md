# SQL Server CREATE LOGIN / CREATE USER — Parameter Reference

## Architecture Overview

SQL Server uses a two-tier security model:
- **Login** (server-level): Authenticates to the SQL Server instance (stored in `master`).
- **User** (database-level): Authorizes access within a specific database (stored in each database).

A login must exist before creating a database user mapped to it (except for contained databases).

---

## CREATE LOGIN

### Full Syntax

```sql
-- SQL Server Authentication login
CREATE LOGIN login_name WITH
    PASSWORD = { 'password' | hashed_password HASHED }
    [ MUST_CHANGE ]
    [ , SID = sid ]
    [ , DEFAULT_DATABASE = database ]
    [ , DEFAULT_LANGUAGE = language ]
    [ , CHECK_EXPIRATION = { ON | OFF } ]
    [ , CHECK_POLICY = { ON | OFF } ]
    [ , CREDENTIAL = credential_name ]
[ ; ]

-- Windows Authentication login
CREATE LOGIN [DOMAIN\UserOrGroup] FROM WINDOWS
    [ WITH DEFAULT_DATABASE = database ]
    [ , DEFAULT_LANGUAGE = language ]
[ ; ]

-- From certificate
CREATE LOGIN login_name FROM CERTIFICATE certificate_name [ ; ]

-- From asymmetric key
CREATE LOGIN login_name FROM ASYMMETRIC KEY asym_key_name [ ; ]
```

### SQL Server Login Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `PASSWORD` | Login password (plain text or hashed) | Required |
| `MUST_CHANGE` | Force password change on first login | OFF |
| `SID` | Explicitly set the security identifier (for migration scenarios) | Auto-generated |
| `DEFAULT_DATABASE` | Database to connect to by default | master |
| `DEFAULT_LANGUAGE` | Default language for system messages | Server default |
| `CHECK_EXPIRATION` | Enforce password expiration policy | OFF |
| `CHECK_POLICY` | Enforce Windows password complexity policy | ON |
| `CREDENTIAL` | Map login to a server credential | None |

### Login Examples

```sql
-- SQL Server authentication login
CREATE LOGIN AppServiceLogin
WITH PASSWORD = N'P@ssw0rd!2024',
     DEFAULT_DATABASE = SalesDB,
     CHECK_EXPIRATION = OFF,
     CHECK_POLICY = ON;

-- Windows authentication login (individual user)
CREATE LOGIN [CORP\john.smith] FROM WINDOWS
WITH DEFAULT_DATABASE = SalesDB;

-- Windows authentication login (AD group)
CREATE LOGIN [CORP\DatabaseAdmins] FROM WINDOWS
WITH DEFAULT_DATABASE = master;

-- Login that must change password on first use
CREATE LOGIN TempConsultantLogin
WITH PASSWORD = N'Temp#1234' MUST_CHANGE,
     CHECK_EXPIRATION = ON,
     CHECK_POLICY = ON;
```

---

## CREATE USER

### Full Syntax

```sql
-- User mapped to a login (most common)
CREATE USER user_name
    [ { FOR | FROM } LOGIN login_name ]
    [ WITH DEFAULT_SCHEMA = schema_name ]
    [ , SID = sid ]
[ ; ]

-- Contained database user with password (no login required)
CREATE USER user_name
    WITH PASSWORD = 'password'
    [ , DEFAULT_SCHEMA = schema_name ]
    [ , DEFAULT_LANGUAGE = language_name ]
    [ , SID = sid ]
[ ; ]

-- User without login (for app roles, certificate mapping, etc.)
CREATE USER user_name WITHOUT LOGIN
    [ WITH DEFAULT_SCHEMA = schema_name ]
[ ; ]

-- User mapped to a certificate
CREATE USER user_name FOR CERTIFICATE certificate_name [ ; ]

-- User mapped to an asymmetric key
CREATE USER user_name FOR ASYMMETRIC KEY asym_key_name [ ; ]

-- Windows user/group as database user
CREATE USER [DOMAIN\UserOrGroup]
    [ WITH DEFAULT_SCHEMA = schema_name ]
[ ; ]
```

### User Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `FOR LOGIN` / `FROM LOGIN` | Map user to an existing server login | Required unless contained or WITHOUT LOGIN |
| `WITHOUT LOGIN` | Create user not mapped to any login | N/A |
| `DEFAULT_SCHEMA` | Default schema for unqualified object references | dbo |
| `SID` | Explicitly set SID (for migration) | Inherited from login |
| `PASSWORD` | Contained user password (CONTAINMENT = PARTIAL only) | Required for contained users |

### User Examples

```sql
-- Map database user to login
USE SalesDB;
GO

CREATE USER AppServiceUser
FOR LOGIN AppServiceLogin
WITH DEFAULT_SCHEMA = sales;

-- Windows user
CREATE USER [CORP\john.smith]
WITH DEFAULT_SCHEMA = dbo;

-- Contained database user (no login needed)
CREATE USER ContainedUser
WITH PASSWORD = N'P@ssw0rd!2024',
     DEFAULT_SCHEMA = dbo;

-- Service account without login (used with EXECUTE AS or module signing)
CREATE USER ServiceModuleUser WITHOUT LOGIN
WITH DEFAULT_SCHEMA = dbo;

-- Guest access (enable the guest user)
ALTER USER guest ENABLE;
```

---

## Grant Database Access to Login

```sql
-- Full workflow:
-- 1. Create server login
CREATE LOGIN SalesAppLogin
WITH PASSWORD = N'Str0ng#Pass2024',
     DEFAULT_DATABASE = SalesDB,
     CHECK_POLICY = ON;
GO

-- 2. Switch to database
USE SalesDB;
GO

-- 3. Create database user mapped to login
CREATE USER SalesAppUser
FOR LOGIN SalesAppLogin
WITH DEFAULT_SCHEMA = sales;
GO

-- 4. Assign roles or permissions
ALTER ROLE db_datareader ADD MEMBER SalesAppUser;
ALTER ROLE db_datawriter ADD MEMBER SalesAppUser;
GRANT EXECUTE ON SCHEMA::sales TO SalesAppUser;
GO
```

---

## Contained Database Users

Available when `CONTAINMENT = PARTIAL` is set on the database. The user authenticates directly to the database without a server login.

```sql
-- Enable contained database authentication (server level)
EXEC sp_configure 'contained database authentication', 1;
RECONFIGURE;
GO

-- Set database containment
ALTER DATABASE SalesDB SET CONTAINMENT = PARTIAL;
GO

-- Create contained user
USE SalesDB;
GO
CREATE USER PortableUser
WITH PASSWORD = N'P@rtable#2024',
     DEFAULT_SCHEMA = dbo;
GO
```

---

## Alter Login and User

```sql
-- Change login password
ALTER LOGIN AppServiceLogin WITH PASSWORD = N'NewP@ss!2024';

-- Disable a login
ALTER LOGIN AppServiceLogin DISABLE;

-- Enable a login
ALTER LOGIN AppServiceLogin ENABLE;

-- Change default database
ALTER LOGIN AppServiceLogin WITH DEFAULT_DATABASE = ReportingDB;

-- Change user's default schema
ALTER USER AppServiceUser WITH DEFAULT_SCHEMA = reporting;

-- Rename a user
ALTER USER AppServiceUser WITH NAME = SalesServiceUser;

-- Map user to a different login (after login rename/migration)
ALTER USER SalesServiceUser WITH LOGIN = NewSalesLogin;
```

---

## Drop Login and User

```sql
-- Drop user first, then login
USE SalesDB;
GO
DROP USER IF EXISTS SalesAppUser;
GO

USE master;
GO
DROP LOGIN IF EXISTS SalesAppLogin;
GO
```

---

## System Views for Inspection

```sql
-- List all logins
SELECT name, type_desc, is_disabled, default_database_name, create_date
FROM sys.server_principals
WHERE type IN ('S', 'U', 'G')  -- SQL, Windows User, Windows Group
ORDER BY name;

-- List all database users
SELECT name, type_desc, authentication_type_desc, default_schema_name,
       create_date, sid
FROM sys.database_principals
WHERE type IN ('S', 'U', 'G', 'C', 'K')  -- SQL, Windows, Group, Certificate, AsymKey
ORDER BY name;

-- Find users mapped to a specific login
SELECT dp.name AS UserName, dp.type_desc, dp.default_schema_name
FROM sys.database_principals dp
WHERE dp.sid = SUSER_SID(N'AppServiceLogin');

-- List login-to-user mapping across all databases
EXEC sp_msloginmappings;
```
