"""
Tests for Memory Settings Tab (Tab 5)
"""

import sys
import pytest
from PyQt6.QtWidgets import QApplication, QSpinBox, QDoubleSpinBox, QComboBox, QCheckBox, QLineEdit, QProgressBar
from ui.tabs.memory_tab import MemorySettingsTab
from core.config import ConfigManager


@pytest.fixture
def app():
    """Create QApplication instance"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def config_manager(tmp_path):
    """Create ConfigManager with temporary config file"""
    config_file = tmp_path / "test_config.yaml"
    cm = ConfigManager(str(config_file))
    return cm


@pytest.fixture
def memory_tab(app, config_manager):
    """Create MemorySettingsTab instance"""
    tab = MemorySettingsTab(config_manager=config_manager)
    return tab


class TestMemorySettingsTabInit:
    """Tests for MemorySettingsTab initialization"""

    def test_tab_init(self, app, config_manager):
        """Test tab initializes correctly"""
        tab = MemorySettingsTab(config_manager=config_manager)
        assert tab is not None

    def test_storage_group_exists(self, memory_tab):
        """Test storage settings group exists"""
        storage_group = memory_tab.findChild(QSpinBox, "short_term_spin")
        assert storage_group is not None or hasattr(memory_tab, 'short_term_spin')

    def test_rag_group_exists(self, memory_tab):
        """Test RAG settings group exists"""
        rag_check = memory_tab.findChild(QCheckBox, "rag_check")
        assert rag_check is not None or hasattr(memory_tab, 'rag_check')

    def test_compression_group_exists(self, memory_tab):
        """Test compression settings group exists"""
        token_progress = memory_tab.findChild(QProgressBar, "token_progress")
        assert token_progress is not None or hasattr(memory_tab, 'token_progress')

    def test_backup_group_exists(self, memory_tab):
        """Test backup settings group exists"""
        auto_backup_check = memory_tab.findChild(QCheckBox, "auto_backup_check")
        assert auto_backup_check is not None or hasattr(memory_tab, 'auto_backup_check')


class TestStorageSettings:
    """Tests for storage settings UI elements"""

    def test_storage_type_combo(self, memory_tab):
        """Test storage type combo box exists and has correct options"""
        combo = memory_tab.storage_type_combo
        assert combo is not None
        assert combo.count() == 3
        assert combo.itemText(0) == "json"
        assert combo.itemText(1) == "sqlite"
        assert combo.itemText(2) == "postgresql"

    def test_db_path_edit(self, memory_tab):
        """Test database path edit exists"""
        edit = memory_tab.db_path_edit
        assert edit is not None
        assert edit.placeholderText() == "memory.db"

    def test_long_term_check(self, memory_tab):
        """Test long-term memory checkbox"""
        check = memory_tab.long_term_check
        assert check is not None
        assert check.text() == "Enable Long-Term Memory"

    def test_short_term_spin_range(self, memory_tab):
        """Test short-term limit spinbox range"""
        spin = memory_tab.short_term_spin
        assert spin.minimum() == 10
        assert spin.maximum() == 1000
        assert spin.value() == 100

    def test_summary_trigger_spin_range(self, memory_tab):
        """Test summary trigger spinbox range"""
        spin = memory_tab.summary_trigger_spin
        assert spin.minimum() == 10
        assert spin.maximum() == 200
        assert spin.value() == 50


class TestRAGSettings:
    """Tests for RAG settings UI elements"""

    def test_rag_check(self, memory_tab):
        """Test RAG checkbox"""
        check = memory_tab.rag_check
        assert check is not None
        assert check.text() == "Enable RAG"

    def test_vector_store_edit(self, memory_tab):
        """Test vector store path edit"""
        edit = memory_tab.vector_store_edit
        assert edit is not None
        assert edit.placeholderText() == "vector_store"

    def test_embedding_combo(self, memory_tab):
        """Test embedding model combo box"""
        combo = memory_tab.embedding_combo
        assert combo is not None
        assert combo.count() == 4
        expected_models = [
            "text-embedding-3-small",
            "text-embedding-3-large",
            "all-MiniLM-L6-v2",
            "all-mpnet-base-v2",
        ]
        for i, model in enumerate(expected_models):
            assert combo.itemText(i) == model

    def test_relevance_spin_range(self, memory_tab):
        """Test relevance threshold spinbox range"""
        spin = memory_tab.relevance_spin
        assert spin.minimum() == 0.0
        assert spin.maximum() == 1.0
        assert spin.value() == 0.7
        assert spin.decimals() == 2

    def test_max_memory_spin_range(self, memory_tab):
        """Test max memory items spinbox range"""
        spin = memory_tab.max_memory_spin
        assert spin.minimum() == 100
        assert spin.maximum() == 100000
        assert spin.value() == 10000

    def test_forget_spin_range(self, memory_tab):
        """Test forget threshold spinbox range"""
        spin = memory_tab.forget_spin
        assert spin.minimum() == 0.0
        assert spin.maximum() == 1.0
        assert spin.value() == 0.3


class TestCompressionSettings:
    """Tests for compression and token settings"""

    def test_token_progress(self, memory_tab):
        """Test token usage progress bar"""
        progress = memory_tab.token_progress
        assert progress is not None
        assert progress.minimum() == 0
        assert progress.maximum() == 128000

    def test_token_count_label(self, memory_tab):
        """Test token count label"""
        label = memory_tab.token_count_label
        assert label is not None
        assert "Current:" in label.text()

    def test_compression_spin_range(self, memory_tab):
        """Test compression ratio spinbox range"""
        spin = memory_tab.compression_spin
        assert spin.minimum() == 0.1
        assert spin.maximum() == 0.9
        assert spin.value() == 0.5


class TestBackupSettings:
    """Tests for backup settings"""

    def test_auto_backup_check(self, memory_tab):
        """Test auto backup checkbox"""
        check = memory_tab.auto_backup_check
        assert check is not None
        assert check.text() == "Enable Auto Backup"

    def test_backup_interval_spin_range(self, memory_tab):
        """Test backup interval spinbox range"""
        spin = memory_tab.backup_interval_spin
        assert spin.minimum() == 300
        assert spin.maximum() == 86400
        assert spin.value() == 3600


class TestConfigIntegration:
    """Tests for config manager integration"""

    def test_load_config(self, app, config_manager):
        """Test loading config from ConfigManager"""
        # Set custom values
        config_manager.set("memory.storage_type", "sqlite")
        config_manager.set("memory.short_term_limit", 200)
        config_manager.set("memory.rag_enabled", False)

        tab = MemorySettingsTab(config_manager=config_manager)

        assert tab.storage_type_combo.currentText() == "sqlite"
        assert tab.short_term_spin.value() == 200
        assert tab.rag_check.isChecked() == False

    def test_config_changed_signal(self, memory_tab, qtbot):
        """Test config_changed signal emission"""
        with qtbot.waitSignal(memory_tab.config_changed, timeout=1000) as blocker:
            memory_tab.storage_type_combo.setCurrentText("sqlite")

        assert blocker.args[0] == "memory.storage_type"
        assert blocker.args[1] == "sqlite"

    def test_update_token_counter(self, memory_tab):
        """Test token counter update"""
        memory_tab.update_token_counter(50000, 100000)

        assert memory_tab.token_progress.maximum() == 100000
        assert memory_tab.token_progress.value() == 50000
        assert "50,000" in memory_tab.token_count_label.text()


class TestUserActions:
    """Tests for user action handlers"""

    def test_reset_to_default(self, app, config_manager):
        """Test reset to default settings"""
        # Change some values
        tab = MemorySettingsTab(config_manager=config_manager)
        tab.short_term_spin.setValue(500)
        tab.rag_check.setChecked(False)

        # Reset
        tab._reset_to_default()

        # Values should be reset to defaults
        assert tab.short_term_spin.value() == 100
        assert tab.rag_check.isChecked() == True

    def test_apply_changes(self, memory_tab, tmp_path):
        """Test applying changes"""
        config_file = tmp_path / "test_config.yaml"
        config_manager = ConfigManager(str(config_file))
        tab = MemorySettingsTab(config_manager=config_manager)

        # Change value
        tab.short_term_spin.setValue(250)

        # Apply
        tab._apply_changes()

        # Reload and verify
        config_manager.load_config()
        assert config_manager.get("memory.short_term_limit") == 250

    def test_import_database(self, memory_tab):
        """Test import database method"""
        # Just test that method exists and doesn't crash
        # Actual file dialog testing requires GUI interaction
        assert hasattr(memory_tab, '_import_database')

    def test_export_database(self, memory_tab):
        """Test export database method"""
        assert hasattr(memory_tab, '_export_database')

    def test_clear_memory(self, memory_tab):
        """Test clear memory method"""
        assert hasattr(memory_tab, '_clear_memory')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
