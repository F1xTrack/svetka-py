"""
Memory Settings Tab (Tab 5)
Реализация вкладки настроек памяти для Svetka AI Assistant.
"""

import sys
import asyncio
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QSpinBox,
    QDoubleSpinBox,
    QComboBox,
    QCheckBox,
    QPushButton,
    QFileDialog,
    QProgressBar,
    QGroupBox,
    QFormLayout,
    QLineEdit,
    QFrame,
    QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class MemoryTab(QWidget):
    """Вкладка настроек памяти (Tab 5)"""

    # Сигналы для обновления конфигурации
    config_changed = pyqtSignal(str, object)

    def __init__(self, config_manager=None, guide_manager=None, context_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.context_manager = context_manager
        self._setup_ui()
        self._load_config()

    def _setup_ui(self):
        """Создание UI элементов вкладки"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # Заголовок вкладки
        header_label = QLabel("⚙️ Memory Settings")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        main_layout.addWidget(header_label)

        # Группа 1: Основные настройки памяти
        storage_group = self._create_storage_group()
        main_layout.addWidget(storage_group)

        # Группа 2: Настройки RAG
        rag_group = self._create_rag_group()
        main_layout.addWidget(rag_group)

        # Группа 3: Управление токенами и сжатие
        compression_group = self._create_compression_group()
        main_layout.addWidget(compression_group)

        # Группа 4: Резервное копирование
        backup_group = self._create_backup_group()
        main_layout.addWidget(backup_group)

        main_layout.addStretch()

        # Кнопки действий
        actions_layout = QHBoxLayout()
        actions_layout.addStretch()

        reset_btn = QPushButton("🔄 Reset to Default")
        reset_btn.clicked.connect(self._reset_to_default)
        actions_layout.addWidget(reset_btn)

        apply_btn = QPushButton("💾 Apply Changes")
        apply_btn.clicked.connect(self._apply_changes)
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        actions_layout.addWidget(apply_btn)

        main_layout.addLayout(actions_layout)

    def _create_storage_group(self) -> QGroupBox:
        """Создание группы настроек хранилища"""
        group = QGroupBox("📦 Storage Settings")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Тип хранилища
        self.storage_type_combo = QComboBox()
        self.storage_type_combo.addItems(["json", "sqlite", "postgresql"])
        self.storage_type_combo.setToolTip(
            "Type of storage for memory data:\n"
            "- json: Simple file-based storage (default, easy to backup)\n"
            "- sqlite: Database format (better for large datasets)\n"
            "- postgresql: External database (for advanced setups)"
        )
        self.storage_type_combo.currentTextChanged.connect(
            lambda v: self._update_config("memory.storage_type", v)
        )
        layout.addRow("Storage Type:", self.storage_type_combo)

        # Путь к базе данных
        db_path_layout = QHBoxLayout()
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setPlaceholderText("memory.db")
        self.db_path_edit.setToolTip(
            "Path to the memory database file.\n"
            "Click the folder button to browse and select a location."
        )
        self.db_path_edit.textChanged.connect(
            lambda v: self._update_config("memory.db_path", v)
        )
        db_path_layout.addWidget(self.db_path_edit)

        db_browse_btn = QPushButton("📂")
        db_browse_btn.setFixedWidth(40)
        db_browse_btn.setToolTip("Browse for database file location")
        db_browse_btn.clicked.connect(self._browse_db_path)
        db_path_layout.addWidget(db_browse_btn)

        layout.addRow("Database Path:", db_path_layout)

        # Долгосрочная память
        self.long_term_check = QCheckBox("Enable Long-Term Memory")
        self.long_term_check.setToolTip(
            "Enable persistent long-term memory storage.\n"
            "When disabled, only short-term session memory is used.\n"
            "Disabling this will reduce disk usage but limit memory capabilities."
        )
        self.long_term_check.stateChanged.connect(
            lambda v: self._update_config("memory.long_term_enabled", v == 2)
        )
        layout.addRow("", self.long_term_check)

        # Лимит краткосрочной памяти
        self.short_term_spin = QSpinBox()
        self.short_term_spin.setRange(10, 1000)
        self.short_term_spin.setValue(100)
        self.short_term_spin.setSuffix(" items")
        self.short_term_spin.setToolTip(
            "Maximum number of items in short-term (session) memory.\n"
            "Range: 10-1000 items.\n"
            "Higher values = more context but increased memory usage.\n"
            "Recommended: 100 for normal use, 500+ for complex tasks."
        )
        self.short_term_spin.valueChanged.connect(
            lambda v: self._update_config("memory.short_term_limit", v)
        )
        layout.addRow("Short-Term Limit:", self.short_term_spin)

        # Триггер суммаризации
        self.summary_trigger_spin = QSpinBox()
        self.summary_trigger_spin.setRange(10, 200)
        self.summary_trigger_spin.setValue(50)
        self.summary_trigger_spin.setSuffix(" interactions")
        self.summary_trigger_spin.setToolTip(
            "Number of interactions before triggering memory summarization.\n"
            "Range: 10-200 interactions.\n"
            "Lower values = more frequent compression (saves tokens).\n"
            "Higher values = more detailed history (uses more tokens).\n"
            "Recommended: 50 for balanced operation."
        )
        self.summary_trigger_spin.valueChanged.connect(
            lambda v: self._update_config("memory.summary_trigger", v)
        )
        layout.addRow("Summary Trigger:", self.summary_trigger_spin)

        return group

    def _create_rag_group(self) -> QGroupBox:
        """Создание группы настроек RAG"""
        group = QGroupBox("🧠 RAG (Retrieval-Augmented Generation)")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Включение RAG
        self.rag_check = QCheckBox("Enable RAG")
        self.rag_check.setToolTip(
            "Enable Retrieval-Augmented Generation for memory queries.\n"
            "RAG allows the AI to search your memory for relevant context\n"
            "before responding. Improves response relevance but uses more tokens."
        )
        self.rag_check.stateChanged.connect(
            lambda v: self._update_config("memory.rag_enabled", v == 2)
        )
        layout.addRow("", self.rag_check)

        # Путь к векторному хранилищу
        vector_path_layout = QHBoxLayout()
        self.vector_store_edit = QLineEdit()
        self.vector_store_edit.setPlaceholderText("vector_store")
        self.vector_store_edit.setToolTip(
            "Path to the vector embeddings store directory.\n"
            "This is where semantic search vectors are stored for RAG."
        )
        self.vector_store_edit.textChanged.connect(
            lambda v: self._update_config("memory.vector_store_path", v)
        )
        vector_path_layout.addWidget(self.vector_store_edit)

        vector_browse_btn = QPushButton("📂")
        vector_browse_btn.setFixedWidth(40)
        vector_browse_btn.setToolTip("Browse for vector store directory")
        vector_browse_btn.clicked.connect(self._browse_vector_store)
        vector_path_layout.addWidget(vector_browse_btn)

        layout.addRow("Vector Store Path:", vector_path_layout)

        # Модель эмбеддингов
        self.embedding_combo = QComboBox()
        self.embedding_combo.addItems([
            "text-embedding-3-small",
            "text-embedding-3-large",
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
        ])
        self.embedding_combo.setToolTip(
            "Model for generating text embeddings (vector representations).\n"
            "- text-embedding-3-small: Fast, cheap, good accuracy (recommended)\n"
            "- text-embedding-3-large: Best accuracy, higher cost\n"
            "- all-MiniLM-L6-v2: Local model, no API needed\n"
            "- all-mpnet-base-v2: Local model, better quality"
        )
        self.embedding_combo.currentTextChanged.connect(
            lambda v: self._update_config("memory.embedding_model", v)
        )
        layout.addRow("Embedding Model:", self.embedding_combo)

        # Порог релевантности
        self.relevance_spin = QDoubleSpinBox()
        self.relevance_spin.setRange(0.0, 1.0)
        self.relevance_spin.setValue(0.7)
        self.relevance_spin.setDecimals(2)
        self.relevance_spin.setSingleStep(0.05)
        self.relevance_spin.setToolTip(
            "Minimum relevance score for memory retrieval results.\n"
            "Range: 0.0-1.0\n"
            "Higher = only very relevant memories (fewer results).\n"
            "Lower = more memories included (may include irrelevant).\n"
            "Recommended: 0.7 for balanced precision/recall."
        )
        self.relevance_spin.valueChanged.connect(
            lambda v: self._update_config("memory.relevance_threshold", v)
        )
        layout.addRow("Relevance Threshold:", self.relevance_spin)

        # Максимум элементов памяти
        self.max_memory_spin = QSpinBox()
        self.max_memory_spin.setRange(100, 100000)
        self.max_memory_spin.setValue(10000)
        self.max_memory_spin.setSuffix(" items")
        self.max_memory_spin.setToolTip(
            "Maximum total number of memory items to store.\n"
            "Range: 100-100,000 items.\n"
            "When limit is reached, oldest/least relevant items are removed.\n"
            "Higher values = more history but more disk space."
        )
        self.max_memory_spin.valueChanged.connect(
            lambda v: self._update_config("memory.max_memory_items", v)
        )
        layout.addRow("Max Memory Items:", self.max_memory_spin)

        # Порог забывания
        self.forget_spin = QDoubleSpinBox()
        self.forget_spin.setRange(0.0, 1.0)
        self.forget_spin.setValue(0.3)
        self.forget_spin.setDecimals(2)
        self.forget_spin.setSingleStep(0.05)
        self.forget_spin.setToolTip(
            "Threshold for automatic memory forgetting.\n"
            "Range: 0.0-1.0\n"
            "Memories with relevance below this threshold are candidates\n"
            "for removal when storage limit is reached.\n"
            "Higher = more aggressive forgetting."
        )
        self.forget_spin.valueChanged.connect(
            lambda v: self._update_config("memory.forget_threshold", v)
        )
        layout.addRow("Forget Threshold:", self.forget_spin)

        return group

    def _create_compression_group(self) -> QGroupBox:
        """Создание группы настроек сжатия"""
        group = QGroupBox("🗜️ Compression & Tokens")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Прогресс-бар использования токенов
        token_layout = QHBoxLayout()
        token_label = QLabel("Token Usage:")
        token_label.setFixedWidth(100)
        self.token_progress = QProgressBar()
        self.token_progress.setRange(0, 128000)
        self.token_progress.setValue(0)
        self.token_progress.setFormat("%v / %m tokens")
        self.token_progress.setToolTip(
            "Visual indicator of current token usage vs maximum limit.\n"
            "Maximum is typically 128,000 tokens for most models.\n"
            "When usage approaches the limit, compression is triggered."
        )
        token_layout.addWidget(token_label)
        token_layout.addWidget(self.token_progress)

        layout.addLayout(token_layout)

        # Счётчик токенов
        token_count_layout = QHBoxLayout()
        self.token_count_label = QLabel("Current: 0 tokens")
        self.token_count_label.setToolTip(
            "Exact count of tokens currently in use for memory context.\n"
            "This number updates in real-time as memories are added/removed."
        )
        token_count_layout.addWidget(self.token_count_label)
        token_count_layout.addStretch()
        layout.addLayout(token_count_layout)

        # Коэффициент сжатия
        compression_layout = QFormLayout()
        self.compression_spin = QDoubleSpinBox()
        self.compression_spin.setRange(0.1, 0.9)
        self.compression_spin.setValue(0.5)
        self.compression_spin.setDecimals(2)
        self.compression_spin.setSingleStep(0.05)
        self.compression_spin.setToolTip(
            "Target compression ratio when summarizing memory.\n"
            "Range: 0.1-0.9\n"
            "0.1 = aggressive compression (90% reduction, less detail).\n"
            "0.9 = light compression (10% reduction, more detail).\n"
            "Recommended: 0.5 for balanced compression."
        )
        self.compression_spin.valueChanged.connect(
            lambda v: self._update_config("memory.compression_ratio", v)
        )
        compression_layout.addRow("Compression Ratio:", self.compression_spin)

        layout.addLayout(compression_layout)

        # Кнопка ручного сжатия
        compress_btn = QPushButton("🗑️ Compress Now")
        compress_btn.setToolTip(
            "Manually trigger memory compression/summarization.\n"
            "This will summarize old memories to reduce token usage.\n"
            "Use this if you want to free up tokens immediately."
        )
        compress_btn.clicked.connect(self._manual_compress)
        layout.addWidget(compress_btn)

        return group

    def _create_backup_group(self) -> QGroupBox:
        """Создание группы настроек резервного копирования"""
        group = QGroupBox("💾 Backup Settings")
        layout = QFormLayout(group)
        layout.setSpacing(10)

        # Автрезервное копирование
        self.auto_backup_check = QCheckBox("Enable Auto Backup")
        self.auto_backup_check.setToolTip(
            "Automatically create backup copies of memory data.\n"
            "Backups are created at the specified interval.\n"
            "Recommended to keep this enabled for data safety."
        )
        self.auto_backup_check.stateChanged.connect(
            lambda v: self._update_config("memory.auto_backup", v == 2)
        )
        layout.addRow("", self.auto_backup_check)

        # Интервал резервирования
        self.backup_interval_spin = QSpinBox()
        self.backup_interval_spin.setRange(300, 86400)
        self.backup_interval_spin.setValue(3600)
        self.backup_interval_spin.setSuffix(" seconds")
        self.backup_interval_spin.setToolTip(
            "Time interval between automatic backups.\n"
            "Range: 300-86,400 seconds (5 minutes to 24 hours).\n"
            "Recommended: 3600 (1 hour) for regular backups\n"
            "without excessive disk writes."
        )
        self.backup_interval_spin.valueChanged.connect(
            lambda v: self._update_config("memory.backup_interval", v)
        )
        layout.addRow("Backup Interval:", self.backup_interval_spin)

        # Кнопки управления бэкапами
        backup_buttons = QHBoxLayout()

        backup_now_btn = QPushButton("💾 Backup Now")
        backup_now_btn.setToolTip(
            "Create an immediate backup of current memory data.\n"
            "Backup file will be saved to the configured location."
        )
        backup_now_btn.clicked.connect(self._backup_now)
        backup_buttons.addWidget(backup_now_btn)

        restore_btn = QPushButton("↩️ Restore")
        restore_btn.setToolTip(
            "Restore memory data from the latest backup.\n"
            "WARNING: This will overwrite current memory data!"
        )
        restore_btn.clicked.connect(self._restore_backup)
        backup_buttons.addWidget(restore_btn)

        layout.addRow("", backup_buttons)

        # Группа импорта/экспорта и очистки
        io_group = QGroupBox("📤 Import/Export & Cleanup")
        io_layout = QHBoxLayout(io_group)

        import_btn = QPushButton("📥 Import DB")
        import_btn.setToolTip(
            "Import memory database from an external file.\n"
            "Supported formats: .db, .sqlite, .json\n"
            "WARNING: This will overwrite current memory data!"
        )
        import_btn.clicked.connect(self._import_database)
        io_layout.addWidget(import_btn)

        export_btn = QPushButton("📤 Export DB")
        export_btn.setToolTip(
            "Export current memory database to a file.\n"
            "Useful for backup, migration, or analysis.\n"
            "Supported formats: .db, .sqlite, .json"
        )
        export_btn.clicked.connect(self._export_database)
        io_layout.addWidget(export_btn)

        clear_btn = QPushButton("🗑️ Clear Memory")
        clear_btn.setToolTip(
            "Permanently delete all stored memories.\n"
            "This action cannot be undone!\n"
            "A confirmation dialog will appear before deletion."
        )
        clear_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        clear_btn.clicked.connect(self._clear_memory)
        io_layout.addWidget(clear_btn)

        layout.addRow("", io_group)

        return group

    def _update_config(self, key: str, value: object):
        """Update config and emit signal"""
        if self.config_manager:
            self.config_manager.set(key, value)
        self.config_changed.emit(key, value)

    def _load_config(self):
        """Загрузка текущей конфигурации"""
        if not self.config_manager:
            return

        # Storage settings
        self.storage_type_combo.setCurrentText(
            self.config_manager.get("memory.storage_type", "json")
        )
        self.db_path_edit.setText(
            self.config_manager.get("memory.db_path", "memory.db")
        )
        self.long_term_check.setChecked(
            self.config_manager.get("memory.long_term_enabled", True)
        )
        self.short_term_spin.setValue(
            self.config_manager.get("memory.short_term_limit", 100)
        )
        self.summary_trigger_spin.setValue(
            self.config_manager.get("memory.summary_trigger", 50)
        )

        # RAG settings
        self.rag_check.setChecked(
            self.config_manager.get("memory.rag_enabled", True)
        )
        self.vector_store_edit.setText(
            self.config_manager.get("memory.vector_store_path", "vector_store")
        )
        self.embedding_combo.setCurrentText(
            self.config_manager.get("memory.embedding_model", "text-embedding-3-small")
        )
        self.relevance_spin.setValue(
            self.config_manager.get("memory.relevance_threshold", 0.7)
        )
        self.max_memory_spin.setValue(
            self.config_manager.get("memory.max_memory_items", 10000)
        )
        self.forget_spin.setValue(
            self.config_manager.get("memory.forget_threshold", 0.3)
        )

        # Compression settings
        self.compression_spin.setValue(
            self.config_manager.get("memory.compression_ratio", 0.5)
        )

        # Backup settings
        self.auto_backup_check.setChecked(
            self.config_manager.get("memory.auto_backup", True)
        )
        self.backup_interval_spin.setValue(
            self.config_manager.get("memory.backup_interval", 3600)
        )
        
        # Update token counter if context manager is available
        if self.context_manager:
            count = len(self.context_manager.history) * 50
            self.update_token_counter(count)

    def _apply_changes(self):
        """Применение изменений"""
        if self.config_manager:
            self.config_manager.save()

    def _reset_to_default(self):
        """Сброс к настройкам по умолчанию"""
        if self.config_manager:
            self.config_manager.reset_section("memory")
            self._load_config()

    def _browse_db_path(self):
        """Выбор пути к базе данных"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Select Database Path",
            "memory.db",
            "Database Files (*.db *.sqlite *.json);;All Files (*)",
        )
        if file_path:
            self.db_path_edit.setText(file_path)
            self._update_config("memory.db_path", file_path)

    def _browse_vector_store(self):
        """Выбор пути к векторному хранилищу"""
        dir_path = QFileDialog.getExistingDirectory(
            self,
            "Select Vector Store Directory",
            "vector_store",
        )
        if dir_path:
            self.vector_store_edit.setText(dir_path)
            self._update_config("memory.vector_store_path", dir_path)

    def _manual_compress(self):
        """Ручное сжатие памяти"""
        if self.context_manager:
            asyncio.create_task(self.context_manager.summarize_now())
            QMessageBox.information(self, "Memory", "Summarization task started in background.")

    def _backup_now(self):
        """Немедленное резервное копирование"""
        if self.context_manager:
            self.context_manager.save_history()
            QMessageBox.information(self, "Memory", "Memory state saved to disk.")

    def _restore_backup(self):
        """Восстановление из резервной копии"""
        if self.context_manager:
            self.context_manager.load_history()
            self._load_config()
            QMessageBox.information(self, "Memory", "Memory state reloaded from disk.")

    def _import_database(self):
        """Импорт базы данных из файла"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Import Database",
            "",
            "Database Files (*.db *.sqlite *.json);;All Files (*)",
        )
        if file_path and self.context_manager:
             self.context_manager.memory_file = Path(file_path)
             self.context_manager.load_history()
             self._load_config()

    def _export_database(self):
        """Экспорт базы данных в файл"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Database",
            "memory_export.db",
            "Database Files (*.db *.sqlite *.json);;All Files (*)",
        )
        if file_path and self.context_manager:
            old_path = self.context_manager.memory_file
            self.context_manager.memory_file = Path(file_path)
            self.context_manager.save_history()
            self.context_manager.memory_file = old_path

    def _clear_memory(self):
        """Очистка всей памяти"""
        reply = QMessageBox.question(
            self,
            "Clear Memory",
            "Are you sure you want to clear all memory? This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if reply == QMessageBox.StandardButton.Yes:
            if self.context_manager:
                self.context_manager.clear_history()
                self.context_manager.rag.clear()
                self._load_config()
                QMessageBox.information(self, "Memory", "Memory cleared successfully.")

    def update_token_counter(self, current: int, limit: int = 128000):
        """Обновление счётчика токенов"""
        self.token_progress.setRange(0, limit)
        self.token_progress.setValue(current)
        self.token_count_label.setText(f"Current: {current:,} tokens (estimate)")

# Alias for backward compatibility
MemorySettingsTab = MemoryTab

if __name__ == "__main__":
    from PyQt6.QtWidgets import QApplication
    from core.config import ConfigManager

    app = QApplication(sys.argv)

    config_manager = ConfigManager("config.yaml")

    window = QWidget()
    window.setWindowTitle("Memory Settings Tab Test")
    window.resize(600, 800)

    layout = QVBoxLayout(window)
    tab = MemoryTab(config_manager=config_manager)
    layout.addWidget(tab)

    window.show()
    sys.exit(app.exec())
