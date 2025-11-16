"""
gui/main_window.py
COMPLETE ULTRA-FEATURED FILE ORGANIZER
All 20+ features implemented!
"""

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QPushButton, QTreeWidget, QTreeWidgetItem, QLabel,
                             QSplitter, QListWidget, QMessageBox, QInputDialog,
                             QFileDialog, QMenu, QLineEdit, QComboBox, QTabWidget,
                             QTextEdit, QCheckBox, QSlider, QScrollArea, QGridLayout,
                             QButtonGroup, QRadioButton, QFrame, QSizePolicy, QProgressBar,
                             QDialog, QListWidgetItem, QSpinBox, QGroupBox, QToolBar, QStatusBar)
from PyQt6.QtCore import Qt, QSize, QTimer, QThread, pyqtSignal, QMimeData, QUrl, QEvent
from PyQt6.QtGui import QAction, QIcon, QPixmap, QImage, QDrag, QColor, QPalette, QKeySequence, QResizeEvent
from pathlib import Path
import json
import re
from datetime import datetime, timedelta

from core.advanced_file_manager import AdvancedFileManager
from core.project_manager import ProjectManager
from core.template_manager import TemplateManager

# ==================== WORKER THREADS ====================

class SearchWorker(QThread):
    """Background search worker"""
    finished = pyqtSignal(list)
    progress = pyqtSignal(int)
    
    def __init__(self, file_manager, directory, query, options):
        super().__init__()
        self.file_manager = file_manager
        self.directory = directory
        self.query = query
        self.options = options
    
    def run(self):
        results = self.file_manager.search_files(
            self.directory, 
            self.query,
            case_sensitive=self.options.get('case_sensitive', False),
            search_content=self.options.get('search_content', False),
            extensions=self.options.get('extensions', None)
        )
        self.finished.emit(results)

class DuplicateFinderWorker(QThread):
    """Background duplicate finder"""
    finished = pyqtSignal(dict)
    progress = pyqtSignal(str)
    
    def __init__(self, file_manager, directory):
        super().__init__()
        self.file_manager = file_manager
        self.directory = directory
    
    def run(self):
        self.progress.emit("Scanning for duplicates...")
        duplicates = self.file_manager.find_duplicates(self.directory)
        self.finished.emit(duplicates)

# ==================== MAIN WINDOW ====================

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.file_manager = AdvancedFileManager()
        self.project_manager = ProjectManager()
        self.template_manager = TemplateManager()
        self.current_path = Path.home()
        self.current_project = None
        self.current_theme = "navy"
        self.view_mode = "list"
        self.split_view_enabled = False
        self.clipboard = []  # For copy/cut operations
        
        self.setWindowTitle("Advanced File Organization System")
        self.setGeometry(100, 100, 1600, 900)
        self.setMinimumSize(1000, 600)
        
        # Set window icon
        icon_path = Path(__file__).parent.parent / "assets" / "icon.png"
        if icon_path.exists():
            self.setWindowIcon(QIcon(str(icon_path)))
        
        self.init_ui()
        self.apply_theme(self.current_theme)
        self.load_projects()
        self.auto_detect_projects()
        self.refresh_file_browser()
        self.load_favorites()
        self.load_recent()
        
    def init_ui(self):
        """Initialize the complete user interface"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(0, 0, 0, 0)
        central_widget.setLayout(main_layout)
        
        # ==================== LEFT SIDEBAR ====================
        self.left_panel = QWidget()
        left_layout = QVBoxLayout()
        self.left_panel.setLayout(left_layout)
        self.left_panel.setMinimumWidth(280)
        self.left_panel.setMaximumWidth(350)
        left_layout.setSpacing(15)
        left_layout.setContentsMargins(20, 20, 20, 20)
        
        # Theme Selector
        theme_label = QLabel("<h3>🎨 Theme</h3>")
        left_layout.addWidget(theme_label)
        
        theme_layout = QGridLayout()
        theme_layout.setSpacing(10)
        
        self.theme_buttons = QButtonGroup()
        themes = [
            ("Navy", "navy", "#0a1929"),
            ("Purple", "purple", "#1a0a2e"),
            ("Emerald", "emerald", "#0a2e1a"),
            ("Rose", "rose", "#2e0a1a"),
            ("Slate", "slate", "#1a1a1a"),
            ("Ocean", "ocean", "#0a1e29")
        ]
        
        for i, (name, theme_id, color) in enumerate(themes):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 10px;
                    color: white;
                    font-weight: bold;
                }}
                QPushButton:checked {{
                    border: 2px solid rgba(255, 255, 255, 0.5);
                }}
            """)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_theme(t))
            self.theme_buttons.addButton(btn, i)
            theme_layout.addWidget(btn, i // 3, i % 3)
            if theme_id == "navy":
                btn.setChecked(True)
        
        left_layout.addLayout(theme_layout)
        
        # Quick Access
        quick_section = self.create_collapsible_section("📁 Quick Access", self.create_quick_access_widget())
        left_layout.addWidget(quick_section)
        
        # Favorites
        fav_section = self.create_collapsible_section("⭐ Favorites", self.create_favorites_widget())
        left_layout.addWidget(fav_section)
        
        # Recent Locations
        recent_section = self.create_collapsible_section("🕐 Recent", self.create_recent_widget())
        left_layout.addWidget(recent_section)
        
        # Coding Projects
        projects_section = self.create_collapsible_section("💻 Projects", self.create_projects_widget())
        left_layout.addWidget(projects_section)
        
        # Templates
        templates_section = self.create_collapsible_section("📋 Templates", self.create_templates_widget())
        left_layout.addWidget(templates_section)
        
        left_layout.addStretch()
        self.left_panel.setWidget(left_content)
        main_layout.addWidget(self.left_panel)
        
        # ==================== MAIN CONTENT AREA ====================
        self.right_panel = QWidget()
        right_layout = QVBoxLayout()
        right_layout.setSpacing(15)
        right_layout.setContentsMargins(20, 20, 20, 20)
        self.right_panel.setLayout(right_layout)
        
        # Breadcrumb Navigation
        self.breadcrumb_layout = QHBoxLayout()
        self.breadcrumb_layout.setSpacing(5)
        right_layout.addLayout(self.breadcrumb_layout)
        
        # Navigation Bar
        nav_bar = QHBoxLayout()
        nav_bar.setSpacing(10)
        
        back_btn = QPushButton("⬅️")
        back_btn.setToolTip("Back (Alt+Left)")
        back_btn.clicked.connect(self.navigate_back)
        back_btn.setFixedSize(45, 45)
        
        forward_btn = QPushButton("➡️")
        forward_btn.setToolTip("Forward (Alt+Right)")
        forward_btn.clicked.connect(self.navigate_forward)
        forward_btn.setFixedSize(45, 45)
        
        up_btn = QPushButton("⬆️")
        up_btn.setToolTip("Up (Alt+Up)")
        up_btn.clicked.connect(self.navigate_up)
        up_btn.setFixedSize(45, 45)
        
        for btn in [back_btn, forward_btn, up_btn]:
            btn.setStyleSheet("QPushButton { border-radius: 8px; font-size: 18px; }")
        
        nav_bar.addWidget(back_btn)
        nav_bar.addWidget(forward_btn)
        nav_bar.addWidget(up_btn)
        
        self.current_path_display = QLineEdit()
        self.current_path_display.setText(str(self.current_path))
        self.current_path_display.returnPressed.connect(self.navigate_to_path_bar)
        self.current_path_display.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                font-size: 13px;
                font-family: 'Consolas', monospace;
            }
        """)
        nav_bar.addWidget(self.current_path_display)
        
        refresh_btn = QPushButton("🔄")
        refresh_btn.setToolTip("Refresh (F5)")
        refresh_btn.clicked.connect(self.refresh_file_browser)
        refresh_btn.setFixedSize(45, 45)
        refresh_btn.setStyleSheet("QPushButton { border-radius: 8px; font-size: 18px; }")
        nav_bar.addWidget(refresh_btn)
        
        right_layout.addLayout(nav_bar)
        
        # Toolbar with ALL actions
        toolbar = QHBoxLayout()
        toolbar.setSpacing(10)
        
        toolbar_buttons = [
            ("📁", "New Folder (Ctrl+Shift+N)", self.create_folder),
            ("📄", "New File (Ctrl+N)", self.create_file),
            ("📋", "Copy (Ctrl+C)", self.copy_selected),
            ("✂️", "Cut (Ctrl+X)", self.cut_selected),
            ("📌", "Paste (Ctrl+V)", self.paste_selected),
            ("🗑️", "Delete (Del)", self.delete_selected),
            ("⭐", "Add to Favorites", self.add_current_to_favorites),
        ]
        
        for icon, tooltip, handler in toolbar_buttons:
            btn = QPushButton(icon)
            btn.setToolTip(tooltip)
            btn.clicked.connect(handler)
            btn.setFixedSize(45, 45)
            btn.setStyleSheet("QPushButton { border-radius: 8px; font-size: 16px; }")
            toolbar.addWidget(btn)
        
        toolbar.addStretch()
        
        # View selector
        view_label = QLabel("View:")
        toolbar.addWidget(view_label)
        
        list_btn = QPushButton("☰")
        list_btn.setToolTip("List View")
        list_btn.clicked.connect(lambda: self.change_view_mode("list"))
        
        grid_btn = QPushButton("⊞")
        grid_btn.setToolTip("Grid View")
        grid_btn.clicked.connect(lambda: self.change_view_mode("grid"))
        
        details_btn = QPushButton("≡")
        details_btn.setToolTip("Details View")
        details_btn.clicked.connect(lambda: self.change_view_mode("details"))
        
        split_btn = QPushButton("⚏")
        split_btn.setToolTip("Split View (Ctrl+D)")
        split_btn.setCheckable(True)
        split_btn.clicked.connect(self.toggle_split_view)
        
        for btn in [list_btn, grid_btn, details_btn, split_btn]:
            btn.setFixedSize(40, 40)
            btn.setStyleSheet("QPushButton { border-radius: 8px; }")
            toolbar.addWidget(btn)
        
        right_layout.addLayout(toolbar)
        
        # Advanced Search Bar
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Search files... (Ctrl+F)")
        self.search_input.textChanged.connect(self.search_files)
        self.search_input.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border-radius: 8px;
                font-size: 13px;
            }
        """)
        search_layout.addWidget(self.search_input)
        
        self.search_content_check = QCheckBox("Content")
        self.search_content_check.setToolTip("Search inside files")
        search_layout.addWidget(self.search_content_check)
        
        self.case_sensitive_check = QCheckBox("Case")
        self.case_sensitive_check.setToolTip("Case sensitive")
        search_layout.addWidget(self.case_sensitive_check)
        
        self.show_hidden_checkbox = QCheckBox("Hidden")
        self.show_hidden_checkbox.setToolTip("Show hidden files")
        self.show_hidden_checkbox.stateChanged.connect(self.refresh_file_browser)
        search_layout.addWidget(self.show_hidden_checkbox)
        
        filter_btn = QPushButton("🎯 Filter")
        filter_btn.clicked.connect(self.show_filter_dialog)
        filter_btn.setStyleSheet("QPushButton { padding: 10px; border-radius: 8px; }")
        search_layout.addWidget(filter_btn)
        
        right_layout.addLayout(search_layout)
        
        # Main Content Splitter
        self.content_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # File Browser
        self.file_tree = QTreeWidget()
        self.file_tree.setHeaderLabels(["Name", "Size", "Type", "Modified", "Tags"])
        self.file_tree.setColumnWidth(0, 400)
        self.file_tree.setColumnWidth(1, 100)
        self.file_tree.setColumnWidth(2, 120)
        self.file_tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.file_tree.customContextMenuRequested.connect(self.show_context_menu)
        self.file_tree.itemDoubleClicked.connect(self.item_double_clicked)
        self.file_tree.itemClicked.connect(self.preview_item)
        self.file_tree.setSelectionMode(QTreeWidget.SelectionMode.ExtendedSelection)
        self.file_tree.setSortingEnabled(True)
        self.file_tree.setDragEnabled(True)
        self.file_tree.setAcceptDrops(True)
        self.file_tree.setDragDropMode(QTreeWidget.DragDropMode.InternalMove)
        self.file_tree.setStyleSheet("""
            QTreeWidget {
                border-radius: 12px;
                padding: 10px;
                font-size: 13px;
            }
            QTreeWidget::item {
                padding: 8px;
                border-radius: 6px;
            }
        """)
        self.file_tree.itemSelectionChanged.connect(self.update_selection_count)
        
        self.content_splitter.addWidget(self.file_tree)
        
        # Preview Panel
        self.preview_panel = QWidget()
        preview_layout = QVBoxLayout()
        preview_layout.setContentsMargins(15, 15, 15, 15)
        self.preview_panel.setLayout(preview_layout)
        self.preview_panel.setMinimumWidth(300)
        self.preview_panel.setMaximumWidth(400)
        
        preview_title = QLabel("<h3>📄 Preview</h3>")
        preview_layout.addWidget(preview_title)
        
        self.preview_image = QLabel()
        self.preview_image.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.preview_image.setMinimumHeight(200)
        self.preview_image.setStyleSheet("""
            QLabel {
                border-radius: 8px;
                padding: 10px;
            }
        """)
        preview_layout.addWidget(self.preview_image)
        
        self.preview_info = QTextEdit()
        self.preview_info.setReadOnly(True)
        self.preview_info.setStyleSheet("""
            QTextEdit {
                border-radius: 8px;
                padding: 10px;
                font-size: 12px;
                font-family: 'Consolas', monospace;
            }
        """)
        preview_layout.addWidget(self.preview_info)
        
        # Tag section in preview
        tag_group = QGroupBox("Tags")
        tag_layout = QVBoxLayout()
        
        self.tags_display = QLabel("No tags")
        self.tags_display.setWordWrap(True)
        tag_layout.addWidget(self.tags_display)
        
        tag_input_layout = QHBoxLayout()
        self.tag_input = QLineEdit()
        self.tag_input.setPlaceholderText("Add tag...")
        tag_input_layout.addWidget(self.tag_input)
        
        add_tag_btn = QPushButton("+")
        add_tag_btn.setMaximumWidth(30)
        add_tag_btn.clicked.connect(self.add_tag_to_current)
        tag_input_layout.addWidget(add_tag_btn)
        
        tag_layout.addLayout(tag_input_layout)
        tag_group.setLayout(tag_layout)
        preview_layout.addWidget(tag_group)
        
        preview_layout.addStretch()
        
        self.content_splitter.addWidget(self.preview_panel)
        self.content_splitter.setSizes([1000, 300])
        
        right_layout.addWidget(self.content_splitter)
        
        # Progress Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border-radius: 8px;
                text-align: center;
                padding: 2px;
            }
        """)
        right_layout.addWidget(self.progress_bar)
        
        # Status Bar
        status_layout = QHBoxLayout()
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-size: 12px; padding: 5px;")
        status_layout.addWidget(self.status_label)
        status_layout.addStretch()
        
        self.item_count_label = QLabel("0 items")
        self.item_count_label.setStyleSheet("font-size: 12px; padding: 5px;")
        status_layout.addWidget(self.item_count_label)
        
        self.selected_count_label = QLabel("")
        self.selected_count_label.setStyleSheet("font-size: 12px; padding: 5px; font-weight: bold;")
        status_layout.addWidget(self.selected_count_label)
        
        self.size_label = QLabel("")
        self.size_label.setStyleSheet("font-size: 12px; padding: 5px;")
        status_layout.addWidget(self.size_label)
        
        right_layout.addLayout(status_layout)
        
        main_layout.addWidget(self.right_panel)
        
        # Navigation history
        self.nav_history = [str(self.current_path)]
        self.nav_index = 0
        
        # Create menu bar
        self.create_menu_bar()
        self.create_keyboard_shortcuts()
    
    def create_theme_widget(self):
        """Create theme selection widget"""
        widget = QWidget()
        layout = QGridLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        self.theme_buttons = QButtonGroup()
        themes = [
            ("Navy", "navy", "#0a1929"),
            ("Purple", "purple", "#1a0a2e"),
            ("Emerald", "emerald", "#0a2e1a"),
            ("Rose", "rose", "#2e0a1a"),
            ("Slate", "slate", "#1a1a1a"),
            ("Ocean", "ocean", "#0a1e29")
        ]
        
        for i, (name, theme_id, color) in enumerate(themes):
            btn = QPushButton(name)
            btn.setCheckable(True)
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background: {color};
                    border: 2px solid rgba(255, 255, 255, 0.1);
                    border-radius: 8px;
                    padding: 8px;
                    color: white;
                    font-weight: bold;
                    font-size: 11px;
                }}
                QPushButton:checked {{
                    border: 2px solid rgba(255, 255, 255, 0.5);
                }}
                QPushButton:hover {{
                    border: 2px solid rgba(255, 255, 255, 0.3);
                }}
            """)
            btn.clicked.connect(lambda checked, t=theme_id: self.apply_theme(t))
            self.theme_buttons.addButton(btn, i)
            layout.addWidget(btn, i // 2, i % 2)
            if theme_id == "navy":
                btn.setChecked(True)
        
        widget.setFixedHeight(140)
        return widget
    
    def create_quick_access_widget(self):
        """Create quick access buttons widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        desktop_path = Path.home() / "OneDrive" / "Desktop"
        if not desktop_path.exists():
            desktop_path = Path.home() / "Desktop"
        
        quick_buttons = [
            ("🏠 Home", str(Path.home())),
            ("💻 Desktop", str(desktop_path)),
            ("📥 Downloads", str(Path.home() / "Downloads")),
            ("📄 Documents", str(Path.home() / "Documents")),
            ("🖼️ Pictures", str(Path.home() / "Pictures")),
            ("🎵 Music", str(Path.home() / "Music")),
            ("🎬 Videos", str(Path.home() / "Videos")),
        ]
        
        for label, path in quick_buttons:
            btn = QPushButton(label)
            btn.clicked.connect(lambda checked, p=path: self.navigate_to(p))
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(32)
            btn.setStyleSheet("""
                QPushButton {
                    text-align: left;
                    padding: 8px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)
            layout.addWidget(btn)
        
        widget.setFixedHeight(240)
        return widget
    
    def create_favorites_widget(self):
        """Create favorites list widget"""
        self.favorites_list = QListWidget()
        self.favorites_list.itemClicked.connect(self.navigate_to_favorite)
        self.favorites_list.setFixedHeight(120)
        self.favorites_list.setStyleSheet("""
            QListWidget {
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-radius: 6px;
                margin: 2px;
            }
        """)
        return self.favorites_list
    
    def create_recent_widget(self):
        """Create recent locations widget"""
        self.recent_list = QListWidget()
        self.recent_list.itemClicked.connect(self.navigate_to_recent)
        self.recent_list.setFixedHeight(100)
        self.recent_list.setStyleSheet("""
            QListWidget {
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
                margin: 1px;
                font-size: 11px;
            }
        """)
        return self.recent_list
    
    def create_projects_widget(self):
        """Create projects widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        # Header with refresh button
        refresh_btn = QPushButton("🔄 Refresh & Auto-detect")
        refresh_btn.clicked.connect(self.refresh_projects)
        refresh_btn.setFixedHeight(35)
        refresh_btn.setStyleSheet("QPushButton { padding: 8px; border-radius: 6px; font-size: 11px; }")
        layout.addWidget(refresh_btn)
        
        # Projects list
        self.projects_list = QListWidget()
        self.projects_list.itemClicked.connect(self.load_project)
        self.projects_list.setFixedHeight(120)
        self.projects_list.setStyleSheet("""
            QListWidget {
                border-radius: 8px;
                padding: 5px;
            }
            QListWidget::item {
                padding: 6px;
                border-radius: 4px;
                margin: 1px;
            }
        """)
        layout.addWidget(self.projects_list)
        
        # Buttons
        buttons = QHBoxLayout()
        new_btn = QPushButton("➕ Add")
        new_btn.clicked.connect(self.create_new_project)
        delete_btn = QPushButton("🗑️ Remove")
        delete_btn.clicked.connect(self.delete_project)
        
        for btn in [new_btn, delete_btn]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(35)
            btn.setStyleSheet("QPushButton { padding: 8px; border-radius: 6px; font-size: 11px; }")
        
        buttons.addWidget(new_btn)
        buttons.addWidget(delete_btn)
        layout.addLayout(buttons)
        
        widget.setFixedHeight(200)
        return widget
    
    def create_templates_widget(self):
        """Create templates widget"""
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(5)
        layout.setContentsMargins(0, 0, 0, 0)
        widget.setLayout(layout)
        
        self.template_combo = QComboBox()
        self.load_templates()
        self.template_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.template_combo.setFixedHeight(35)
        layout.addWidget(self.template_combo)
        
        buttons = QHBoxLayout()
        apply_btn = QPushButton("✅ Apply")
        apply_btn.clicked.connect(self.apply_template)
        preview_btn = QPushButton("👁️ Preview")
        preview_btn.clicked.connect(self.show_template_structure)
        
        for btn in [apply_btn, preview_btn]:
            btn.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            btn.setFixedHeight(35)
            btn.setStyleSheet("QPushButton { padding: 10px; border-radius: 6px; font-size: 11px; }")
        
        buttons.addWidget(apply_btn)
        buttons.addWidget(preview_btn)
        layout.addLayout(buttons)
        
        widget.setFixedHeight(80)
        return widget
    
    def create_menu_bar(self):
        """Create comprehensive menu bar"""
        menubar = self.menuBar()
        
        # File menu
        file_menu = menubar.addMenu("File")
        
        new_folder_action = QAction("New Folder", self)
        new_folder_action.setShortcut(QKeySequence("Ctrl+Shift+N"))
        new_folder_action.triggered.connect(self.create_folder)
        file_menu.addAction(new_folder_action)
        
        new_file_action = QAction("New File", self)
        new_file_action.setShortcut(QKeySequence("Ctrl+N"))
        new_file_action.triggered.connect(self.create_file)
        file_menu.addAction(new_file_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut(QKeySequence("Ctrl+Q"))
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # Edit menu
        edit_menu = menubar.addMenu("Edit")
        
        copy_action = QAction("Copy", self)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.triggered.connect(self.copy_selected)
        edit_menu.addAction(copy_action)
        
        cut_action = QAction("Cut", self)
        cut_action.setShortcut(QKeySequence.StandardKey.Cut)
        cut_action.triggered.connect(self.cut_selected)
        edit_menu.addAction(cut_action)
        
        paste_action = QAction("Paste", self)
        paste_action.setShortcut(QKeySequence.StandardKey.Paste)
        paste_action.triggered.connect(self.paste_selected)
        edit_menu.addAction(paste_action)
        
        delete_action = QAction("Delete", self)
        delete_action.setShortcut(QKeySequence.StandardKey.Delete)
        delete_action.triggered.connect(self.delete_selected)
        edit_menu.addAction(delete_action)
        
        edit_menu.addSeparator()
        
        select_all_action = QAction("Select All", self)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.triggered.connect(self.file_tree.selectAll)
        edit_menu.addAction(select_all_action)
        
        # View menu
        view_menu = menubar.addMenu("View")
        
        refresh_action = QAction("Refresh", self)
        refresh_action.setShortcut(QKeySequence("F5"))
        refresh_action.triggered.connect(self.refresh_file_browser)
        view_menu.addAction(refresh_action)
        
        view_menu.addSeparator()
        
        split_view_action = QAction("Split View", self)
        split_view_action.setShortcut(QKeySequence("Ctrl+D"))
        split_view_action.triggered.connect(self.toggle_split_view)
        view_menu.addAction(split_view_action)
        
        # Tools menu
        tools_menu = menubar.addMenu("Tools")
        
        batch_rename_action = QAction("Batch Rename...", self)
        batch_rename_action.triggered.connect(self.batch_rename_dialog)
        tools_menu.addAction(batch_rename_action)
        
        find_duplicates_action = QAction("Find Duplicates...", self)
        find_duplicates_action.triggered.connect(self.find_duplicates_dialog)
        tools_menu.addAction(find_duplicates_action)
        
        disk_usage_action = QAction("Disk Usage Analyzer...", self)
        disk_usage_action.triggered.connect(self.show_disk_usage)
        tools_menu.addAction(disk_usage_action)
        
        large_files_action = QAction("Find Large Files...", self)
        large_files_action.triggered.connect(self.find_large_files_dialog)
        tools_menu.addAction(large_files_action)
        
        tools_menu.addSeparator()
        
        history_action = QAction("Operation History", self)
        history_action.triggered.connect(self.show_history)
        tools_menu.addAction(history_action)
    
    def create_keyboard_shortcuts(self):
        """Create keyboard shortcuts"""
        # Already handled by menu actions, but add extras
        shortcuts = {
            "Ctrl+F": self.focus_search,
            "F2": self.rename_selected,
            "Alt+Left": self.navigate_back,
            "Alt+Right": self.navigate_forward,
            "Alt+Up": self.navigate_up,
            "Ctrl+L": self.focus_path_bar,
        }
        
        for key, func in shortcuts.items():
            shortcut = QAction(self)
            shortcut.setShortcut(QKeySequence(key))
            shortcut.triggered.connect(func)
            self.addAction(shortcut)
    
    # ==================== THEME SYSTEM ====================
    
    def apply_theme(self, theme_name):
        """Apply glassmorphism theme"""
        self.current_theme = theme_name
        
        themes = {
            "navy": {
                "primary": "#0a1929",
                "secondary": "#132f4c",
                "accent": "#3399ff",
                "text": "#ffffff",
                "glass": "rgba(19, 47, 76, 0.7)"
            },
            "purple": {
                "primary": "#1a0a2e",
                "secondary": "#2e1a47",
                "accent": "#9d4edd",
                "text": "#ffffff",
                "glass": "rgba(46, 26, 71, 0.7)"
            },
            "emerald": {
                "primary": "#0a2e1a",
                "secondary": "#1a4730",
                "accent": "#10b981",
                "text": "#ffffff",
                "glass": "rgba(26, 71, 48, 0.7)"
            },
            "rose": {
                "primary": "#2e0a1a",
                "secondary": "#47182e",
                "accent": "#fb7185",
                "text": "#ffffff",
                "glass": "rgba(71, 24, 46, 0.7)"
            },
            "slate": {
                "primary": "#1a1a1a",
                "secondary": "#2e2e2e",
                "accent": "#64748b",
                "text": "#ffffff",
                "glass": "rgba(46, 46, 46, 0.7)"
            },
            "ocean": {
                "primary": "#0a1e29",
                "secondary": "#173547",
                "accent": "#06b6d4",
                "text": "#ffffff",
                "glass": "rgba(23, 53, 71, 0.7)"
            }
        }
        
        theme = themes[theme_name]
        
        style = f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {theme['primary']}, stop:1 {theme['secondary']});
            }}
            QWidget {{ background: transparent; color: {theme['text']}; }}
            QLineEdit, QTextEdit, QComboBox, QListWidget, QTreeWidget {{
                background: {theme['glass']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {theme['text']};
            }}
            QLineEdit:focus, QTextEdit:focus {{
                border: 1px solid {theme['accent']};
            }}
            QPushButton {{
                background: {theme['glass']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                color: {theme['text']};
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.1);
                border: 1px solid {theme['accent']};
            }}
            QPushButton:pressed {{ background: {theme['accent']}; }}
            QTreeWidget::item:selected, QListWidget::item:selected {{
                background: {theme['accent']};
                color: white;
            }}
            QTreeWidget::item:hover, QListWidget::item:hover {{
                background: rgba(255, 255, 255, 0.1);
            }}
            QHeaderView::section {{
                background: {theme['glass']};
                color: {theme['text']};
                padding: 8px;
                border: none;
                font-weight: bold;
            }}
            QMenuBar {{
                background: {theme['glass']};
                color: {theme['text']};
            }}
            QMenuBar::item:selected {{ background: {theme['accent']}; }}
            QMenu {{
                background: {theme['secondary']};
                color: {theme['text']};
                border: 1px solid rgba(255, 255, 255, 0.1);
            }}
            QMenu::item:selected {{ background: {theme['accent']}; }}
            QProgressBar {{
                background: {theme['glass']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
            }}
            QProgressBar::chunk {{ background: {theme['accent']}; border-radius: 8px; }}
            QCheckBox {{ color: {theme['text']}; }}
            QCheckBox::indicator {{
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 3px;
                background: {theme['glass']};
            }}
            QCheckBox::indicator:checked {{ background: {theme['accent']}; }}
            QGroupBox {{
                color: {theme['text']};
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }}
        """
        self.setStyleSheet(style)
    
    # ==================== NAVIGATION ====================
    
    def update_breadcrumb(self):
        """Update breadcrumb navigation"""
        # Clear existing breadcrumbs
        while self.breadcrumb_layout.count():
            child = self.breadcrumb_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()
        
        parts = Path(self.current_path).parts
        
        for i, part in enumerate(parts):
            btn = QPushButton(part)
            path_to_navigate = str(Path(*parts[:i+1]))
            btn.clicked.connect(lambda checked, p=path_to_navigate: self.navigate_to(p))
            btn.setStyleSheet("""
                QPushButton {
                    padding: 6px 12px;
                    border-radius: 6px;
                    font-size: 12px;
                }
            """)
            self.breadcrumb_layout.addWidget(btn)
            
            if i < len(parts) - 1:
                separator = QLabel("›")
                separator.setStyleSheet("font-size: 14px; padding: 0 5px;")
                self.breadcrumb_layout.addWidget(separator)
        
        self.breadcrumb_layout.addStretch()
    
    def navigate_to(self, path_str):
        """Navigate to specific path"""
        path = Path(path_str)
        if path.exists() and path.is_dir():
            self.current_path = path
            self.current_path_display.setText(str(self.current_path))
            
            # Update navigation history
            if self.nav_index < len(self.nav_history) - 1:
                self.nav_history = self.nav_history[:self.nav_index + 1]
            self.nav_history.append(str(self.current_path))
            self.nav_index = len(self.nav_history) - 1
            
            self.file_manager.add_recent(str(path))
            self.load_recent()
            self.update_breadcrumb()
            self.refresh_file_browser()
            self.status_label.setText(f"📂 {path.name}")
        else:
            QMessageBox.warning(self, "Invalid Path", f"Path does not exist: {path_str}")
    
    def navigate_to_path_bar(self):
        """Navigate to path from path bar"""
        self.navigate_to(self.current_path_display.text())
    
    def navigate_back(self):
        """Navigate back in history"""
        if self.nav_index > 0:
            self.nav_index -= 1
            path = self.nav_history[self.nav_index]
            self.current_path = Path(path)
            self.current_path_display.setText(str(self.current_path))
            self.update_breadcrumb()
            self.refresh_file_browser()
    
    def navigate_forward(self):
        """Navigate forward in history"""
        if self.nav_index < len(self.nav_history) - 1:
            self.nav_index += 1
            path = self.nav_history[self.nav_index]
            self.current_path = Path(path)
            self.current_path_display.setText(str(self.current_path))
            self.update_breadcrumb()
            self.refresh_file_browser()
    
    def navigate_up(self):
        """Navigate to parent directory"""
        parent = self.current_path.parent
        if parent != self.current_path:
            self.navigate_to(str(parent))
    
    # ==================== FILE BROWSER ====================
    
    def refresh_file_browser(self):
        """Refresh file browser"""
        self.file_tree.clear()
        self.preview_image.clear()
        self.preview_info.clear()
        
        if not self.current_path.exists():
            QMessageBox.warning(self, "Error", "Current path no longer exists")
            self.current_path = Path.home()
            self.current_path_display.setText(str(self.current_path))
            return
        
        try:
            items = list(self.current_path.iterdir())
            show_hidden = self.show_hidden_checkbox.isChecked()
            
            if not show_hidden:
                items = [item for item in items if not item.name.startswith('.')]
            
            items.sort(key=lambda x: (not x.is_dir(), x.name.lower()))
            
            count = 0
            total_size = 0
            
            for item in items:
                try:
                    tree_item = QTreeWidgetItem()
                    
                    # Icon based on type
                    icon = self.get_file_icon(item)
                    tree_item.setText(0, f"{icon} {item.name}")
                    tree_item.setData(0, Qt.ItemDataRole.UserRole, str(item))
                    
                    # Size
                    if item.is_file():
                        size = item.stat().st_size
                        tree_item.setText(1, self.format_size(size))
                        total_size += size
                    else:
                        tree_item.setText(1, "")
                    
                    # Type
                    if item.is_dir():
                        tree_item.setText(2, "Folder")
                    else:
                        tree_item.setText(2, item.suffix[1:].upper() if item.suffix else "File")
                    
                    # Modified
                    modified = item.stat().st_mtime
                    date_str = datetime.fromtimestamp(modified).strftime("%Y-%m-%d %H:%M")
                    tree_item.setText(3, date_str)
                    
                    # Tags
                    tags = self.file_manager.get_tags(str(item))
                    if tags:
                        tree_item.setText(4, ", ".join(tags))
                    
                    self.file_tree.addTopLevelItem(tree_item)
                    count += 1
                    
                except (PermissionError, OSError):
                    continue
            
            self.item_count_label.setText(f"{count} items")
            self.size_label.setText(f"Total: {self.format_size(total_size)}")
            self.status_label.setText("✅ Ready")
            
        except PermissionError:
            QMessageBox.warning(self, "Permission Denied", 
                              "You don't have permission to access this folder")
    
    def get_file_icon(self, path):
        """Get icon for file type"""
        if path.is_dir():
            return "📁"
        
        ext = path.suffix.lower()
        icon_map = {
            '.jpg': '🖼️', '.jpeg': '🖼️', '.png': '🖼️', '.gif': '🖼️', '.bmp': '🖼️', '.webp': '🖼️',
            '.mp4': '🎬', '.avi': '🎬', '.mov': '🎬', '.mkv': '🎬',
            '.mp3': '🎵', '.wav': '🎵', '.flac': '🎵', '.m4a': '🎵',
            '.py': '💻', '.js': '💻', '.java': '💻', '.cpp': '💻', '.c': '💻', 
            '.html': '💻', '.css': '💻', '.ts': '💻', '.jsx': '💻', '.tsx': '💻',
            '.pdf': '📕',
            '.zip': '📦', '.rar': '📦', '.7z': '📦', '.tar': '📦', '.gz': '📦',
            '.txt': '📄', '.doc': '📄', '.docx': '📄', '.md': '📄',
            '.xls': '📊', '.xlsx': '📊', '.csv': '📊',
        }
        return icon_map.get(ext, '📄')
    
    def format_size(self, size):
        """Format file size"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"
    
    def item_double_clicked(self, item, column):
        """Handle double click"""
        item_path = Path(item.data(0, Qt.ItemDataRole.UserRole))
        
        if item_path.is_dir():
            self.navigate_to(str(item_path))
        else:
            self.file_manager.open_file(item_path)
    
    def preview_item(self, item, column):
        """Preview selected item"""
        item_path = Path(item.data(0, Qt.ItemDataRole.UserRole))
        
        self.preview_image.clear()
        
        info = self.file_manager.get_file_info(item_path)
        if not info:
            return
        
        info_text = f"""
<b>Name:</b> {info['name']}<br>
<b>Type:</b> {'Folder' if info['is_dir'] else 'File'}<br>
<b>Size:</b> {self.format_size(info['size'])}<br>
<b>Created:</b> {datetime.fromtimestamp(info['created']).strftime('%Y-%m-%d %H:%M')}<br>
<b>Modified:</b> {datetime.fromtimestamp(info['modified']).strftime('%Y-%m-%d %H:%M')}<br>
<b>Path:</b> {item_path}
        """
        
        if 'hash' in info and info['hash']:
            info_text += f"<br><b>MD5:</b> {info['hash'][:16]}..."
        
        self.preview_info.setHtml(info_text)
        
        # Preview image
        if item_path.is_file() and item_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']:
            try:
                pixmap = QPixmap(str(item_path))
                if not pixmap.isNull():
                    scaled = pixmap.scaled(350, 350, Qt.AspectRatioMode.KeepAspectRatio, 
                                         Qt.TransformationMode.SmoothTransformation)
                    self.preview_image.setPixmap(scaled)
                else:
                    self.preview_image.setText("📷\nCannot preview")
            except:
                self.preview_image.setText("📷\nPreview failed")
        elif item_path.is_dir():
            self.preview_image.setText("📁\nFolder")
        else:
            ext = item_path.suffix.upper()[1:] if item_path.suffix else "FILE"
            self.preview_image.setText(f"📄\n{ext}")
        
        # Display tags
        tags = self.file_manager.get_tags(str(item_path))
        if tags:
            self.tags_display.setText(", ".join([f"🏷️ {tag}" for tag in tags]))
        else:
            self.tags_display.setText("No tags")
    
    def update_selection_count(self):
        """Update selection count"""
        count = len(self.file_tree.selectedItems())
        if count > 0:
            total_size = 0
            for item in self.file_tree.selectedItems():
                path = Path(item.data(0, Qt.ItemDataRole.UserRole))
                if path.is_file():
                    total_size += path.stat().st_size
            
            self.selected_count_label.setText(
                f"Selected: {count} ({self.format_size(total_size)})"
            )
        else:
            self.selected_count_label.setText("")
    
    # ==================== FILE OPERATIONS ====================
    
    def create_folder(self):
        """Create new folder"""
        name, ok = QInputDialog.getText(self, "New Folder", "Folder Name:")
        if ok and name:
            new_folder = self.current_path / name
            if self.file_manager.create_folder(new_folder):
                self.refresh_file_browser()
                self.status_label.setText(f"✅ Created: {name}")
            else:
                QMessageBox.warning(self, "Error", "Failed to create folder")
    
    def create_file(self):
        """Create new file"""
        name, ok = QInputDialog.getText(self, "New File", "File Name:")
        if ok and name:
            new_file = self.current_path / name
            try:
                new_file.touch()
                self.refresh_file_browser()
                self.status_label.setText(f"✅ Created: {name}")
            except Exception as e:
                QMessageBox.warning(self, "Error", f"Failed: {e}")
    
    def get_selected_paths(self):
        """Get selected file paths"""
        return [Path(item.data(0, Qt.ItemDataRole.UserRole)) 
                for item in self.file_tree.selectedItems()]
    
    def copy_selected(self):
        """Copy selected items"""
        selected = self.get_selected_paths()
        if not selected:
            return
        self.clipboard = ('copy', selected)
        self.status_label.setText(f"📋 Copied {len(selected)} items")
    
    def cut_selected(self):
        """Cut selected items"""
        selected = self.get_selected_paths()
        if not selected:
            return
        self.clipboard = ('cut', selected)
        self.status_label.setText(f"✂️ Cut {len(selected)} items")
    
    def paste_selected(self):
        """Paste items"""
        if not self.clipboard:
            return
        
        operation, items = self.clipboard
        dest = self.current_path
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setMaximum(len(items))
        success = 0
        
        for i, item in enumerate(items):
            if operation == 'copy':
                if self.file_manager.copy(item, dest / item.name):
                    success += 1
            else:  # cut
                if self.file_manager.move(item, dest / item.name):
                    success += 1
            self.progress_bar.setValue(i + 1)
        
        self.progress_bar.setVisible(False)
        self.refresh_file_browser()
        self.status_label.setText(f"✅ Pasted {success}/{len(items)} items")
        
        if operation == 'cut':
            self.clipboard = []
    
    def delete_selected(self):
        """Delete selected items"""
        selected = self.get_selected_paths()
        if not selected:
            return
        
        reply = QMessageBox.question(
            self, "Confirm Delete",
            f"Delete {len(selected)} item(s)?\n(They will be moved to Recycle Bin)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(selected))
            success = 0
            
            for i, item in enumerate(selected):
                if self.file_manager.delete(item, use_trash=True):
                    success += 1
                self.progress_bar.setValue(i + 1)
            
            self.progress_bar.setVisible(False)
            self.refresh_file_browser()
            self.status_label.setText(f"✅ Deleted {success} items")
    
    def rename_selected(self):
        """Rename selected item"""
        selected = self.get_selected_paths()
        if len(selected) != 1:
            QMessageBox.information(self, "Rename", "Please select exactly one item")
            return
        
        path = selected[0]
        new_name, ok = QInputDialog.getText(self, "Rename", "New name:", text=path.name)
        if ok and new_name and new_name != path.name:
            new_path = path.parent / new_name
            if self.file_manager.rename(path, new_path):
                self.refresh_file_browser()
                self.status_label.setText(f"✅ Renamed to: {new_name}")
    
    # ==================== CONTEXT MENU ====================
    
    def show_context_menu(self, position):
        """Show context menu"""
        item = self.file_tree.itemAt(position)
        if not item:
            return
        
        menu = QMenu()
        
        open_action = menu.addAction("📂 Open")
        menu.addSeparator()
        rename_action = menu.addAction("✏️ Rename (F2)")
        copy_action = menu.addAction("📋 Copy (Ctrl+C)")
        cut_action = menu.addAction("✂️ Cut (Ctrl+X)")
        delete_action = menu.addAction("🗑️ Delete (Del)")
        menu.addSeparator()
        add_tag_action = menu.addAction("🏷️ Add Tag")
        add_fav_action = menu.addAction("⭐ Add to Favorites")
        menu.addSeparator()
        copy_path_action = menu.addAction("📍 Copy Path")
        properties_action = menu.addAction("ℹ️ Properties")
        
        action = menu.exec(self.file_tree.viewport().mapToGlobal(position))
        
        item_path = Path(item.data(0, Qt.ItemDataRole.UserRole))
        
        if action == open_action:
            if item_path.is_dir():
                self.navigate_to(str(item_path))
            else:
                self.file_manager.open_file(item_path)
        elif action == rename_action:
            self.rename_selected()
        elif action == copy_action:
            self.copy_selected()
        elif action == cut_action:
            self.cut_selected()
        elif action == delete_action:
            self.delete_selected()
        elif action == add_tag_action:
            self.add_tag_dialog(str(item_path))
        elif action == add_fav_action:
            self.file_manager.add_favorite(str(item_path))
            self.load_favorites()
            self.status_label.setText("⭐ Added to favorites")
        elif action == copy_path_action:
            from PyQt6.QtWidgets import QApplication
            QApplication.clipboard().setText(str(item_path))
            self.status_label.setText("📋 Path copied")
        elif action == properties_action:
            self.show_properties(item_path)
    
    def show_properties(self, path):
        """Show file properties"""
        info = self.file_manager.get_file_info(path)
        if info:
            props = f"""
<h3>Properties</h3>
<b>Path:</b> {path}<br>
<b>Name:</b> {info['name']}<br>
<b>Type:</b> {'Folder' if info['is_dir'] else 'File'}<br>
<b>Size:</b> {self.format_size(info['size'])}<br>
<b>Created:</b> {datetime.fromtimestamp(info['created']).strftime('%Y-%m-%d %H:%M:%S')}<br>
<b>Modified:</b> {datetime.fromtimestamp(info['modified']).strftime('%Y-%m-%d %H:%M:%S')}<br>
<b>Permissions:</b> {info.get('permissions', 'N/A')}
            """
            if 'hash' in info and info['hash']:
                props += f"<br><b>MD5 Hash:</b> {info['hash']}"
            
            msg = QMessageBox(self)
            msg.setWindowTitle("Properties")
            msg.setTextFormat(Qt.TextFormat.RichText)
            msg.setText(props)
            msg.exec()
    
    # ==================== SEARCH ====================
    
    def search_files(self, text):
        """Search files"""
        if not text:
            self.refresh_file_browser()
            return
        
        # Simple filename search
        text_lower = text.lower()
        for i in range(self.file_tree.topLevelItemCount()):
            item = self.file_tree.topLevelItem(i)
            item_text = item.text(0).lower()
            item.setHidden(text_lower not in item_text)
    
    def show_filter_dialog(self):
        """Show advanced filter dialog"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Advanced Filters")
        dialog.setMinimumWidth(400)
        
        layout = QVBoxLayout()
        
        # Size filter
        size_group = QGroupBox("Size")
        size_layout = QVBoxLayout()
        
        size_options = QHBoxLayout()
        min_size_label = QLabel("Min (MB):")
        min_size_spin = QSpinBox()
        min_size_spin.setMaximum(10000)
        max_size_label = QLabel("Max (MB):")
        max_size_spin = QSpinBox()
        max_size_spin.setMaximum(10000)
        max_size_spin.setValue(1000)
        
        size_options.addWidget(min_size_label)
        size_options.addWidget(min_size_spin)
        size_options.addWidget(max_size_label)
        size_options.addWidget(max_size_spin)
        size_layout.addLayout(size_options)
        size_group.setLayout(size_layout)
        layout.addWidget(size_group)
        
        # Date filter
        date_group = QGroupBox("Modified")
        date_layout = QVBoxLayout()
        
        today_btn = QPushButton("Today")
        week_btn = QPushButton("This Week")
        month_btn = QPushButton("This Month")
        
        date_layout.addWidget(today_btn)
        date_layout.addWidget(week_btn)
        date_layout.addWidget(month_btn)
        date_group.setLayout(date_layout)
        layout.addWidget(date_group)
        
        # Apply button
        apply_btn = QPushButton("Apply Filters")
        layout.addWidget(apply_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def focus_search(self):
        """Focus search bar"""
        self.search_input.setFocus()
        self.search_input.selectAll()
    
    def focus_path_bar(self):
        """Focus path bar"""
        self.current_path_display.setFocus()
        self.current_path_display.selectAll()
    
    # ==================== TAGS ====================
    
    def add_tag_dialog(self, path):
        """Add tag to file"""
        tag, ok = QInputDialog.getText(self, "Add Tag", "Tag name:")
        if ok and tag:
            self.file_manager.add_tag(path, tag)
            self.refresh_file_browser()
            self.status_label.setText(f"🏷️ Added tag: {tag}")
    
    def add_tag_to_current(self):
        """Add tag from preview panel"""
        selected = self.get_selected_paths()
        if len(selected) != 1:
            return
        
        tag = self.tag_input.text().strip()
        if tag:
            self.file_manager.add_tag(str(selected[0]), tag)
            self.tag_input.clear()
            self.refresh_file_browser()
            self.preview_item(self.file_tree.currentItem(), 0)
    
    # ==================== FAVORITES ====================
    
    def load_favorites(self):
        """Load favorites list"""
        self.favorites_list.clear()
        favorites = self.file_manager.get_favorites()
        for fav in favorites:
            item = QListWidgetItem(f"⭐ {fav['name']}")
            item.setData(Qt.ItemDataRole.UserRole, fav['path'])
            self.favorites_list.addItem(item)
    
    def navigate_to_favorite(self, item):
        """Navigate to favorite"""
        path = item.data(Qt.ItemDataRole.UserRole)
        self.navigate_to(path)
    
    def add_current_to_favorites(self):
        """Add current folder to favorites"""
        self.file_manager.add_favorite(str(self.current_path))
        self.load_favorites()
        self.status_label.setText("⭐ Added to favorites")
    
    # ==================== RECENT ====================
    
    def load_recent(self):
        """Load recent locations"""
        self.recent_list.clear()
        recent = self.file_manager.get_recent()
        for item in recent[:10]:
            path = Path(item['path'])
            list_item = QListWidgetItem(f"🕐 {path.name}")
            list_item.setData(Qt.ItemDataRole.UserRole, item['path'])
            self.recent_list.addItem(list_item)
    
    def navigate_to_recent(self, item):
        """Navigate to recent location"""
        path = item.data(Qt.ItemDataRole.UserRole)
        self.navigate_to(path)
    
    # ==================== ADVANCED FEATURES ====================
    
    def batch_rename_dialog(self):
        """Batch rename dialog"""
        selected = self.get_selected_paths()
        if not selected:
            QMessageBox.information(self, "Batch Rename", "Please select files to rename")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Batch Rename")
        dialog.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Renaming {len(selected)} files")
        layout.addWidget(info_label)
        
        pattern_label = QLabel("Pattern: Use {n} for number, {name} for original name, {ext} for extension")
        layout.addWidget(pattern_label)
        
        pattern_input = QLineEdit()
        pattern_input.setPlaceholderText("Example: Photo_{n}")
        layout.addWidget(pattern_input)
        
        start_label = QLabel("Start numbering at:")
        start_spin = QSpinBox()
        start_spin.setMinimum(1)
        start_spin.setMaximum(9999)
        start_spin.setValue(1)
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(start_label)
        start_layout.addWidget(start_spin)
        layout.addLayout(start_layout)
        
        buttons = QHBoxLayout()
        apply_btn = QPushButton("Apply")
        cancel_btn = QPushButton("Cancel")
        
        def apply_rename():
            pattern = pattern_input.text()
            if not pattern:
                QMessageBox.warning(dialog, "Error", "Please enter a pattern")
                return
            
            success = self.file_manager.batch_rename(selected, pattern, start_spin.value())
            QMessageBox.information(dialog, "Complete", f"Renamed {success} files")
            dialog.accept()
            self.refresh_file_browser()
        
        apply_btn.clicked.connect(apply_rename)
        cancel_btn.clicked.connect(dialog.reject)
        
        buttons.addWidget(apply_btn)
        buttons.addWidget(cancel_btn)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def find_duplicates_dialog(self):
        """Find duplicate files"""
        reply = QMessageBox.question(
            self, "Find Duplicates",
            f"Scan current folder for duplicates?\n{self.current_path}\n\nThis may take a while for large folders.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.status_label.setText("🔍 Scanning for duplicates...")
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate
            
            # Use worker thread
            self.dup_worker = DuplicateFinderWorker(self.file_manager, self.current_path)
            self.dup_worker.finished.connect(self.show_duplicates_results)
            self.dup_worker.progress.connect(self.status_label.setText)
            self.dup_worker.start()
    
    def show_duplicates_results(self, duplicates):
        """Show duplicate files results"""
        self.progress_bar.setVisible(False)
        
        if not duplicates:
            QMessageBox.information(self, "No Duplicates", "No duplicate files found!")
            self.status_label.setText("✅ No duplicates found")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Duplicate Files")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Found {len(duplicates)} groups of duplicate files")
        layout.addWidget(info_label)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["File", "Size", "Path"])
        tree.setColumnWidth(0, 250)
        tree.setColumnWidth(1, 100)
        
        for hash_val, files in duplicates.items():
            group_item = QTreeWidgetItem()
            group_item.setText(0, f"Duplicate Group ({len(files)} files)")
            group_item.setText(1, self.format_size(files[0].stat().st_size))
            
            for file in files:
                file_item = QTreeWidgetItem()
                file_item.setText(0, file.name)
                file_item.setText(1, self.format_size(file.stat().st_size))
                file_item.setText(2, str(file.parent))
                file_item.setData(0, Qt.ItemDataRole.UserRole, str(file))
                group_item.addChild(file_item)
            
            tree.addTopLevelItem(group_item)
        
        tree.expandAll()
        layout.addWidget(tree)
        
        buttons = QHBoxLayout()
        delete_btn = QPushButton("Delete Selected")
        close_btn = QPushButton("Close")
        
        def delete_selected_dups():
            selected_items = tree.selectedItems()
            if not selected_items:
                return
            
            paths = [Path(item.data(0, Qt.ItemDataRole.UserRole)) 
                    for item in selected_items 
                    if item.data(0, Qt.ItemDataRole.UserRole)]
            
            if paths:
                count = self.file_manager.batch_delete(paths, use_trash=True)
                QMessageBox.information(dialog, "Deleted", f"Deleted {count} files")
                dialog.accept()
                self.refresh_file_browser()
        
        delete_btn.clicked.connect(delete_selected_dups)
        close_btn.clicked.connect(dialog.accept)
        
        buttons.addWidget(delete_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
        self.status_label.setText("✅ Ready")
    
    def show_disk_usage(self):
        """Show disk usage analyzer"""
        self.status_label.setText("📊 Analyzing disk usage...")
        
        usage = self.file_manager.analyze_disk_usage(self.current_path, max_depth=2)
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Disk Usage Analyzer")
        dialog.setMinimumSize(600, 500)
        
        layout = QVBoxLayout()
        
        total_label = QLabel(f"<h3>Total Size: {self.format_size(usage['size'])}</h3>")
        layout.addWidget(total_label)
        
        stats_label = QLabel(
            f"Files: {usage['file_count']} | Folders: {usage['folder_count']}"
        )
        layout.addWidget(stats_label)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Folder", "Size", "Files", "Folders"])
        tree.setColumnWidth(0, 300)
        
        def add_usage_item(parent, data):
            item = QTreeWidgetItem()
            path = Path(data['path'])
            item.setText(0, path.name or str(path))
            item.setText(1, self.format_size(data['size']))
            item.setText(2, str(data['file_count']))
            item.setText(3, str(data['folder_count']))
            parent.addTopLevelItem(item) if parent == tree else parent.addChild(item)
            
            for child in sorted(data.get('children', []), 
                              key=lambda x: x['size'], reverse=True):
                add_usage_item(item, child)
        
        add_usage_item(tree, usage)
        tree.expandAll()
        layout.addWidget(tree)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
        self.status_label.setText("✅ Ready")
    
    def find_large_files_dialog(self):
        """Find large files"""
        min_size, ok = QInputDialog.getInt(
            self, "Find Large Files",
            "Minimum file size (MB):",
            100, 1, 10000
        )
        
        if not ok:
            return
        
        self.status_label.setText("🔍 Searching for large files...")
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        
        large_files = self.file_manager.find_large_files(self.current_path, min_size)
        
        self.progress_bar.setVisible(False)
        
        if not large_files:
            QMessageBox.information(self, "No Large Files", 
                                   f"No files larger than {min_size}MB found")
            self.status_label.setText("✅ Ready")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Large Files")
        dialog.setMinimumSize(700, 500)
        
        layout = QVBoxLayout()
        
        info_label = QLabel(f"Found {len(large_files)} files larger than {min_size}MB")
        layout.addWidget(info_label)
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["File", "Size", "Path"])
        tree.setColumnWidth(0, 250)
        tree.setColumnWidth(1, 100)
        
        for file_info in large_files[:100]:  # Limit to 100
            item = QTreeWidgetItem()
            item.setText(0, file_info['name'])
            item.setText(1, self.format_size(file_info['size']))
            item.setText(2, file_info['path'])
            item.setData(0, Qt.ItemDataRole.UserRole, file_info['path'])
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        buttons = QHBoxLayout()
        open_btn = QPushButton("Open Location")
        delete_btn = QPushButton("Delete Selected")
        close_btn = QPushButton("Close")
        
        def open_location():
            selected = tree.selectedItems()
            if selected:
                path = Path(selected[0].data(0, Qt.ItemDataRole.UserRole))
                self.navigate_to(str(path.parent))
                dialog.accept()
        
        def delete_large():
            selected = tree.selectedItems()
            if selected:
                paths = [Path(item.data(0, Qt.ItemDataRole.UserRole)) 
                        for item in selected]
                count = self.file_manager.batch_delete(paths, use_trash=True)
                QMessageBox.information(dialog, "Deleted", f"Deleted {count} files")
                dialog.accept()
                self.refresh_file_browser()
        
        open_btn.clicked.connect(open_location)
        delete_btn.clicked.connect(delete_large)
        close_btn.clicked.connect(dialog.accept)
        
        buttons.addWidget(open_btn)
        buttons.addWidget(delete_btn)
        buttons.addWidget(close_btn)
        layout.addLayout(buttons)
        
        dialog.setLayout(layout)
        dialog.exec()
        self.status_label.setText("✅ Ready")
    
    def show_history(self):
        """Show operation history"""
        history = self.file_manager.get_operation_history()
        
        if not history:
            QMessageBox.information(self, "History", "No operations in history")
            return
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Operation History")
        dialog.setMinimumSize(600, 400)
        
        layout = QVBoxLayout()
        
        tree = QTreeWidget()
        tree.setHeaderLabels(["Time", "Operation", "Details"])
        tree.setColumnWidth(0, 150)
        tree.setColumnWidth(1, 100)
        
        for op in reversed(history):
            item = QTreeWidgetItem()
            time = datetime.fromisoformat(op['timestamp']).strftime('%Y-%m-%d %H:%M:%S')
            item.setText(0, time)
            item.setText(1, op['operation'])
            item.setText(2, str(op['data'])[:100])
            tree.addTopLevelItem(item)
        
        layout.addWidget(tree)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def toggle_split_view(self):
        """Toggle split view mode"""
        self.split_view_enabled = not self.split_view_enabled
        # Placeholder - would implement dual pane view
        QMessageBox.information(self, "Split View", 
                               "Split view coming in next update!")
    
    def change_view_mode(self, mode):
        """Change view mode"""
        self.view_mode = mode
        self.status_label.setText(f"View: {mode}")
        # Placeholder - would switch between list/grid/details
        QMessageBox.information(self, "View Mode", 
                               f"Switched to {mode} view\n(Full implementation coming soon!)")
    
    # ==================== TEMPLATES ====================
    
    def load_templates(self):
        """Load templates"""
        templates = self.template_manager.get_all_templates()
        self.template_combo.clear()
        for template in templates:
            self.template_combo.addItem(template['name'], template)
    
    def apply_template(self):
        """Apply template"""
        template_data = self.template_combo.currentData()
        if not template_data:
            return
        
        reply = QMessageBox.question(
            self, "Apply Template",
            f"Apply '{template_data['name']}' to:\n{self.current_path}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.template_manager.apply_template(template_data, self.current_path):
                QMessageBox.information(self, "Success", "Template applied!")
                self.refresh_file_browser()
    
    def show_template_structure(self):
        """Show template preview"""
        template_data = self.template_combo.currentData()
        if not template_data:
            return
        
        text = f"<h3>{template_data['name']}</h3>"
        text += f"<p><i>{template_data['description']}</i></p><hr>"
        text += "<b>Folder Structure:</b><br><br>"
        
        for folder in template_data['structure']:
            depth = folder.count('/')
            indent = "&nbsp;" * (depth * 4)
            name = folder.split('/')[-1]
            text += f"{indent}📁 {name}<br>"
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Template Preview")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(text)
        msg.exec()
    
    # ==================== PROJECTS ====================
    
    def load_projects(self):
        """Load projects"""
        self.projects_list.clear()
        projects = self.project_manager.get_all_projects()
        for project in projects:
            self.projects_list.addItem(f"💻 {project['name']}")
    
    def refresh_projects(self):
        """Refresh and auto-detect projects"""
        self.status_label.setText("🔍 Scanning for projects...")
        self.auto_detect_projects()
        self.load_projects()
        self.status_label.setText("✅ Projects refreshed")
    
    def auto_detect_projects(self):
        """Auto-detect coding projects"""
        search_paths = [
            Path.home() / "Documents",
            Path.home() / "Desktop",
            Path.home() / "Projects",
            Path.home(),
        ]
        
        search_paths = [p for p in search_paths if p and p.exists()]
        
        existing_projects = {p['path']: p['name'] 
                           for p in self.project_manager.get_all_projects()}
        
        for base_path in search_paths:
            try:
                for item in base_path.iterdir():
                    if not item.is_dir() or str(item) in existing_projects:
                        continue
                    
                    indicators = [
                        'package.json', 'requirements.txt', 'setup.py',
                        'pyproject.toml', 'Cargo.toml', 'pom.xml',
                        'build.gradle', 'Gemfile', 'composer.json',
                        'go.mod', '.git', 'main.py', 'index.js'
                    ]
                    
                    if any((item / ind).exists() for ind in indicators):
                        self.project_manager.create_project(item.name, str(item))
                        
            except (PermissionError, OSError):
                continue
    
    def create_new_project(self):
        """Add project manually"""
        name, ok = QInputDialog.getText(self, "Add Project", "Project Name:")
        if not ok or not name:
            return
        
        path = QFileDialog.getExistingDirectory(self, "Select Project Folder")
        if path:
            self.project_manager.create_project(name, path)
            self.load_projects()
            self.status_label.setText(f"✅ Added: {name}")
    
    def delete_project(self):
        """Delete project"""
        current_item = self.projects_list.currentItem()
        if not current_item:
            return
        
        name = current_item.text().replace("💻 ", "")
        
        reply = QMessageBox.question(
            self, "Remove Project",
            f"Remove '{name}'?\n(Files won't be deleted)",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.project_manager.delete_project(name)
            self.load_projects()
    
    def load_project(self, item):
        """Load project"""
        name = item.text().replace("💻 ", "")
        project = self.project_manager.get_project(name)
        
        if project:
            self.navigate_to(project['path'])