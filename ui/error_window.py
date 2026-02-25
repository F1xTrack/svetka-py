"""
Error Window Module
Модуль для отображения всплывающих уведомлений об ошибках с веб-интерфейсом
"""
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QApplication
from PyQt6.QtCore import Qt, QUrl, QTimer, pyqtSlot
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEnginePage


class ErrorWebPage(QWebEnginePage):
    """Кастомная веб-страница для обработки сигналов от окна ошибок"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        
    @pyqtSlot()
    def closeWindow(self):
        """Закрытие окна ошибок"""
        if self.parent():
            self.parent().close()
            
    @pyqtSlot(float, float)
    def savePosition(self, x, y):
        """Сохранение позиции окна"""
        if self.parent():
            self.parent().save_position(x, y)


class ErrorOverlayWindow(QWidget):
    """
    Веб-окно ошибок с кастомизируемым интерфейсом
    
    Функционал:
    - HTML/CSS темизация
    - Drag-and-Drop
    - Автозакрытие
    - Сохранение позиции
    - Копирование текста ошибки
    """
    
    def __init__(
        self,
        message="Error Occurred",
        title="Error",
        details=None,
        opacity=80,
        color_index=0,
        auto_close_seconds=5,
        save_position=True,
        parent=None
    ):
        super().__init__(parent)
        
        self.message = message
        self.title = title
        self.details = details or ""
        self.opacity = opacity
        self.color_index = color_index
        self.auto_close_seconds = auto_close_seconds
        self.save_position_enabled = save_position
        
        # Путь к шаблону
        self.template_path = os.path.join(
            os.path.dirname(os.path.dirname(__file__)),
            "assets",
            "error_overlay_template.html"
        )
        
        self.setup_ui()
        self.load_content()
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        self.web_view = QWebEngineView()
        self.web_page = ErrorWebPage(self)
        self.web_view.setPage(self.web_page)
        
        layout.addWidget(self.web_view)
        
        self.resize(400, 200)
        self.center_on_screen()
        
    def load_content(self):
        """Загрузка HTML контента с параметрами"""
        # Формирование URL с параметрами
        from urllib.parse import quote
        
        params = {
            'opacity': self.opacity,
            'color': self.color_index,
            'autoClose': self.auto_close_seconds if self.auto_close_seconds > 0 else 0,
            'message': quote(self.message),
            'title': quote(self.title),
            'details': quote(self.details) if self.details else ''
        }
        
        query_string = '&'.join(f"{k}={v}" for k, v in params.items())
        
        # Загрузка локального файла с параметрами
        if os.path.exists(self.template_path):
            url = QUrl.fromLocalFile(self.template_path)
            url.setQuery(query_string)
            self.web_view.load(url)
        else:
            # Fallback: генерация простого HTML
            html = self.generate_fallback_html()
            self.web_view.setHtml(html)
            
    def generate_fallback_html(self) -> str:
        """Генерация резервного HTML если шаблон не найден"""
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{
                    background: rgba(50, 50, 50, {self.opacity / 100});
                    color: white;
                    font-family: 'Segoe UI', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    user-select: none;
                }}
                .container {{
                    text-align: center;
                    padding: 30px;
                    border: 2px solid #FF5555;
                    border-radius: 10px;
                }}
                h2 {{ color: #FF5555; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>⚠️ {self.title}</h2>
                <p>{self.message}</p>
            </div>
        </body>
        </html>
        """
        
    def center_on_screen(self):
        """Центрирование окна на экране"""
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - self.width()) // 2
        y = (screen.height() - self.height()) // 2
        
        # Проверка сохранённой позиции
        if self.save_position_enabled:
            saved_pos = self.load_saved_position()
            if saved_pos:
                x, y = saved_pos
                
        self.move(x, y)
        
    def save_position(self, x, y):
        """
        Сохранение позиции окна
        
        Args:
            x: Координата X
            y: Координата Y
        """
        if not self.save_position_enabled:
            return
            
        # Здесь будет интеграция с ConfigManager
        print(f"Saving window position: x={x}, y={y}")
        
    def load_saved_position(self):
        """
        Загрузка сохранённой позиции
        
        Returns:
            Кортеж (x, y) или None
        """
        # Здесь будет загрузка из ConfigManager
        return None
        
    def close_event(self, event):
        """Обработчик закрытия окна"""
        event.accept()


# Обратная совместимость со старым классом
OverlayWindow = ErrorOverlayWindow


if __name__ == "__main__":
    import sys
    
    app = QApplication(sys.argv)
    
    # Тест с параметрами
    error = ErrorOverlayWindow(
        message="Test Error: Connection failed to database server",
        title="Database Error",
        details="ConnectionError: Could not connect to localhost:5432\nTimeout after 30 seconds",
        opacity=85,
        color_index=0,  # Red
        auto_close_seconds=7,
        save_position=True
    )
    error.show()
    
    sys.exit(app.exec())
