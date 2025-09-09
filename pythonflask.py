from flask import Flask, render_template, request, redirect, url_for, flash
import pandas as pd
from datetime import datetime, timedelta
import os
from werkzeug.utils import secure_filename


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # Required for flash messages

# Configuration for file uploads
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xlsx', 'xls', 'csv', 'json'}
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB max file size

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create upload directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

EXCEL_FILE1 = 'None.xlsx'      # Default Excel file path
CURRENT_FILE = EXCEL_FILE1       # Track current active file

def allowed_file(filename):
    """Check if file has allowed extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def init_excel():       # Initialize Excel file with sample data if it doesn't exist
    try:
        pd.read_excel(EXCEL_FILE1)
    except FileNotFoundError:
        data = {
            'Project Name': [],
            'Task Name': [],
            'Assigned to': [],
            'Start Date': [],
            'Days Required': [],
            'End Date': [],
            'Progress': []  
        }
        df = pd.DataFrame(data)
        df.to_excel(EXCEL_FILE1, index=False)

init_excel()

@app.route('/')         #displaying the dashboard
def dashboard():
    global CURRENT_FILE
    df = pd.read_excel(CURRENT_FILE)
    
    # Discover available columns
    available_columns = list(df.columns)
    
    # Handle Progress column if it exists
    if 'Progress' in df.columns:
        if df['Progress'].dtype in [float, int]:
            df['Progress'] = (df['Progress'].fillna(0) * 100).astype(int)
    else:
        df['Progress'] = 0  # Default progress if column doesn't exist
    
    tasks = df.to_dict(orient='records')
    for task in tasks:
        progress = task.get('Progress', 0)
        task['color'] = 'red' if progress == 0 else 'lightgreen'
        task['width'] = progress
        
    # Get current filename for display
    current_filename = os.path.basename(CURRENT_FILE)
    return render_template('dashboard.html', tasks=tasks, current_file=current_filename, available_columns=available_columns)

@app.route('/convert', methods=['GET', 'POST'])
def convert_csv():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith('.csv'):
            try:
                df = pd.read_csv(file)
                
                # Create converted file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_converted_{file.filename.replace('.csv', '.xlsx')}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                
                df.to_excel(filepath, index=False)
                
                from flask import send_file
                return send_file(filepath, as_attachment=True, download_name=f"converted_{file.filename.replace('.csv', '.xlsx')}")
                
            except Exception as e:
                flash(f'Error converting file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            flash('Please select a CSV file', 'error')
            return redirect(request.url)
    
    return render_template('convert.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_file():
    global CURRENT_FILE
    
    if request.method == 'POST':
        # Check if file was uploaded
        if 'file' not in request.files:
            flash('No file selected', 'error')
            return redirect(request.url)
        
        file = request.files['file']
        
        # Check if file was actually selected
        if file.filename == '':
            flash('No file selected', 'error')
            return redirect(request.url)
        
        # Debug: Print file info
        print(f"File received: {file.filename}")
        print(f"File allowed: {allowed_file(file.filename)}")
        
        # Process uploaded file directly
        if file and allowed_file(file.filename):
            try:
                # Read and process file based on extension
                filename = secure_filename(file.filename)
                file_ext = filename.rsplit('.', 1)[1].lower()
                print(f"Processing file extension: {file_ext}")
                
                if file_ext == 'csv':
                    df = pd.read_csv(file)
                elif file_ext == 'json':
                    df = pd.read_json(file)
                elif file_ext in ['xlsx', 'xls']:
                    df = pd.read_excel(file)
                else:
                    raise ValueError(f"Unsupported file type: {file_ext}")
                
                print(f"DataFrame loaded successfully with shape: {df.shape}")
                
                # Save uploaded file
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                base_name = filename.rsplit('.', 1)[0]
                new_filename = f"{timestamp}_{base_name}.xlsx"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], new_filename)
                
                # Basic data processing with error handling
                try:
                    df['Start Date'] = pd.to_datetime(df['Start Date']).dt.strftime('%Y-%m-%d')
                except:
                    pass  # Skip if column doesn't exist or can't be converted
                
                try:
                    df['End Date'] = pd.to_datetime(df['End Date']).dt.strftime('%Y-%m-%d')
                except:
                    pass  # Skip if column doesn't exist or can't be converted
                
                # Handle Progress column if it exists
                if 'Progress' in df.columns:
                    try:
                        if df['Progress'].dtype == 'object':
                            df['Progress'] = df['Progress'].astype(str).str.replace('%', '').astype(float) / 100
                        elif df['Progress'].max() > 1:
                            df['Progress'] = df['Progress'] / 100
                    except:
                        pass  # Skip if conversion fails
                
                df.to_excel(filepath, index=False, engine='openpyxl')
                CURRENT_FILE = filepath
                
                flash(f'File "{file.filename}" uploaded successfully!', 'success')
                return redirect(url_for('dashboard'))
                
            except Exception as e:
                print(f"Error processing file: {str(e)}")
                flash(f'Error processing file: {str(e)}', 'error')
                return redirect(request.url)
        else:
            print(f"File rejected. Filename: {file.filename if file else 'No file'}")
            flash('Invalid file type. Supported formats: .xlsx or .xls or csv or json', 'error')
            return redirect(request.url)
    
    return render_template('upload.html')

@app.route('/filter', methods=['POST'])
def filter_tasks():
    global CURRENT_FILE
    df = pd.read_excel(CURRENT_FILE)
    
    # Discover available columns
    available_columns = list(df.columns)
    
    # Handle Progress column if it exists
    if 'Progress' in df.columns:
        if df['Progress'].dtype in [float, int]:
            df['Progress'] = (df['Progress'].fillna(0) * 100).astype(int)
    else:
        df['Progress'] = 0

    # Apply filters based on available columns
    for field_name, field_value in request.form.items():
        if field_value and field_name in df.columns:
            df = df[df[field_name].astype(str) == str(field_value)]

    tasks = df.to_dict(orient='records')
    for task in tasks:
        progress = task.get('Progress', 0)
        task['color'] = 'red' if progress == 0 else 'lightgreen'
        task['width'] = progress * 100 if progress <= 1 else progress
    
    current_filename = os.path.basename(CURRENT_FILE)
    return render_template('dashboard.html', tasks=tasks, current_file=current_filename, available_columns=available_columns)

@app.route('/update', methods=['POST'])         # Route to update task progress
def update_progress():
    global CURRENT_FILE
    task_name = request.form.get('task_name')
    progress = request.form.get('progress')

    if '%' in progress:
        progress = int(progress.strip('%'))
    else:
        progress = int(progress)

    progress = max(0, min(100, progress))

    df = pd.read_excel(CURRENT_FILE)

    # Find the first column that could be used as task identifier
    task_column = None
    for col in ['Task Name', 'Task', 'Name', 'Title']:
        if col in df.columns:
            task_column = col
            break
    
    # Find progress column
    progress_column = None
    for col in ['Progress', 'Complete', 'Done', 'Status']:
        if col in df.columns:
            progress_column = col
            break
    
    if task_column and progress_column:
        df.loc[df[task_column] == task_name, progress_column] = progress / 100
        df.to_excel(CURRENT_FILE, index=False)
        flash(f'Progress updated for task: {task_name}', 'success')
    else:
        flash('Cannot update progress: no suitable columns found', 'error')
    
    return redirect(url_for('dashboard'))

@app.route('/edit', methods=['POST'])
def edit_field():
    global CURRENT_FILE
    row_index = int(request.form.get('row_index'))
    column = request.form.get('column')
    new_value = request.form.get('new_value')
    
    df = pd.read_excel(CURRENT_FILE)
    df.iloc[row_index, df.columns.get_loc(column)] = new_value
    df.to_excel(CURRENT_FILE, index=False)
    
    flash(f'Updated {column} successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/add', methods=['POST'])        # Route to add a new task
def add_task():
    global CURRENT_FILE
    df = pd.read_excel(CURRENT_FILE)
    
    # Get all form data
    form_data = request.form.to_dict()
    
    # Create new task using existing columns or add to empty file
    new_task = {}
    for column in df.columns:
        # Map form fields to existing columns
        if column in form_data:
            new_task[column] = form_data[column]
        else:
            new_task[column] = ''  # Default empty value
    
    # If file is empty, use all form data
    if df.empty:
        new_task = form_data
    
    df = pd.concat([df, pd.DataFrame([new_task])], ignore_index=True)
    df.to_excel(CURRENT_FILE, index=False)
    
    flash(f'New entry added successfully!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/download')
def download_file():
    """Download current data as Excel file"""
    global CURRENT_FILE
    from flask import send_file
    import tempfile
    
    # Check if file exists
    if not os.path.exists(CURRENT_FILE):
        flash('No file to download', 'error')
        return redirect(url_for('dashboard'))
    
    # Create a temporary copy for download
    df = pd.read_excel(CURRENT_FILE)
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
    df.to_excel(temp_file.name, index=False)
    temp_file.close()
    
    return send_file(temp_file.name, as_attachment=True, download_name='dashboard_data.xlsx')

@app.route('/reset')
def reset_to_default():
    """Reset to default tasks.xlsx file"""
    global CURRENT_FILE
    CURRENT_FILE = EXCEL_FILE1
    flash('Reset to default file', 'info')
    return redirect(url_for('dashboard'))

@app.errorhandler(413)
def too_large(e):
    flash('File too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload_file'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)