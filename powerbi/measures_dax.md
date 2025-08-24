# DAX Measures for ETL Dashboard

This document provides pre-built DAX measures for analyzing the processed ETL data in Power BI.

## Table of Contents
- [Part Status Measures](#part-status-measures)
- [Quality Measures](#quality-measures)
- [Date Intelligence Measures](#date-intelligence-measures)
- [Project/Plant Measures](#projectplant-measures)
- [Supplier Measures](#supplier-measures)
- [Percentage Measures](#percentage-measures)

## Part Status Measures

### Basic Counts
```dax
Active Parts = 
COUNTROWS(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "active"
    )
)
```

```dax
Inactive Parts = 
COUNTROWS(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "inactive"
    )
)
```

```dax
New Parts = 
COUNTROWS(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "new"
    )
)
```

```dax
Duplicate Parts = 
COUNTROWS(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "duplicate"
    )
)
```

```dax
Total Parts = 
DISTINCTCOUNT(plant_item_status[part_id_std])
```

### Status Distribution
```dax
Active Parts % = 
DIVIDE([Active Parts], [Total Parts], 0) * 100
```

```dax
New Parts % = 
DIVIDE([New Parts], [Total Parts], 0) * 100
```

```dax
Status Distribution = 
"Active: " & FORMAT([Active Parts %], "0.0%") & 
" | New: " & FORMAT([New Parts %], "0.0%") & 
" | Inactive: " & FORMAT(DIVIDE([Inactive Parts], [Total Parts], 0), "0.0%")
```

## Quality Measures

### PSW (Part Submission Warrant) Measures
```dax
PSW OK Count = 
COUNTROWS(
    FILTER(
        fact_parts,
        fact_parts[psw_ok] = TRUE
    )
)
```

```dax
PSW OK % = 
DIVIDE([PSW OK Count], COUNTROWS(fact_parts), 0)
```

```dax
PSW Available = 
COUNTROWS(
    FILTER(
        fact_parts,
        NOT ISBLANK(fact_parts[PSW]) && fact_parts[PSW] <> ""
    )
)
```

### FAR (First Article Report) Measures
```dax
FAR OK Count = 
COUNTROWS(
    FILTER(
        fact_parts,
        fact_parts[far_ok] = TRUE
    )
)
```

```dax
FAR OK % = 
DIVIDE([FAR OK Count], COUNTROWS(fact_parts), 0)
```

### IMDS (International Material Data System) Measures
```dax
IMDS OK Count = 
COUNTROWS(
    FILTER(
        fact_parts,
        fact_parts[imds_ok] = TRUE
    )
)
```

```dax
IMDS OK % = 
DIVIDE([IMDS OK Count], COUNTROWS(fact_parts), 0)
```

### Handling Manual Measures
```dax
Has Handling Manual = 
COUNTROWS(
    FILTER(
        fact_parts,
        fact_parts[has_handling_manual] = TRUE
    )
)
```

```dax
Handling Manual % = 
DIVIDE([Has Handling Manual], COUNTROWS(fact_parts), 0)
```

### Overall Quality Score
```dax
Quality Score = 
VAR PSWScore = [PSW OK %]
VAR FARScore = [FAR OK %]
VAR IMDSScore = [IMDS OK %]
VAR HandlingScore = [Handling Manual %]
RETURN
    (PSWScore + FARScore + IMDSScore + HandlingScore) / 4
```

## Date Intelligence Measures

### Time-based Comparisons
```dax
Parts This Month = 
CALCULATE(
    [Total Parts],
    DATESMTD(dim_dates[date])
)
```

```dax
Parts Last Month = 
CALCULATE(
    [Total Parts],
    DATEADD(dim_dates[date], -1, MONTH)
)
```

```dax
Parts MoM Growth = 
DIVIDE([Parts This Month] - [Parts Last Month], [Parts Last Month], 0)
```

### Approval Trends
```dax
Approved This Quarter = 
CALCULATE(
    COUNTROWS(masterbom_clean),
    DATESQTD(dim_dates[date]),
    NOT ISBLANK(masterbom_clean[Approved Date_date])
)
```

```dax
Average Days to Approval = 
AVERAGEX(
    FILTER(
        masterbom_clean,
        NOT ISBLANK(masterbom_clean[Approved Date_date]) &&
        NOT ISBLANK(masterbom_clean[PSW Date OK_date])
    ),
    DATEDIFF(
        masterbom_clean[PSW Date OK_date],
        masterbom_clean[Approved Date_date],
        DAY
    )
)
```

## Project/Plant Measures

### Plant Performance
```dax
Active Plants = 
DISTINCTCOUNT(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "active"
    )[project_plant]
)
```

```dax
Plants with New Parts = 
DISTINCTCOUNT(
    FILTER(
        plant_item_status,
        plant_item_status[status_class] = "new"
    )[project_plant]
)
```

```dax
Average Parts per Plant = 
DIVIDE([Total Parts], DISTINCTCOUNT(plant_item_status[project_plant]), 0)
```

### Project Status
```dax
Project Completion % = 
VAR TotalProjectParts = 
    SUMX(
        VALUES(plant_item_status[project_plant]),
        CALCULATE(COUNTROWS(plant_item_status))
    )
VAR ActiveProjectParts = 
    SUMX(
        VALUES(plant_item_status[project_plant]),
        CALCULATE(
            COUNTROWS(plant_item_status),
            plant_item_status[status_class] = "active"
        )
    )
RETURN
    DIVIDE(ActiveProjectParts, TotalProjectParts, 0)
```

## Supplier Measures

### Supplier Performance
```dax
Unique Suppliers = 
DISTINCTCOUNT(fact_parts[Supplier Name])
```

```dax
Top Supplier by Parts = 
TOPN(
    1,
    SUMMARIZE(
        fact_parts,
        fact_parts[Supplier Name],
        "Part Count", COUNTROWS(fact_parts)
    ),
    [Part Count],
    DESC
)
```

```dax
Supplier Quality Score = 
AVERAGEX(
    VALUES(fact_parts[Supplier Name]),
    CALCULATE([Quality Score])
)
```

## Percentage Measures

### Status Project Breakdown
```dax
Project Status Summary = 
VAR CurrentProject = SELECTEDVALUE(plant_item_status[project_plant])
VAR ActiveCount = CALCULATE([Active Parts], plant_item_status[project_plant] = CurrentProject)
VAR NewCount = CALCULATE([New Parts], plant_item_status[project_plant] = CurrentProject)
VAR InactiveCount = CALCULATE([Inactive Parts], plant_item_status[project_plant] = CurrentProject)
VAR TotalCount = ActiveCount + NewCount + InactiveCount
RETURN
    "Active: " & ActiveCount & " (" & FORMAT(DIVIDE(ActiveCount, TotalCount, 0), "0%") & ")" &
    " | New: " & NewCount & " (" & FORMAT(DIVIDE(NewCount, TotalCount, 0), "0%") & ")" &
    " | Inactive: " & InactiveCount & " (" & FORMAT(DIVIDE(InactiveCount, TotalCount, 0), "0%") & ")"
```

### Conditional Formatting Measures
```dax
Status Color = 
SWITCH(
    TRUE(),
    [Active Parts %] >= 80, "Green",
    [Active Parts %] >= 60, "Yellow",
    "Red"
)
```

```dax
Quality Color = 
SWITCH(
    TRUE(),
    [Quality Score] >= 0.9, "Green",
    [Quality Score] >= 0.7, "Yellow",
    "Red"
)
```

## Advanced Measures

### Ranking Measures
```dax
Plant Rank by Active Parts = 
RANKX(
    ALL(plant_item_status[project_plant]),
    CALCULATE([Active Parts]),
    ,
    DESC
)
```

```dax
Supplier Rank by Quality = 
RANKX(
    ALL(fact_parts[Supplier Name]),
    CALCULATE([Quality Score]),
    ,
    DESC
)
```

### Variance Measures
```dax
Parts Variance from Average = 
VAR PlantAverage = 
    CALCULATE(
        [Average Parts per Plant],
        ALL(plant_item_status[project_plant])
    )
VAR CurrentPlantParts = [Total Parts]
RETURN
    CurrentPlantParts - PlantAverage
```

### What-If Analysis
```dax
Projected Active Parts = 
VAR ImprovementRate = 'What-If Parameters'[Improvement Rate Value] / 100
VAR CurrentActive = [Active Parts]
VAR CurrentNew = [New Parts]
VAR ProjectedFromNew = CurrentNew * ImprovementRate
RETURN
    CurrentActive + ProjectedFromNew
```

## Usage Tips

1. **Measure Tables**: Create a dedicated "Measures" table to organize all measures
2. **Formatting**: Use FORMAT() function for consistent number formatting
3. **Error Handling**: Always use DIVIDE() instead of "/" to handle division by zero
4. **Performance**: Use CALCULATE() efficiently and avoid complex nested calculations
5. **Documentation**: Add descriptions to measures using the Description property

## Relationships Required

Ensure these relationships exist in your data model:
- `plant_item_status[part_id_std]` → `fact_parts[part_id_std]` (Many-to-One)
- `masterbom_clean[part_id_std]` → `fact_parts[part_id_std]` (Many-to-One)
- Date columns → `dim_dates[date]` (Many-to-One)
