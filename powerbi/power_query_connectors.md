# Power Query Connectors for ETL Dashboard

This document provides Power Query M scripts to connect Power BI to the processed data from the ETL Dashboard.

## Table of Contents
- [CSV Folder Connection](#csv-folder-connection)
- [Parquet Files Connection](#parquet-files-connection)
- [SQLite Database Connection](#sqlite-database-connection)
- [Individual Table Connections](#individual-table-connections)

## CSV Folder Connection

Connect to all CSV files in the processed data folder:

```m
let
    Source = Folder.Files("C:\path\to\your\data\processed"),
    FilterCSV = Table.SelectRows(Source, each Text.EndsWith([Name], ".csv")),
    AddTableColumn = Table.AddColumn(FilterCSV, "Data", each Csv.Document([Content], [Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None])),
    AddTableName = Table.AddColumn(AddTableColumn, "TableName", each Text.BeforeDelimiter([Name], ".")),
    ExpandData = Table.ExpandTableColumn(AddTableColumn, "Data", null, null),
    PromoteHeaders = Table.PromoteHeaders(ExpandData, [PromoteAllScalars=true])
in
    PromoteHeaders
```

## Parquet Files Connection

Connect to Parquet files (requires Power BI Premium or Pro):

```m
let
    Source = Folder.Files("C:\path\to\your\data\processed"),
    FilterParquet = Table.SelectRows(Source, each Text.EndsWith([Name], ".parquet")),
    AddTableColumn = Table.AddColumn(FilterParquet, "Data", each Parquet.Document([Content])),
    AddTableName = Table.AddColumn(AddTableColumn, "TableName", each Text.BeforeDelimiter([Name], ".")),
    SelectTables = Table.SelectColumns(AddTableColumn, {"TableName", "Data"})
in
    SelectTables
```

## SQLite Database Connection

Connect to the SQLite database containing all tables:

### Prerequisites
1. Install SQLite ODBC driver from: http://www.ch-werner.de/sqliteodbc/
2. Create ODBC DSN or use connection string

### Connection Script
```m
let
    Source = Odbc.DataSource("Driver={SQLite3 ODBC Driver};Database=C:\path\to\your\data\processed\etl.sqlite;", [HierarchicalNavigation=true]),
    Database = Source{[Name="main"]}[Data],
    Tables = Database
in
    Tables
```

### Alternative: Direct File Connection
```m
let
    Source = Sqlite.Database(File.Contents("C:\path\to\your\data\processed\etl.sqlite"))
in
    Source
```

## Individual Table Connections

### MasterBOM Clean Table
```m
let
    Source = Csv.Document(File.Contents("C:\path\to\your\data\processed\masterbom_clean.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"part_id_std", type text},
        {"part_id_raw", type text},
        {"Item Description", type text},
        {"Supplier Name", type text},
        {"PSW", type text},
        {"Approved Date_date", type date},
        {"PSW Date OK_date", type date}
    })
in
    ChangeTypes
```

### Plant Item Status Table
```m
let
    Source = Csv.Document(File.Contents("C:\path\to\your\data\processed\plant_item_status.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"part_id_std", type text},
        {"project_plant", type text},
        {"raw_status", type text},
        {"status_class", type text},
        {"is_duplicate", type logical},
        {"is_new", type logical},
        {"n_active", Int64.Type},
        {"n_inactive", Int64.Type},
        {"n_new", Int64.Type},
        {"n_duplicate", Int64.Type}
    })
in
    ChangeTypes
```

### Fact Parts Table
```m
let
    Source = Csv.Document(File.Contents("C:\path\to\your\data\processed\fact_parts.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"part_id_std", type text},
        {"part_id_raw", type text},
        {"Item Description", type text},
        {"Supplier Name", type text},
        {"psw_ok", type logical},
        {"has_handling_manual", type logical},
        {"far_ok", type logical},
        {"imds_ok", type logical}
    })
in
    ChangeTypes
```

### Status Clean Table
```m
let
    Source = Csv.Document(File.Contents("C:\path\to\your\data\processed\status_clean.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"OEM", type text},
        {"Project", type text},
        {"Total_Part_Numbers", Int64.Type},
        {"PSW_Available", type number},
        {"Drawing_Available", type number},
        {"First_PPAP_Milestone", type text}
    })
in
    ChangeTypes
```

### Date Dimension Table
```m
let
    Source = Csv.Document(File.Contents("C:\path\to\your\data\processed\dim_dates.csv"),[Delimiter=",", Columns=null, Encoding=65001, QuoteStyle=QuoteStyle.None]),
    PromoteHeaders = Table.PromoteHeaders(Source, [PromoteAllScalars=true]),
    ChangeTypes = Table.TransformColumnTypes(PromoteHeaders,{
        {"date", type date},
        {"role", type text},
        {"year", Int64.Type},
        {"month", Int64.Type},
        {"day", Int64.Type},
        {"quarter", Int64.Type},
        {"week", Int64.Type},
        {"weekday", Int64.Type},
        {"month_name", type text},
        {"day_name", type text}
    })
in
    ChangeTypes
```

## Data Refresh Configuration

### Automatic Refresh
To set up automatic refresh:

1. **Power BI Service**: Configure scheduled refresh in the dataset settings
2. **Power BI Desktop**: Use "Refresh" button or set up automatic refresh intervals
3. **Gateway**: For on-premises data, configure Power BI Gateway

### Incremental Refresh
For large datasets, consider incremental refresh:

```m
let
    Source = YourDataSource,
    FilteredRows = Table.SelectRows(Source, each [LastModified] >= RangeStart and [LastModified] < RangeEnd)
in
    FilteredRows
```

## Troubleshooting

### Common Issues

1. **File Path Errors**: Ensure file paths are correct and accessible
2. **Permission Issues**: Verify Power BI has read access to the data folder
3. **Data Type Errors**: Check column data types match the schema
4. **Encoding Issues**: Use UTF-8 encoding for CSV files

### Performance Tips

1. **Use Parquet**: Parquet files load faster than CSV
2. **SQLite for Complex Queries**: Use SQLite for joins and complex filtering
3. **Column Selection**: Only import needed columns
4. **Data Types**: Specify correct data types to improve performance

## Security Considerations

1. **File Permissions**: Restrict access to processed data folder
2. **Connection Strings**: Avoid hardcoding sensitive paths
3. **Data Gateway**: Use secure gateway for on-premises connections
4. **Row-Level Security**: Implement RLS in Power BI if needed
