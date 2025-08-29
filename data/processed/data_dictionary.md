# Data Dictionary

Generated data dictionary for ETL processed tables.

## masterbom_clean

**Rows:** 4313
**Columns:** 111

| Column | Type | Description |
|--------|------|-------------|
| Yazaki PN | object | Data column |
| BX726_BEV_JOB1+90_YMOK | object | Data column |
| BX726_BEV_JOB1+90_YRL | object | Data column |
| BX726_MCA_JOB1+90_YMOK | object | Data column |
| BX726_MCA_JOB1+90_YRL | object | Data column |
| BX726_GSR_TT_YMOK | object | Data column |
| BX726_GSR_TT_YRL | object | Data column |
| CX482_24MY_YBE | object | Data column |
| V710_B1_W2_HV_JOB1+90_YBE | object | Data column |
| V710_JOB1+90_YMO-K | object | Data column |
| V710_JOB1+90_YOT-G | object | Data column |
| V710_JOB1+90_YOT-K | object | Data column |
| V710_JOB1+90_YWTT | object | Data column |
| V710_B2_J74_JOB1+90_YMOK | object | Data column |
| V710_B2_J74_JOB1+90_YOT-G | object | Data column |
| V710_B2_J74_JOB1+90_YOT-K | object | Data column |
| V710_B2_J74_JOB1+90_YWTT | object | Data column |
| V710_HV_AWD_TT_YBE | object | Data column |
| V710_AWD_PP_YMOK | object | Data column |
| V710_AWD_TT_YOTG | object | Data column |
| V710_AWD_PP_YOTK | object | Data column |
| V710_AWD_PP_YWTT | object | Data column |
| FORD_V769_JOB1+180_HV_YRL | object | Data column |
| Item Description | object | Part description |
| Supplier Name | object | Primary supplier name |
| Supplier PN | object | Data column |
| Original Supplier Name | object | Data column |
| Original Supplier PN | object | Data column |
| Customer PN | object | Data column |
| Document Complete | object | Data column |
| IsCustomerDrawing | object | Data column |
| PSW Type | object | Data column |
| PSW Sub Type | object | Data column |
| Approved Date | object | Data column |
| PSW Date OK | object | Data column |
| PSW | object | Part Submission Warrant status |
| Part Specification | object | Data column |
| Plant FAR | object | Data column |
| TDC Remarks | object | Data column |
| YPN Status | object | Data column |
| Handling Manual | object | Data column |
| Customer Engineering Approval | object | Data column |
| Promised Date | object | Data column |
| IMDS STATUS
(Yes, No, N/A) | object | Data column |
| IMDS REMARKS | object | Data column |
| FAR Status | object | First Article Report status |
| FAR Promised date | object | Data column |
| PPAP Details | object | Production Part Approval Process details |
| BUHIN | object | Data column |
| R @R OK/NOK | object | Data column |
| Active Parts | object | Data column |
| YBE All Projects | object | Data column |
| YMO-K All Projects | object | Data column |
| YOT-G All Projects | object | Data column |
| YOT-K All Projects | object | Data column |
| YRL All Projects | object | Data column |
| YWTT All Projects | object | Data column |
| BX726 BEV | object | Data column |
| V769 | object | Data column |
| BX726 MCA | object | Data column |
| BX726 GSR | object | Data column |
| V710 B1 | object | Data column |
| CX482 | object | Data column |
| V710 B2 | object | Data column |
| V710 ICA AWD BEV | object | Data column |
| Not 100% Approved
(Under Deviation) | object | Data column |
| Parts Under Deviation | object | Data column |
| part_id_raw | object | Original part ID from source |
| part_id_std | object | Standardized part ID (cleaned) |
| Supplier PN_date | object | Data column |
| Supplier PN_year | float64 | Data column |
| Supplier PN_month | float64 | Data column |
| Supplier PN_day | float64 | Data column |
| Supplier PN_qtr | float64 | Data column |
| Supplier PN_week | UInt32 | Data column |
| Original Supplier PN_date | object | Data column |
| Original Supplier PN_year | float64 | Data column |
| Original Supplier PN_month | float64 | Data column |
| Original Supplier PN_day | float64 | Data column |
| Original Supplier PN_qtr | float64 | Data column |
| Original Supplier PN_week | UInt32 | Data column |
| Approved Date_date | object | Data column |
| Approved Date_year | float64 | Data column |
| Approved Date_month | float64 | Data column |
| Approved Date_day | float64 | Data column |
| Approved Date_qtr | float64 | Data column |
| Approved Date_week | UInt32 | Data column |
| PSW Date OK_date | datetime64[ns] | Data column |
| PSW Date OK_year | float64 | Data column |
| PSW Date OK_month | float64 | Data column |
| PSW Date OK_day | float64 | Data column |
| PSW Date OK_qtr | float64 | Data column |
| PSW Date OK_week | UInt32 | Data column |
| PSW_date | object | Data column |
| PSW_year | float64 | Data column |
| PSW_month | float64 | Data column |
| PSW_day | float64 | Data column |
| PSW_qtr | float64 | Data column |
| PSW_week | UInt32 | Data column |
| Promised Date_date | object | Data column |
| Promised Date_year | float64 | Data column |
| Promised Date_month | float64 | Data column |
| Promised Date_day | float64 | Data column |
| Promised Date_qtr | float64 | Data column |
| Promised Date_week | UInt32 | Data column |
| FAR Promised date_date | object | Data column |
| FAR Promised date_year | float64 | Data column |
| FAR Promised date_month | float64 | Data column |
| FAR Promised date_day | float64 | Data column |
| FAR Promised date_qtr | float64 | Data column |
| FAR Promised date_week | UInt32 | Data column |

## plant_item_status

**Rows:** 87582
**Columns:** 13

| Column | Type | Description |
|--------|------|-------------|
| part_id_std | object | Standardized part ID |
| part_id_raw | object | Data column |
| Yazaki PN | object | Data column |
| project_plant | object | Project/plant identifier |
| raw_status | object | Original status value (X/D/0/blank) |
| status_class | object | Classified status (active/inactive/new/duplicate) |
| is_duplicate | bool | Whether part is marked as duplicate |
| is_new | bool | Whether part is new to project/plant |
| notes | object | Data column |
| n_active | int64 | Count of active plants for this part |
| n_inactive | int64 | Count of inactive plants for this part |
| n_new | int64 | Data column |
| n_duplicate | int64 | Data column |

## fact_parts

**Rows:** 3981
**Columns:** 15

| Column | Type | Description |
|--------|------|-------------|
| part_id_std | object | Standardized part ID (primary key) |
| part_id_raw | object | Data column |
| Item Description | object | Data column |
| Supplier Name | object | Data column |
| Supplier PN | object | Data column |
| PSW | object | Data column |
| PSW Type | object | Data column |
| PSW Sub Type | object | Data column |
| YPN Status | object | Data column |
| Handling Manual | object | Data column |
| FAR Status | object | Data column |
| PPAP Details | object | Data column |
| psw_ok | bool | Whether PSW is available and OK |
| has_handling_manual | bool | Whether handling manual exists |
| far_ok | bool | Whether FAR status is OK |

## status_clean

**Rows:** 31
**Columns:** 36

| Column | Type | Description |
|--------|------|-------------|
| OEM | object | Original Equipment Manufacturer |
