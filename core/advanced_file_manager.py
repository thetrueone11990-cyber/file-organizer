"""
core/advanced_file_manager.py
Enhanced file manager with ALL advanced features
"""

import os
import shutil
import subprocess
import platform
import hashlib
import json
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime
from send2trash import send2trash

class AdvancedFileManager:
    """Enhanced file manager with advanced features"""
    
    def __init__(self):
        self.system = platform.system()
        self.config_dir = Path.home() / '.file_organizer'
        self.config_dir.mkdir(exist_ok=True)
        
        self.favorites_file = self.config_dir / 'favorites.json'
        self.history_file = self.config_dir / 'history.json'
        self.tags_file = self.config_dir / 'tags.json'
        self.recent_file = self.config_dir / 'recent.json'
        
        # Operation history for undo
        self.operation_history = []
        self.max_history = 50
    
    # ==================== BASIC OPERATIONS ====================
    
    def create_folder(self, path: Path) -> bool:
        """Create a new folder"""
        try:
            path.mkdir(parents=True, exist_ok=False)
            self._add_to_history('create_folder', str(path))
            return True
        except Exception as e:
            print(f"Error creating folder: {e}")
            return False
    
    def rename(self, old_path: Path, new_path: Path) -> bool:
        """Rename a file or folder"""
        try:
            old_path.rename(new_path)
            self._add_to_history('rename', {'old': str(old_path), 'new': str(new_path)})
            return True
        except Exception as e:
            print(f"Error renaming: {e}")
            return False
    
    def delete(self, path: Path, use_trash: bool = True) -> bool:
        """Delete a file or folder (safely to trash by default)"""
        try:
            if use_trash:
                send2trash(str(path))
            else:
                if path.is_file():
                    path.unlink()
                elif path.is_dir():
                    shutil.rmtree(path)
            self._add_to_history('delete', str(path))
            return True
        except Exception as e:
            print(f"Error deleting: {e}")
            return False
    
    def move(self, source: Path, destination: Path) -> bool:
        """Move a file or folder"""
        try:
            shutil.move(str(source), str(destination))
            self._add_to_history('move', {'from': str(source), 'to': str(destination)})
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
            self._add_to_history('copy', {'from': str(source), 'to': str(destination)})
            return True
        except Exception as e:
            print(f"Error copying: {e}")
            return False
    
    def open_file(self, path: Path) -> bool:
        """Open a file with default application"""
        try:
            if self.system == 'Windows':
                os.startfile(path)
            elif self.system == 'Darwin':
                subprocess.run(['open', path])
            else:
                subprocess.run(['xdg-open', path])
            return True
        except Exception as e:
            print(f"Error opening file: {e}")
            return False
    
    # ==================== ADVANCED FILE INFO ====================
    
    def get_file_info(self, path: Path) -> dict:
        """Get detailed file information"""
        try:
            stat = path.stat()
            info = {
                'name': path.name,
                'path': str(path),
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'accessed': stat.st_atime,
                'is_dir': path.is_dir(),
                'extension': path.suffix if path.is_file() else None,
                'permissions': oct(stat.st_mode)[-3:],
            }
            
            # Add hash for files
            if path.is_file() and stat.st_size < 100 * 1024 * 1024:  # < 100MB
                info['hash'] = self.calculate_hash(path)
            
            return info
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {}
    
    def calculate_hash(self, path: Path, algorithm: str = 'md5') -> str:
        """Calculate file hash"""
        try:
            hash_obj = hashlib.new(algorithm)
            with open(path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b''):
                    hash_obj.update(chunk)
            return hash_obj.hexdigest()
        except Exception as e:
            print(f"Error calculating hash: {e}")
            return ''
    
    def get_folder_size(self, path: Path) -> int:
        """Calculate total size of folder"""
        total = 0
        try:
            for item in path.rglob('*'):
                if item.is_file():
                    total += item.stat().st_size
        except Exception as e:
            print(f"Error calculating folder size: {e}")
        return total
    
    # ==================== FAVORITES ====================
    
    def add_favorite(self, path: str, name: str = None):
        """Add path to favorites"""
        favorites = self.get_favorites()
        if name is None:
            name = Path(path).name
        
        favorite = {
            'path': path,
            'name': name,
            'added': datetime.now().isoformat()
        }
        
        # Don't add duplicates
        if not any(f['path'] == path for f in favorites):
            favorites.append(favorite)
            self._save_json(self.favorites_file, favorites)
    
    def remove_favorite(self, path: str):
        """Remove from favorites"""
        favorites = self.get_favorites()
        favorites = [f for f in favorites if f['path'] != path]
        self._save_json(self.favorites_file, favorites)
    
    def get_favorites(self) -> List[Dict]:
        """Get all favorites"""
        return self._load_json(self.favorites_file, [])
    
    def is_favorite(self, path: str) -> bool:
        """Check if path is in favorites"""
        favorites = self.get_favorites()
        return any(f['path'] == path for f in favorites)
    
    # ==================== RECENT LOCATIONS ====================
    
    def add_recent(self, path: str):
        """Add to recent locations"""
        recent = self.get_recent()
        
        # Remove if already exists
        recent = [r for r in recent if r['path'] != path]
        
        # Add to beginning
        recent.insert(0, {
            'path': path,
            'accessed': datetime.now().isoformat()
        })
        
        # Keep only last 20
        recent = recent[:20]
        
        self._save_json(self.recent_file, recent)
    
    def get_recent(self) -> List[Dict]:
        """Get recent locations"""
        return self._load_json(self.recent_file, [])
    
    def clear_recent(self):
        """Clear recent locations"""
        self._save_json(self.recent_file, [])
    
    # ==================== FILE TAGGING ====================
    
    def add_tag(self, path: str, tag: str):
        """Add tag to file"""
        tags = self.get_all_tags()
        
        if path not in tags:
            tags[path] = []
        
        if tag not in tags[path]:
            tags[path].append(tag)
            self._save_json(self.tags_file, tags)
    
    def remove_tag(self, path: str, tag: str):
        """Remove tag from file"""
        tags = self.get_all_tags()
        
        if path in tags and tag in tags[path]:
            tags[path].remove(tag)
            if not tags[path]:
                del tags[path]
            self._save_json(self.tags_file, tags)
    
    def get_tags(self, path: str) -> List[str]:
        """Get tags for a file"""
        tags = self.get_all_tags()
        return tags.get(path, [])
    
    def get_all_tags(self) -> Dict:
        """Get all tags"""
        return self._load_json(self.tags_file, {})
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Find all files with a specific tag"""
        tags = self.get_all_tags()
        return [path for path, file_tags in tags.items() if tag in file_tags]
    
    # ==================== DUPLICATE FINDER ====================
    
    def find_duplicates(self, directory: Path) -> Dict[str, List[Path]]:
        """Find duplicate files by hash"""
        hashes = {}
        duplicates = {}
        
        try:
            for file in directory.rglob('*'):
                if file.is_file():
                    # Skip large files
                    if file.stat().st_size > 100 * 1024 * 1024:
                        continue
                    
                    file_hash = self.calculate_hash(file)
                    
                    if file_hash in hashes:
                        if file_hash not in duplicates:
                            duplicates[file_hash] = [hashes[file_hash]]
                        duplicates[file_hash].append(file)
                    else:
                        hashes[file_hash] = file
        except Exception as e:
            print(f"Error finding duplicates: {e}")
        
        return duplicates
    
    # ==================== BATCH OPERATIONS ====================
    
    def batch_rename(self, files: List[Path], pattern: str, start_num: int = 1) -> int:
        """Batch rename files with pattern
        Pattern: use {n} for number, {name} for original name, {ext} for extension
        Example: "Photo_{n}" -> Photo_1.jpg, Photo_2.jpg, ...
        """
        success_count = 0
        
        for i, file in enumerate(files, start=start_num):
            try:
                # Build new name
                new_name = pattern.replace('{n}', str(i))
                new_name = new_name.replace('{name}', file.stem)
                new_name = new_name.replace('{ext}', file.suffix)
                
                if not new_name.endswith(file.suffix):
                    new_name += file.suffix
                
                new_path = file.parent / new_name
                
                if self.rename(file, new_path):
                    success_count += 1
                    
            except Exception as e:
                print(f"Error renaming {file}: {e}")
        
        return success_count
    
    def batch_move(self, files: List[Path], destination: Path) -> int:
        """Move multiple files"""
        success_count = 0
        for file in files:
            if self.move(file, destination / file.name):
                success_count += 1
        return success_count
    
    def batch_copy(self, files: List[Path], destination: Path) -> int:
        """Copy multiple files"""
        success_count = 0
        for file in files:
            if self.copy(file, destination / file.name):
                success_count += 1
        return success_count
    
    def batch_delete(self, files: List[Path], use_trash: bool = True) -> int:
        """Delete multiple files"""
        success_count = 0
        for file in files:
            if self.delete(file, use_trash):
                success_count += 1
        return success_count
    
    # ==================== SEARCH ====================
    
    def search_files(self, directory: Path, query: str, case_sensitive: bool = False,
                    search_content: bool = False, extensions: List[str] = None) -> List[Path]:
        """Advanced file search"""
        results = []
        
        if not case_sensitive:
            query = query.lower()
        
        try:
            for item in directory.rglob('*'):
                # Search in filename
                name = item.name if case_sensitive else item.name.lower()
                
                # Filter by extension
                if extensions and item.suffix.lower() not in extensions:
                    continue
                
                # Check filename match
                if query in name:
                    results.append(item)
                    continue
                
                # Search in content (text files only)
                if search_content and item.is_file():
                    try:
                        if item.suffix.lower() in ['.txt', '.py', '.js', '.html', '.css', '.md']:
                            with open(item, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                if not case_sensitive:
                                    content = content.lower()
                                if query in content:
                                    results.append(item)
                    except:
                        pass
                        
        except Exception as e:
            print(f"Error searching: {e}")
        
        return results
    
    # ==================== DISK USAGE ====================
    
    def analyze_disk_usage(self, directory: Path, max_depth: int = 3) -> Dict:
        """Analyze disk usage by folder"""
        usage = {
            'path': str(directory),
            'size': 0,
            'file_count': 0,
            'folder_count': 0,
            'children': []
        }
        
        try:
            if max_depth <= 0:
                return usage
            
            for item in directory.iterdir():
                if item.is_file():
                    usage['size'] += item.stat().st_size
                    usage['file_count'] += 1
                elif item.is_dir():
                    usage['folder_count'] += 1
                    child_usage = self.analyze_disk_usage(item, max_depth - 1)
                    usage['size'] += child_usage['size']
                    usage['file_count'] += child_usage['file_count']
                    usage['folder_count'] += child_usage['folder_count']
                    usage['children'].append(child_usage)
                    
        except Exception as e:
            print(f"Error analyzing disk usage: {e}")
        
        return usage
    
    def find_large_files(self, directory: Path, min_size_mb: int = 100) -> List[Dict]:
        """Find large files"""
        min_size = min_size_mb * 1024 * 1024
        large_files = []
        
        try:
            for file in directory.rglob('*'):
                if file.is_file():
                    size = file.stat().st_size
                    if size >= min_size:
                        large_files.append({
                            'path': str(file),
                            'size': size,
                            'name': file.name
                        })
        except Exception as e:
            print(f"Error finding large files: {e}")
        
        # Sort by size descending
        large_files.sort(key=lambda x: x['size'], reverse=True)
        return large_files
    
    # ==================== HISTORY & UNDO ====================
    
    def _add_to_history(self, operation: str, data):
        """Add operation to history"""
        self.operation_history.append({
            'operation': operation,
            'data': data,
            'timestamp': datetime.now().isoformat()
        })
        
        # Keep only last N operations
        if len(self.operation_history) > self.max_history:
            self.operation_history.pop(0)
    
    def get_operation_history(self) -> List[Dict]:
        """Get operation history"""
        return self.operation_history
    
    # ==================== HELPER METHODS ====================
    
    def _load_json(self, file_path: Path, default=None):
        """Load JSON file"""
        try:
            if file_path.exists():
                with open(file_path, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
        return default if default is not None else {}
    
    def _save_json(self, file_path: Path, data):
        """Save JSON file"""
        try:
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving {file_path}: {e}")