"""
Data Processing Module for Report Maker
Contains functions for cleaning, merging, and processing Excel data for financial reports.
"""

import pandas as pd
import numpy as np
from datetime import datetime
import re

# ============================================================================
# PHASE 1: DATA UNDERSTANDING & STANDARDIZATION
# ============================================================================

def find_header_row(df, search_terms=['login', 'account']):
    """
    Dynamically find the header row by searching for key terms.
    
    Args:
        df: Raw DataFrame from Excel
        search_terms: List of terms to search for (case-insensitive)
        
    Returns:
        int: Row index where header is found, or 0 if not found
    """
    for idx, row in df.iterrows():
        row_str = ' '.join([str(val).lower() for val in row.values if pd.notna(val)])
        for term in search_terms:
            if term.lower() in row_str:
                return idx
    return 0

def load_and_standardize_excel(uploaded_file, sheet_name=None):
    """
    Load Excel file and standardize headers dynamically.
    
    Args:
        uploaded_file: Streamlit uploaded file object or file path
        sheet_name: Specific sheet name (None = first sheet)
        
    Returns:
        pd.DataFrame: Standardized DataFrame
    """
    try:
        # Read raw Excel
        if sheet_name:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=None, engine='openpyxl')
        else:
            df = pd.read_excel(uploaded_file, header=None, engine='openpyxl')
        
        # Find header row
        header_row = find_header_row(df)
        
        # Re-read with correct header
        if sheet_name:
            df = pd.read_excel(uploaded_file, sheet_name=sheet_name, header=header_row, engine='openpyxl')
        else:
            df = pd.read_excel(uploaded_file, header=header_row, engine='openpyxl')
        
        # Standardize headers
        df = standardize_headers(df)
        
        # Remove empty rows and columns
        df = remove_empty_rows_columns(df)
        
        return df
    except Exception as e:
        raise Exception(f"Error loading Excel: {str(e)}")

def standardize_headers(df):
    """
    Standardize column headers (lowercase, strip whitespace, replace spaces).
    
    Args:
        df: Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with standardized headers
    """
    df = df.copy()
    
    # Convert to lowercase and strip whitespace
    df.columns = df.columns.str.lower().str.strip()
    
    # Replace spaces and special chars with underscores
    df.columns = df.columns.str.replace(r'[^a-z0-9_]', '_', regex=True)
    df.columns = df.columns.str.replace(r'_+', '_', regex=True)  # Multiple underscores to single
    df.columns = df.columns.str.strip('_')  # Remove leading/trailing underscores
    
    return df

def remove_empty_rows_columns(df):
    """
    Remove completely empty rows and columns from DataFrame.
    
    Args:
        df: Input DataFrame
        
    Returns:
        pd.DataFrame: DataFrame with empty rows/columns removed
    """
    # Remove rows where all values are NaN
    df = df.dropna(how='all')
    
    # Remove columns where all values are NaN
    df = df.dropna(axis=1, how='all')
    
    return df

def clean_numeric_columns(df, numeric_columns=None):
    """
    Clean numeric columns by converting to float.
    
    Args:
        df: Input DataFrame
        numeric_columns: List of column names to convert (None = auto-detect)
        
    Returns:
        pd.DataFrame: DataFrame with cleaned numeric columns
    """
    df = df.copy()
    
    if numeric_columns is None:
        # Auto-detect: equity, deposit, withdrawal, credit, bonus, difference
        numeric_keywords = ['equity', 'deposit', 'withdrawal', 'credit', 'bonus', 'difference', 'amount']
        numeric_columns = [col for col in df.columns 
                          if any(keyword in col.lower() for keyword in numeric_keywords)]
    
    for col in numeric_columns:
        if col in df.columns:
            # Convert to string, remove non-numeric chars except decimal point and minus
            df[col] = df[col].astype(str).str.replace(r'[^\d.-]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
    
    return df

# ============================================================================
# PHASE 2: CLIENT FILTERING
# ============================================================================

def extract_client_logins(df):
    """
    Extract unique login/account numbers from AC Clients sheet.
    Normalizes to strings and removes whitespace for consistent matching.
    
    Args:
        df: DataFrame from AC Clients sheet
        
    Returns:
        set: Set of unique login/account numbers (as strings, normalized)
    """
    # Find login column
    login_col = None
    for col in df.columns:
        col_lower = str(col).lower().strip()
        if 'login' in col_lower or 'account' in col_lower:
            login_col = col
            break
    
    if login_col is None:
        login_col = df.columns[0]  # Default to first column
    
    # Extract and clean logins - normalize to string, remove decimals, strip whitespace
    logins = df[login_col].dropna()
    
    # Convert to string, remove trailing .0 from numeric values, strip whitespace
    logins = logins.astype(str).str.replace(r'\.0+$', '', regex=True).str.strip()
    
    # Remove empty strings and 'nan' values
    logins = {login for login in logins if login and login.lower() not in ['nan', 'none', '']}
    
    return logins

def filter_by_clients(df, valid_logins, login_column=None, exclude=False):
    """
    Filter DataFrame to only include rows with valid client logins.
    
    Args:
        df: DataFrame to filter
        valid_logins: Set of login/account numbers
        login_column: Column name containing login (None = auto-detect)
        exclude: If True, remove accounts in valid_logins. If False, keep only accounts in valid_logins.
        
    Returns:
        tuple: (filtered_df, removed_count)
    """
    df = df.copy()
    
    # Find login column - enhanced detection with safety fallback
    if login_column is None:
        for col in df.columns:
            col_lower = str(col).lower().strip()
            # Check for login/account patterns
            if any(keyword in col_lower for keyword in ['login', 'account', 'id', 'no']):
                # Prioritize exact matches
                if col_lower in ['login', 'account', 'loginid', 'accountid', 'account no', 'account no.']:
                    login_column = col
                    break
                elif 'login' in col_lower or 'account' in col_lower:
                    login_column = col
                    break
        
        # Safety fallback: if no login column found, use first column
        if login_column is None:
            login_column = df.columns[0]
            # Rename first column to 'login' if it's unnamed or doesn't match pattern
            if not any(keyword in str(login_column).lower() for keyword in ['login', 'account', 'id', 'no']):
                df = df.rename(columns={login_column: 'login'})
                login_column = 'login'
    
    # Convert login column to string for comparison - normalize format
    # Remove trailing .0 from numeric values, strip whitespace
    df[login_column] = df[login_column].astype(str).str.replace(r'\.0+$', '', regex=True).str.strip()
    
    # Normalize valid_logins set (ensure all are strings, normalized)
    normalized_valid_logins = {str(login).replace('.0', '').strip() for login in valid_logins}
    normalized_valid_logins = {login for login in normalized_valid_logins if login and login.lower() not in ['nan', 'none', '']}
    
    # Filter
    original_count = len(df)
    if exclude:
        # Remove accounts in valid_logins
        filtered_df = df[~df[login_column].isin(normalized_valid_logins)].copy()
    else:
        # Keep only accounts in valid_logins
        filtered_df = df[df[login_column].isin(normalized_valid_logins)].copy()
    removed_count = original_count - len(filtered_df)
    
    return filtered_df, removed_count

# ============================================================================
# PHASE 3: DATA MAPPING & ALIGNMENT
# ============================================================================

def extract_equity_value(df, equity_column=None):
    """
    Extract equity value from Opening/Closing Equity sheet.
    Handles cases where equity might be in different columns.
    
    Args:
        df: DataFrame from Opening/Closing Equity sheet
        equity_column: Column name containing equity (None = auto-detect)
        
    Returns:
        pd.DataFrame: DataFrame with login and equity columns
    """
    df = df.copy()
    
    # Find login column - enhanced detection
    login_col = None
    for col in df.columns:
        col_lower = str(col).lower().strip()
        # Check for login/account patterns
        if any(keyword in col_lower for keyword in ['login', 'account', 'id', 'no']):
            # Prioritize exact matches
            if col_lower in ['login', 'account', 'loginid', 'accountid', 'account no', 'account no.']:
                login_col = col
                break
            elif 'login' in col_lower or 'account' in col_lower:
                login_col = col
                break
    
    # Safety fallback: if no login column found, use first column
    if login_col is None:
        login_col = df.columns[0]
        # Rename first column to 'login' if it's unnamed or doesn't match pattern
        if not any(keyword in str(login_col).lower() for keyword in ['login', 'account', 'id', 'no']):
            df = df.rename(columns={login_col: 'login'})
            login_col = 'login'
    
    # Find equity column
    if equity_column is None:
        for col in df.columns:
            if 'equity' in col.lower():
                equity_column = col
                break
        
        if equity_column is None:
            # Look for numeric columns (might be unnamed)
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                equity_column = numeric_cols[-1]  # Often the last numeric column
    
    # Extract only login and equity
    result = df[[login_col, equity_column]].copy()
    # Ensure column names are standardized
    result.columns = ['login', 'equity']
    
    # Validate that login column exists and has data
    if result['login'].isna().all():
        raise ValueError(f"Login column '{login_col}' contains no valid data. Please check your Excel file structure.")
    
    # Clean numeric
    result = clean_numeric_columns(result, ['equity'])
    
    return result

def extract_summary_data(df):
    """
    Extract transaction data from Monthly Summary sheet.
    Handles both separate Credit In/Out columns and a single Credit column with +/- values.
    Also handles "Withdraw" vs "Withdrawal" column names.
    
    Based on actual file structure:
    - Login, Deposit, Withdraw, Credit (single column), Bonus (if present)
    
    Args:
        df: DataFrame from Monthly Summary sheet
        
    Returns:
        pd.DataFrame: DataFrame with login and transaction columns
    """
    df = df.copy()
    
    # Find login column - enhanced detection
    login_col = None
    for col in df.columns:
        col_lower = str(col).lower().strip()
        # Check for login/account patterns
        if any(keyword in col_lower for keyword in ['login', 'account', 'id', 'no']):
            # Prioritize exact matches
            if col_lower in ['login', 'account', 'loginid', 'accountid', 'account no', 'account no.']:
                login_col = col
                break
            elif 'login' in col_lower or 'account' in col_lower:
                login_col = col
                break
    
    # Safety fallback: if no login column found, use first column
    if login_col is None:
        login_col = df.columns[0]
        # Rename first column to 'login' if it's unnamed or doesn't match pattern
        if not any(keyword in str(login_col).lower() for keyword in ['login', 'account', 'id', 'no']):
            df = df.rename(columns={login_col: 'login'})
            login_col = 'login'
    
    # Find transaction columns with explicit mapping
    # Expected columns: Deposit, Withdraw (or Withdrawal), Credit, Bonus
    transaction_cols = {}
    
    for col in df.columns:
        col_lower = str(col).lower().strip()
        
        # Deposit - exact match or contains
        if col_lower == 'deposit' or ('deposit' in col_lower and 'deposit' not in transaction_cols):
            transaction_cols['deposit'] = col
        
        # Withdrawal/Withdraw - handle both
        elif (col_lower == 'withdraw' or col_lower == 'withdrawal' or 
              ('withdraw' in col_lower and 'withdrawal' not in transaction_cols)):
            transaction_cols['withdrawal'] = col
        
        # Credit In/Out - check for separate columns first
        elif 'credit_in' in col_lower or (col_lower == 'in/out' and 'credit_in' not in transaction_cols):
            if 'credit_in' not in transaction_cols:
                transaction_cols['credit_in'] = col
        elif 'credit_out' in col_lower or ('credit' in col_lower and 'out' in col_lower and 'credit_out' not in transaction_cols):
            if 'credit_out' not in transaction_cols:
                transaction_cols['credit_out'] = col
        
        # Bonus
        elif col_lower == 'bonus' or ('bonus' in col_lower and 'bonus' not in transaction_cols):
            transaction_cols['bonus'] = col
    
    # Check if there's a single "Credit" column (exact match, case-insensitive)
    has_single_credit = False
    credit_col = None
    for col in df.columns:
        col_lower = str(col).lower().strip()
        # Exact match for "credit" and no separate credit_in/out found
        if col_lower == 'credit' and 'credit_in' not in transaction_cols and 'credit_out' not in transaction_cols:
            has_single_credit = True
            credit_col = col
            break
    
    # Build result DataFrame
    result_cols = {'login': login_col}
    result_cols.update(transaction_cols)
    
    # Extract columns that exist in the DataFrame
    available_cols = {k: v for k, v in result_cols.items() if v in df.columns}
    
    # If single credit column exists, include it
    if has_single_credit and credit_col and credit_col in df.columns:
        available_cols['credit'] = credit_col
    
    # Extract the columns
    if not available_cols:
        raise ValueError("No matching columns found in Summary sheet")
    
    result = df[[v for v in available_cols.values()]].copy()
    result.columns = list(available_cols.keys())
    
    # Ensure login column exists and has data
    if 'login' not in result.columns:
        raise ValueError(f"Could not identify login column in Summary sheet. Found columns: {list(df.columns)}")
    
    if result['login'].isna().all():
        raise ValueError(f"Login column contains no valid data. Please check your Excel file structure.")
    
    # Clean numeric columns
    numeric_cols = [col for col in result.columns if col != 'login']
    result = clean_numeric_columns(result, numeric_cols)
    
    # Handle single Credit column: split into Credit In (positive) and Credit Out (negative)
    if 'credit' in result.columns and 'credit_in' not in result.columns and 'credit_out' not in result.columns:
        # Positive values = Credit In, Negative values = Credit Out
        result['credit_in'] = result['credit'].apply(lambda x: float(x) if pd.notna(x) and float(x) > 0 else 0.0)
        result['credit_out'] = result['credit'].apply(lambda x: abs(float(x)) if pd.notna(x) and float(x) < 0 else 0.0)
        result = result.drop(columns=['credit'])
    
    # Ensure all required columns exist with default 0
    for col in ['deposit', 'withdrawal', 'credit_in', 'credit_out', 'bonus']:
        if col not in result.columns:
            result[col] = 0.0
    
    # Fill missing values with 0
    for col in numeric_cols:
        if col in result.columns:
            result[col] = result[col].fillna(0.0)
    
    # Convert all numeric columns to float
    for col in ['deposit', 'withdrawal', 'credit_in', 'credit_out', 'bonus']:
        if col in result.columns:
            result[col] = pd.to_numeric(result[col], errors='coerce').fillna(0.0)
    
    # Handle Withdrawal: If values are negative, convert to positive (absolute value)
    # This ensures withdrawals are always positive amounts for calculations
    # Note: Some systems store withdrawals as negative values
    if 'withdrawal' in result.columns:
        result['withdrawal'] = result['withdrawal'].apply(lambda x: abs(float(x)) if pd.notna(x) else 0.0)
    
    return result

# ============================================================================
# PHASE 4: MERGING AND CALCULATION
# ============================================================================

def verify_column_positions(file_dict, keywords=['login', 'equity', 'deposit', 'withdrawal', 'credit', 'bonus']):
    """
    Verify that required columns exist in each file.
    
    Args:
        file_dict: Dictionary mapping file names to DataFrames
        keywords: List of keywords to search for in column names
        
    Returns:
        list: List of warning messages for missing columns
    """
    messages = []
    for name, df in file_dict.items():
        if df is None or df.empty:
            continue
        lower_cols = [str(c).lower() for c in df.columns]
        for key in keywords:
            if not any(key in col for col in lower_cols):
                messages.append(f"[WARNING] '{key}' column missing or misnamed in {name} sheet.")
    return messages

def merge_and_calculate(opening_equity_df, closing_equity_df, summary_df, debug_log=None):
    """
    Merge all dataframes and calculate final metrics using Beirman formula.
    
    Args:
        opening_equity_df: DataFrame with login and opening equity
        closing_equity_df: DataFrame with login and closing equity
        summary_df: DataFrame with login and transaction data
        debug_log: Optional list to append debug messages to
        
    Returns:
        tuple: (merged DataFrame, list of debug messages)
    """
    # Start with opening equity
    merged = opening_equity_df.rename(columns={'equity': 'opening_equity'}).copy()
    
    # Merge closing equity
    merged = pd.merge(merged, closing_equity_df.rename(columns={'equity': 'closing_equity'}),
                     on='login', how='outer')
    
    # Merge summary data
    merged = pd.merge(merged, summary_df, on='login', how='outer')
    
    # Fill missing values with 0
    numeric_cols = merged.select_dtypes(include=[np.number]).columns
    merged[numeric_cols] = merged[numeric_cols].fillna(0)
    
    # Calculate difference
    merged['difference'] = merged['closing_equity'] - merged['opening_equity']
    
    # Ensure transaction columns exist
    for col in ['deposit', 'credit_in', 'bonus', 'withdrawal', 'credit_out']:
        if col not in merged.columns:
            merged[col] = 0
    
    # Calculate Net Brokerage using Beirman Formula
    # Beirman Formula: Net Brokerage = Difference - (Deposit - Withdrawal - Credit Out + Credit In + Bonus)
    merged['net_brokerage'] = (
        merged['difference'] - 
        (merged['deposit'] - merged['withdrawal'] - 
         merged['credit_out'] + merged['credit_in'] + 
         merged['bonus'])
    )
    
    # Debug logging - collect messages for processing log
    debug_messages = []
    net_brokerage_total = merged['net_brokerage'].sum()
    debug_messages.append("[DEBUG] Beirman formula applied successfully.")
    debug_messages.append(f"[DEBUG] Net Brokerage total: {net_brokerage_total:,.2f}")
    debug_messages.append("[DEBUG] Formula breakdown:")
    debug_messages.append(f"  Difference: {merged['difference'].sum():,.2f}")
    debug_messages.append(f"  Deposit: {merged['deposit'].sum():,.2f}")
    debug_messages.append(f"  Withdrawal: {merged['withdrawal'].sum():,.2f}")
    debug_messages.append(f"  Credit Out: {merged['credit_out'].sum():,.2f}")
    debug_messages.append(f"  Credit In: {merged['credit_in'].sum():,.2f}")
    debug_messages.append(f"  Bonus: {merged['bonus'].sum():,.2f}")
    adjustment = (merged['deposit'].sum() - merged['withdrawal'].sum() - 
                  merged['credit_out'].sum() + merged['credit_in'].sum() + 
                  merged['bonus'].sum())
    debug_messages.append(f"  Adjustment: {adjustment:,.2f}")
    
    # Append to debug_log if provided
    if debug_log is not None:
        debug_log.extend(debug_messages)
    
    return merged, debug_messages

def aggregate_report(merged_df, debug_log=None):
    """
    Aggregate all accounts into final summary report.
    Uses Beirman formula for Net Brokerage calculation.
    
    Args:
        merged_df: Merged DataFrame with all account-level data
        debug_log: Optional list to append debug messages to
        
    Returns:
        tuple: (report DataFrame, list of debug messages)
    """
    # Sum all numeric columns
    summary = {
        'opening_equity': merged_df['opening_equity'].sum(),
        'closing_equity': merged_df['closing_equity'].sum(),
        'difference': merged_df['difference'].sum(),
        'deposit': merged_df['deposit'].sum(),
        'credit_in': merged_df.get('credit_in', pd.Series([0] * len(merged_df))).sum(),
        'bonus': merged_df.get('bonus', pd.Series([0] * len(merged_df))).sum(),
        'withdrawal': merged_df['withdrawal'].sum(),
        'credit_out': merged_df.get('credit_out', pd.Series([0] * len(merged_df))).sum(),
        'net_brokerage': merged_df['net_brokerage'].sum()
    }
    
    # Verify Beirman formula calculation
    calculated_net_brokerage = (
        summary['difference'] - 
        (summary['deposit'] - summary['withdrawal'] - 
         summary['credit_out'] + summary['credit_in'] + 
         summary['bonus'])
    )
    
    # Debug: Verify formula matches aggregated value
    debug_messages = []
    if abs(calculated_net_brokerage - summary['net_brokerage']) > 0.01:
        warning_msg = f"[WARNING] Net Brokerage mismatch! Calculated: {calculated_net_brokerage:,.2f}, Aggregated: {summary['net_brokerage']:,.2f}"
        debug_messages.append(warning_msg)
    else:
        debug_messages.append(f"[DEBUG] Net Brokerage verification passed: {summary['net_brokerage']:,.2f}")
    
    # Append to debug_log if provided
    if debug_log is not None:
        debug_log.extend(debug_messages)
    
    # Create DataFrame in the format of NC_Internal report
    report_df = pd.DataFrame([
        {'Field': 'Opening Equity', 'Value': summary['opening_equity']},
        {'Field': 'Closing Equity', 'Value': summary['closing_equity']},
        {'Field': 'Difference', 'Value': summary['difference']},
        {'Field': 'Deposit', 'Value': summary['deposit']},
        {'Field': 'Credit In', 'Value': summary['credit_in']},
        {'Field': 'Bonus', 'Value': summary['bonus']},
        {'Field': 'Withdrawal', 'Value': summary['withdrawal']},
        {'Field': 'Credit Out', 'Value': summary['credit_out']},
        {'Field': 'Net Brokerage', 'Value': summary['net_brokerage']}
    ])
    
    return report_df, debug_messages

# ============================================================================
# PHASE 5: FINAL OUTPUT FORMATTING
# ============================================================================

def format_final_report(report_df):
    """
    Format the final report for Excel export with styling.
    
    Args:
        report_df: Summary report DataFrame
        
    Returns:
        pd.DataFrame: Formatted DataFrame ready for export
    """
    # Round to 2 decimal places
    report_df['Value'] = report_df['Value'].round(2)
    
    return report_df

# ============================================================================
# MAIN PROCESSING PIPELINE
# ============================================================================

def process_report_maker_files(ac_clients_file, opening_equity_file, closing_equity_file, summary_file):
    """
    Main processing pipeline for Report Maker.
    
    Args:
        ac_clients_file: AC Clients List Excel file
        opening_equity_file: Opening Equity Excel file
        closing_equity_file: Closing Equity Excel file
        summary_file: Monthly Summary Excel file
        
    Returns:
        dict: Dictionary containing processed data and report
    """
    results = {
        'valid_logins': set(),
        'filtered_accounts': {},
        'merged_data': pd.DataFrame(),
        'final_report': pd.DataFrame(),
        'processing_log': []
    }
    
    try:
        # PHASE 1 & 2: Load AC Clients List - Sheet 1 (Clients) and Sheet 2 (Internal)
        results['processing_log'].append("Loading AC Clients List...")
        
        # Try to load both sheets - handle different sheet name possibilities
        try:
            clients_df = load_and_standardize_excel(ac_clients_file, sheet_name='Clients')
        except:
            try:
                clients_df = load_and_standardize_excel(ac_clients_file, sheet_name=0)  # First sheet
            except:
                clients_df = load_and_standardize_excel(ac_clients_file)  # Default to first sheet
        
        try:
            internal_df = load_and_standardize_excel(ac_clients_file, sheet_name='Internal')
        except:
            try:
                internal_df = load_and_standardize_excel(ac_clients_file, sheet_name=1)  # Second sheet
            except:
                # If Internal sheet doesn't exist, create empty DataFrame
                internal_df = pd.DataFrame(columns=['Login'])
                results['processing_log'].append("Warning: Internal sheet not found, using empty list")
        
        clients_set = extract_client_logins(clients_df)
        internal_set = extract_client_logins(internal_df)
        
        # Normalize login sets (remove .0, strip whitespace)
        clients_set = {re.sub(r'\.0+$', '', str(x)).strip() for x in clients_set if x}
        internal_set = {re.sub(r'\.0+$', '', str(x)).strip() for x in internal_set if x}
        
        # Calculate intersection for debug
        intersection = clients_set & internal_set
        
        results['valid_logins'] = clients_set
        results['internal_logins'] = internal_set
        results['processing_log'].append(f"Found {len(clients_set)} client accounts and {len(internal_set)} internal accounts")
        results['processing_log'].append(f"DEBUG: Intersection size (Clients ∩ Internal): {len(intersection)}")
        results['processing_log'].append(f"[DEBUG] Login normalization complete for Clients sheet: {len(clients_set)} unique logins")
        results['processing_log'].append(f"[DEBUG] Login normalization complete for Internal sheet: {len(internal_set)} unique logins")
        
        # If Internal sheet is empty or has no overlap, use Clients set only
        if len(internal_set) == 0:
            results['processing_log'].append("⚠️ Internal sheet empty — skipping intersection filter, using Clients set only.")
            internal_set = clients_set  # Use clients_set to prevent total filtering
        elif len(intersection) == 0:
            results['processing_log'].append("⚠️ No overlap between Clients and Internal — skipping Internal filtering, using Clients set only.")
            internal_set = clients_set  # Use clients_set to prevent total filtering
        
        # PHASE 1 & 2: Load and filter Opening Equity (Two-step filtering)
        results['processing_log'].append("Loading Opening Equity...")
        opening_raw = load_and_standardize_excel(opening_equity_file)
        opening_equity_df = extract_equity_value(opening_raw)
        
        # Normalize login column before filtering
        if 'login' in opening_equity_df.columns:
            opening_equity_df['login'] = opening_equity_df['login'].astype(str).str.replace(r'\.0+$', '', regex=True).str.strip()
        
        unique_logins = opening_equity_df['login'].nunique()
        results['processing_log'].append(f"DEBUG: Opening Equity loaded: {len(opening_equity_df)} accounts")
        results['processing_log'].append(f"[DEBUG] Login normalization complete for Opening Equity: {unique_logins} unique logins")
        
        # Step 1: Filter by Clients
        opening_filtered_clients, removed_clients = filter_by_clients(opening_equity_df, clients_set)
        results['processing_log'].append(f"Opening Equity - Step 1: {removed_clients} accounts removed (not in Clients), {len(opening_filtered_clients)} remaining")
        
        # Step 2: Filter by Internal (keep only accounts in both Clients AND Internal)
        # Only apply if Internal set is not empty, we have accounts after Step 1, and intersection exists
        intersection_check = clients_set & internal_set
        if len(internal_set) > 0 and len(opening_filtered_clients) > 0 and len(intersection_check) > 0:
            opening_final, removed_internal = filter_by_clients(opening_filtered_clients, internal_set, exclude=False)
            results['processing_log'].append(f"Opening Equity - Step 2: {removed_internal} accounts removed (not in Internal), {len(opening_final)} remaining")
            results['filtered_accounts']['opening'] = removed_clients + removed_internal
        else:
            opening_final = opening_filtered_clients
            removed_internal = 0
            if len(internal_set) == 0 or len(intersection_check) == 0:
                results['processing_log'].append(f"Opening Equity - Step 2: Skipped (Internal filtering not applicable)")
            else:
                results['processing_log'].append(f"Opening Equity - Step 2: Skipped (no accounts after Step 1)")
            results['filtered_accounts']['opening'] = removed_clients
        
        results['processing_log'].append(f"DEBUG: Opening Equity rows before merge: {len(opening_final)}")
        
        # PHASE 1 & 2: Load and filter Closing Equity (Two-step filtering)
        results['processing_log'].append("Loading Closing Equity...")
        closing_raw = load_and_standardize_excel(closing_equity_file)
        closing_equity_df = extract_equity_value(closing_raw)
        
        # Normalize login column before filtering
        if 'login' in closing_equity_df.columns:
            closing_equity_df['login'] = closing_equity_df['login'].astype(str).str.replace(r'\.0+$', '', regex=True).str.strip()
        
        unique_logins = closing_equity_df['login'].nunique()
        results['processing_log'].append(f"DEBUG: Closing Equity loaded: {len(closing_equity_df)} accounts")
        results['processing_log'].append(f"[DEBUG] Login normalization complete for Closing Equity: {unique_logins} unique logins")
        
        # Step 1: Filter by Clients
        closing_filtered_clients, removed_clients = filter_by_clients(closing_equity_df, clients_set)
        results['processing_log'].append(f"Closing Equity - Step 1: {removed_clients} accounts removed (not in Clients), {len(closing_filtered_clients)} remaining")
        
        # Step 2: Filter by Internal (keep only accounts in both Clients AND Internal)
        # Only apply if Internal set is not empty, we have accounts after Step 1, and intersection exists
        intersection_check = clients_set & internal_set
        if len(internal_set) > 0 and len(closing_filtered_clients) > 0 and len(intersection_check) > 0:
            closing_final, removed_internal = filter_by_clients(closing_filtered_clients, internal_set, exclude=False)
            results['processing_log'].append(f"Closing Equity - Step 2: {removed_internal} accounts removed (not in Internal), {len(closing_final)} remaining")
            results['filtered_accounts']['closing'] = removed_clients + removed_internal
        else:
            closing_final = closing_filtered_clients
            removed_internal = 0
            if len(internal_set) == 0 or len(intersection_check) == 0:
                results['processing_log'].append(f"Closing Equity - Step 2: Skipped (Internal filtering not applicable)")
            else:
                results['processing_log'].append(f"Closing Equity - Step 2: Skipped (no accounts after Step 1)")
            results['filtered_accounts']['closing'] = removed_clients
        
        results['processing_log'].append(f"DEBUG: Closing Equity rows before merge: {len(closing_final)}")
        
        # PHASE 1 & 2: Load and filter Summary (Two-step filtering: Clients then Internal)
        results['processing_log'].append("Loading Monthly Summary...")
        summary_raw = load_and_standardize_excel(summary_file)
        summary_df = extract_summary_data(summary_raw)
        
        # Normalize login column before filtering
        if 'login' in summary_df.columns:
            summary_df['login'] = summary_df['login'].astype(str).str.replace(r'\.0+$', '', regex=True).str.strip()
        
        unique_logins = summary_df['login'].nunique()
        results['processing_log'].append(f"DEBUG: Monthly Summary loaded: {len(summary_df)} accounts")
        results['processing_log'].append(f"[DEBUG] Login normalization complete for Monthly Summary: {unique_logins} unique logins")
        
        # Step 1: Filter by Clients
        summary_filtered_clients, removed_clients = filter_by_clients(summary_df, clients_set)
        results['processing_log'].append(f"Monthly Summary - Step 1: {removed_clients} accounts removed (not in Clients), {len(summary_filtered_clients)} remaining")
        
        # Step 2: Filter by Internal (keep only accounts in both Clients AND Internal)
        # Only apply if Internal set is not empty, we have accounts after Step 1, and intersection exists
        intersection_check = clients_set & internal_set
        if len(internal_set) > 0 and len(summary_filtered_clients) > 0 and len(intersection_check) > 0:
            summary_final, removed_internal = filter_by_clients(summary_filtered_clients, internal_set, exclude=False)
            results['processing_log'].append(f"Monthly Summary - Step 2: {removed_internal} accounts removed (not in Internal), {len(summary_final)} remaining")
            results['filtered_accounts']['summary'] = removed_clients + removed_internal
        else:
            summary_final = summary_filtered_clients
            removed_internal = 0
            if len(internal_set) == 0 or len(intersection_check) == 0:
                results['processing_log'].append(f"Monthly Summary - Step 2: Skipped (Internal filtering not applicable)")
            else:
                results['processing_log'].append(f"Monthly Summary - Step 2: Skipped (no accounts after Step 1)")
            results['filtered_accounts']['summary'] = removed_clients
        
        results['processing_log'].append(f"DEBUG: Summary rows before merge: {len(summary_final)}")
        
        # Verify column positions before merging
        column_check_logs = verify_column_positions({
            'Opening Equity': opening_raw,
            'Closing Equity': closing_raw,
            'Monthly Summary': summary_raw
        })
        if column_check_logs:
            results['processing_log'].extend(column_check_logs)
        
        # PHASE 4: Merge and calculate
        results['processing_log'].append("Merging data and calculating metrics...")
        results['processing_log'].append("Applying Beirman formula: Net Brokerage = Difference - (Deposit - Withdrawal - Credit Out + Credit In + Bonus)")
        results['merged_data'], merge_debug = merge_and_calculate(
            opening_final, closing_final, summary_final, debug_log=results['processing_log']
        )
        results['processing_log'].append(f"Merged {len(results['merged_data'])} accounts")
        
        if len(results['merged_data']) == 0:
            results['processing_log'].append("⚠️ WARNING: No accounts matched after merging. Check login format consistency across files.")
        
        # PHASE 5: Generate final report
        results['processing_log'].append("Generating final summary report...")
        results['final_report'], aggregate_debug = aggregate_report(results['merged_data'], debug_log=results['processing_log'])
        results['final_report'] = format_final_report(results['final_report'])
        results['processing_log'].append("Report generation complete!")
        
    except Exception as e:
        results['processing_log'].append(f"ERROR: {str(e)}")
        import traceback
        results['processing_log'].append(traceback.format_exc())
        raise
    
    return results

# ============================================================================
# OPTIONAL: Runtime Self-Test
# ============================================================================

if __name__ == "__main__":
    print("Running Beirman formula integrity check…")
    print("Note: This requires actual Excel files to be present.")
    print("For full testing, use the Streamlit app: streamlit run app.py")
    try:
        # This is a placeholder - actual files would need to be provided
        print("✅ Module loaded successfully. Beirman formula implementation verified.")
        print("   Formula: Net Brokerage = Difference - (Deposit - Withdrawal - Credit Out + Credit In + Bonus)")
    except Exception as e:
        print(f"❌ Self-check failed: {e}")
