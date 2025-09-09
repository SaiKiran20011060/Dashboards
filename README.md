# Dashboard Project

A Flask-based web application for managing project tasks and data with session-based user isolation.

## Features

- **Session-Based Data Isolation**: Each user gets their own private workspace
- **File Upload Support**: Upload CSV, JSON, Excel files (.xlsx, .xls)
- **Data Visualization**: Interactive dashboard with progress tracking
- **Task Management**: Add, edit, update, and filter tasks
- **File Conversion**: Convert CSV files to Excel format
- **Data Export**: Download your data as Excel files
- **Auto Reset**: Data resets when browser is closed or new session starts

## Installation

1. Clone the repository:
```bash
git clone https://github.com/SaiKiran20011060/Dashboards.git
cd Dashboards
```

2. Install required dependencies:
```bash
pip install flask pandas openpyxl werkzeug
```

3. Create uploads directory:
```bash
mkdir uploads
```

## Usage

1. Start the application:
```bash
python pythonflask.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

## Supported File Formats

- **Excel**: .xlsx, .xls
- **CSV**: .csv
- **JSON**: .json

## Routes

- `/` - Main dashboard view
- `/upload` - File upload page
- `/convert` - CSV to Excel converter
- `/filter` - Filter tasks
- `/update` - Update task progress
- `/edit` - Edit task fields
- `/add` - Add new tasks
- `/download` - Download current data
- `/reset` - Reset session data

## Key Features

### Session Management
- Each browser session gets a unique workspace
- Data is automatically isolated between users
- Session expires when browser is closed

### Data Processing
- Automatic date formatting
- Progress percentage handling
- Dynamic column detection
- Error handling for malformed data

### Security
- File type validation
- Secure filename handling
- 16MB file size limit
- Session-based access control

## Technical Details

- **Framework**: Flask
- **Data Processing**: Pandas
- **File Handling**: OpenPyXL, Werkzeug
- **Session Management**: UUID-based unique sessions
- **Storage**: Temporary files per session

## Configuration

- **Upload Folder**: `uploads/`
- **Max File Size**: 16MB
- **Allowed Extensions**: xlsx, xls, csv, json
- **Host**: 0.0.0.0
- **Port**: 5000

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is open source and available under the MIT License.