import pandas as pd
import os

# Test CSV to Excel conversion
def test_conversion():
    # Create a sample CSV file
    test_data = {
        'Project Name': ['Project A', 'Project B'],
        'Task Name': ['Task 1', 'Task 2'],
        'Assigned to': ['John', 'Jane'],
        'Start Date': ['2024-01-01', '2024-01-02'],
        'End Date': ['2024-01-10', '2024-01-15'],
        'Progress': [50, 75]
    }
    
    df = pd.DataFrame(test_data)
    
    # Save as CSV
    csv_file = 'test_sample.csv'
    df.to_csv(csv_file, index=False)
    print(f"Created test CSV: {csv_file}")
    
    # Convert to Excel
    try:
        df_read = pd.read_csv(csv_file)
        excel_file = 'test_converted.xlsx'
        df_read.to_excel(excel_file, index=False)
        print(f"Successfully converted to Excel: {excel_file}")
        
        # Verify the conversion
        df_excel = pd.read_excel(excel_file)
        print("Excel file contents:")
        print(df_excel)
        
        return True
    except Exception as e:
        print(f"Conversion failed: {e}")
        return False

if __name__ == "__main__":
    test_conversion()