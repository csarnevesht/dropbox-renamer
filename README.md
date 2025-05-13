# Dropbox File Renamer

A simple tool that downloads files from Dropbox and renames them with their modification dates as prefixes.

## Prerequisites

- Python 3.6 or higher
- Internet connection
- Dropbox account
- Dropbox access token with "Full Dropbox" permissions

## Creating the Distribution Package

1. Navigate to the scripts directory:
   ```bash
   cd scripts
   ```

2. Install build dependencies:
   ```bash
   pip3 install build
   ```

3. Create the distribution package:
   ```bash
   python3 -m build
   ```

4. The distribution files will be created in the `dist` directory:
   - `dropbox_file_renamer-1.0.0.tar.gz` (source distribution)
   - `dropbox_file_renamer-1.0.0-py3-none-any.whl` (wheel distribution)

### Creating Windows Executable

> **Note**: The Windows executable must be created on a Windows system. You can use GitHub Codespaces or Replit's free Windows environment to create it.

#### Using GitHub Codespaces:

1. Create a GitHub account if you don't have one
2. Create a new repository:
   - Click "New repository"
   - Name it "dropbox-renamer"
   - Make it public (required for free Codespaces)
   - Click "Create repository"

3. Upload your files:
   - Upload the entire `scripts` directory to your repository
   - Make sure to maintain the directory structure

4. Open in Codespaces:
   - Go to your repository
   - Click the "Code" button
   - Select the "Codespaces" tab
   - Click "Create codespace on main"

5. In the Codespace terminal:
   ```bash
   # Install PyInstaller
   pip install pyinstaller

   # Create the executable
   pyinstaller --onefile --name dropbox-renamer dropbox_renamer/rename_files_with_date.py
   ```

6. Download the executable:
   - The executable will be created in the `dist` directory
   - Right-click on `dist/dropbox-renamer.exe` in the file explorer
   - Select "Download"

7. Create a zip file containing:
   - `dropbox-renamer.exe`
   - `README.windows.md`

#### Using Replit:

1. Go to [Replit](https://replit.com) and create a free account
2. Create a new Repl:
   - Click "Create Repl"
   - Choose "Python" as the language
   - Name it "dropbox-renamer"
   - Click "Create Repl"

3. Upload your files:
   - Upload the entire `scripts` directory to your Repl
   - Make sure to maintain the directory structure

4. Install PyInstaller:
   ```bash
   pip install pyinstaller
   ```

5. Create the executable:
   ```bash
   pyinstaller --onefile --name dropbox-renamer dropbox_renamer/rename_files_with_date.py
   ```

6. Download the executable:
   - The executable will be created in the `dist` directory
   - Click on the `dist` folder in the file explorer
   - Download `dropbox-renamer.exe`

7. Create a zip file containing:
   - `dropbox-renamer.exe`
   - `README.windows.md`

Alternative Free Windows Cloud Options:
- [Google Cloud Shell](https://shell.cloud.google.com) (free tier available)
- [Azure Cloud Shell](https://shell.azure.com) (free tier available)

### Distribution Package Contents

The distribution packages contain:

1. **Source Distribution** (`*.tar.gz`):
   - Python source code
   - Package configuration files
   - Documentation
   - License information
   - Required for installing on all platforms

2. **Wheel Distribution** (`*.whl`):
   - Pre-built package for Python
   - Faster installation than source distribution
   - Platform-independent Python code
   - Required dependencies listed

3. **Windows Executable** (created separately):
   - Standalone `.exe` file
   - No Python installation required
   - Includes all dependencies
   - Windows-specific binary
   - Created using PyInstaller
   - Packaged in a zip file for distribution
   - Must be created on a Windows system

For Windows users, the executable package is the recommended option as it doesn't require Python installation. For other platforms, use the Python package installation method.

## Installation

1. Download the latest release zip file
2. Extract the zip file to a location of your choice
3. Open Terminal
4. Navigate to the extracted folder:
   ```bash
   cd path/to/extracted/folder
   ```
5. Install the package:
   ```bash
   pip3 install .
   ```

## Getting a Dropbox Access Token

1. Go to [Dropbox App Console](https://www.dropbox.com/developers/apps)
2. Click "Create app"
3. Choose "Scoped access"
4. Choose "Full Dropbox" access type
5. Name your app (e.g., "File Renamer")
6. Click "Create app"
7. Under "OAuth 2", click "Generate" to create an access token
8. Copy the generated token

### Important Notes About Access Tokens

- Keep your access token secure and never share it
- The token provides full access to your Dropbox account
- If you suspect your token has been compromised, revoke it immediately in the Dropbox App Console
- You can create multiple tokens for different purposes
- Tokens don't expire unless you revoke them

## Usage

Run the script with the following command:
```bash
dropbox-renamer --dropbox-folder /YourFolder
```

When prompted, enter your Dropbox access token.

### Command Line Arguments

- `--dropbox-folder` or `-f`: Dropbox folder path to process (required)
- `--directory` or `-d`: Base directory to save files (default: ./Customers)

## Troubleshooting

### Common Issues

1. **Access Token Not Found**
   - Make sure you've entered the token correctly when prompted
   - Verify the token is valid
   - Check if the token has the required permissions

2. **Permission Denied**
   - Ensure you have write permissions in the target directory
   - Check if the Dropbox folder path is correct

3. **Connection Issues**
   - Verify your internet connection
   - Check if the access token is still valid

## Support

For issues or questions, please:
1. Check the error messages for specific problems
2. Verify your access token and permissions
3. Contact support if you need further assistance 