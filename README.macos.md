# Dropbox File Renamer (macOS)

A simple tool that downloads files from Dropbox and renames them with their modification dates as prefixes.

## Prerequisites

- macOS 10.14 or later
- Internet connection
- Dropbox account
- Dropbox access token with "Full Dropbox" permissions

## Quick Start

1. Download the latest release zip file
2. Extract the zip file to a location of your choice
3. Open Terminal
4. Navigate to the extracted folder:
   ```bash
   cd path/to/dropbox-renamer-macos
   ```
5. Make the executable runnable (if needed):
   ```bash
   chmod +x dropbox-renamer
   ```
6. Run the program:
   ```bash
   ./dropbox-renamer --dropbox-folder /YourFolder
   ```
7. When prompted, enter your Dropbox access token

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

## Command Line Arguments

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