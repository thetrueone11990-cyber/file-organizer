"""
core/file_manager.py
Core file operations module
"""

import os
import shutil
import subprocess
import platform
from pathlib import Path
from typing import Optional

class FileManager:
    """Handles all file and folder operations"""
    
    def __init__(self):
        self.system = platform.system()
    
    def create_folder(self, path: Path) -> bool:
        """Create a new folder"""
        try:
            path.mkdir(parents=True, exist_ok=False)
            return True
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def rename(self, old_path: Path, new_path: Path) -> bool:
        """Rename a file or folder"""
        try:
            old_path.rename(new_path)
            return True
        except Exception as e:
            print(f"Error renaming: {e}")
            return False
    
    def delete(self, path: Path) -> bool:
        """Delete a file or folder"""
        try:
            if path.is_file():
                path.unlink()
            elif path.is_dir():
                shutil.rmtree(path)
            return True
        except Exception as e:
            print(f"Error deleting: {e}")
            return False
    
    def move(self, source: Path, destination: Path) -> bool:
        """Move a file or folder"""
        try:
            shutil.move(str(source), str(destination))
            return True
        except Exception as e:
            print(f"Error moving: {e}")
            return False
    
    def copy(self, source: Path, destination: Path) -> bool:
        """Copy a file or folder"""
        try:
            if source.is_file():
                shutil.copy2(source, destination)
            else:
                shutil.copytree(source, destination)
            return True
        except Exception as e:
            print(f"Error copying: {e}")
            return False
    
    def open_file(self, path: Path) -> bool:
        """Open a file with default application"""
        try:
            if self.system == 'Windows':
                os.startfile(path)
            elif self.system == 'Darwin':  # macOS
                subprocess.run(['open', path])
            else:  # Linux
                subprocess.run(['xdg-open', path])
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
    
    def get_file_info(self, path: Path) -> dict:
        """Get detailed file information"""
        try:
            stat = path.stat()
            return {
                'name': path.name,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_dir': path.is_dir(),
                'extension': path.suffix if path.is_file() else None
            }
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {}