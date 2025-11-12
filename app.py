"""
Report Maker
A Streamlit application for processing Excel files and generating financial reports.
"""

import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import os
from datetime import datetime
import io
from data_processor import process_report_maker_files

# Page configuration
st.set_page_config(
    page_title="Report Maker",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'report_ready' not in st.session_state:
    st.session_state.report_ready = False

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def export_to_excel(report_df, merged_df=None):
    """
    Export report DataFrame to Excel file with formatting.
    
    Args:
        report_df: Final summary report DataFrame
        merged_df: Optional account-level merged data
        
    Returns:
        bytes: Excel file as bytes for download
    """
    output = io.BytesIO()
    
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        # Write summary report
        report_df.to_excel(writer, sheet_name='Summary', index=False)
        
        # Get workbook and worksheet for formatting
        workbook = writer.book
        worksheet = writer.sheets['Summary']
        
        # Define formats
        header_format = workbook.add_format({
            'bold': True,
            'bg_color': '#366092',
            'font_color': 'white',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1
        })
        
        value_format = workbook.add_format({
            'num_format': '#,##0.00',
            'align': 'right',
            'border': 1
        })
        
        net_brokerage_format = workbook.add_format({
            'bold': True,
            'num_format': '#,##0.00',
            'bg_color': '#FFFF00',  # Yellow highlight
            'align': 'right',
            'border': 1
        })
        
        # Apply header format
        worksheet.set_row(0, None, header_format)
        
        # Set column widths
        worksheet.set_column('A:A', 20)
        worksheet.set_column('B:B', 20)
        
        # Apply value formats
        for row_num in range(1, len(report_df) + 1):
            field = report_df.iloc[row_num - 1]['Field']
            if field == 'Net Brokerage':
                worksheet.write(row_num, 1, report_df.iloc[row_num - 1]['Value'], net_brokerage_format)
            else:
                worksheet.write(row_num, 1, report_df.iloc[row_num - 1]['Value'], value_format)
        
        # Write account-level data if provided
        if merged_df is not None and not merged_df.empty:
            merged_df.to_excel(writer, sheet_name='Account Details', index=False)
            worksheet2 = writer.sheets['Account Details']
            worksheet2.set_column('A:J', 15)
    
    output.seek(0)
    return output.getvalue()

# ============================================================================
# STREAMLIT UI
# ============================================================================

# Title and description
st.title("📊 Report Maker")
st.markdown("---")
st.markdown("Generate financial reports by processing Opening Equity, Closing Equity, and Monthly Summary data.")

# Sidebar - File Upload Section
with st.sidebar:
    st.header("📁 File Upload")
    st.markdown("Upload the 4 required Excel files:")
    
    # File uploaders
    ac_clients_file = st.file_uploader(
        "1. AC Clients List",
        type=['xlsx', 'xls'],
        help="Excel file containing valid client accounts"
    )
    
    opening_equity_file = st.file_uploader(
        "2. Opening Equity Sheet",
        type=['xlsx', 'xls'],
        help="Excel file with opening equity values"
    )
    
    closing_equity_file = st.file_uploader(
        "3. Closing Equity Sheet",
        type=['xlsx', 'xls'],
        help="Excel file with closing equity values"
    )
    
    summary_file = st.file_uploader(
        "4. Monthly Summary Sheet",
        type=['xlsx', 'xls'],
        help="Excel file with transaction data (Deposits, Withdrawals, Credits, Bonus)"
    )
    
    st.markdown("---")
    
    # Process button
    all_files_uploaded = all([ac_clients_file, opening_equity_file, closing_equity_file, summary_file])
    
    if all_files_uploaded:
        if st.button("🔄 Generate Report", type="primary", use_container_width=True):
            st.session_state.processed_data = None
            st.session_state.report_ready = False
            
            with st.spinner("Processing files... This may take a moment."):
                try:
                    # Process files
                    results = process_report_maker_files(
                        ac_clients_file,
                        opening_equity_file,
                        closing_equity_file,
                        summary_file
                    )
                    
                    st.session_state.processed_data = results
                    st.session_state.report_ready = True
                    # Store file references for debug section
                    st.session_state.opening_equity_file = opening_equity_file
                    st.session_state.summary_file = summary_file
                    st.success("✅ Report generated successfully!")
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error processing files: {str(e)}")
                    st.exception(e)
    else:
        st.info("👆 Please upload all 4 files to generate the report.")

# Main content area
if st.session_state.report_ready and st.session_state.processed_data:
    results = st.session_state.processed_data
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Summary Report", "📊 Account Details", "📝 Processing Log", "📥 Download"])
    
    with tab1:
        st.header("Final Summary Report")
        st.markdown("---")
        
        # Display report in table format
        report_df = results['final_report']
        
        # Create styled display
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Report Summary")
            for idx, row in report_df.iterrows():
                field = row['Field']
                value = row['Value']
                
                if field == 'Net Brokerage':
                    st.markdown(f"**<span style='background-color: yellow; padding: 5px;'>{field}:</span>**", unsafe_allow_html=True)
                    st.markdown(f"**<span style='background-color: yellow; padding: 5px;'>{value:,.2f}</span>**", unsafe_allow_html=True)
                else:
                    st.markdown(f"**{field}:**")
                    st.markdown(f"{value:,.2f}")
        
        with col2:
            # Display as DataFrame
            display_df = report_df.copy()
            display_df['Value'] = display_df['Value'].apply(lambda x: f"{x:,.2f}")
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        
        # Statistics
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Accounts Processed", len(results['merged_data']))
        with col2:
            st.metric("Valid Client Accounts", len(results['valid_logins']))
        with col3:
            st.metric("Internal Accounts", len(results.get('internal_logins', set())))
        with col4:
            total_filtered = sum(results['filtered_accounts'].values())
            st.metric("Accounts Filtered Out", total_filtered)
        
        # Debug information (expandable)
        with st.expander("🔍 Debug Information", expanded=False):
            st.write("**Clients Set Sample (first 10):**")
            clients_list = list(results['valid_logins'])[:10]
            st.write(clients_list)
            
            st.write("**Internal Set Sample (first 10):**")
            internal_list = list(results.get('internal_logins', set()))[:10]
            st.write(internal_list if internal_list else "Empty")
            
            if not results['merged_data'].empty:
                st.write("**Merged Data Sample (first 5 logins):**")
                st.dataframe(results['merged_data'][['login']].head(5))
            else:
                st.warning("⚠️ No accounts matched after filtering. Check Processing Log for details.")
                
                # Show sample logins from each source
                st.write("**Sample logins from Opening Equity (first 5):**")
                try:
                    from data_processor import load_and_standardize_excel, extract_equity_value
                    # Reset file pointer if needed
                    if hasattr(opening_equity_file, 'seek'):
                        opening_equity_file.seek(0)
                    opening_raw = load_and_standardize_excel(opening_equity_file)
                    opening_df = extract_equity_value(opening_raw)
                    st.write(opening_df['login'].head(5).tolist())
                except Exception as e:
                    st.write(f"Could not load Opening Equity: {str(e)}")
                
                st.write("**Sample logins from Summary (first 5):**")
                try:
                    from data_processor import load_and_standardize_excel, extract_summary_data
                    # Reset file pointer if needed
                    if hasattr(summary_file, 'seek'):
                        summary_file.seek(0)
                    summary_raw = load_and_standardize_excel(summary_file)
                    summary_df = extract_summary_data(summary_raw)
                    st.write(summary_df['login'].head(5).tolist())
                except Exception as e:
                    st.write(f"Could not load Summary: {str(e)}")
    
    with tab2:
        st.header("Account-Level Details")
        
        if not results['merged_data'].empty:
            merged_df = results['merged_data']
            
            # Display data
            st.dataframe(merged_df, use_container_width=True)
            
            # Summary statistics
            st.markdown("---")
            st.subheader("Account Statistics")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Accounts", len(merged_df))
            with col2:
                st.metric("Avg Opening Equity", f"{merged_df['opening_equity'].mean():,.2f}")
            with col3:
                st.metric("Avg Closing Equity", f"{merged_df['closing_equity'].mean():,.2f}")
            with col4:
                st.metric("Avg Net Brokerage", f"{merged_df['net_brokerage'].mean():,.2f}")
        else:
            st.warning("No account-level data available.")
    
    with tab3:
        st.header("Processing Log")
        st.markdown("---")
        
        for log_entry in results['processing_log']:
            if log_entry.startswith("ERROR"):
                st.error(log_entry)
            else:
                st.info(log_entry)
        
        # Filtering details
        st.markdown("---")
        st.subheader("Filtering Details")
        filtering_df = pd.DataFrame([
            {'Sheet': 'Opening Equity', 'Accounts Removed': results['filtered_accounts'].get('opening', 0)},
            {'Sheet': 'Closing Equity', 'Accounts Removed': results['filtered_accounts'].get('closing', 0)},
            {'Sheet': 'Monthly Summary', 'Accounts Removed': results['filtered_accounts'].get('summary', 0)}
        ])
        st.dataframe(filtering_df, use_container_width=True, hide_index=True)
    
    with tab4:
        st.header("Download Report")
        st.markdown("---")
        
        if not results['final_report'].empty:
            st.success("✅ Report is ready for download!")
            
            # Preview
            st.subheader("Report Preview")
            st.dataframe(results['final_report'], use_container_width=True, hide_index=True)
            
            # Download button with month/year naming
            now = datetime.now()
            month_name = now.strftime("%B")  # Full month name (e.g., "November")
            year = now.year
            filename = f"Report_Maker_{month_name}_{year}.xlsx"
            
            excel_bytes = export_to_excel(results['final_report'], results.get('merged_data'))
            
            st.download_button(
                label="📥 Download Report (Excel)",
                data=excel_bytes,
                file_name=filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary"
            )
            
            # Report summary
            st.markdown("---")
            st.subheader("Report Summary")
            summary_row = results['final_report'][results['final_report']['Field'] == 'Net Brokerage'].iloc[0]
            net_brokerage = summary_row['Value']
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Net Brokerage", f"{net_brokerage:,.2f}")
            with col2:
                st.metric("Total Accounts", len(results['merged_data']))
        else:
            st.warning("Report DataFrame is empty. Please regenerate the report.")
    
else:
    # Welcome screen
    st.info("👆 Please upload all 4 required Excel files using the sidebar to get started.")
    
    # Instructions
    with st.expander("📖 How to use Report Maker"):
        st.markdown("""
        ### Step-by-Step Guide:
        
        1. **Upload AC Clients List**
           - Excel file containing valid client account numbers
           - Used to filter accounts in other sheets
        
        2. **Upload Opening Equity Sheet**
           - Excel file with equity values as of the start date
           - Should contain Login/Account and Equity columns
        
        3. **Upload Closing Equity Sheet**
           - Excel file with equity values as of the end date
           - Should contain Login/Account and Equity columns
        
        4. **Upload Monthly Summary Sheet**
           - Excel file with all transactions for the period
           - Should contain: Deposit, Withdrawal, Credit In, Credit Out, Bonus columns
        
        5. **Generate Report**
           - Click "Generate Report" button
           - The app will:
             - Filter accounts to only include those in AC Clients List
             - Calculate Opening Equity, Closing Equity, and Difference
             - Calculate Net Brokerage using the formula:
               `Net Brokerage = Difference - (Deposits - Withdrawals + Credit Out - Credit In + Bonus)`
             - Generate a formatted summary report
        
        6. **Download Report**
           - View the summary in the "Summary Report" tab
           - Check account-level details in "Account Details" tab
           - Download formatted Excel file from "Download" tab
        
        ### Expected File Structure:
        - **Headers**: May start at row 1, 2, or 3 (auto-detected)
        - **Login/Account Column**: Contains account numbers
        - **Numeric Columns**: Equity, Deposit, Withdrawal, etc.
        - **Format**: .xlsx or .xls files
        """)
    
    # Features
    st.subheader("✨ Features")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        **🔍 Smart Header Detection**
        - Automatically finds header rows
        - Handles inconsistent Excel formats
        """)
    
    with col2:
        st.markdown("""
        **🎯 Client Filtering**
        - Filters accounts by AC Clients List
        - Removes internal/extra accounts
        """)
    
    with col3:
        st.markdown("""
        **📊 Auto Calculations**
        - Opening/Closing Equity difference
        - Net Brokerage calculation
        - Transaction summaries
        """)

# Footer
st.markdown("---")
st.caption("Report Maker | Built with Streamlit")
