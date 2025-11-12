# Report Maker — System Behavior Guide (Beirman Formula Edition)

## Overview

Report Maker is a Streamlit-based automation tool that processes monthly brokerage reconciliation by merging **Opening Equity**, **Closing Equity**, and **Monthly Summary** Excel sheets for both **Client** and **Internal** accounts. The system applies the Beirman formula to calculate Net Brokerage, providing a fully auditable workflow with complete transparency in the Processing Log.

---

## Inputs

### AC Clients List
- **Structure**: Excel file containing two sheets:
  - **Sheet 1 (Clients)**: Contains valid client account numbers (Login/Account column)
  - **Sheet 2 (Internal)**: Contains internal/house account numbers for intersection filtering
- **Purpose**: Defines which accounts to include in the final report
- **Filtering Logic**: Only accounts present in **both** Clients and Internal sheets are processed (intersection)

### Opening Equity
- **Structure**: Excel file with Login and Equity columns
- **Purpose**: Starting balance/equity values for each account at the beginning of the period
- **Header Detection**: Automatically detects header row (row 1, 2, or 3)

### Closing Equity
- **Structure**: Excel file with Login and Equity columns
- **Purpose**: Ending balance/equity values for each account at the end of the period
- **Header Detection**: Automatically detects header row (row 1, 2, or 3)

### Monthly Summary
- **Structure**: Excel file with transaction data
- **Required Columns**: Login, Deposit, Withdrawal (or Withdraw), Credit, Bonus (optional)
- **Special Handling**: 
  - Single "Credit" column is automatically split:
    - Positive values → Credit In
    - Negative values → Credit Out (absolute value)
  - Withdrawal values are normalized to positive (handles negative withdrawals)

### Login Normalization
All login/account identifiers are normalized across all input files:
- Removes trailing `.0` from numeric logins (e.g., `123456.0` → `123456`)
- Strips whitespace from login strings
- Handles various column names (Login, Account, LoginID, ID, No)
- Ensures consistent matching across all data sources

### Client/Internal Filtering (Two-Stage Process)
1. **Stage 1 - Clients Filter**: Keep only accounts present in Clients sheet
2. **Stage 2 - Internal Filter**: From Stage 1 result, keep only accounts also in Internal sheet
3. **Result**: Final accounts = Clients ∩ Internal (intersection)
4. **Safety**: If Internal sheet is empty or has no overlap, uses Clients set only (prevents total filtering)

---

## Processing Flow

### 1. Header Detection and Normalization
- **Smart Header Detection**: Automatically finds header row by searching for "Login" or "Account" keywords
- **Column Standardization**: All column names normalized to lowercase, snake_case format
- **Data Type Validation**: Ensures numeric columns are properly typed

### 2. Data Cleaning and Numeric Conversion
- **Empty Row/Column Removal**: Drops rows and columns that are entirely empty
- **Numeric Conversion**: Converts transaction columns (Deposit, Withdrawal, Credit, Bonus) to numeric, handling non-numeric characters
- **Missing Value Handling**: Defaults to 0 for any missing transaction data

### 3. Client/Internal Filtering
- **Two-Stage Filtering**: Applies Clients filter first, then Internal intersection
- **Account Count Tracking**: Logs accounts removed at each stage for transparency
- **Conditional Logic**: Skips Internal filtering if sheet is empty or has no overlap

### 4. Merge and Compute Metrics
- **Merge Strategy**: Outer join on `login` column across all three data sources (Opening, Closing, Summary)
- **Difference Calculation**: `Difference = Closing Equity - Opening Equity`
- **Account Alignment**: Ensures all accounts from filtered sets are included

### 5. Apply Beirman Formula
The system calculates Net Brokerage using the **Beirman formula**:

```
Net Brokerage = Difference - (Deposit - Withdrawal - Credit Out + Credit In + Bonus)
```

**Formula Components:**
- **Difference** = Closing Equity - Opening Equity (net equity change)
- **Deposit** = Total deposits (positive values, represents cash inflow)
- **Withdrawal** = Total withdrawals (normalized to positive, represents cash outflow)
- **Credit Out** = Credits removed from accounts (positive values, represents credit outflow)
- **Credit In** = Credits added to accounts (positive values, represents credit inflow)
- **Bonus** = Bonus adjustments (positive values, represents additional credit)

**Sign Logic:**
- The adjustment term `(Deposit - Withdrawal - Credit Out + Credit In + Bonus)` represents net cash and credit movements
- **Outflows are subtracted** (Withdrawal, Credit Out) — money leaving accounts
- **Inflows are added** (Deposit, Credit In, Bonus) — money entering accounts
- Subtracting this net adjustment from the equity difference isolates the pure brokerage component
- Negative Net Brokerage indicates losses, positive indicates gains

### 6. Verify Aggregated Totals
- **Dynamic Verification**: After aggregation, recalculates Net Brokerage from totals using the Beirman formula
- **Mismatch Detection**: Warns if calculated value differs from aggregated value (> 0.01 tolerance)
- **Formula Integrity**: Confirms Beirman formula was applied correctly at both account and aggregate levels

### 7. Export Formatted Excel + Display Processing Log
- **Output Format**: Single summary report matching NC_Internal template structure
- **File Naming**: `Report_Maker_Month_Year.xlsx` (e.g., `Report_Maker_November_2025.xlsx`)
- **Formatting**: Bold headers, highlighted Net Brokerage row, numeric formatting
- **Account Details**: Optional account-level breakdown sheet included
- **Processing Log**: All computation steps, verifications, and warnings displayed in Streamlit "Processing Log" tab

---

## Logging & Transparency

Every computation step, verification, and header check is routed to the Streamlit **Processing Log** tab, making the workflow fully auditable:

- **Login Normalization**: Reports unique login count for each file
- **Filtering Steps**: Shows accounts removed at each filtering stage
- **Formula Breakdown**: Displays all formula components with totals:
  - Difference, Deposit, Withdrawal, Credit Out, Credit In, Bonus, Adjustment
- **Verification Results**: Confirms calculation correctness
- **Column Warnings**: Alerts if required columns are missing or misnamed
- **Intersection Size**: Reports Clients ∩ Internal overlap count

**Zero Console Output**: All debug messages route to Streamlit interface — nothing is hidden in terminal output. This ensures complete transparency for auditors and compliance teams.

---

## Output

### Final Report Fields
1. **Opening Equity**: Sum of all account opening balances
2. **Closing Equity**: Sum of all account closing balances
3. **Difference**: Closing - Opening (net equity change)
4. **Deposit**: Total deposits across all accounts
5. **Credit In**: Total credits added to accounts
6. **Bonus**: Total bonus adjustments
7. **Withdrawal**: Total withdrawals from accounts
8. **Credit Out**: Total credits removed from accounts
9. **Net Brokerage**: Calculated using Beirman formula (highlighted in yellow)

### Export Format
- **File Name**: `Report_Maker_Month_Year.xlsx` (automatically generated)
- **Sheets**: 
  - "Summary" (formatted NC-style report)
  - "Account Details" (raw merged data for audit trail)
- **Styling**: Bold headers, highlighted Net Brokerage, numeric formatting

---

## Intended Use

This tool is designed for:
- **Brokers**: Monthly reconciliation of client equity and transaction data
- **Auditors**: Complete audit trail of all calculations and filtering decisions
- **Financial Analysts**: Automated calculation of brokerage metrics using Beirman methodology
- **Compliance Teams**: Transparent processing with full logging of all steps

---

© TDFX Capital — Automated Report Maker | Beirman Formula Edition
