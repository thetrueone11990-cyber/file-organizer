"""
core/project_manager.py
Manages multiple file organization projects
"""

import json
from pathlib import Path
from typing import List, Optional, Dict
from datetime import datetime

class ProjectManager:
    """Manages organization projects"""
    
    def __init__(self):
        self.config_dir = Path.home() / '.file_organizer'
        self.projects_file = self.config_dir / 'projects.json'
        self.ensure_config_dir()
        self.projects = self.load_projects()
    
    def ensure_config_dir(self):
        """Ensure configuration directory exists"""
        self.config_dir.mkdir(parents=True, exist_ok=True)
        if not self.projects_file.exists():
            self.projects_file.write_text('[]')
    
    def load_projects(self) -> List[Dict]:
        """Load all projects from config file"""
        try:
            with open(self.projects_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading projects: {e}")
            return []
    
    def save_projects(self):
        """Save projects to config file"""
        try:
            with open(self.projects_file, 'w') as f:
                json.dump(self.projects, f, indent=2)
        except Exception as e:
            print(f"Error saving projects: {e}")
    
    def create_project(self, name: str, path: str) -> Dict:
        """Create a new project"""
        project = {
            'name': name,
            'path': path,
            'created': datetime.now().isoformat(),
            'last_modified': datetime.now().isoformat()
        }
        
        self.projects.append(project)
        self.save_projects()
        return project
    
    def get_project(self, name: str) -> Optional[Dict]:
        """Get a project by name"""
        for project in self.projects:
            if project['name'] == name:
                return project
        return None
    
    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        return self.projects
    
    def delete_project(self, name: str) -> bool:
        """Delete a project"""
        self.projects = [p for p in self.projects if p['name'] != name]
        self.save_projects()
        return True
    
    def update_project(self, name: str, updates: Dict) -> bool:
        """Update project information"""
        for project in self.projects:
            if project['name'] == name:
                project.update(updates)
                project['last_modified'] = datetime.now().isoformat()
                self.save_projects()
                return True
        return False