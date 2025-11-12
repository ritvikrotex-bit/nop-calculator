"""
Test script to verify Report Maker processing logic with actual Excel files.
This simulates what happens when files are uploaded in Streamlit.
"""

import pandas as pd
from data_processor import (
    load_and_standardize_excel,
    extract_client_logins,
    extract_equity_value,
    extract_summary_data,
    filter_by_clients,
    merge_and_calculate,
    aggregate_report
)

def test_processing():
    """Test the processing pipeline with actual Excel files."""
    
    print("=" * 60)
    print("Report Maker - Processing Test")
    print("=" * 60)
    print()
    
    # Test 1: Load Opening Equity
    print("1. Testing Opening Equity loading...")
    try:
        opening_df = load_and_standardize_excel('Opening Equity.xlsx')
        opening_equity = extract_equity_value(opening_df)
        print(f"   [OK] Opening Equity loaded: {len(opening_equity)} accounts")
        print(f"   Sample: Login={opening_equity['login'].iloc[0]}, Equity={opening_equity['equity'].iloc[0]}")
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        return False
    
    # Test 2: Load Closing Equity
    print("\n2. Testing Closing Equity loading...")
    try:
        closing_df = load_and_standardize_excel('Closing Equity.xlsx')
        closing_equity = extract_equity_value(closing_df)
        print(f"   [OK] Closing Equity loaded: {len(closing_equity)} accounts")
        print(f"   Sample: Login={closing_equity['login'].iloc[0]}, Equity={closing_equity['equity'].iloc[0]}")
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        return False
    
    # Test 3: Load Summary
    print("\n3. Testing Summary loading...")
    try:
        summary_df = load_and_standardize_excel('Summary 2025_11_12 14_23_03.xlsx')
        summary_data = extract_summary_data(summary_df)
        print(f"   [OK] Summary loaded: {len(summary_data)} accounts")
        print(f"   Columns: {list(summary_data.columns)}")
        print(f"   Sample Credit In: {summary_data['credit_in'].head(3).tolist()}")
        print(f"   Sample Credit Out: {summary_data['credit_out'].head(3).tolist()}")
        print(f"   Sample Withdrawal: {summary_data['withdrawal'].head(3).tolist()}")
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        return False
    
    # Test 4: Test filtering (simulate with sample client list)
    print("\n4. Testing filtering logic...")
    try:
        # Create sample client set from first 10 accounts in opening equity
        sample_clients = set(opening_equity['login'].head(10).astype(str))
        sample_internal = set(opening_equity['login'].head(5).astype(str))  # Intersection of first 5
        
        # Test two-step filtering
        filtered_step1, removed1 = filter_by_clients(opening_equity, sample_clients)
        filtered_step2, removed2 = filter_by_clients(filtered_step1, sample_internal, exclude=False)
        
        print(f"   [OK] Filtering works:")
        print(f"      Step 1: {len(filtered_step1)} accounts (removed {removed1})")
        print(f"      Step 2: {len(filtered_step2)} accounts (removed {removed2})")
        print(f"      Final: {len(filtered_step2)} accounts in intersection")
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        return False
    
    # Test 5: Test merge and calculation
    print("\n5. Testing merge and calculation...")
    try:
        # Use sample filtered data
        merged = merge_and_calculate(
            opening_equity.head(10),
            closing_equity.head(10),
            summary_data.head(10)
        )
        print(f"   [OK] Merge successful: {len(merged)} accounts")
        print(f"   Columns: {list(merged.columns)}")
        
        # Test aggregation
        report = aggregate_report(merged)
        print(f"   [OK] Report generated: {len(report)} fields")
        print(f"   Report structure:")
        for _, row in report.iterrows():
            print(f"      {row['Field']}: {row['Value']:,.2f}")
    except Exception as e:
        print(f"   [ERROR] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("[SUCCESS] ALL TESTS PASSED!")
    print("=" * 60)
    print("\nNote: AC Clients file not found - this is expected.")
    print("The app will work when you upload the AC Clients file with:")
    print("  - Sheet 1: 'Clients' (or first sheet)")
    print("  - Sheet 2: 'Internal' (or second sheet)")
    
    return True

if __name__ == "__main__":
    test_processing()

