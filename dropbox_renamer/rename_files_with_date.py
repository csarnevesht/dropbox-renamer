#!/usr/bin/env python3

"""
Dropbox File Renamer

This script downloads files from Dropbox and renames both files and folders
with their modification dates as prefixes.
"""

import os
import datetime
import argparse
from pathlib import Path
import dropbox
from dropbox.exceptions import ApiError
import tempfile
import shutil
from dotenv import load_dotenv
import sys
import re

def create_timestamped_directory(base_dir):
    """Create a new directory with current timestamp."""
    timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    dir_name = f"dropbox_download_{timestamp}"
    full_path = os.path.join(base_dir, dir_name)
    os.makedirs(full_path, exist_ok=True)
    return full_path

def ensure_directory_exists(directory):
    """Ensure the directory exists, create it if it doesn't."""
    try:
        os.makedirs(directory, exist_ok=True)
        print(f"Ensuring directory exists: {directory}")
        return True
    except Exception as e:
        print(f"Error creating directory {directory}: {str(e)}")
        return False

def has_date_prefix(name):
    """Check if the filename already has a date prefix (YYYYMMDD)."""
    # Regular expression to match YYYYMMDD at the beginning of the filename
    pattern = r'^(19|20)\d{6}\s+'
    return bool(re.match(pattern, name))

def get_renamed_path(metadata, path, is_folder=False):
    """Get the renamed path with date prefix."""
    try:
        # Get the original name
        original_name = os.path.basename(path)
        
        # If the name already has a date prefix, don't modify it
        if has_date_prefix(original_name):
            print(f"File already has date prefix: {original_name}")
            return original_name
        
        # Get modification date from metadata
        if is_folder:
            # For folders, use current date since they don't have server_modified
            date_prefix = datetime.datetime.now().strftime("%Y%m%d")
        else:
            date_prefix = metadata.server_modified.strftime("%Y%m%d")
        
        # Create new name with date prefix
        new_name = f"{date_prefix} {original_name}"
        
        # If it's a folder, ensure it ends with a slash
        if is_folder and not new_name.endswith('/'):
            new_name += '/'
            
        return new_name
    except Exception as e:
        print(f"Error generating renamed path for {path}: {e}")
        return os.path.basename(path)

def download_and_rename_file(dbx, dropbox_path, local_dir):
    """Download a file from Dropbox and rename it with its modification date."""
    try:
        # Get file metadata
        metadata = dbx.files_get_metadata(dropbox_path)
        
        # Generate new filename with date prefix
        new_name = get_renamed_path(metadata, dropbox_path)
        local_path = os.path.join(local_dir, new_name)
        
        # Download the file
        print(f"Downloading: {dropbox_path} -> {local_path}")
        dbx.files_download_to_file(local_path, dropbox_path)
        
    except Exception as e:
        print(f"Error processing file {dropbox_path}: {e}")

def process_dropbox_folder(dbx, dropbox_path, local_dir):
    """Process a Dropbox folder recursively."""
    try:
        # List all entries in the folder
        result = dbx.files_list_folder(dropbox_path)
        
        # Process all entries
        for entry in result.entries:
            entry_path = entry.path_display
            
            if isinstance(entry, dropbox.files.FileMetadata):
                # It's a file, download and rename it
                download_and_rename_file(dbx, entry_path, local_dir)
            elif isinstance(entry, dropbox.files.FolderMetadata):
                # It's a folder, create local directory and process its contents
                folder_name = get_renamed_path(entry, entry_path, is_folder=True)
                new_local_dir = os.path.join(local_dir, folder_name)
                ensure_directory_exists(new_local_dir)
                process_dropbox_folder(dbx, entry_path, new_local_dir)
        
        # Handle pagination if there are more entries
        while result.has_more:
            result = dbx.files_list_folder_continue(result.cursor)
            for entry in result.entries:
                entry_path = entry.path_display
                
                if isinstance(entry, dropbox.files.FileMetadata):
                    download_and_rename_file(dbx, entry_path, local_dir)
                elif isinstance(entry, dropbox.files.FolderMetadata):
                    folder_name = get_renamed_path(entry, entry_path, is_folder=True)
                    new_local_dir = os.path.join(local_dir, folder_name)
                    ensure_directory_exists(new_local_dir)
                    process_dropbox_folder(dbx, entry_path, new_local_dir)
                    
    except Exception as e:
        print(f"Error processing folder {dropbox_path}: {e}")

def update_env_file(env_file, token):
    """Update the .env file with the new token."""
    try:
        with open(env_file, 'w') as f:
            f.write(f"DROPBOX_ACCESS_TOKEN={token}\n")
        print(f"Access token saved to {env_file}")
    except Exception as e:
        print(f"Error saving access token: {e}")
        raise

def get_access_token(env_file):
    """Get the access token from environment or prompt user."""
    # Load environment variables
    load_dotenv(env_file)
    
    # Try to get token from environment
    access_token = os.getenv('DROPBOX_ACCESS_TOKEN')
    
    # If no token found, prompt user
    if not access_token:
        print("\nDropbox Access Token not found.")
        print("Please follow these steps:")
        print("1. Create a file named 'token.txt' in the current directory")
        print("2. Paste your Dropbox access token into this file")
        print("3. Save the file")
        print("4. Press Enter to continue...")
        
        # Wait for user to create the file
        input()
        
        try:
            # Read token from file
            if os.path.exists('token.txt'):
                with open('token.txt', 'r') as f:
                    access_token = f.read().strip()
                
                # Delete the token file for security
                os.remove('token.txt')
                
                if not access_token:
                    print("Error: Token file is empty")
                    return get_access_token(env_file)
                
                print(f"Token length: {len(access_token)}")
                
                # Update .env file with the new token
                update_env_file(env_file, access_token)
            else:
                print("Error: token.txt file not found")
                return get_access_token(env_file)
                
        except Exception as e:
            print(f"Error reading token: {e}")
            return get_access_token(env_file)
    
    return access_token

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Download and rename Dropbox files with their modification dates.')
    parser.add_argument('--dropbox-folder', '-f', required=True,
                      help='Dropbox folder path to process (e.g., /Customers)')
    parser.add_argument('--directory', '-d', default='./Customers',
                      help='Base directory to save files (default: ./Customers)')
    parser.add_argument('--env-file', '-e', default='.env',
                      help='Path to .env file (default: .env)')
    
    args = parser.parse_args()
    
    try:
        # Get access token
        access_token = get_access_token(args.env_file)
        
        # Create base directory if it doesn't exist
        ensure_directory_exists(args.directory)
        
        # Create timestamped directory for this download
        download_dir = create_timestamped_directory(args.directory)
        print(f"\nCreated download directory: {download_dir}")
        
        # Initialize Dropbox client
        dbx = dropbox.Dropbox(access_token)
        
        # Verify the token works
        try:
            dbx.users_get_current_account()
            print("Successfully connected to Dropbox")
        except ApiError as e:
            print(f"Error connecting to Dropbox: {e}")
            print("Please check your access token and try again.")
            return
        
        # Process the Dropbox folder
        print(f"\nProcessing Dropbox folder: {args.dropbox_folder}")
        process_dropbox_folder(dbx, args.dropbox_folder, download_dir)
        print("\nDownload complete!")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 