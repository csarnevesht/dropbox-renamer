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
    # This will match both formats: "20240101 document.pdf" and "20240101document.pdf"
    pattern = r'^(19|20)\d{6}(?:\s+|$)'
    return bool(re.match(pattern, name))

def get_folder_creation_date(dbx, path):
    """Get the creation date of a folder by looking at its contents."""
    try:
        # List the folder contents
        result = dbx.files_list_folder(path)
        
        # If folder has contents, find the oldest file
        if result.entries:
            oldest_date = None
            for entry in result.entries:
                if isinstance(entry, dropbox.files.FileMetadata):
                    if oldest_date is None or entry.server_modified < oldest_date:
                        oldest_date = entry.server_modified
            
            # If we found files, use the oldest file's date
            if oldest_date:
                return oldest_date
        
        # If no files found or empty folder, try looking at the folder info
        folder_info = dbx.files_get_metadata(path)
        
        # Some Dropbox API versions might include a 'client_modified' field
        if hasattr(folder_info, 'client_modified'):
            return folder_info.client_modified
            
        # Try getting the shared folder info which might have creation date
        try:
            shared_info = dbx.sharing_get_folder_metadata(path)
            if hasattr(shared_info, 'time_created'):
                return shared_info.time_created
        except:
            pass
        
        # If all else fails, use the current date
        return datetime.datetime.now()
        
    except Exception as e:
        print(f"Error getting folder creation date for {path}: {e}")
        return datetime.datetime.now()

def get_renamed_path(metadata, path, is_folder=False, dbx=None):
    """Get the renamed path with date prefix."""
    try:
        # Get the original name
        original_name = os.path.basename(path)
        
        # If the name already has a date prefix, don't modify it
        if has_date_prefix(original_name):
            print(f"File/folder already has date prefix: {original_name}")
            return original_name
        
        # Get date for prefix
        if is_folder:
            # For folders, try to get creation date
            if dbx:
                date_obj = get_folder_creation_date(dbx, path)
                date_prefix = date_obj.strftime("%Y%m%d")
                print(f"Using folder creation date for {path}: {date_prefix}")
            else:
                # Fallback to current date if dbx not provided
                date_prefix = datetime.datetime.now().strftime("%Y%m%d")
        else:
            # For files, use modification date from metadata
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
    """Download a file from Dropbox and rename it with its modification date if it doesn't already have a date prefix."""
    try:
        # Get file metadata
        metadata = dbx.files_get_metadata(dropbox_path)
        
        # Get the original name
        original_name = os.path.basename(dropbox_path)
        
        # Check if file already has a date prefix
        if has_date_prefix(original_name):
            print(f"File already has date prefix, downloading with original name: {original_name}")
            local_path = os.path.join(local_dir, original_name)
        else:
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
                # Skip the "DEAD file" folder
                folder_name = os.path.basename(entry_path)
                if folder_name == "DEAD file":
                    print(f"Skipping folder: {entry_path}")
                    continue
                    
                # It's a folder, create local directory with original name and process its contents
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
                    # Skip the "DEAD file" folder
                    folder_name = os.path.basename(entry_path)
                    if folder_name == "DEAD file":
                        print(f"Skipping folder: {entry_path}")
                        continue
                        
                    # It's a folder, create local directory with original name and process its contents
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

def clean_dropbox_path(path):
    """Clean and format the Dropbox path from URL or user input."""
    print(f"\nOriginal path: {path}")
    
    # Remove URL parts if present
    if 'dropbox.com/home' in path:
        path = path.split('dropbox.com/home')[-1]
        print(f"After removing URL: {path}")
    
    # Remove any URL encoding
    path = path.replace('%20', ' ')
    print(f"After URL decoding: {path}")
    
    # Remove any trailing slashes
    path = path.rstrip('/')
    
    # Ensure path starts with a single forward slash
    if not path.startswith('/'):
        path = '/' + path
    
    # Remove any "All files" prefix if present
    if path.startswith('/All files'):
        path = path[10:]  # Remove '/All files' prefix
    
    # Try to normalize the path
    path_parts = [p for p in path.split('/') if p]
    
    # Handle case sensitivity issues by trying different case combinations
    if len(path_parts) > 0:
        # Try with original case first
        path = '/' + '/'.join(path_parts)
        print(f"Trying path with original case: {path}")
        
        # If that fails, try with lowercase
        path_lower = '/' + '/'.join(p.lower() for p in path_parts)
        print(f"Trying path with lowercase: {path_lower}")
        
        # If that fails, try with uppercase
        path_upper = '/' + '/'.join(p.upper() for p in path_parts)
        print(f"Trying path with uppercase: {path_upper}")
    
    print(f"Final cleaned path: {path}")
    return path

def list_folder_contents(dbx, path):
    """List the contents of a Dropbox folder for debugging."""
    try:
        print(f"\nAttempting to list contents of: {path}")
        
        # Try to get metadata first
        try:
            metadata = dbx.files_get_metadata(path)
            print(f"Folder metadata: {metadata}")
        except Exception as e:
            print(f"Error getting metadata: {e}")
        
        # Then try to list contents
        result = dbx.files_list_folder(path)
        print(f"\nContents of {path}:")
        for entry in result.entries:
            print(f"- {entry.path_display} ({type(entry).__name__})")
        return result.entries
    except Exception as e:
        print(f"Error listing folder {path}: {e}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")
        return []

def find_folder_path(dbx, target_folder):
    """Try to find the correct path to a folder by searching from root."""
    print("\nSearching for folder path...")
    
    # First try the exact path
    try:
        metadata = dbx.files_get_metadata(target_folder)
        if isinstance(metadata, dropbox.files.FolderMetadata):
            return target_folder
    except:
        pass
    
    # Try different case variations
    path_parts = [p for p in target_folder.split('/') if p]
    variations = [
        '/' + '/'.join(path_parts),  # Original case
        '/' + '/'.join(p.lower() for p in path_parts),  # Lowercase
        '/' + '/'.join(p.upper() for p in path_parts),  # Uppercase
    ]
    
    for variation in variations:
        try:
            metadata = dbx.files_get_metadata(variation)
            if isinstance(metadata, dropbox.files.FolderMetadata):
                print(f"Found matching folder: {variation}")
                return variation
        except:
            continue
    
    # If exact match fails, try searching from root
    try:
        result = dbx.files_list_folder('')
        for entry in result.entries:
            if isinstance(entry, dropbox.files.FolderMetadata):
                print(f"\nChecking folder: {entry.path_display}")
                try:
                    if target_folder.lower() in entry.path_display.lower():
                        return entry.path_display
                except Exception as e:
                    print(f"Error checking folder: {e}")
    except Exception as e:
        print(f"Error searching from root: {e}")
    
    return None

def list_all_namespaces_and_roots(dbx):
    """List all available namespaces (personal, team, shared) and their root contents."""
    print("\nEnumerating all Dropbox namespaces (personal, team, shared)...")
    try:
        # Print current user's root namespace
        try:
            account = dbx.users_get_current_account()
            print(f"Current account: {account.name.display_name} (ID: {account.account_id})")
        except Exception as e:
            print(f"Could not get current account info: {e}")
        
        # List all shared folders
        try:
            shared_folders = dbx.sharing_list_folders().entries
            print("\nShared folders:")
            for folder in shared_folders:
                print(f"- {folder.name} (shared_folder_id: {folder.shared_folder_id})")
                # Try to get the folder metadata and path
                try:
                    metadata = dbx.sharing_get_folder_metadata(folder.shared_folder_id)
                    print(f"  Path: {getattr(metadata, 'path_lower', None)}")
                except Exception as e:
                    print(f"  Could not get metadata for shared folder {folder.name}: {e}")
        except Exception as e:
            print(f"Could not list shared folders: {e}")
        
        # Fallback: List root and mounted folders as before
        print("\nRoot contents:")
        try:
            result = dbx.files_list_folder('')
            for entry in result.entries:
                print(f"- {entry.name} ({entry.path_display}) [{type(entry).__name__}]")
        except Exception as e:
            print(f"Could not list root contents: {e}")
        print("\nMounted folders:")
        try:
            mounted = dbx.files_list_folder('', include_mounted_folders=True)
            for entry in mounted.entries:
                if isinstance(entry, dropbox.files.FolderMetadata):
                    print(f"- [MOUNTED] {entry.name} -- API path: {entry.path_display}")
        except Exception as e:
            print(f"Could not list mounted folders: {e}")
    except Exception as e:
        print(f"Error enumerating namespaces: {e}")

def list_app_folder_contents(dbx):
    """List contents of the app folder."""
    print("\nListing app folder contents:")
    try:
        # Get app info
        app_info = dbx.check_app()
        print(f"App folder name: {app_info.name}")
        
        # List app folder contents
        result = dbx.files_list_folder('')
        print("\nApp folder contents:")
        for entry in result.entries:
            print(f"- {entry.name} ({entry.path_display}) [{type(entry).__name__}]")
            if isinstance(entry, dropbox.files.FolderMetadata):
                try:
                    subentries = dbx.files_list_folder(entry.path_display)
                    print(f"  Contents of {entry.path_display}:")
                    for subentry in subentries.entries:
                        print(f"    - {subentry.name} ({subentry.path_display}) [{type(subentry).__name__}]")
                except Exception as e:
                    print(f"  Could not list contents of {entry.path_display}: {e}")
    except Exception as e:
        print(f"Error listing app folder contents: {e}")

def main():
    """Main function to run the script."""
    parser = argparse.ArgumentParser(description='Download and rename Dropbox files with their modification dates.')
    parser.add_argument('--dropbox-folder', '-f', required=True,
                      help='Dropbox folder path to process (e.g., /Customers or full Dropbox URL)')
    parser.add_argument('--directory', '-d', default='./Customers',
                      help='Base directory to save files (default: ./Customers)')
    parser.add_argument('--env-file', '-e', default='.env',
                      help='Path to .env file (default: .env)')
    parser.add_argument('--debug', action='store_true',
                      help='List folder contents for debugging')
    
    args = parser.parse_args()
    
    try:
        # Get access token
        access_token = get_access_token(args.env_file)
        
        # Clean and format the Dropbox path
        dropbox_path = clean_dropbox_path(args.dropbox_folder)
        
        # Create base directory if it doesn't exist
        ensure_directory_exists(args.directory)
        
        # Create timestamped directory for this download
        download_dir = create_timestamped_directory(args.directory)
        print(f"\nCreated download directory: {download_dir}")
        
        # Initialize Dropbox client with a longer timeout
        dbx = dropbox.Dropbox(access_token, timeout=30)
        
        # Verify the token works and get account info
        try:
            account = dbx.users_get_current_account()
            print(f"Successfully connected to Dropbox as: {account.name.display_name}")
            print(f"Account ID: {account.account_id}")
            print(f"Email: {account.email}")
        except ApiError as e:
            print(f"Error connecting to Dropbox: {e}")
            print("Please check your access token and try again.")
            return
        
        # Debug: List app folder contents
        if args.debug:
            print("\nListing app folder contents:")
            list_app_folder_contents(dbx)
        
        # Debug: List all namespaces and their root contents
        if args.debug:
            print("\nListing all namespaces and their root contents:")
            list_all_namespaces_and_roots(dbx)
        
        # Try to find the correct folder path
        found_path = find_folder_path(dbx, dropbox_path)
        if found_path:
            print(f"\nFound matching folder path: {found_path}")
            dropbox_path = found_path
        else:
            print(f"\nCould not find exact folder path. Will try with original path: {dropbox_path}")
        
        # Debug: List root folder contents
        if args.debug:
            print("\nListing root directory contents:")
            entries = list_folder_contents(dbx, "")
            
            if not entries:
                print("\nNo entries found in root directory. Checking permissions...")
                try:
                    # Try to get account space usage
                    usage = dbx.users_get_space_usage()
                    print(f"Account space usage: {usage.used} / {usage.allocation}")
                    
                    # Try to list each part of the path
                    path_parts = [p for p in dropbox_path.split('/') if p]
                    current_path = ""
                    for part in path_parts:
                        current_path += "/" + part
                        print(f"\nTrying to list: {current_path}")
                        list_folder_contents(dbx, current_path)
                except Exception as e:
                    print(f"Error getting space usage: {e}")
        
        # Process the Dropbox folder
        print(f"\nProcessing Dropbox folder: {dropbox_path}")
        process_dropbox_folder(dbx, dropbox_path, download_dir)
        print("\nDownload complete!")
        
    except Exception as e:
        print(f"Error: {e}")
        if hasattr(e, 'error'):
            print(f"Error details: {e.error}")

if __name__ == "__main__":
    main() 