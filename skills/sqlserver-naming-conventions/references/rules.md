# SQL Server Naming Conventions — Reference

These conventions ensure consistent, readable, and maintainable database objects across the SQL Server environment.

---

## General Principles

- Use **PascalCase** for most database objects (tables, columns, procedures, functions, views).
- Use **lowercase** for schema names.
- Avoid abbreviations unless they are universally understood (Id, Qty, Amt).
- Never use reserved words as object names.
- Always qualify object names with their schema when referencing them in DDL or DML.
- All constraint names must be explicit — never rely on system-generated names.

---

## Tables

| Rule | Example |
|------|---------|
| Singular nouns, PascalCase | `Customer`, `OrderLine`, `ProductCategory` |
| Avoid plurals | `Customer` not `Customers` |
| Junction/association tables: combine both entity names | `CustomerProduct`, `OrderTag` |
| Avoid prefixes like `tbl_` or `t_` | `Customer` not `tbl_Customer` |

```sql
CREATE TABLE sales.Customer (...);
CREATE TABLE sales.OrderLine (...);
CREATE TABLE catalog.ProductCategory (...);
CREATE TABLE hr.EmployeeDepartment (...);
```

---

## Schemas

| Rule | Example |
|------|---------|
| All lowercase | `sales`, `hr`, `finance`, `dbo`, `audit` |
| Reflect business domain or team | `sales`, `inventory`, `reporting` |
| Default schema for application objects | `dbo` (only for truly shared/global objects) |

```sql
CREATE SCHEMA sales;
CREATE SCHEMA hr;
CREATE SCHEMA finance;
CREATE SCHEMA audit;
```

---

## Columns

| Rule | Example |
|------|---------|
| PascalCase | `CustomerId`, `CreatedAt`, `IsActive` |
| Primary key: `<TableName>Id` | `CustomerId`, `OrderLineId` |
| Foreign key: same name as referenced PK | `CustomerId` (FK referencing `Customer.CustomerId`) |
| Boolean columns: `Is<Condition>` or `Has<Condition>` | `IsActive`, `HasDiscount`, `IsDeleted` |
| Date/time columns: describe point in time | `CreatedAt`, `UpdatedAt`, `ShippedAt`, `DeletedAt` |
| Avoid generic names | `OrderDate` not `Date`, `TotalAmount` not `Total` |
| Avoid type suffixes | `CustomerName` not `CustomerNameVarchar` |

```sql
CustomerId    INT           NOT NULL IDENTITY(1,1),
CustomerName  NVARCHAR(200) NOT NULL,
Email         NVARCHAR(256) NULL,
IsActive      BIT           NOT NULL DEFAULT 1,
CreatedAt     DATETIME2     NOT NULL DEFAULT GETDATE(),
UpdatedAt     DATETIME2     NOT NULL DEFAULT GETDATE(),
```

---

## Constraints

### Primary Keys
- Pattern: `PK_<TableName>`
- Always CLUSTERED unless explicitly justified otherwise

```sql
CONSTRAINT PK_Customer PRIMARY KEY CLUSTERED (CustomerId)
CONSTRAINT PK_OrderLine PRIMARY KEY CLUSTERED (OrderLineId)
```

### Foreign Keys
- Pattern: `FK_<ChildTable>_<ParentTable>`
- If multiple FKs to same parent, append column: `FK_Order_Customer_BillingAddress`

```sql
CONSTRAINT FK_OrderLine_Order FOREIGN KEY (OrderId) REFERENCES sales.[Order](OrderId)
CONSTRAINT FK_OrderLine_Product FOREIGN KEY (ProductId) REFERENCES catalog.Product(ProductId)
```

### Unique Constraints
- Pattern: `UQ_<TableName>_<Column(s)>`
- For composite: list all columns with underscores

```sql
CONSTRAINT UQ_Customer_Email UNIQUE (Email)
CONSTRAINT UQ_Product_CodeVersion UNIQUE (ProductCode, Version)
```

### Check Constraints
- Pattern: `CK_<TableName>_<Column>`
- Describe the rule, not just the column name when useful

```sql
CONSTRAINT CK_OrderLine_Quantity CHECK (Quantity > 0)
CONSTRAINT CK_Customer_Email CHECK (Email LIKE '%@%.%')
CONSTRAINT CK_Order_DueDateAfterOrder CHECK (DueDate >= OrderDate)
```

### Default Constraints
- Pattern: `DF_<TableName>_<Column>`

```sql
CONSTRAINT DF_Customer_IsActive DEFAULT 1
CONSTRAINT DF_Order_Status DEFAULT N'Pending'
CONSTRAINT DF_OrderLine_CreatedAt DEFAULT GETDATE()
```

---

## Indexes

| Type | Pattern | Example |
|------|---------|---------|
| Non-clustered | `IX_<Table>_<Column(s)>` | `IX_Customer_Email` |
| Clustered (non-PK) | `CX_<Table>_<Column(s)>` | `CX_Order_OrderDate` |
| Unique non-clustered | `UX_<Table>_<Column(s)>` | `UX_Customer_Email` |
| Filtered | `IX_<Table>_<Column>_<Filter>` | `IX_Customer_Email_Active` |
| Columnstore | `NCCI_<Table>` or `CCI_<Table>` | `CCI_FactSales`, `NCCI_OrderLine_Analytics` |

```sql
CREATE NONCLUSTERED INDEX IX_Customer_Email
    ON sales.Customer (Email);

CREATE CLUSTERED COLUMNSTORE INDEX CCI_FactSales
    ON dw.FactSales;

CREATE NONCLUSTERED INDEX IX_Order_CustomerId_Active
    ON sales.[Order] (CustomerId)
    WHERE Status = N'Active';
```

---

## Stored Procedures

- Pattern: `usp_<action>_<object>` (user stored procedure)
- Action verbs: `get`, `create`, `update`, `delete`, `process`, `validate`, `sync`
- Avoid generic names like `usp_proc1`

```sql
usp_get_customer_by_id
usp_create_order
usp_update_order_status
usp_delete_expired_sessions
usp_process_payment
usp_sync_inventory
```

```sql
CREATE OR ALTER PROCEDURE sales.usp_get_customer_by_id
    @CustomerId INT
AS ...
```

---

## Functions

| Type | Pattern | Example |
|------|---------|---------|
| Scalar function | `ufn_<name>` | `ufn_format_phone`, `ufn_calculate_tax` |
| Table-valued function | `uft_<name>` | `uft_get_customer_orders`, `uft_get_employee_hierarchy` |

```sql
CREATE OR ALTER FUNCTION dbo.ufn_format_phone (@PhoneNumber NVARCHAR(20)) ...
CREATE OR ALTER FUNCTION sales.uft_get_customer_orders (@CustomerId INT, ...) ...
```

---

## Triggers

- Pattern: `tr_<TableName>_<Event>`
- Event: `Insert`, `Update`, `Delete`, `InsertUpdate`, `InsteadOfInsert`

```sql
tr_Customer_Insert
tr_Order_Update
tr_OrderLine_Delete
tr_Employee_InsertUpdate
tr_v_OrderDetails_InsteadOfInsert
tr_AuditDDL   (for DDL triggers on DATABASE)
```

```sql
CREATE OR ALTER TRIGGER sales.tr_Order_Update
ON sales.[Order]
AFTER UPDATE AS ...
```

---

## Views

| Type | Pattern | Example |
|------|---------|---------|
| Standard view | `v_<Name>` | `v_ActiveCustomers`, `v_OrderSummary` |
| Indexed (materialized) view | `v_<Name>` (same, but document it) | `v_DailyRevenue` |
| Alternative prefix | `vw_<Name>` | `vw_ActiveCustomers` |

```sql
CREATE OR ALTER VIEW sales.v_ActiveCustomers AS ...
CREATE OR ALTER VIEW sales.v_OrderSummary AS ...
```

---

## Sequences

- Pattern: `seq_<object>_<column>` or `seq_<purpose>`

```sql
seq_invoice_number
seq_order_id
seq_batch_job_id
```

```sql
CREATE SEQUENCE finance.seq_invoice_number AS INT START WITH 1 ...
```

---

## User-Defined Types

| Type | Pattern | Example |
|------|---------|---------|
| Alias type | `<SemanticName>` | `CustomerName`, `EmailAddress`, `PhoneNumber` |
| Table type | `<Name>TableType` or `<Name>List` | `OrderLineTableType`, `IntIdList` |

```sql
CREATE TYPE dbo.EmailAddress FROM NVARCHAR(256) NULL;
CREATE TYPE dbo.OrderLineTableType AS TABLE (...);
CREATE TYPE dbo.IntIdList AS TABLE (Id INT NOT NULL PRIMARY KEY);
```

---

## Full-Text Objects

| Object | Pattern | Example |
|--------|---------|---------|
| Full-text catalog | `<Purpose>FTCatalog` | `ProductSearchCatalog`, `DocumentSearchCatalog` |
| Full-text stoplist | `<Purpose>Stoplist` | `ProductStoplist`, `DocumentStoplist` |

---

## Summary Quick Reference

| Object | Pattern |
|--------|---------|
| Schema | `lowercase` |
| Table | `PascalCase` singular |
| Column | `PascalCase` |
| PK | `PK_<Table>` |
| FK | `FK_<Child>_<Parent>` |
| Unique constraint | `UQ_<Table>_<Column>` |
| Check constraint | `CK_<Table>_<Column>` |
| Default constraint | `DF_<Table>_<Column>` |
| Non-clustered index | `IX_<Table>_<Column>` |
| Clustered index (non-PK) | `CX_<Table>_<Column>` |
| Stored procedure | `usp_<action>_<object>` |
| Scalar function | `ufn_<name>` |
| Table-valued function | `uft_<name>` |
| Trigger | `tr_<Table>_<Event>` |
| View | `v_<Name>` or `vw_<Name>` |
| Sequence | `seq_<purpose>` |
| Table type | `<Name>TableType` |
| Alias type | `<SemanticName>` |
