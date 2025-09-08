import pandas as pd
import os
from typing import Dict, List, Tuple, Optional

class FileStructureDetector:
    """Detects and validates file structures for the dashboard application"""
    
    def __init__(self):
        self.supported_formats = {'.xlsx', '.xls', '.csv'}
        self.required_columns = ['Project Name', 'Task Name', 'Assigned to', 'Start Date', 'Days Required', 'End Date', 'Progress']
    
    def detect_file_type(self, filepath: str) -> str:
        """Detect file type based on extension"""
        _, ext = os.path.splitext(filepath.lower())
        return ext
    
    def analyze_structure(self, filepath: str) -> Dict:
        """Analyze file structure and return detailed information"""
        if not os.path.exists(filepath):
            return {'status': 'error', 'message': 'File not found'}
        
        file_type = self.detect_file_type(filepath)
        
        if file_type not in self.supported_formats:
            return {'status': 'error', 'message': f'Unsupported file type: {file_type}'}
        
        try:
            # Read file based on type
            if file_type in ['.xlsx', '.xls']:
                df = pd.read_excel(filepath)
            elif file_type == '.csv':
                df = pd.read_csv(filepath)
            
            analysis = {
                'status': 'success',
                'file_type': file_type,
                'rows': len(df),
                'columns': list(df.columns),
                'column_count': len(df.columns),
                'missing_columns': [],
                'extra_columns': [],
                'data_types': df.dtypes.to_dict(),
                'structure_valid': False,
                'suggestions': []
            }
            
            # Check required columns
            missing_cols = [col for col in self.required_columns if col not in df.columns]
            extra_cols = [col for col in df.columns if col not in self.required_columns]
            
            analysis['missing_columns'] = missing_cols
            analysis['extra_columns'] = extra_cols
            analysis['structure_valid'] = len(missing_cols) == 0
            
            # Generate suggestions
            if missing_cols:
                analysis['suggestions'].append(f"Add missing columns: {', '.join(missing_cols)}")
            
            if extra_cols:
                analysis['suggestions'].append(f"Consider removing extra columns: {', '.join(extra_cols)}")
            
            # Check data quality
            self._check_data_quality(df, analysis)
            
            return analysis
            
        except Exception as e:
            return {'status': 'error', 'message': f'Error reading file: {str(e)}'}
    
    def _check_data_quality(self, df: pd.DataFrame, analysis: Dict):
        """Check data quality and add suggestions"""
        # Check for empty rows
        empty_rows = df.isnull().all(axis=1).sum()
        if empty_rows > 0:
            analysis['suggestions'].append(f"Remove {empty_rows} empty rows")
        
        # Check Progress column format
        if 'Progress' in df.columns:
            progress_col = df['Progress']
            if progress_col.dtype == 'object':
                analysis['suggestions'].append("Progress column contains text - should be numeric (0-100 or 0-1)")
            elif progress_col.max() > 100:
                analysis['suggestions'].append("Progress values exceed 100 - check format")
        
        # Check date columns
        date_columns = ['Start Date', 'End Date']
        for col in date_columns:
            if col in df.columns:
                try:
                    pd.to_datetime(df[col])
                except:
                    analysis['suggestions'].append(f"{col} column has invalid date format")

def respond_to_structure(analysis: Dict) -> str:
    """Generate appropriate response based on file structure analysis"""
    if analysis['status'] == 'error':
        return f"❌ Error: {analysis['message']}"
    
    response = []
    
    # File info
    response.append(f"📁 File Type: {analysis['file_type'].upper()}")
    response.append(f"📊 Data: {analysis['rows']} rows, {analysis['column_count']} columns")
    
    # Structure validation
    if analysis['structure_valid']:
        response.append("✅ Structure: Valid - All required columns present")
    else:
        response.append("⚠️ Structure: Invalid")
        if analysis['missing_columns']:
            response.append(f"   Missing: {', '.join(analysis['missing_columns'])}")
    
    # Extra columns
    if analysis['extra_columns']:
        response.append(f"ℹ️ Extra columns: {', '.join(analysis['extra_columns'])}")
    
    # Suggestions
    if analysis['suggestions']:
        response.append("\n💡 Suggestions:")
        for suggestion in analysis['suggestions']:
            response.append(f"   • {suggestion}")
    
    # Action recommendations
    response.append("\n🔧 Recommended Actions:")
    if analysis['structure_valid']:
        response.append("   • File is ready to use")
        response.append("   • Upload directly to dashboard")
    else:
        response.append("   • Fix missing columns before upload")
        response.append("   • Use template file as reference")
    
    return "\n".join(response)