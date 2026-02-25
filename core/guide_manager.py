import yaml
import re
from pathlib import Path
from typing import Dict, Optional, List, Any, Callable
from PyQt6.QtCore import QObject, pyqtSignal, QStringListModel
from PyQt6.QtWidgets import (
    QWidget,
    QLabel,
    QDialog,
    QVBoxLayout,
    QScrollArea,
    QTextBrowser,
    QPushButton,
)


class GuideData:
    def __init__(
        self,
        key: str,
        title: str,
        description: str,
        tooltip: str = "",
        inline: str = "",
        rich_text: str = "",
        trigger: str = "always",
    ):
        self.key = key
        self.title = title
        self.description = description
        self.tooltip = tooltip or description
        self.inline = inline or description
        self.rich_text = rich_text or description
        self.trigger = trigger

    @classmethod
    def from_dict(cls, key: str, data: Dict) -> "GuideData":
        return cls(
            key=key,
            title=data.get("title", ""),
            description=data.get("description", ""),
            tooltip=data.get("tooltip", ""),
            inline=data.get("inline", ""),
            rich_text=data.get("rich_text", ""),
            trigger=data.get("trigger", "always"),
        )


class GuideManager(QObject):
    guide_updated = pyqtSignal(str)
    guides_loaded = pyqtSignal()

    def __init__(self, config_path: str = "config.yaml"):
        super().__init__()
        self.config_path = Path(config_path)
        self._guides: Dict[str, GuideData] = {}
        self._triggers: Dict[str, Callable[[], bool]] = {}
        self._trigger_cache: Dict[str, bool] = {}
        self._widgets_bound: Dict[str, List[QWidget]] = {}
        self._load_guides()
        self._register_default_triggers()

    def _register_default_triggers(self):
        self.register_trigger("always", lambda: True)
        self.register_trigger("first_run", self._check_first_run)
        self.register_trigger("on_change", self._check_on_change)

    def _check_first_run(self) -> bool:
        import os

        marker = self.config_path.parent / ".first_run_done"
        return not marker.exists()

    def _check_on_change(self) -> bool:
        return True

    def register_trigger(self, trigger_name: str, condition: Callable[[], bool]):
        self._triggers[trigger_name] = condition

    def _load_guides(self):
        if not self.config_path.exists():
            return
        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)

            if not config:
                return

            self._extract_guides_from_config(config)
            self.guides_loaded.emit()
        except Exception as e:
            print(f"Error loading guides: {e}")

    def _extract_guides_from_config(self, config: Dict, prefix: str = ""):
        for key, value in config.items():
            full_key = f"{prefix}.{key}" if prefix else key

            if isinstance(value, dict):
                if "_guide" in value:
                    guide_info = value["_guide"]
                    if isinstance(guide_info, dict):
                        self._guides[full_key] = GuideData.from_dict(
                            full_key, guide_info
                        )
                else:
                    self._extract_guides_from_config(value, full_key)

    def reload_guides(self):
        self._guides.clear()
        self._load_guides()

    def get_guide(self, key: str) -> Optional[GuideData]:
        return self._guides.get(key)

    def get_tooltip(self, key: str) -> str:
        guide = self.get_guide(key)
        if guide:
            return self._format_tooltip(guide.tooltip)
        return ""

    def get_inline(self, key: str) -> str:
        guide = self.get_guide(key)
        return guide.inline if guide else ""

    def get_rich_text(self, key: str) -> str:
        guide = self.get_guide(key)
        return guide.rich_text if guide else ""

    def get_title(self, key: str) -> str:
        guide = self.get_guide(key)
        return guide.title if guide else ""

    def get_description(self, key: str) -> str:
        guide = self.get_guide(key)
        return guide.description if guide else ""

    def _format_tooltip(self, text: str) -> str:
        if not text:
            return ""
        formatted = text.replace("\n", "<br>")
        if len(formatted) > 200:
            formatted = f"<html><body>{formatted}</body></html>"
        return formatted

    def bind_to_widget(self, key: str, widget: QWidget, mode: str = "tooltip"):
        if key not in self._widgets_bound:
            self._widgets_bound[key] = []
        self._widgets_bound[key].append(widget)

        if mode == "tooltip":
            self._bind_tooltip(key, widget)
        elif mode == "inline":
            self._bind_inline(key, widget)
        elif mode == "whats_this":
            self._bind_whats_this(key, widget)

    def _bind_tooltip(self, key: str, widget: QWidget):
        tooltip = self.get_tooltip(key)
        if tooltip:
            widget.setToolTip(tooltip)

    def _bind_inline(self, key: str, widget: QWidget):
        inline_text = self.get_inline(key)
        if inline_text and hasattr(widget, "setWhatsThis"):
            widget.setWhatsThis(inline_text)

    def _bind_whats_this(self, key: str, widget: QWidget):
        text = self.get_description(key)
        if text and hasattr(widget, "setWhatsThis"):
            widget.setWhatsThis(text)

    def auto_bind_widgets(
        self, widgets_dict: Dict[str, QWidget], mode: str = "tooltip"
    ):
        for key, widget in widgets_dict.items():
            self.bind_to_widget(key, widget, mode)

    def check_trigger(self, key: str) -> bool:
        guide = self.get_guide(key)
        if not guide:
            return True

        trigger = guide.trigger
        if trigger == "always":
            return True

        if trigger in self._triggers:
            return self._triggers[trigger]()

        return True

    def should_show_guide(self, key: str) -> bool:
        if key not in self._trigger_cache:
            self._trigger_cache[key] = self.check_trigger(key)
        return self._trigger_cache[key]

    def refresh_triggers(self):
        self._trigger_cache.clear()

    def show_modal(self, key: str, parent: Optional[QWidget] = None) -> bool:
        guide = self.get_guide(key)
        if not guide:
            return False

        dialog = QDialog(parent)
        dialog.setWindowTitle(guide.title or "Help")
        dialog.setMinimumSize(500, 400)

        layout = QVBoxLayout(dialog)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)

        browser = QTextBrowser()
        browser.setOpenExternalLinks(True)
        content = f"<h2>{guide.title}</h2>"
        content += f"<p>{guide.rich_text}</p>"
        if guide.description:
            content += f"<hr><p><b>Description:</b> {guide.description}</p>"
        browser.setHtml(content)

        scroll.setWidget(browser)
        layout.addWidget(scroll)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)

        dialog.exec()
        return True

    def mark_first_run_done(self):
        import os

        marker = self.config_path.parent / ".first_run_done"
        marker.touch()

    def get_all_keys(self) -> List[str]:
        return list(self._guides.keys())

    def search_guides(self, query: str) -> List[str]:
        query_lower = query.lower()
        results = []
        for key, guide in self._guides.items():
            if (
                query_lower in key.lower()
                or query_lower in guide.title.lower()
                or query_lower in guide.description.lower()
            ):
                results.append(key)
        return results


def parse_guide_comments(config_text: str) -> Dict[str, Dict]:
    guides = {}
    current_section = ""
    current_key = ""
    in_guide = False
    guide_data = {}

    for line in config_text.split("\n"):
        if line.strip().startswith("# guide:"):
            in_guide = True
            guide_data = {}
            match = re.search(r"# guide:\s*(\S+)", line)
            if match:
                current_key = match.group(1)
        elif in_guide:
            if line.strip().startswith("#") and not line.strip().startswith("# guide:"):
                key_match = re.search(r"#\s*(\w+):\s*(.+)", line)
                if key_match:
                    guide_data[key_match.group(1)] = key_match.group(2).strip()
            elif line.strip() and not line.strip().startswith("#"):
                in_guide = False
                if current_key and guide_data:
                    guides[current_key] = guide_data

    return guides
