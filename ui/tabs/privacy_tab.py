"""
Privacy Settings Tab (Tab 7)
Реализация вкладки настроек приватности и безопасности для Svetka AI
"""
import sys
import ctypes
from ctypes import wintypes
from typing import List, Dict, Any
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QListView,
    QListWidget,
    QListWidgetItem,
    QPushButton,
    QCheckBox,
    QGroupBox,
    QFrame,
    QStatusBar,
    QSpacerItem,
    QSizePolicy,
    QComboBox,
    QSpinBox,
    QTextEdit,
    QTableView,
    QMessageBox,
    QFileDialog,
    QDialog,
    QDialogButtonBox,
    QInputDialog,
)
from PyQt6.QtGui import QFont, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QThread
from datetime import datetime


# === Win32 API функции для работы с окнами ===
class WindowEnumerationHandler:
    """Обработчик для перечисления окон"""
    def __init__(self):
        self.windows = []

    def __call__(self, hwnd, lparam):
        if ctypes.windll.user32.IsWindowVisible(hwnd):
            length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
            if length > 0:
                buf = ctypes.create_unicode_buffer(length + 1)
                ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
                title = buf.value
                
                # Получаем имя процесса
                pid = wintypes.DWORD()
                ctypes.windll.user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                
                self.windows.append((hwnd, title, pid.value))
        return True


def get_active_window_title():
    """Получение заголовка активного окна через Win32 API"""
    try:
        hwnd = ctypes.windll.user32.GetForegroundWindow()
        length = ctypes.windll.user32.GetWindowTextLengthW(hwnd)
        if length > 0:
            buf = ctypes.create_unicode_buffer(length + 1)
            ctypes.windll.user32.GetWindowTextW(hwnd, buf, length + 1)
            return buf.value
    except Exception as e:
        print(f"[PrivacyTab] Error getting active window: {e}")
    return None


def get_all_visible_windows() -> List[Dict[str, Any]]:
    """Получение списка всех видимых окон"""
    handler = WindowEnumerationHandler()
    ctypes.windll.user32.EnumWindows(handler, 0)
    
    windows = []
    for hwnd, title, pid in handler.windows:
        # Получаем имя процесса по PID
        process_name = get_process_name_by_pid(pid)
        windows.append({
            "hwnd": hwnd,
            "title": title,
            "pid": pid,
            "process_name": process_name
        })
    
    return windows


def get_process_name_by_pid(pid: int) -> str:
    """Получение имени процесса по PID"""
    try:
        from ctypes import windll, wintypes, Structure, c_void_p, POINTER, byref
        
        class PROCESSENTRY32(Structure):
            _fields_ = [
                ('dwSize', wintypes.DWORD),
                ('cntUsage', wintypes.DWORD),
                ('th32ProcessID', wintypes.DWORD),
                ('th32DefaultHeapID', POINTER(wintypes.LONG)),
                ('th32ModuleID', wintypes.DWORD),
                ('cntThreads', wintypes.DWORD),
                ('th32ParentProcessID', wintypes.DWORD),
                ('pcPriClassBase', wintypes.LONG),
                ('dwFlags', wintypes.DWORD),
                ('szExeFile', wintypes.CHAR * 260)
            ]
        
        h_snapshot = windll.kernel32.CreateToolhelp32Snapshot(
            0x00000002,  # TH32CS_SNAPPROCESS
            0
        )
        
        if h_snapshot == -1:
            return "unknown"
        
        pe32 = PROCESSENTRY32()
        pe32.dwSize = ctypes.sizeof(PROCESSENTRY32)
        
        if not windll.kernel32.Process32First(h_snapshot, byref(pe32)):
            windll.kernel32.CloseHandle(h_snapshot)
            return "unknown"
        
        while True:
            if pe32.th32ProcessID == pid:
                process_name = pe32.szExeFile.decode('utf-8', errors='ignore')
                windll.kernel32.CloseHandle(h_snapshot)
                return process_name
            
            if not windll.kernel32.Process32Next(h_snapshot, byref(pe32)):
                break
        
        windll.kernel32.CloseHandle(h_snapshot)
        return "unknown"
    
    except Exception as e:
        print(f"[PrivacyTab] Error getting process name: {e}")
        return "unknown"


class PrivacyTab(QWidget):
    """Вкладка настроек Privacy с полной интеграцией ConfigManager и Guide Engine"""

    # Сигналы для уведомления об изменениях
    config_changed = pyqtSignal(str, object)
    blacklist_updated = pyqtSignal(list)
    offline_mode_changed = pyqtSignal(bool)
    data_wipe_requested = pyqtSignal()

    def __init__(self, config_manager=None, guide_manager=None, context_manager=None, parent=None):
        super().__init__(parent)
        self.config_manager = config_manager
        self.guide_manager = guide_manager
        self.context_manager = context_manager
        self.blacklist: List[str] = []
        self.log_history: List[Dict] = []

        self._init_ui()
        self._load_config()
        self._refresh_blacklist()

    def _init_ui(self):
        """Инициализация UI компонентов вкладки"""
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)

        # === Header секция ===
        header_layout = QHBoxLayout()
        header_label = QLabel("🔒 Privacy & Security")
        header_label.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_layout.addWidget(header_label)
        header_layout.addStretch()

        # Guide button (если есть guide_manager)
        if self.guide_manager:
            from ui.guide_widget import GuideWidget
            self.guide_widget = GuideWidget("privacy", self.guide_manager)
            header_layout.addWidget(self.guide_widget)

        main_layout.addLayout(header_layout)

        # === Основная сетка настроек ===
        settings_frame = QFrame()
        settings_frame.setObjectName("settingsFrame")
        settings_layout = QVBoxLayout(settings_frame)
        settings_layout.setSpacing(12)

        # 1. Группа: Фильтрация приложений (Blacklist)
        blacklist_group = self._create_blacklist_group()
        settings_layout.addWidget(blacklist_group)

        # 2. Группа: Маскирование и Offline режим
        masking_group = self._create_masking_group()
        settings_layout.addWidget(masking_group)

        # 3. Группа: Аудит и удаление данных
        audit_group = self._create_audit_group()
        settings_layout.addWidget(audit_group)

        main_layout.addWidget(settings_frame)

        # === Статус-бар модуля ===
        self.status_bar = QStatusBar()
        self.status_bar.setSizeGripEnabled(False)
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #2b2b2b;
                border: 1px solid #3c3c3c;
                border-radius: 4px;
                padding: 4px;
            }
            QLabel {
                color: #4ec9b0;
                font-size: 12px;
            }
        """)
        self.status_label = QLabel("🟢 Privacy Module: Ready")
        self.status_bar.addWidget(self.status_label)
        main_layout.addWidget(self.status_bar)

        # Spacer
        main_layout.addStretch()

    def _create_blacklist_group(self) -> QGroupBox:
        """Группа 1: Фильтрация приложений (Blacklist)"""
        group = QGroupBox("🚫 Blacklist - Игнорируемые приложения")
        layout = QVBoxLayout(group)
        layout.setSpacing(10)

        # Описание
        desc_label = QLabel(
            "Приложения из чёрного списка будут игнорироваться при захвате экрана и аудио. "
            "Svetka не будет анализировать содержимое этих окон."
        )
        desc_label.setWordWrap(True)
        desc_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(desc_label)

        # Список игнорируемых окон
        list_layout = QHBoxLayout()
        
        self.blacklist_widget = QListWidget()
        self.blacklist_widget.setSelectionMode(
            QListWidget.SelectionMode.ExtendedSelection
        )
        self.blacklist_widget.setToolTip(
            "Список окон/процессов, которые будут игнорироваться. "
            "Выделите элемент и нажмите 'Удалить' для удаления из списка."
        )
        self.blacklist_widget.setMinimumHeight(150)
        list_layout.addWidget(self.blacklist_widget, 1)

        # Кнопки управления
        buttons_layout = QVBoxLayout()
        
        self.add_active_btn = QPushButton("➕ Добавить активное окно")
        self.add_active_btn.setToolTip(
            "Добавить текущее активное окно в чёрный список. "
            "Используется Win32 API для получения заголовка окна."
        )
        self.add_active_btn.clicked.connect(self._add_active_window)
        buttons_layout.addWidget(self.add_active_btn)
        
        self.add_custom_btn = QPushButton("➕ Добавить вручную")
        self.add_custom_btn.setToolTip(
            "Добавить название окна или процесса вручную."
        )
        self.add_custom_btn.clicked.connect(self._add_custom_window)
        buttons_layout.addWidget(self.add_custom_btn)
        
        self.remove_btn = QPushButton("➖ Удалить выбранное")
        self.remove_btn.setToolTip(
            "Удалить выбранные элементы из чёрного списка."
        )
        self.remove_btn.clicked.connect(self._remove_selected)
        buttons_layout.addWidget(self.remove_btn)
        
        buttons_layout.addStretch()
        list_layout.addLayout(buttons_layout)

        layout.addLayout(list_layout)

        # Статистика
        self.blacklist_count_label = QLabel("В чёрном списке: 0 окон")
        self.blacklist_count_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(self.blacklist_count_label)

        return group

    def _create_masking_group(self) -> QGroupBox:
        """Группа 2: Маскирование и Offline режим"""
        group = QGroupBox("🎭 Маскирование и Режимы доступа")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Offline-Only Mode
        offline_layout = QHBoxLayout()
        self.offline_check = QCheckBox("🔌 Offline-Only Mode (Полная автономность)")
        self.offline_check.setToolTip(
            "В этом режиме Svetka работает полностью автономно. "
            "Все сетевые запросы к API блокируются. Данные не покидают ваше устройство."
        )
        self.offline_check.stateChanged.connect(self._on_offline_mode_changed)
        offline_layout.addWidget(self.offline_check)
        offline_layout.addStretch()
        layout.addLayout(offline_layout)

        offline_desc = QLabel(
            "⚠️ Внимание: В режиме Offline-Only все функции, требующие подключения к интернету, "
            "будут отключены (AI-ответы, облачная синхронизация, обновления)."
        )
        offline_desc.setWordWrap(True)
        offline_desc.setStyleSheet("color: #cc8800; font-size: 11px;")
        layout.addWidget(offline_desc)

        # Маскирование чувствительных данных
        mask_layout = QHBoxLayout()
        self.mask_sensitive_check = QCheckBox("🎭 Маскировать чувствительные данные")
        self.mask_sensitive_check.setToolTip(
            "Автоматическое обнаружение и маскирование паролей, номеров карт, "
            "социальных номеров и других чувствительных данных."
        )
        self.mask_sensitive_check.stateChanged.connect(self._on_mask_sensitive_changed)
        mask_layout.addWidget(self.mask_sensitive_check)
        mask_layout.addStretch()
        layout.addLayout(mask_layout)

        # Настройка паттернов
        patterns_label = QLabel("Паттерны чувствительных данных:")
        patterns_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(patterns_label)
        
        self.patterns_edit = QTextEdit()
        self.patterns_edit.setPlaceholderText(
            "password\ncredit_card\nssn\napi_key\nsecret"
        )
        self.patterns_edit.setMaximumHeight(80)
        self.patterns_edit.setToolTip(
            "Список паттернов (ключевых слов) для поиска чувствительных данных. "
            "Каждый паттерн с новой строки."
        )
        self.patterns_edit.textChanged.connect(self._on_patterns_changed)
        layout.addWidget(self.patterns_edit)

        return group

    def _create_audit_group(self) -> QGroupBox:
        """Группа 3: Аудит и удаление данных"""
        group = QGroupBox("📊 Аудит и Управление данными")
        layout = QVBoxLayout(group)
        layout.setSpacing(15)

        # Журнал передачи данных
        log_label = QLabel("📜 Журнал передачи данных:")
        log_label.setStyleSheet("color: #888; font-size: 11px;")
        layout.addWidget(log_label)

        self.log_table = QTableView()
        self.log_model = QStandardItemModel(0, 4)
        self.log_model.setHorizontalHeaderLabels([
            "Время", "Тип", "Объём", "Статус"
        ])
        self.log_table.setModel(self.log_model)
        self.log_table.setMinimumHeight(150)
        self.log_table.setToolTip(
            "Журнал всех операций передачи данных. "
            "Показывает время, тип операции, объём данных и статус."
        )
        layout.addWidget(self.log_table)

        # Кнопки управления данными
        buttons_layout = QHBoxLayout()
        
        self.export_log_btn = QPushButton("📤 Экспорт журнала")
        self.export_log_btn.setToolTip(
            "Экспортировать журнал передачи данных в CSV файл."
        )
        self.export_log_btn.clicked.connect(self._export_log)
        buttons_layout.addWidget(self.export_log_btn)
        
        self.clear_log_btn = QPushButton("🗑️ Очистить журнал")
        self.clear_log_btn.setToolTip(
            "Очистить журнал передачи данных без удаления основных данных."
        )
        self.clear_log_btn.clicked.connect(self._clear_log)
        buttons_layout.addWidget(self.clear_log_btn)
        
        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        # Разделитель
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: #3c3c3c;")
        layout.addWidget(line)

        # Кнопка полной очистки (Wipe)
        wipe_layout = QHBoxLayout()
        
        wipe_info = QLabel(
            "⚠️ Полная очистка данных удалит всю историю, кэш, настройки и логи. "
            "Это действие необратимо!"
        )
        wipe_info.setWordWrap(True)
        wipe_info.setStyleSheet("color: #cc4444; font-size: 11px;")
        wipe_layout.addWidget(wipe_info, 1)
        
        self.wipe_data_btn = QPushButton("🔥 Очистка данных (Wipe)")
        self.wipe_data_btn.setStyleSheet(
            "QPushButton { background-color: #cc4444; color: white; font-weight: bold; }"
            "QPushButton:hover { background-color: #ee6666; }"
        )
        self.wipe_data_btn.setToolTip(
            "Полная очистка всех данных Svetka: история, кэш, логи, настройки. "
            "Требует подтверждения."
        )
        self.wipe_data_btn.clicked.connect(self._wipe_data)
        wipe_layout.addWidget(self.wipe_data_btn)
        
        layout.addLayout(wipe_layout)

        return group

    def _load_config(self):
        """Загрузка настроек из ConfigManager"""
        if not self.config_manager:
            return

        try:
            privacy = self.config_manager.config["privacy"]
            privacy_dict = privacy._section.model_dump()

            # Blacklist
            self.blacklist = privacy_dict.get("blacklist", [])

            # Offline mode
            offline_mode = privacy_dict.get("offline_only", False)
            self.offline_check.setChecked(offline_mode)

            # Mask sensitive data
            mask_sensitive = privacy_dict.get("mask_sensitive_data", True)
            self.mask_sensitive_check.setChecked(mask_sensitive)

            # Sensitive patterns
            patterns = privacy_dict.get("sensitive_patterns", ["password", "credit_card", "ssn"])
            self.patterns_edit.setText("\n".join(patterns))

            # Data retention
            retention_days = privacy_dict.get("data_retention_days", 30)
            if hasattr(self, 'retention_spin'):
                self.retention_spin.setValue(retention_days)

            self._update_blacklist_ui()
            self._update_status("Настройки загружены")

        except Exception as e:
            print(f"[PrivacyTab] Error loading config: {e}")

    def _save_config(self, key: str, value: Any):
        """Сохранение настройки в ConfigManager"""
        if not self.config_manager:
            return
        
        try:
            self.config_manager.update_and_notify(f"privacy.{key}", value)
            self._update_status(f"{key}: сохранено")
        except Exception as e:
            print(f"[PrivacyTab] Error saving config: {e}")

    def _refresh_blacklist(self):
        """Обновление списка игнорируемых окон"""
        self._update_blacklist_ui()
        self.blacklist_updated.emit(self.blacklist)

    def _update_blacklist_ui(self):
        """Обновление UI чёрного списка"""
        self.blacklist_widget.clear()
        for item in self.blacklist:
            self.blacklist_widget.addItem(item)
        
        count = len(self.blacklist)
        self.blacklist_count_label.setText(f"В чёрном списке: {count} окон")

    # === Обработчики событий: Blacklist ===

    def _add_active_window(self):
        """Добавление текущего активного окна в чёрный список"""
        window_title = get_active_window_title()
        
        if window_title:
            if window_title not in self.blacklist:
                self.blacklist.append(window_title)
                self._update_blacklist_ui()
                self._save_config("blacklist", self.blacklist)
                self._update_status(f"Добавлено: {window_title[:50]}")
            else:
                self._update_status("Окно уже в чёрном списке")
        else:
            self._update_status("Не удалось получить активное окно")

    def _add_custom_window(self):
        """Добавление окна вручную"""
        from PyQt6.QtWidgets import QInputDialog
        
        text, ok = QInputDialog.getText(
            self,
            "Добавить окно",
            "Введите название окна или процесса:"
        )
        
        if ok and text:
            if text not in self.blacklist:
                self.blacklist.append(text)
                self._update_blacklist_ui()
                self._save_config("blacklist", self.blacklist)
                self._update_status(f"Добавлено: {text}")
            else:
                self._update_status("Элемент уже в чёрном списке")

    def _remove_selected(self):
        """Удаление выбранных элементов из чёрного списка"""
        selected_items = self.blacklist_widget.selectedItems()
        
        if not selected_items:
            self._update_status("Ничего не выбрано")
            return
        
        for item in selected_items:
            text = item.text()
            if text in self.blacklist:
                self.blacklist.remove(text)
        
        self._update_blacklist_ui()
        self._save_config("blacklist", self.blacklist)
        self._update_status(f"Удалено элементов: {len(selected_items)}")

    # === Обработчики событий: Masking & Offline ===

    def _on_offline_mode_changed(self, state):
        """Изменение режима Offline-Only"""
        enabled = state == Qt.CheckState.Checked
        self.offline_mode_changed.emit(enabled)
        self._save_config("offline_only", enabled)
        
        if enabled:
            self._update_status("🔌 Offline-Only Mode: ВКЛЮЧЁН")
        else:
            self._update_status("🌐 Online Mode: ВКЛЮЧЁН")

    def _on_mask_sensitive_changed(self, state):
        """Изменение маскирования чувствительных данных"""
        enabled = state == Qt.CheckState.Checked
        self._save_config("mask_sensitive_data", enabled)
        self._update_status(f"Маскирование: {'ВКЛ' if enabled else 'ВЫКЛ'}")

    def _on_patterns_changed(self):
        """Изменение паттернов чувствительных данных"""
        text = self.patterns_edit.toPlainText()
        patterns = [p.strip() for p in text.split("\n") if p.strip()]
        self._save_config("sensitive_patterns", patterns)

    # === Обработчики событий: Audit & Wipe ===

    def _export_log(self):
        """Экспорт журнала в CSV"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Экспорт журнала",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write("Время,Тип,Объём,Статус\n")
                    for row in range(self.log_model.rowCount()):
                        row_data = []
                        for col in range(4):
                            item = self.log_model.item(row, col)
                            row_data.append(item.text() if item else "")
                        f.write(",".join(row_data) + "\n")
                
                self._update_status(f"Журнал экспортирован: {file_path}")
            except Exception as e:
                print(f"[PrivacyTab] Error exporting log: {e}")
                self._update_status("Ошибка экспорта")

    def _clear_log(self):
        """Очистка журнала"""
        reply = QMessageBox.question(
            self,
            "Очистка журнала",
            "Вы уверены, что хотите очистить журнал передачи данных?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.log_model.removeRows(0, self.log_model.rowCount())
            self.log_history.clear()
            self._update_status("Журнал очищен")

    def _wipe_data(self):
        """Полная очистка данных (Wipe)"""
        reply = QMessageBox.warning(
            self,
            "⚠️ Полная очистка данных",
            "ВНИМАНИЕ: Это действие необратимо удалит:\n\n"
            "- Всю историю переписки\n"
            "- Кэш и временные файлы\n"
            "- Журналы передачи данных\n"
            "- Пользовательские настройки\n\n"
            "Продолжить?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Запрос повторного подтверждения
            confirm_reply = QMessageBox.warning(
                self,
                "⚠️ Подтверждение",
                "ВЫ УВЕРЕНЫ? Это действие НЕВОЗМОЖНО отменить!",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if confirm_reply == QMessageBox.StandardButton.Yes:
                self.data_wipe_requested.emit()
                
                # Реализовать полную очистку через Core Manager
                if self.context_manager:
                    self.context_manager.full_wipe()
                
                # Очищаем UI
                self.blacklist.clear()
                self._update_blacklist_ui()
                self.log_model.removeRows(0, self.log_model.rowCount())
                self.log_history.clear()
                
                self._update_status("🔥 Данные очищены")
                QMessageBox.information(
                    self,
                    "Очистка завершена",
                    "Все данные Svetka были успешно удалены."
                )

    def _update_status(self, message: str):
        """Обновление статус-бара"""
        self.status_label.setText(f"🟢 {message}")
        QTimer.singleShot(3000, lambda: self.status_label.setText("🟢 Privacy Module: Ready"))

    def add_log_entry(self, entry_type: str, volume: str, status: str):
        """Добавление записи в журнал"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        row = self.log_model.rowCount()
        self.log_model.insertRow(row)
        
        self.log_model.setItem(row, 0, QStandardItem(timestamp))
        self.log_model.setItem(row, 1, QStandardItem(entry_type))
        self.log_model.setItem(row, 2, QStandardItem(volume))
        self.log_model.setItem(row, 3, QStandardItem(status))
        
        self.log_history.append({
            "timestamp": timestamp,
            "type": entry_type,
            "volume": volume,
            "status": status
        })

    def refresh(self):
        """Публичный метод для обновления вкладки"""
        self._load_config()
        self._refresh_blacklist()


# Экспорт для использования в main_window.py
__all__ = ["PrivacyTab"]
