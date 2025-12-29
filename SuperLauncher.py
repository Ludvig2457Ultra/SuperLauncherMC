import sys
import os
import json
import subprocess
import threading
import time
import datetime
import hashlib
import secrets
import platform
import shutil
import zipfile
import tempfile
import base64
import urllib.parse
import webbrowser
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any, Union
from uuid import uuid1
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

# Внешние библиотеки
import requests
from packaging import version as packaging_version
from tqdm import tqdm
from pypresence import Presence
from random_username.generate import generate_username

# Дополнительные библиотеки (опционально)
try:
    from cryptography.fernet import Fernet
    CRYPTO_AVAILABLE = True
except ImportError:
    CRYPTO_AVAILABLE = False
    print("⚠️ Шифрование отключено (cryptography не установлен)")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    print("⚠️ JWT отключен (PyJWT не установлен)")

# Minecraft библиотеки
from minecraft_launcher_lib.utils import get_minecraft_directory, get_version_list
from minecraft_launcher_lib.install import install_minecraft_version
from minecraft_launcher_lib.command import get_minecraft_command

# =========== PYQT6 ИМПОРТЫ ===========

# PyQt6 Core - ОСНОВНЫЕ
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QSize, QTimer, QPropertyAnimation, 
    QEasingCurve, pyqtProperty, QUrl, QDateTime, QTime, QDate, 
    QRect, QRectF, QPoint, QPointF, QModelIndex,
    QObject, QEvent, QMargins,
    QByteArray, QBuffer, QIODevice, QLibraryInfo, QLocale,
    QSettings, QVariant, QMetaObject, QRunnable, QThreadPool,
    QProcess, QProcessEnvironment, QStandardPaths, QDir, QFile, QFileInfo,
    QTextStream, QDataStream, QCoreApplication,
    QRegularExpression  # Для регулярных выражений
)

# PyQt6 Widgets - ОСНОВНЫЕ ВИДЖЕТЫ
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QFrame, QStackedWidget, QButtonGroup,
    QLineEdit, QComboBox, QProgressBar, QSpacerItem, QSizePolicy,
    QMessageBox, QScrollArea, QDialog, QCheckBox, QFormLayout,
    QListWidget, QListWidgetItem, QRadioButton, QFileDialog,
    QGridLayout, QGroupBox, QTabWidget
)

# PyQt6 GUI - ОСНОВНЫЕ
from PyQt6.QtGui import (
    QPixmap, QCursor, QIcon, QPainter, QBrush, QPen, 
    QLinearGradient, QColor, QFont, QFontDatabase, QFontMetrics,
    QRadialGradient, QConicalGradient, QGradient, QImage,
    QPalette, QPainterPath, QKeySequence, QAction, QMovie,
    QTextCursor, QTextCharFormat, QTextFormat, QTextDocument,
    QTextOption, QTextBlockFormat, QTextLength,
    QBitmap, QRegion, QTransform, QPolygon, QPolygonF,
    QGuiApplication, QScreen, QClipboard, QDrag,
    QStandardItemModel, QStandardItem
)

# Валидаторы из QtGui (правильное место в PyQt6)
from PyQt6.QtGui import QValidator, QIntValidator, QDoubleValidator, QRegularExpressionValidator

# =========== ОПЦИОНАЛЬНЫЕ ИМПОРТЫ ===========

# Дополнительные виджеты
try:
    from PyQt6.QtWidgets import (
        QTreeWidget, QTableWidget, QSplitter, QToolBar, QMenuBar, 
        QStatusBar, QToolButton, QHeaderView, QStyleFactory, QInputDialog,
        QColorDialog, QFontDialog, QSlider, QSpinBox, QDoubleSpinBox,
        QTextEdit, QPlainTextEdit, QCompleter, QSystemTrayIcon, QMenu
    )
    EXTRA_WIDGETS = True
except ImportError:
    EXTRA_WIDGETS = False
    print("⚠️ Дополнительные виджеты не доступны")

# Дополнительные GUI элементы
try:
    from PyQt6.QtGui import (
        QVector2D, QVector3D, QVector4D, QMatrix4x4,
        QSurfaceFormat, QOpenGLContext, QOpenGLFunctions
    )
    EXTRA_GUI = True
except ImportError:
    EXTRA_GUI = False
    print("⚠️ 3D графика не доступна")

# Сортировка и фильтрация
try:
    from PyQt6.QtCore import QSortFilterProxyModel
    from PyQt6.QtGui import QAbstractItemModel
    SORTING_AVAILABLE = True
except ImportError:
    SORTING_AVAILABLE = False
    print("⚠️ Сортировка моделей не доступна")

# Мультимедиа
try:
    from PyQt6.QtMultimedia import QMediaPlayer, QAudioOutput
    MULTIMEDIA_AVAILABLE = True
except ImportError:
    MULTIMEDIA_AVAILABLE = False
    print("⚠️ Мультимедиа отключено")

# Сеть
try:
    from PyQt6.QtNetwork import (
        QNetworkAccessManager, QNetworkRequest, QNetworkReply
    )
    NETWORK_AVAILABLE = True
except ImportError:
    NETWORK_AVAILABLE = False
    print("⚠️ Сетевые функции ограничены")

# WebEngine
try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    WEBENGINE_AVAILABLE = True
except ImportError:
    WEBENGINE_AVAILABLE = False
    print("⚠️ WebEngine отключен")

# Charts
try:
    from PyQt6.QtCharts import QChart, QChartView, QLineSeries
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
    print("⚠️ Графики отключены")

# Pillow для изображений
try:
    from PIL import Image
    PILLOW_AVAILABLE = True
except ImportError:
    PILLOW_AVAILABLE = False
    print("⚠️ Обработка изображений ограничена")

# Мониторинг ресурсов
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    print("⚠️ Мониторинг ресурсов отключен")

# Уведомления Windows
try:
    from win10toast import ToastNotifier
    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False
    print("⚠️ Уведомления Windows отключены")

# =========== КОНСТАНТЫ ===========

CONFIG_FILE = "settings.json"
ACCOUNTS_FILE = "accounts.json"
LICENSES_FILE = "licenses.json"
GIFTS_FILE = "gifts.json"
UI_SETTINGS_FILE = "ui_settings.json"
SERVERS_FILE = "servers_list.json"
CURRENT_VERSION = "v2.0.0_2026"
MODRINTH_API = "https://api.modrinth.com/v2"

# =========== ИНИЦИАЛИЗАЦИЯ ===========

# Получаем путь Minecraft
try:
    minecraft_directory = get_minecraft_directory()
    print(f"🎮 Путь к Minecraft: {minecraft_directory}")
    
    if not os.path.exists(minecraft_directory):
        print("📁 Создаю папку Minecraft...")
        os.makedirs(minecraft_directory, exist_ok=True)
    
except Exception as e:
    print(f"⚠️ Ошибка: {e}")
    # Резервный путь
    if platform.system() == "Windows":
        minecraft_directory = os.path.join(os.getenv('APPDATA'), '.minecraft')
    elif platform.system() == "Darwin":
        minecraft_directory = os.path.expanduser("~/Library/Application Support/minecraft")
    else:
        minecraft_directory = os.path.expanduser("~/.minecraft")
    
    os.makedirs(minecraft_directory, exist_ok=True)
    print(f"📁 Использую резервный путь: {minecraft_directory}")

# Создаем профиль если нужно
profile_path = os.path.join(minecraft_directory, 'launcher_profiles.json')
if not os.path.isfile(profile_path):
    print("📄 Создаю launcher_profiles.json...")
    empty_profile = {
        "profiles": {},
        "settings": {},
        "selectedProfile": None
    }
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(empty_profile, f, indent=4)

# Создаем папки
folders = [
    "assets/holiday", "assets/skins", "assets/themes", "assets/icons",
    "user_data", "servers", "builds", "mods_cache", "logs", "temp"
]

for folder in folders:
    os.makedirs(folder, exist_ok=True)

print(f"✅ SuperLauncher {CURRENT_VERSION} готов к запуску!")
print(f"📊 PyQt6 виджеты: {'✅' if EXTRA_WIDGETS else '⚠️'}")
print(f"🎵 Мультимедиа: {'✅' if MULTIMEDIA_AVAILABLE else '⚠️'}")
print(f"🌐 WebEngine: {'✅' if WEBENGINE_AVAILABLE else '⚠️'}")
print(f"📊 Графики: {'✅' if CHARTS_AVAILABLE else '⚠️'}")
print("=" * 50)

CONFIG_FILE = "settings.json"

translations = {
    "ru": {
        # --- SettingsPage ---
        "Theme:": "Тема:",
        "Language:": "Язык:",
        "Minecraft launch mode:": "Способ запуска Minecraft:",
        "minecraft-launcher-lib (default)": "minecraft-launcher-lib (по умолчанию)",
        "Java (specify path)": "Java (указать путь)",
        "Java path (if Java is selected):": "Путь к Java (если выбран Java):",
        "Browse Java path": "Выбрать путь к Java",
        "Page backgrounds:": "Фоны страниц:",
        "Save settings": "Сохранить настройки",

        # --- MinecraftPage ---
        "Play": "Играть",
        "Username": "Имя пользователя",
        "No versions available": "Версии недоступны",

        # --- ModsPage ---
        "Mods from Modrinth": "Моды из Modrinth",
        "Search mod...": "Найти мод...",
        "Open mods folder": "Открыть папку модов",
        "Delete all mods": "Удалить все моды",
        "Error": "Ошибка",
        "Downloading mod": "Загрузка мода",
        "Done": "Готово",
        "All mods deleted": "Удалено модов",
        "No available versions": "Нет доступных версий",
        "No supported builds": "Нет поддерживаемых билдов",
        "File not found": "Файл не найден",
        "Install mod": "Установка мода",
        "Minecraft version and loader:": "Версия Minecraft и ядро:",

        # --- NewsPage ---
        "News": "Новости",
        "2025-08-12 v1.4.0.7: Discord RPC added": "2025-08-12 v1.4.0.7: Добавлен Discord RPC",
        "2025-07-24 v1.4.0.5: Added support for downloading mods from Modrind and launcher settings": "2025-07-24 v1.4.0.5: Добавлена поддержка скачивания модов из Modrind и настроек лаунчера",
        "2025-07-23 v1.4.0.4: Added ability to create and manage local Minecraft servers directly from the launcher...": "2025-07-23 v1.4.0.4: Добавлена возможность создавать и управлять локальными Minecraft-серверами прямо из лаунчера...",
        "2025-07-23 v1.4.0.3: New design added and code restored": "2025-07-23 v1.4.0.3: Добавлен новый дизайн и восстановлен код",
        "2025-06-26 v1.4.0.2: New design added, but code lost": "2025-06-26 v1.4.0.2: Добавлен новый дизайн, но утерян код",
        "2025-06-26 v1.4.0.1: Bugs fixed, but design outdated": "2025-06-26 v1.4.0.1: Исправлены баги, но дизайн устаревший",
        "2025-06-26 v1.4.0.0: Bugs fixed, but design outdated": "2025-06-26 v1.4.0.0: Исправлены баги, но дизайн устаревший",
        "2025-06-26 v1.3: Launcher will exit beta in the next release": "2025-06-26 v1.3: Лаунчер выйдет из бета в следующем релизе",
        "No news available": "Новости недоступны",

        # --- HomePage ---
        "Welcome to SuperLauncher!": "Добро пожаловать в SuperLauncher!",

        # --- ServersPage ---
        "🖧 Minecraft Servers": "🖧 Серверы Minecraft",
        "Create your own server": "Создать свой сервер",
        "Server Name": "Имя сервера",
        "IP or domain": "IP или домен",
        "Add server": "Добавить сервер",
        "Manage": "Управление",
        "Delete": "Удалить",
        "Delete confirmation": "Подтверждение удаления",
        "Are you sure you want to delete the server '{server_name}'? This action cannot be undone.": "Вы уверены, что хотите удалить сервер '{server_name}'? Это действие нельзя отменить.",
        "Folder in use": "Папка занята",
        "Cannot delete folder because it is used by the following processes:\n{proc_names}\n\nDo you want to terminate them and try again?": "Не удалось удалить папку, так как её используют процессы:\n{proc_names}\n\nХотите завершить эти процессы и попробовать снова?",
        "Terminate processes": "Завершить процессы",
        "Cancel": "Отмена",
        "Success": "Успех",
        "Folder successfully deleted after terminating processes.": "Папка успешно удалена после завершения процессов.",
        "Failed to delete folder:\n{error}": "Не удалось удалить папку:\n{error}",
        "Deletion canceled.": "Удаление папки отменено.",
        "Please fill in the server name and IP.": "Пожалуйста, заполните имя и IP сервера.",

        # --- ServerControlPanel ---
        "Settings": "Настройки",
        "I accept the EULA": "Я принимаю лицензионное соглашение EULA",
        "Enable offline mode (cracked)": "Включить оффлайн режим (пиратка)",
        "Use playit.gg (tunnel)": "Использовать playit.gg (туннель)",
        "Control": "Управление",
        "Start server": "Запустить сервер",
        "Stop server": "Остановить сервер",
        "You must accept the EULA!": "Вы должны принять лицензионное соглашение EULA!",
        "Managing server: ": "Управление сервером: ",
        "Manage server": "Управление сервером",
        "Server started.": "Сервер запущен.",
        "Server stopped.": "Сервер остановлен.",
        "Server is already running.": "Сервер уже запущен.",
        "Server is not running.": "Сервер не запущен.",
        "Server forcefully stopped.": "Сервер принудительно остановлен.",

        # --- CreateServerDialog ---
        "Create your own server": "Создать свой сервер Minecraft",
        "Port": "Порт",
        "Version": "Версия",
        "Core": "Ядро",
        "Create": "Создать",
        "Please enter a valid server name and port (number).": "Пожалуйста, введите корректное имя и порт (число).",
        "Error": "Ошибка"
    },

    "en": {
        # --- SettingsPage ---
        "Theme:": "Theme:",
        "Language:": "Language:",
        "Minecraft launch mode:": "Minecraft launch mode:",
        "minecraft-launcher-lib (default)": "minecraft-launcher-lib (default)",
        "Java (specify path)": "Java (specify path)",
        "Java path (if Java is selected):": "Java path (if Java is selected):",
        "Browse Java path": "Browse Java path",
        "Page backgrounds:": "Page backgrounds:",
        "Save settings": "Save settings",

        # --- MinecraftPage ---
        "Play": "Play",
        "Username": "Username",
        "No versions available": "No versions available",

        # --- ModsPage ---
        "Mods from Modrinth": "Mods from Modrinth",
        "Search mod...": "Search mod...",
        "Open mods folder": "Open mods folder",
        "Delete all mods": "Delete all mods",
        "Error": "Error",
        "Downloading mod": "Downloading mod",
        "Done": "Done",
        "All mods deleted": "All mods deleted",
        "No available versions": "No available versions",
        "No supported builds": "No supported builds",
        "File not found": "File not found",
        "Install mod": "Install mod",
        "Minecraft version and loader:": "Minecraft version and loader:",

        # --- NewsPage ---
        "News": "News",
        "2025-08-12 v1.4.0.7: Discord RPC added": "2025-08-12 v1.4.0.7: Discord RPC added",
        "2025-07-24 v1.4.0.5: Added support for downloading mods from Modrind and launcher settings": "2025-07-24 v1.4.0.5: Added support for downloading mods from Modrind and launcher settings",
        "2025-07-23 v1.4.0.4: Added ability to create and manage local Minecraft servers directly from the launcher...": "2025-07-23 v1.4.0.4: Added ability to create and manage local Minecraft servers directly from the launcher...",
        "2025-07-23 v1.4.0.3: New design added and code restored": "2025-07-23 v1.4.0.3: New design added and code restored",
        "2025-06-26 v1.4.0.2: New design added, but code lost": "2025-06-26 v1.4.0.2: New design added, but code lost",
        "2025-06-26 v1.4.0.1: Bugs fixed, but design outdated": "2025-06-26 v1.4.0.1: Bugs fixed, but design outdated",
        "2025-06-26 v1.4.0.0: Bugs fixed, but design outdated": "2025-06-26 v1.4.0.0: Bugs fixed, but design outdated",
        "2025-06-26 v1.3: Launcher will exit beta in the next release": "2025-06-26 v1.3: Launcher will exit beta in the next release",
        "No news available": "No news available",

        # --- HomePage ---
        "Welcome to SuperLauncher!": "Welcome to SuperLauncher!",

        # --- ServersPage ---
        "🖧 Minecraft Servers": "🖧 Minecraft Servers",
        "Create your own server": "Create your own server",
        "Server Name": "Server Name",
        "IP or domain": "IP or domain",
        "Add server": "Add server",
        "Manage": "Manage",
        "Delete": "Delete",
        "Delete confirmation": "Delete confirmation",
        "Are you sure you want to delete the server '{server_name}'? This action cannot be undone.": "Are you sure you want to delete the server '{server_name}'? This action cannot be undone.",
        "Folder in use": "Folder in use",
        "Cannot delete folder because it is used by the following processes:\n{proc_names}\n\nDo you want to terminate them and try again?": "Cannot delete folder because it is used by the following processes:\n{proc_names}\n\nDo you want to terminate them and try again?",
        "Terminate processes": "Terminate processes",
        "Cancel": "Cancel",
        "Success": "Success",
        "Folder successfully deleted after terminating processes.": "Folder successfully deleted after terminating processes.",
        "Failed to delete folder:\n{error}": "Failed to delete folder:\n{error}",
        "Deletion canceled.": "Deletion canceled.",
        "Please fill in the server name and IP.": "Please fill in the server name and IP.",

        # --- ServerControlPanel ---
        "Settings": "Settings",
        "I accept the EULA": "I accept the EULA",
        "Enable offline mode (cracked)": "Enable offline mode (cracked)",
        "Use playit.gg (tunnel)": "Use playit.gg (tunnel)",
        "Control": "Control",
        "Start server": "Start server",
        "Stop server": "Stop server",
        "You must accept the EULA!": "You must accept the EULA!",
        "Managing server: ": "Managing server: ",
        "Manage server": "Manage server",
        "Server started.": "Server started.",
        "Server stopped.": "Server stopped.",
        "Server is already running.": "Server is already running.",
        "Server is not running.": "Server is not running.",
        "Server forcefully stopped.": "Server forcefully stopped.",

        # --- CreateServerDialog ---
        "Create your own server": "Create your own server",
        "Port": "Port",
        "Version": "Version",
        "Core": "Core",
        "Create": "Create",
        "Please enter a valid server name and port (number).": "Please enter a valid server name and port (number).",
        "Error": "Error"
    }
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    # Если файла нет или ошибка, возвращаем значения по умолчанию
    return {
        "java_path": "",
        "ram": 4096,
        "language": "ru",
        "theme": "dark",
        "launch_mode": "launcher_lib"
    }


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Ошибка сохранения настроек:", e)


MODRINTH_API = "https://api.modrinth.com/v2"

# Путь к папке Minecraft
minecraft_directory = get_minecraft_directory()
print("Path to Minecraft:", minecraft_directory)

if not os.path.exists(minecraft_directory):
    print("Minecraft folder not found! Creating...")
    os.makedirs(minecraft_directory, exist_ok=True)

print("Contents of the Minecraft folder:", os.listdir(minecraft_directory))

profile_path = os.path.join(minecraft_directory, 'launcher_profiles.json')
print("Path to launcher_profiles.json:", profile_path)

if not os.path.isfile(profile_path):
    print("launcher_profiles.json not found, creating new...")
    empty_profile = {
        "profiles": {},
        "settings": {},
        "selectedProfile": None
    }
    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(empty_profile, f, indent=4)
    print("Empty launcher_profiles.json created")
else:
    print("launcher_profiles.json already exists")

class HolidayTheme:
    def __init__(self):
        self.current_holiday = self.detect_holiday()
        self.snowflakes = []
        self.snow_timer = None
        
    def detect_holiday(self):
        """Определение текущего праздника"""
        now = datetime.datetime.now()
        month, day = now.month, now.day
        
        if month == 12 and 20 <= day <= 31:
            return "christmas"
        elif month == 1 and 1 <= day <= 15:
            return "new_year"
        elif month == 12 and 15 <= day <= 31:
            return "new_year_eve"
        return None
    
    def get_holiday_assets(self):
        """Получение ресурсов для праздника"""
        if self.current_holiday in ["christmas", "new_year", "new_year_eve"]:
            return {
                "name": self.current_holiday,
                "background": "assets/holiday/new_year_bg.png",
                "icons": {
                    "home": "🎄",
                    "mods": "🎁",
                    "news": "❄️",
                    "updates": "🌟",
                    "servers": "🦌",
                    "settings": "🔔",
                    "minecraft": "⛄",
                    "account": "🎅",
                    "gifts": "🎁"
                },
                "colors": {
                    "primary": "#FF3333",    # Красный
                    "secondary": "#33FF57",   # Зеленый
                    "accent": "#FFD700",      # Золотой
                    "background": "#0A2E36"   # Темно-синий
                },
                "music": "assets/holiday/christmas_music.mp3",
                "sounds": {
                    "click": "assets/holiday/bell.wav",
                    "success": "assets/holiday/success.wav"
                }
            }
        return None
    
    def apply_holiday_style(self, widget):
        """Применить праздничные стили к виджету"""
        assets = self.get_holiday_assets()
        if assets:
            style = f"""
                QWidget {{
                    background-color: {assets['colors']['background']};
                }}
                QPushButton {{
                    background-color: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 {assets['colors']['primary']},
                        stop:1 {assets['colors']['secondary']});
                    color: white;
                    border-radius: 10px;
                    padding: 10px;
                    font-size: 14px;
                    font-weight: bold;
                    border: 2px solid {assets['colors']['accent']};
                }}
                QPushButton:hover {{
                    background-color: {assets['colors']['accent']};
                }}
                QLabel {{
                    color: {assets['colors']['accent']};
                }}
            """
            widget.setStyleSheet(style)
            
            # Добавить снежинки на главное окно
            if isinstance(widget, QMainWindow):
                self.setup_snow_effect(widget)
    
    def setup_snow_effect(self, window):
        """Настройка эффекта снежинок"""
        self.snowflakes = []
        for _ in range(50):
            self.snowflakes.append({
                'x': secrets.randbelow(window.width()),
                'y': secrets.randbelow(100) - 110,  # ОТ -10 ДО -110
                'size': secrets.randbelow(15) + 10,  # ОТ 10 ДО 25
                'speed': secrets.randbelow(4) + 1,   # ОТ 1 ДО 5
                'wiggle': secrets.randbelow(5) - 2   # ОТ -2 ДО 2
            })
        
        if not self.snow_timer:
            self.snow_timer = QTimer()
            self.snow_timer.timeout.connect(lambda: self.update_snow(window))
            self.snow_timer.start(50)
    
    def update_snow(self, window):
        """Обновление позиций снежинок"""
        for flake in self.snowflakes:
            flake['y'] += flake['speed']
            flake['x'] += flake['wiggle']
            
            if flake['y'] > window.height():
                flake['y'] = -10
                flake['x'] = secrets.randbelow(window.width())
            
            if flake['x'] < 0 or flake['x'] > window.width():
                flake['wiggle'] = -flake['wiggle']
        
        window.update()
    
    def paint_snow(self, painter, window):
        """Отрисовка снежинок"""
        if self.current_holiday:
            painter.setBrush(QBrush(QColor(255, 255, 255, 200)))
            painter.setPen(Qt.PenStyle.NoPen)
            
            for flake in self.snowflakes:
                painter.drawEllipse(
                    flake['x'], flake['y'],
                    flake['size'], flake['size']
                )

# =========== ДОБАВИТЬ ПОСЛЕ HolidayTheme ===========
class AccountSystem:
    def __init__(self):
        self.accounts_file = "accounts.json"
        self.licenses_file = "licenses.json"
        self.current_user = None
        self.load_initial_data()
    
    def load_initial_data(self):
        """Загрузка начальных данных"""
        if not os.path.exists(self.accounts_file):
            self.save_accounts([])
        
        if not os.path.exists(self.licenses_file):
            self.save_licenses({})
    
    def save_accounts(self, accounts):
        """Сохранение аккаунтов"""
        with open(self.accounts_file, "w", encoding="utf-8") as f:
            json.dump(accounts, f, indent=2)
    
    def save_licenses(self, licenses):
        """Сохранение лицензий"""
        with open(self.licenses_file, "w", encoding="utf-8") as f:
            json.dump(licenses, f, indent=2)
    
    def load_accounts(self):
        """Загрузка аккаунтов"""
        try:
            with open(self.accounts_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    
    def generate_license_key(self, user_id, tier="standard", duration=365):
        """Генерация ключа лицензии"""
        timestamp = int(datetime.datetime.now().timestamp())
        key_base = f"{user_id}_{tier}_{duration}_{timestamp}_{secrets.token_hex(4)}"
        license_key = hashlib.sha256(key_base.encode()).hexdigest()[:24].upper()
        
        # Форматирование в группы по 6 символов
        formatted_key = '-'.join([license_key[i:i+6] for i in range(0, len(license_key), 6)])
        
        # Сохранение лицензии
        licenses = self.load_licenses()
        licenses[formatted_key] = {
            "user_id": user_id,
            "tier": tier,
            "duration_days": duration,
            "created_at": timestamp,
            "expires_at": timestamp + (duration * 86400),
            "activated": False
        }
        self.save_licenses(licenses)
        
        return formatted_key
    
    def load_licenses(self):
        """Загрузка лицензий"""
        try:
            with open(self.licenses_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {}
    
    def activate_license(self, license_key, user_id):
        """Активация лицензии"""
        licenses = self.load_licenses()
        
        if license_key in licenses:
            license_data = licenses[license_key]
            
            if license_data["activated"]:
                return False, "Лицензия уже активирована"
            
            if datetime.datetime.now().timestamp() > license_data["expires_at"]:
                return False, "Срок действия лицензии истек"
            
            license_data["activated"] = True
            license_data["activated_by"] = user_id
            license_data["activated_at"] = datetime.datetime.now().timestamp()
            
            # Обновление пользователя
            accounts = self.load_accounts()
            for account in accounts:
                if account["user_id"] == user_id:
                    account["license_tier"] = license_data["tier"]
                    account["license_expires"] = license_data["expires_at"]
                    account["premium_features"] = self.get_premium_features(license_data["tier"])
                    break
            
            self.save_accounts(accounts)
            self.save_licenses(licenses)
            
            return True, "Лицензия успешно активирована"
        
        return False, "Неверный ключ лицензии"
    
    def get_premium_features(self, tier):
        """Получение премиум функций по уровню"""
        features = {
            "standard": ["basic_skins", "daily_gifts", "cloud_sync"],
            "premium": ["all_skins", "priority_support", "custom_themes", "no_ads"],
            "ultimate": ["early_access", "server_hosting", "dedicated_support", "all_features"]
        }
        return features.get(tier, ["basic_skins"])
    
    def register_user(self, username, email, password):
        """Регистрация пользователя"""
        # Проверка существования
        accounts = self.load_accounts()
        
        for account in accounts:
            if account["username"] == username:
                return False, "Имя пользователя уже занято"
            if account["email"] == email:
                return False, "Email уже зарегистрирован"
        
        # Создание пользователя
        user_id = secrets.token_hex(16)
        salt = secrets.token_hex(8)
        password_hash = hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
        
        user_data = {
            "user_id": user_id,
            "username": username,
            "email": email,
            "password_hash": password_hash,
            "salt": salt,
            "created_at": datetime.datetime.now().isoformat(),
            "last_login": None,
            "license_tier": "free",
            "xp": 0,
            "level": 1,
            "gifts_claimed": [],
            "achievements": [],
            "settings": {},
            "skins": ["default"],
            "friends": []
        }
        
        accounts.append(user_data)
        self.save_accounts(accounts)
        
        # Создание папки пользователя
        user_folder = f"user_data/{user_id}"
        os.makedirs(user_folder, exist_ok=True)
        os.makedirs(f"{user_folder}/skins", exist_ok=True)
        os.makedirs(f"{user_folder}/configs", exist_ok=True)
        
        return True, user_data
    
    def login(self, username_or_email, password):
        """Вход в аккаунт"""
        accounts = self.load_accounts()
        
        for account in accounts:
            if account["username"] == username_or_email or account["email"] == username_or_email:
                # Проверка пароля
                test_hash = hashlib.sha256(
                    f"{password}{account['salt']}".encode()
                ).hexdigest()
                
                if test_hash == account["password_hash"]:
                    account["last_login"] = datetime.datetime.now().isoformat()
                    self.save_accounts(accounts)
                    self.current_user = account
                    return True, account
        
        return False, "Неверное имя пользователя или пароль"
    
    def logout(self):
        """Выход из аккаунта"""
        self.current_user = None
    
    def is_premium(self):
        """Проверка премиум статуса"""
        if not self.current_user:
            return False
        
        if self.current_user.get("license_tier") == "free":
            return False
        
        expires = self.current_user.get("license_expires", 0)
        return datetime.datetime.now().timestamp() < expires
    
    def get_user_folder(self):
        """Получение папки пользователя"""
        if self.current_user:
            return f"user_data/{self.current_user['user_id']}"
        return "user_data/guest"
    
# =========== ДОБАВИТЬ ПОСЛЕ AccountSystem ===========
class GiftSystem:
    def __init__(self, account_system):
        self.account_system = account_system
        self.gifts_file = "gifts.json"
        self.load_gifts()
    
    def load_gifts(self):
        """Загрузка подарков"""
        try:
            with open(self.gifts_file, "r", encoding="utf-8") as f:
                self.gifts = json.load(f)
        except:
            # Базовые подарки
            self.gifts = {
                "daily": [
                    {"id": "xp_100", "type": "xp", "amount": 100, "name": "Опыт новичка", "icon": "🌟"},
                    {"id": "skin_hat", "type": "skin", "skin_id": "santa_hat", "name": "Шапка Санты", "icon": "🎅"},
                    {"id": "theme_holiday", "type": "theme", "theme_id": "holiday", "name": "Праздничная тема", "icon": "🎄"},
                    {"id": "resource_winter", "type": "resource_pack", "pack_id": "winter", "name": "Зимний набор", "icon": "❄️"}
                ],
                "special": [
                    {"id": "new_year_2026", "type": "premium", "days": 7, "name": "Премиум на неделю", "icon": "🎉",
                     "available": "2026-01-01"},
                    {"id": "christmas_suit", "type": "skin", "skin_id": "santa_suit", "name": "Костюм Санты", "icon": "🎅",
                     "available": "2025-12-25"}
                ],
                "level_up": [
                    {"level": 5, "gift": {"type": "skin", "skin_id": "epic", "name": "Эпический скин"}},
                    {"level": 10, "gift": {"type": "theme", "theme_id": "premium", "name": "Премиум тема"}},
                    {"level": 20, "gift": {"type": "license", "tier": "standard", "days": 30, "name": "Месяц Standard"}}
                ]
            }
            self.save_gifts()
    
    def save_gifts(self):
        """Сохранение подарков"""
        with open(self.gifts_file, "w", encoding="utf-8") as f:
            json.dump(self.gifts, f, indent=2)
    
    def get_daily_gift(self):
        """Получение ежедневного подарка"""
        if not self.account_system.current_user:
            return None, "Требуется вход в аккаунт"
        
        user = self.account_system.current_user
        today = datetime.date.today().isoformat()
        
        # Проверяем, получал ли сегодня
        claimed = user.get("gifts_claimed", [])
        for gift in claimed:
            if gift.get("date") == today:
                return None, "Сегодняшний подарок уже получен"
        
        # Выбираем случайный подарок
        import random
        available_gifts = []
        
        for gift in self.gifts["daily"]:
            available_gifts.append(gift)
        
        # Добавляем специальные подарки если доступны
        for gift in self.gifts["special"]:
            if gift.get("available"):
                available_date = datetime.date.fromisoformat(gift["available"])
                if datetime.date.today() == available_date:
                    available_gifts.append(gift)
        
        if not available_gifts:
            return None, "Нет доступных подарков"
        
        selected_gift = random.choice(available_gifts)
        
        # Применяем подарок
        self.apply_gift(selected_gift, user)
        
        # Сохраняем факт получения
        claimed.append({
            "date": today,
            "gift_id": selected_gift["id"],
            "gift_name": selected_gift["name"]
        })
        user["gifts_claimed"] = claimed
        
        # Сохраняем пользователя
        self.account_system.save_accounts(
            self.account_system.load_accounts()  # Нужно обновить в общем списке
        )
        
        return selected_gift, "Подарок получен!"
    
    def apply_gift(self, gift, user):
        """Применение подарка"""
        gift_type = gift["type"]
        
        if gift_type == "xp":
            user["xp"] = user.get("xp", 0) + gift["amount"]
            self.check_level_up(user)
        
        elif gift_type == "skin":
            skins = user.get("skins", ["default"])
            if gift["skin_id"] not in skins:
                skins.append(gift["skin_id"])
                user["skins"] = skins
        
        elif gift_type == "theme":
            # Добавить тему
            pass
        
        elif gift_type == "license":
            # Активировать лицензию
            license_key = self.account_system.generate_license_key(
                user["user_id"],
                gift.get("tier", "standard"),
                gift.get("days", 30)
            )
            self.account_system.activate_license(license_key, user["user_id"])
    
    def check_level_up(self, user):
        """Проверка повышения уровня"""
        xp_needed = user["level"] * 1000
        current_xp = user.get("xp", 0)
        
        while current_xp >= xp_needed:
            user["level"] += 1
            current_xp -= xp_needed
            xp_needed = user["level"] * 1000
            
            # Дарим подарок за уровень
            self.give_level_up_gift(user["level"], user)
        
        user["xp"] = current_xp
    
    def give_level_up_gift(self, level, user):
        """Выдача подарка за уровень"""
        for level_gift in self.gifts["level_up"]:
            if level_gift["level"] == level:
                self.apply_gift(level_gift["gift"], user)
                return level_gift["gift"]
        return None
    
    def get_available_gifts(self):
        """Получение списка доступных подарков"""
        available = []
        today = datetime.date.today()
        
        # Ежедневные подарки
        available.extend(self.gifts["daily"])
        
        # Специальные подарки
        for gift in self.gifts["special"]:
            if gift.get("available"):
                gift_date = datetime.date.fromisoformat(gift["available"])
                if gift_date == today:
                    available.append(gift)
        
        return available
    
# =========== ДОБАВИТЬ ПОСЛЕ GiftSystem ===========
class CustomizableUI:
    def __init__(self):
        self.settings_file = "ui_settings.json"
        self.load_settings()
    
    def load_settings(self):
        """Загрузка настроек UI"""
        try:
            with open(self.settings_file, "r", encoding="utf-8") as f:
                self.settings = json.load(f)
        except:
            self.settings = {
                "theme": "dark",
                "accent_color": "#4facfe",
                "background_type": "gradient",  # gradient, image, solid
                "background_image": None,
                "gradient_start": "#1a1a2e",
                "gradient_end": "#16213e",
                "animations": True,
                "particles": True,
                "snow_effect": True,
                "font_size": 14,
                "font_family": "Segoe UI",
                "rounded_corners": True,
                "button_style": "modern",  # modern, classic, flat
                "transparency": 0.95,
                "custom_css": ""
            }
            self.save_settings()
    
    def save_settings(self):
        """Сохранение настроек"""
        with open(self.settings_file, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, indent=2)
    
    def apply_to_widget(self, widget):
        """Применение настроек к виджету"""
        style = self.generate_stylesheet()
        widget.setStyleSheet(style)
        
        # Установка шрифта
        font = QFont()
        font.setFamily(self.settings["font_family"])
        font.setPointSize(self.settings["font_size"])
        widget.setFont(font)
    
    def generate_stylesheet(self):
        """Генерация CSS стилей"""
        theme = self.settings["theme"]
        
        if theme == "dark":
            base_colors = {
                "bg": "#1e1e2e",
                "fg": "#cdd6f4",
                "accent": self.settings["accent_color"],
                "border": "#313244"
            }
        elif theme == "light":
            base_colors = {
                "bg": "#f5f5f5",
                "fg": "#333333",
                "accent": self.settings["accent_color"],
                "border": "#dddddd"
            }
        else:  # holiday
            base_colors = {
                "bg": "#0A2E36",
                "fg": "#FFFFFF",
                "accent": "#FFD700",
                "border": "#1B4B5A"
            }
        
        border_radius = "15px" if self.settings["rounded_corners"] else "5px"
        
        stylesheet = f"""
            QMainWindow {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.settings['gradient_start']},
                    stop:1 {self.settings['gradient_end']});
            }}
            
            QPushButton {{
                background-color: {base_colors['accent']};
                color: white;
                border-radius: {border_radius};
                padding: 10px 20px;
                font-size: {self.settings['font_size']}px;
                font-weight: bold;
                border: 2px solid {base_colors['accent']};
                font-family: '{self.settings['font_family']}';
            }}
            
            QPushButton:hover {{
                background-color: {self.darken_color(base_colors['accent'], 20)};
                border-color: {self.darken_color(base_colors['accent'], 30)};
            }}
            
            QPushButton:pressed {{
                background-color: {self.darken_color(base_colors['accent'], 40)};
            }}
            
            QLabel {{
                color: {base_colors['fg']};
                font-family: '{self.settings['font_family']}';
                font-size: {self.settings['font_size']}px;
            }}
            
            QLineEdit, QComboBox, QTextEdit {{
                background-color: rgba(255, 255, 255, 0.1);
                border: 2px solid {base_colors['border']};
                border-radius: {border_radius};
                padding: 8px;
                color: {base_colors['fg']};
                font-family: '{self.settings['font_family']}';
            }}
            
            QProgressBar {{
                border: 2px solid {base_colors['border']};
                border-radius: {border_radius};
                text-align: center;
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QProgressBar::chunk {{
                background-color: {base_colors['accent']};
                border-radius: {border_radius};
            }}
            
            QListWidget, QTreeWidget, QTableWidget {{
                background-color: rgba(255, 255, 255, 0.05);
                border: 2px solid {base_colors['border']};
                border-radius: {border_radius};
                color: {base_colors['fg']};
                font-family: '{self.settings['font_family']}';
            }}
            
            QListWidget::item:hover {{
                background-color: rgba(255, 255, 255, 0.1);
            }}
            
            QListWidget::item:selected {{
                background-color: {base_colors['accent']};
            }}
            
            QScrollBar:vertical {{
                background: transparent;
                width: 12px;
                margin: 0px;
            }}
            
            QScrollBar::handle:vertical {{
                background: {base_colors['accent']};
                border-radius: 6px;
                min-height: 20px;
            }}
            
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """
        
        # Добавляем пользовательский CSS
        stylesheet += self.settings.get("custom_css", "")
        
        return stylesheet
    
    def darken_color(self, color, percent):
        """Затемнение цвета"""
        from PyQt6.QtGui import QColor
        c = QColor(color)
        return c.darker(100 + percent).name()
    
    def create_theme_presets(self):
        """Создание пресетов тем"""
        return {
            "dark_default": {
                "theme": "dark",
                "accent_color": "#4facfe",
                "gradient_start": "#1a1a2e",
                "gradient_end": "#16213e"
            },
            "new_year_2026": {
                "theme": "holiday",
                "accent_color": "#FFD700",
                "gradient_start": "#0A2E36",
                "gradient_end": "#1B4B5A",
                "snow_effect": True
            },
            "christmas": {
                "theme": "holiday",
                "accent_color": "#FF3333",
                "gradient_start": "#1A3C27",
                "gradient_end": "#0D2818",
                "snow_effect": True
            },
            "light_modern": {
                "theme": "light",
                "accent_color": "#667eea",
                "gradient_start": "#f5f7fa",
                "gradient_end": "#c3cfe2"
            }
        }
    
    def apply_theme_preset(self, preset_name):
        """Применение пресета темы"""
        presets = self.create_theme_presets()
        if preset_name in presets:
            self.settings.update(presets[preset_name])
            self.save_settings()
            return True
        return False
    
# =========== ДОБАВИТЬ ПОСЛЕ CustomizableUI ===========
class CrossPlatformSupport:
    @staticmethod
    def get_platform_info():
        """Получение информации о платформе"""
        system = platform.system()
        info = {
            "system": system,
            "release": platform.release(),
            "version": platform.version(),
            "architecture": platform.architecture()[0],
            "processor": platform.processor() or "Unknown",
            "python_version": platform.python_version(),
            "machine": platform.machine()
        }
        
        # Дополнительная информация для конкретных ОС
        if system == "Darwin":  # macOS
            try:
                import subprocess
                mac_version = subprocess.check_output(
                    ["sw_vers", "-productVersion"], 
                    text=True
                ).strip()
                info["mac_version"] = mac_version
            except:
                pass
        
        elif system == "Windows":
            info["windows_version"] = platform.win32_ver()
        
        elif system == "Linux":
            try:
                import distro
                info["distro"] = distro.name(pretty=True)
                info["distro_version"] = distro.version()
            except:
                pass
        
        return info
    
    @staticmethod
    def get_minecraft_path():
        """Получение пути к Minecraft для текущей ОС"""
        system = platform.system()
        
        if system == "Darwin":  # macOS
            return os.path.expanduser("~/Library/Application Support/minecraft")
        
        elif system == "Windows":
            return os.path.join(os.getenv('APPDATA'), '.minecraft')
        
        elif system == "Linux":
            return os.path.expanduser("~/.minecraft")
        
        else:
            return os.path.expanduser("~/.minecraft")
    
    @staticmethod
    def get_app_data_path():
        """Получение пути для данных приложения"""
        system = platform.system()
        app_name = "SuperLauncher"
        
        if system == "Darwin":  # macOS
            return os.path.expanduser(f"~/Library/Application Support/{app_name}")
        
        elif system == "Windows":
            return os.path.join(os.getenv('APPDATA'), app_name)
        
        elif system == "Linux":
            return os.path.expanduser(f"~/.config/{app_name}")
        
        else:
            return "."
    
    @staticmethod
    def get_java_path():
        """Поиск пути к Java"""
        system = platform.system()
        
        # Общие пути для поиска Java
        common_paths = []
        
        if system == "Darwin":  # macOS
            common_paths = [
                "/usr/bin/java",
                "/Library/Internet Plug-Ins/JavaAppletPlugin.plugin/Contents/Home/bin/java",
                "/System/Library/Frameworks/JavaVM.framework/Versions/Current/Commands/java",
                "/opt/homebrew/opt/openjdk/bin/java",
                "/usr/local/opt/openjdk/bin/java"
            ]
        
        elif system == "Windows":
            program_files = os.getenv("ProgramFiles", "C:\\Program Files")
            program_files_x86 = os.getenv("ProgramFiles(x86)", "C:\\Program Files (x86)")
            
            common_paths = [
                os.path.join(program_files, "Java", "jdk-*", "bin", "java.exe"),
                os.path.join(program_files, "Java", "jre-*", "bin", "java.exe"),
                os.path.join(program_files_x86, "Java", "jdk-*", "bin", "java.exe"),
                os.path.join(program_files_x86, "Java", "jre-*", "bin", "java.exe"),
                "C:\\ProgramData\\Oracle\\Java\\javapath\\java.exe"
            ]
        
        elif system == "Linux":
            common_paths = [
                "/usr/bin/java",
                "/usr/lib/jvm/default-java/bin/java",
                "/usr/lib/jvm/java-*-openjdk/bin/java",
                "/opt/jdk-*/bin/java"
            ]
        
        # Проверка каждого пути
        for path in common_paths:
            if "*" in path:
                # Поиск по шаблону
                import glob
                matches = glob.glob(path)
                if matches:
                    return matches[0]
            else:
                if os.path.exists(path):
                    return path
        
        # Проверка переменной PATH
        import shutil
        java_path = shutil.which("java")
        if java_path:
            return java_path
        
        return ""
    
    @staticmethod
    def is_mac_arm():
        """Проверка Apple Silicon (M1/M2/M3)"""
        if platform.system() == "Darwin":
            try:
                import subprocess
                result = subprocess.run(
                    ["sysctl", "-n", "machdep.cpu.brand_string"],
                    capture_output=True,
                    text=True
                )
                return "Apple" in result.stdout
            except:
                pass
        return False
    
    @staticmethod
    def optimize_for_platform():
        """Оптимизация для конкретной платформы"""
        system = platform.system()
        recommendations = []
        
        if system == "Darwin":
            recommendations = [
                "Используйте ARM-версию Java для лучшей производительности на Apple Silicon",
                "Включите Metal API в настройках Minecraft для улучшения FPS",
                "Проверьте доступность обновлений через App Store"
            ]
        
        elif system == "Windows":
            recommendations = [
                "Убедитесь, что установлены последние драйверы видеокарты",
                "Включите игровой режим в настройках Windows",
                "Проверьте антивирус на предмет блокировки лаунчера"
            ]
        
        elif system == "Linux":
            recommendations = [
                "Установите проприетарные драйверы NVIDIA для лучшей производительности",
                "Используйте OpenJDK 17 или новее",
                "Проверьте права доступа к папке .minecraft"
            ]
        
        return recommendations
    
# =========== ДОБАВИТЬ ПОСЛЕ CrossPlatformSupport ===========
class BuildsManager:
    def __init__(self):
        self.modrinth_api = "https://api.modrinth.com/v2"
        self.curseforge_api = "https://api.curseforge.com/v1"
        self.modpacks_cache = {}
        
    def search_modpacks(self, query="", minecraft_version="", loader="", limit=20):
        """Поиск сборок на Modrinth"""
        try:
            params = {
                "limit": limit,
                "index": "relevance",
                "facets": '[["project_type:modpack"]]'
            }
            
            if query:
                params["query"] = query
            
            # Добавляем версии и лоадеры в facets
            facets = []
            if minecraft_version:
                facets.append(f'["versions:{minecraft_version}"]')
            if loader:
                facets.append(f'["categories:{loader}"]')
            
            if facets:
                params["facets"] = f'[{",".join(facets)}]'
            
            url = f"{self.modrinth_api}/search"
            response = requests.get(url, params=params)
            data = response.json()
            
            modpacks = []
            for hit in data["hits"]:
                modpacks.append({
                    "id": hit["project_id"],
                    "slug": hit.get("slug"),
                    "name": hit["title"],
                    "description": hit.get("description", ""),
                    "icon_url": hit.get("icon_url"),
                    "downloads": hit.get("downloads", 0),
                    "follows": hit.get("follows", 0),
                    "author": hit.get("author", "Unknown"),
                    "versions": hit.get("versions", []),
                    "loaders": hit.get("loaders", []),
                    "source": "modrinth"
                })
            
            return modpacks
            
        except Exception as e:
            print(f"Ошибка поиска сборок: {e}")
            return []
    
    def get_modpack_versions(self, project_id):
        """Получение версий сборки"""
        try:
            url = f"{self.modrinth_api}/project/{project_id}/version"
            response = requests.get(url)
            return response.json()
        except:
            return []
    
    def download_modpack(self, version_id, install_path):
        """Скачивание и установка сборки"""
        try:
            # Получаем информацию о версии
            version_url = f"{self.modrinth_api}/version/{version_id}"
            version_data = requests.get(version_url).json()
            
            # Создаем папку для сборки
            pack_name = version_data["name"]
            pack_folder = os.path.join(install_path, pack_name)
            os.makedirs(pack_folder, exist_ok=True)
            
            # Скачиваем файлы
            files = version_data["files"]
            for file in files:
                if file["primary"]:
                    # Основной файл (обычно .mrpack)
                    download_url = file["url"]
                    filename = file["filename"]
                    filepath = os.path.join(pack_folder, filename)
                    
                    self.download_file(download_url, filepath)
                    
                    # Если это .mrpack файл, распаковываем
                    if filename.endswith(".mrpack"):
                        self.extract_mrpack(filepath, pack_folder)
            
            return pack_folder
            
        except Exception as e:
            print(f"Ошибка скачивания сборки: {e}")
            return None
    
    def download_file(self, url, save_path):
        """Скачивание файла"""
        response = requests.get(url, stream=True)
        total_size = int(response.headers.get("content-length", 0))
        
        with open(save_path, "wb") as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    # Можно добавить прогресс бар здесь
    
    def extract_mrpack(self, mrpack_path, extract_to):
        """Распаковка .mrpack файла"""
        import zipfile
        
        with zipfile.ZipFile(mrpack_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        
        # Создаем конфигурацию для установки
        self.create_install_config(extract_to)
    
    def create_install_config(self, pack_folder):
        """Создание конфигурации для установки"""
        config = {
            "type": "modrinth_modpack",
            "install_path": pack_folder,
            "installed_at": datetime.datetime.now().isoformat()
        }
        
        config_path = os.path.join(pack_folder, "superlauncher_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
    
    def get_installed_packs(self, install_path):
        """Получение списка установленных сборок"""
        installed = []
        
        if os.path.exists(install_path):
            for folder in os.listdir(install_path):
                pack_folder = os.path.join(install_path, folder)
                config_path = os.path.join(pack_folder, "superlauncher_config.json")
                
                if os.path.exists(config_path):
                    try:
                        with open(config_path, "r", encoding="utf-8") as f:
                            config = json.load(f)
                            config["name"] = folder
                            installed.append(config)
                    except:
                        pass
        
        return installed
    
    def create_custom_build(self, name, minecraft_version, loader, mods):
        """Создание кастомной сборки"""
        build_folder = f"builds/{name}_{minecraft_version}_{loader}"
        os.makedirs(build_folder, exist_ok=True)
        
        config = {
            "name": name,
            "minecraft_version": minecraft_version,
            "loader": loader,
            "mods": mods,
            "created_at": datetime.datetime.now().isoformat(),
            "type": "custom"
        }
        
        config_path = os.path.join(build_folder, "build_config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)
        
        return build_folder
    
# =========== ДОБАВИТЬ ПОСЛЕ BuildsManager ===========
class NewYearCountdown(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.new_year = self.get_next_new_year()
        self.update_interval = 1000  # 1 секунда
        
        self.setStyleSheet("""
            NewYearCountdown {
                background-color: rgba(10, 46, 54, 0.8);
                border: 2px solid #FFD700;
                border-radius: 15px;
                padding: 10px;
                font-size: 16px;
                font-weight: bold;
                color: #FFD700;
                text-align: center;
                margin: 5px;
            }
        """)
        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_countdown)
        self.timer.start(self.update_interval)
        
        self.update_countdown()
    
    def get_next_new_year(self):
        """Получение даты следующего Нового Года"""
        now = datetime.datetime.now()
        current_year = now.year
        
        # Если уже январь, следующий Новый Год в следующем году
        if now.month == 1 and now.day < 15:
            return datetime.datetime(current_year, 1, 1, 0, 0, 0)
        else:
            return datetime.datetime(current_year + 1, 1, 1, 0, 0, 0)
    
    def update_countdown(self):
        """Обновление счетчика"""
        now = datetime.datetime.now()
        time_left = self.new_year - now
        
        if time_left.total_seconds() <= 0:
            self.setText("🎉 С НОВЫМ 2026 ГОДОМ! 🎉")
            self.setStyleSheet("""
                NewYearCountdown {
                    background-color: rgba(255, 51, 51, 0.8);
                    border: 3px solid #FFD700;
                    border-radius: 15px;
                    padding: 15px;
                    font-size: 20px;
                    font-weight: bold;
                    color: #FFFFFF;
                    text-align: center;
                    margin: 5px;
                }
            """)
            self.timer.stop()
            
            # Запускаем праздничные эффекты
            self.start_celebration()
        else:
            days = time_left.days
            hours, remainder = divmod(time_left.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            
            # Эмодзи для каждого периода
            emoji = "🎄" if days > 3 else "🎅" if days > 1 else "⏰"
            
            self.setText(
                f"{emoji} До Нового 2026 Года: "
                f"{days} д {hours:02d}:{minutes:02d}:{seconds:02d}"
            )
            
            # Меняем цвет при приближении
            if days == 0:
                self.setStyleSheet("""
                    NewYearCountdown {
                        background-color: rgba(255, 215, 0, 0.3);
                        border: 2px solid #FF3333;
                        border-radius: 15px;
                        padding: 10px;
                        font-size: 18px;
                        font-weight: bold;
                        color: #FF3333;
                        text-align: center;
                        margin: 5px;
                        animation: pulse 2s infinite;
                    }
                """)
    
    def start_celebration(self):
        """Запуск праздничных эффектов"""
        # Можно добавить анимации, звуки и т.д.
        pass

# =========== ДОБАВИТЬ ПОСЛЕ NewYearCountdown ===========
class SkinsManager:
    def __init__(self, account_system):
        self.account_system = account_system
        self.skins_dir = "assets/skins"
        os.makedirs(self.skins_dir, exist_ok=True)
        
        self.load_skin_library()
    
    def load_skin_library(self):
        """Загрузка библиотеки скинов"""
        self.skin_library = {
            "default": {
                "name": "Стандартный",
                "file": "default.png",
                "rarity": "common",
                "unlocked_by_default": True,
                "price": 0
            },
            "santa_hat": {
                "name": "Шапка Санты",
                "file": "santa_hat.png",
                "rarity": "holiday",
                "unlocked_by_default": False,
                "price": 0,  # Бесплатно в праздники
                "holiday_only": True
            },
            "santa_suit": {
                "name": "Костюм Санты",
                "file": "santa_suit.png",
                "rarity": "epic",
                "unlocked_by_default": False,
                "price": 500,  # XP или валюта
                "holiday_only": True
            },
            "new_year_2026": {
                "name": "2026 Новый Год",
                "file": "new_year_2026.png",
                "rarity": "legendary",
                "unlocked_by_default": False,
                "price": 1000,
                "event": "new_year_2026"
            },
            "reindeer": {
                "name": "Олень Рудольф",
                "file": "reindeer.png",
                "rarity": "rare",
                "unlocked_by_default": False,
                "price": 300,
                "holiday_only": True
            },
            "snowman": {
                "name": "Снеговик",
                "file": "snowman.png",
                "rarity": "rare",
                "unlocked_by_default": False,
                "price": 250,
                "holiday_only": True
            }
        }
    
    def get_available_skins(self, user=None):
        """Получение доступных скинов для пользователя"""
        if not user and self.account_system.current_user:
            user = self.account_system.current_user
        
        available_skins = []
        
        for skin_id, skin_data in self.skin_library.items():
            # Проверяем условия доступа
            if self.can_access_skin(skin_id, user):
                available_skins.append({
                    "id": skin_id,
                    **skin_data,
                    "unlocked": self.is_skin_unlocked(skin_id, user)
                })
        
        return available_skins
    
    def can_access_skin(self, skin_id, user):
        """Проверка доступа к скину"""
        skin_data = self.skin_library.get(skin_id)
        if not skin_data:
            return False
        
        # Проверка праздничных ограничений
        if skin_data.get("holiday_only"):
            holiday_theme = HolidayTheme()
            if not holiday_theme.current_holiday:
                return False
        
        # Проверка ивентов
        if skin_data.get("event"):
            # Проверка участия в ивенте
            pass
        
        return True
    
    def is_skin_unlocked(self, skin_id, user):
        """Проверка разблокирован ли скин"""
        if not user:
            return False
        
        # По умолчанию разблокированы
        if skin_id == "default":
            return True
        
        # Проверяем в списке скинов пользователя
        user_skins = user.get("skins", ["default"])
        return skin_id in user_skins
    
    def unlock_skin(self, skin_id, user):
        """Разблокировка скина"""
        if self.is_skin_unlocked(skin_id, user):
            return False, "Скин уже разблокирован"
        
        skin_data = self.skin_library.get(skin_id)
        if not skin_data:
            return False, "Скин не найден"
        
        # Проверяем условия
        if not self.can_access_skin(skin_id, user):
            return False, "Скин недоступен"
        
        # Проверяем цену
        price = skin_data.get("price", 0)
        if price > 0:
            user_xp = user.get("xp", 0)
            if user_xp < price:
                return False, f"Недостаточно XP (нужно {price})"
            
            # Списываем XP
            user["xp"] = user_xp - price
        
        # Добавляем скин
        if "skins" not in user:
            user["skins"] = []
        
        user["skins"].append(skin_id)
        
        # Сохраняем обновления
        self.account_system.save_accounts(
            self.account_system.load_accounts()
        )
        
        return True, f"Скин '{skin_data['name']}' разблокирован!"
    
    def apply_skin_to_minecraft(self, skin_id):
        """Применение скина в Minecraft"""
        if not self.account_system.current_user:
            return False, "Требуется вход в аккаунт"
        
        skin_data = self.skin_library.get(skin_id)
        if not skin_data:
            return False, "Скин не найден"
        
        # Проверяем разблокирован ли скин
        if not self.is_skin_unlocked(skin_id, self.account_system.current_user):
            return False, "Скин не разблокирован"
        
        # Путь к файлу скина
        skin_file = os.path.join(self.skins_dir, skin_data["file"])
        if not os.path.exists(skin_file):
            return False, "Файл скина не найден"
        
        # Копируем скин в папку Minecraft
        minecraft_path = CrossPlatformSupport.get_minecraft_path()
        skins_path = os.path.join(minecraft_path, "skins")
        os.makedirs(skins_path, exist_ok=True)
        
        # Копируем файл
        import shutil
        shutil.copy2(skin_file, os.path.join(skins_path, "custom_skin.png"))
        
        # Обновляем настройки пользователя
        self.account_system.current_user["current_skin"] = skin_id
        
        return True, f"Скин '{skin_data['name']}' применен!"
    
    def upload_custom_skin(self, image_path):
        """Загрузка кастомного скина"""
        if not self.account_system.current_user:
            return False, "Требуется вход в аккаунт"
        
        # Проверяем файл
        if not os.path.exists(image_path):
            return False, "Файл не найден"
        
        # Проверяем размер и формат
        try:
            from PIL import Image
            img = Image.open(image_path)
            
            # Minecraft скины обычно 64x64 или 64x32
            if img.size not in [(64, 64), (64, 32)]:
                return False, "Неверный размер скина (должен быть 64x64 или 64x32)"
            
            # Сохраняем в папку пользователя
            user_folder = self.account_system.get_user_folder()
            user_skins_dir = os.path.join(user_folder, "skins")
            os.makedirs(user_skins_dir, exist_ok=True)
            
            # Генерируем имя файла
            skin_id = f"custom_{secrets.token_hex(8)}"
            skin_filename = f"{skin_id}.png"
            skin_path = os.path.join(user_skins_dir, skin_filename)
            
            # Копируем/конвертируем
            img.save(skin_path)
            
            # Добавляем в библиотеку пользователя
            self.account_system.current_user.setdefault("custom_skins", []).append({
                "id": skin_id,
                "name": "Мой скин",
                "file": skin_filename,
                "uploaded_at": datetime.datetime.now().isoformat()
            })
            
            return True, skin_id
            
        except Exception as e:
            return False, f"Ошибка обработки изображения: {e}"
        
# =========== ДОБАВИТЬ ПОСЛЕ SkinsManager ===========
class LoginDialog(QDialog):
    def __init__(self, account_system, parent=None):
        super().__init__(parent)
        self.account_system = account_system
        self.user_data = None
        
        self.setWindowTitle("👤 Вход / Регистрация")
        self.setFixedSize(400, 500)
        
        layout = QVBoxLayout()
        
        # Заголовок
        title = QLabel("🎄 SuperLauncher Аккаунт")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: #4facfe;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Вкладки: Вход / Регистрация
        self.tab_widget = QTabWidget()
        
        # Вкладка входа
        login_tab = QWidget()
        self.setup_login_tab(login_tab)
        self.tab_widget.addTab(login_tab, "Вход")
        
        # Вкладка регистрации
        register_tab = QWidget()
        self.setup_register_tab(register_tab)
        self.tab_widget.addTab(register_tab, "Регистрация")
        
        layout.addWidget(self.tab_widget)
        
        # Кнопки
        button_layout = QHBoxLayout()
        
        self.btn_login = QPushButton("Войти")
        self.btn_login.clicked.connect(self.perform_login)
        button_layout.addWidget(self.btn_login)
        
        self.btn_register = QPushButton("Зарегистрироваться")
        self.btn_register.clicked.connect(self.perform_register)
        button_layout.addWidget(self.btn_register)
        
        self.btn_cancel = QPushButton("Отмена")
        self.btn_cancel.clicked.connect(self.reject)
        button_layout.addWidget(self.btn_cancel)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def setup_login_tab(self, tab):
        """Настройка вкладки входа"""
        layout = QFormLayout(tab)
        
        self.login_username = QLineEdit()
        self.login_username.setPlaceholderText("Имя пользователя или Email")
        layout.addRow("Логин:", self.login_username)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Пароль")
        self.login_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", self.login_password)
        
        # Запомнить меня
        self.remember_me = QCheckBox("Запомнить меня")
        layout.addRow(self.remember_me)
        
        # Ссылка "Забыли пароль?"
        forgot_link = QLabel('<a href="#" style="color: #4facfe;">Забыли пароль?</a>')
        forgot_link.setOpenExternalLinks(False)
        forgot_link.linkActivated.connect(self.forgot_password)
        layout.addRow(forgot_link)
        
        tab.setLayout(layout)
    
    def setup_register_tab(self, tab):
        """Настройка вкладки регистрации"""
        layout = QFormLayout(tab)
        
        self.register_username = QLineEdit()
        self.register_username.setPlaceholderText("Придумайте имя пользователя")
        layout.addRow("Имя пользователя:", self.register_username)
        
        self.register_email = QLineEdit()
        self.register_email.setPlaceholderText("Ваш email")
        layout.addRow("Email:", self.register_email)
        
        self.register_password = QLineEdit()
        self.register_password.setPlaceholderText("Придумайте пароль")
        self.register_password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Пароль:", self.register_password)
        
        self.register_password_confirm = QLineEdit()
        self.register_password_confirm.setPlaceholderText("Повторите пароль")
        self.register_password_confirm.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Подтверждение:", self.register_password_confirm)
        
        # Соглашение
        self.terms_agreement = QCheckBox("Я принимаю условия пользования")
        layout.addRow(self.terms_agreement)
        
        tab.setLayout(layout)
    
    def perform_login(self):
        """Выполнение входа"""
        username = self.login_username.text().strip()
        password = self.login_password.text()
        
        if not username or not password:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        success, result = self.account_system.login(username, password)
        
        if success:
            self.user_data = result
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка входа", result)
    
    def perform_register(self):
        """Выполнение регистрации"""
        username = self.register_username.text().strip()
        email = self.register_email.text().strip()
        password = self.register_password.text()
        password_confirm = self.register_password_confirm.text()
        
        # Валидация
        if not all([username, email, password, password_confirm]):
            QMessageBox.warning(self, "Ошибка", "Заполните все поля")
            return
        
        if password != password_confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают")
            return
        
        if len(password) < 6:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть не менее 6 символов")
            return
        
        if not self.terms_agreement.isChecked():
            QMessageBox.warning(self, "Ошибка", "Примите условия пользования")
            return
        
        # Регистрация
        success, result = self.account_system.register_user(username, email, password)
        
        if success:
            self.user_data = result
            self.accept()
        else:
            QMessageBox.critical(self, "Ошибка регистрации", result)
    
    def forgot_password(self):
        """Восстановление пароля"""
        QMessageBox.information(self, "Восстановление пароля",
                              "Функция в разработке. Свяжитесь с поддержкой.")
    
    def get_user(self):
        """Получение данных пользователя"""
        return self.user_data
    
# =========== ДОБАВИТЬ ПОСЛЕ LoginDialog ===========
class GiftNotification(QDialog):
    def __init__(self, gift_data, parent=None):
        super().__init__(parent)
        self.gift_data = gift_data
        
        self.setWindowTitle("🎁 Новый подарок!")
        self.setFixedSize(400, 300)
        
        layout = QVBoxLayout()
        
        # Иконка подарка
        icon_label = QLabel(gift_data.get("icon", "🎁"))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet("font-size: 64px;")
        layout.addWidget(icon_label)
        
        # Название
        name_label = QLabel(f"<h2>{gift_data['name']}</h2>")
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        name_label.setStyleSheet("color: #FFD700;")
        layout.addWidget(name_label)
        
        # Описание
        description = self.get_gift_description(gift_data)
        desc_label = QLabel(description)
        desc_label.setWordWrap(True)
        desc_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(desc_label)
        
        # Кнопка
        self.btn_claim = QPushButton("Получить подарок!")
        self.btn_claim.setStyleSheet("""
            QPushButton {
                background-color: #FF3333;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 15px;
                border-radius: 10px;
            }
        """)
        self.btn_claim.clicked.connect(self.accept)
        layout.addWidget(self.btn_claim)
        
        self.setLayout(layout)
    
    def get_gift_description(self, gift_data):
        """Получение описания подарка"""
        gift_type = gift_data["type"]
        
        if gift_type == "xp":
            return f"Вы получили {gift_data['amount']} опыта!"
        elif gift_type == "skin":
            return f"Новый скин: {gift_data['name']}"
        elif gift_type == "theme":
            return f"Новая тема оформления!"
        elif gift_type == "premium":
            return f"Премиум доступ на {gift_data['days']} дней!"
        elif gift_type == "resource_pack":
            return "Новый набор текстур!"
        else:
            return "Специальный подарок!"

class AnimatedButton(QPushButton):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._animation_progress = 0
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(45)

        self.animation = QPropertyAnimation(self, b"animation_progress")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def get_animation_progress(self):
        return self._animation_progress

    def set_animation_progress(self, value):
        self._animation_progress = value
        self.update()

    animation_progress = pyqtProperty(float, get_animation_progress, set_animation_progress)

    def enterEvent(self, event):
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(1, QColor("#764ba2"))

        if self._animation_progress > 0:
            bg_color = QColor(47, 47, 47)
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor(79, 172, 254), 2))
            painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

            fill_width = int(self.width() * self._animation_progress)
            painter.setBrush(QBrush(gradient))
            painter.setPen(Qt.PenStyle.NoPen)
            painter.drawRoundedRect(1, 1, fill_width, self.height() - 2, 8, 8)
        else:
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(79, 172, 254), 2))
            painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 8, 8)

        painter.setPen(QPen(QColor(255, 255, 255)))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class GlassFrame(QFrame):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            GlassFrame {
                background: rgba(25, 25, 35, 0.85);
                border: 1px solid rgba(255, 255, 255, 0.15);
                border-radius: 20px;
            }
        """)


class ModernSidebar(QWidget):
    def __init__(self, main_window, parent=None):
        super().__init__(parent)
        self.main_window = main_window
        # Уменьшаем ширину для компактности
        self.setFixedWidth(90)  # Было 70
        self.expanded_width = 280  # Было 220
        self.is_expanded = False
        
        # Упрощаем стиль
        self.setStyleSheet("""
            ModernSidebar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 rgba(20, 20, 30, 0.95), 
                    stop:1 rgba(35, 35, 45, 0.95));
                border-right: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)

        layout = QVBoxLayout()
        layout.setContentsMargins(5, 15, 5, 15)
        layout.setSpacing(8)

        self.burger_btn = AnimatedButton("☰")
        self.burger_btn.setFixedSize(55, 55)
        self.burger_btn.clicked.connect(self.toggle_expand)
        layout.addWidget(self.burger_btn)

        layout.addSpacing(25)

        self.nav_buttons = []
        
        # ОПРЕДЕЛЯЕМ ТОЛЬКО РЕАЛЬНЫЕ СТРАНИЦЫ
        # Порядок должен совпадать с порядком добавления в QStackedWidget
        self.nav_items = [
            ("🏠", "Главная", "#ff6b6b"),
            ("👤", "Аккаунт", "#4ecdc4"),
            ("🎁", "Подарки", "#45b7d1"),
            ("🧩", "Моды", "#96ceb4"),
            ("📦", "Сборки", "#feca57"),
            ("🖼️", "Скины", "#ff9ff3"),
            ("📢", "Новости", "#54a0ff"),
            ("🔄", "Обновления", "#5f27cd"),
            ("🖧", "Серверы", "#ff9f43"),
            ("⚙️", "Настройки", "#00d2d3"),
            ("⛏️", "Minecraft", "#1dd1a1")
        ]

        for icon, text, color in self.nav_items:
            btn = self.create_nav_button(icon, text, color)
            self.nav_buttons.append(btn)
            layout.addWidget(btn)

        layout.addStretch()
        
        # Статус пользователя
        self.user_status = QLabel("👤 Гость")
        self.user_status.setStyleSheet("""
            QLabel {
                color: #888;
                font-size: 10px;
                padding: 5px;
                text-align: center;
            }
        """)
        layout.addWidget(self.user_status)

        self.setLayout(layout)

        self.animation = QPropertyAnimation(self, b"minimumWidth")
        self.animation.setDuration(350)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)

    def create_nav_button(self, icon, text, color):
        btn = QPushButton(f"  {icon}")
        btn.setFixedHeight(55)
        btn.setCheckable(True)
        btn.setProperty("color", color)
        btn.setProperty("full_text", f"  {icon}  {text}")
        btn.setProperty("short_text", f"  {icon}")

        # УПРОЩЕННЫЙ CSS БЕЗ transition И transform
        btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: white;
                font-size: 22px;
                text-align: left;
                padding-left: 12px;
                border-radius: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background: rgba(255, 255, 255, 0.08);
                border: 1px solid rgba(255, 255, 255, 0.2);
            }}
            QPushButton:checked {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2);
                border: 1px solid qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #667eea,
                    stop:1 #764ba2);
            }}
        """)

        btn.clicked.connect(lambda checked, idx=len(self.nav_buttons): self.on_nav_clicked(idx))
        return btn

    def on_nav_clicked(self, index):
        # Проверяем, что индекс в пределах допустимого
        if index < len(self.main_window.pages):
            self.main_window.pages.setCurrentIndex(index)
            for i, btn in enumerate(self.nav_buttons):
                btn.setChecked(i == index)
        else:
            print(f"Ошибка: страница с индексом {index} не существует")

    def toggle_expand(self):
        self.is_expanded = not self.is_expanded

        if self.is_expanded:
            self.animation.setStartValue(70)
            self.animation.setEndValue(self.expanded_width)
            for btn in self.nav_buttons:
                btn.setText(btn.property("full_text"))
        else:
            self.animation.setStartValue(self.expanded_width)
            self.animation.setEndValue(70)
            for btn in self.nav_buttons:
                btn.setText(btn.property("short_text"))

        self.animation.start()

class GradientLabel(QLabel):
    def __init__(self, text="", parent=None):
        super().__init__(text, parent)
        self._animation_progress = 0

        self.animation = QPropertyAnimation(self, b"animation_progress")
        self.animation.setDuration(2000)
        self.animation.setLoopCount(-1)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)

    def get_animation_progress(self):
        return self._animation_progress

    def set_animation_progress(self, value):
        self._animation_progress = value
        self.update()

    animation_progress = pyqtProperty(float, get_animation_progress, set_animation_progress)

    def showEvent(self, event):
        self.animation.start()
        super().showEvent(event)

    def hideEvent(self, event):
        self.animation.stop()
        super().hideEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        gradient = QLinearGradient(0, 0, self.width(), 0)
        gradient.setColorAt(0, QColor("#667eea"))
        gradient.setColorAt(0.5, QColor("#764ba2"))
        gradient.setColorAt(1, QColor("#667eea"))

        painter.setPen(QPen(QBrush(gradient), 2))
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class LaunchThread(QThread):
    launch_setup_signal = pyqtSignal(str, str)
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
        self.version_id = ''
        self.username = ''
        self.loader_type = 'vanilla'  # по умолчанию ванилла
        self.progress = 0
        self.progress_max = 100
        self.progress_label = ''

    def launch_setup(self, version_id, username):
        self.username = username
        # Убираем проверку forge и fabric
        self.loader_type = "vanilla"
        self.version_id = version_id

    def update_progress_label(self, value):
        self.progress_label = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress(self, value):
        self.progress = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def update_progress_max(self, value):
        self.progress_max = value
        self.progress_update_signal.emit(self.progress, self.progress_max, self.progress_label)

    def run(self):
        self.state_update_signal.emit(True)
        try:
            if self.loader_type == "vanilla":
                install_minecraft_version(
                    version=self.version_id,
                    minecraft_directory=minecraft_directory,
                    callback={
                        'setStatus': self.update_progress_label,
                        'setProgress': self.update_progress,
                        'setMax': self.update_progress_max
                    }
                )
            else:
                raise Exception("Неизвестный тип загрузчика")

            if self.username == '':
                self.username = generate_username()[0]

            options = {
                'username': self.username,
                'uuid': str(uuid1()),
                'token': ''
            }
            cmd = get_minecraft_command(
                version=self.version_id,
                minecraft_directory=minecraft_directory,
                options=options
            )
            print("Запускаем команду:", cmd)
            proc = subprocess.Popen(cmd, cwd=minecraft_directory)
            proc.wait()
            print(f"Процесс Minecraft завершился с кодом: {proc.returncode}")
        except Exception as e:
            print("Ошибка при запуске Minecraft:", e)
        finally:
            self.state_update_signal.emit(False)


# Функция возвращает все версии без фильтрации (Vanilla + Snapshots + Fabric + Forge)
def get_all_versions():
    versions = get_version_list()  # vanilla + snapshots
    versions_dir = os.path.join(minecraft_directory, 'versions')
    if os.path.exists(versions_dir):
        for folder in os.listdir(versions_dir):
            full_path = os.path.join(versions_dir, folder)
            if os.path.isdir(full_path):
                if not any(v['id'] == folder for v in versions):
                    versions.append({'id': folder})
    return versions


class MinecraftLauncherPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # сохраняем ссылку на родителя
        self.config = load_config()  # читаем текущий язык

        # Логотип
        self.logo = QLabel()
        self.logo.setMaximumSize(QSize(256, 37))
        pixmap = QPixmap('assets/title.png')
        if not pixmap.isNull():
            self.logo.setPixmap(pixmap)
        self.logo.setScaledContents(True)

        # Spacer
        self.titlespacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        # Поле для имени пользователя
        self.username = QLineEdit()
        self.username.setPlaceholderText(self.tr("Username"))
        self.username.setStyleSheet("""
            background-color: #2f2f2f;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 5px;
        """)

        # Список версий
        self.version_select = QComboBox()
        self.version_select.setStyleSheet("""
            background-color: #2f2f2f;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 3px;
        """)
        self.update_versions_list()

        # Прогрессбар
        self.progress_spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)
        self.start_progress_label = QLabel('')
        self.start_progress_label.setVisible(False)
        self.start_progress = QProgressBar()
        self.start_progress.setValue(0)
        self.start_progress.setVisible(False)

        # Кнопка запуска
        self.start_button = QPushButton(self.tr("Play"))
        self.start_button.setStyleSheet("""
            background-color: #2f2f2f;
            color: white;
            border: 1px solid #4facfe;
            border-radius: 8px;
            padding: 8px;
            font-weight: bold;
        """)
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.addWidget(self.logo, 0, Qt.AlignmentFlag.AlignHCenter)
        layout.addItem(self.titlespacer)
        layout.addWidget(self.username)
        layout.addWidget(self.version_select)
        layout.addItem(self.progress_spacer)
        layout.addWidget(self.start_progress_label)
        layout.addWidget(self.start_progress)
        layout.addWidget(self.start_button)

    # --- Перевод ---
    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.username.setPlaceholderText(self.tr("Username"))
        self.start_button.setText(self.tr("Play"))

    # --- Версии Minecraft ---
    def update_versions_list(self):
        self.version_select.clear()
        versions = self.get_all_versions()
        for version in versions:
            self.version_select.addItem(version['id'])

    @staticmethod
    def get_all_versions():
        from minecraft_launcher_lib.utils import get_version_list, get_minecraft_directory
        versions = []

        try:
            online_versions = get_version_list()
            versions.extend(online_versions)
        except Exception as e:
            print("Онлайн-версии недоступны, используем локальные:", e)

        versions_dir = os.path.join(get_minecraft_directory(), 'versions')
        if os.path.exists(versions_dir):
            for folder in os.listdir(versions_dir):
                full_path = os.path.join(versions_dir, folder)
                if os.path.isdir(full_path):
                    if not any(v['id'] == folder for v in versions):
                        versions.append({'id': folder})

        if not versions:
            versions.append({'id': 'No versions available'})
        return versions


class SettingsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.labels = {}
        self.buttons = {}

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ===== Тема =====
        self.labels["theme"] = QLabel()
        layout.addWidget(self.labels["theme"])
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["dark", "light"])
        self.theme_combo.setCurrentText(self.config.get("theme", "dark"))
        layout.addWidget(self.theme_combo)

        # ===== Язык =====
        self.labels["lang"] = QLabel()
        layout.addWidget(self.labels["lang"])
        self.lang_combo = QComboBox()
        self.lang_combo.addItems(list(translations.keys()))
        self.lang_combo.setCurrentText(self.config.get("language", "ru"))
        self.lang_combo.currentTextChanged.connect(self.change_language)
        layout.addWidget(self.lang_combo)

        # ===== Способ запуска =====
        self.labels["launch_mode"] = QLabel()
        layout.addWidget(self.labels["launch_mode"])
        self.rb_launcher_lib = QRadioButton()
        self.rb_java = QRadioButton()
        layout.addWidget(self.rb_launcher_lib)
        layout.addWidget(self.rb_java)
        launch_mode = self.config.get("launch_mode", "launcher_lib")
        if launch_mode == "java":
            self.rb_java.setChecked(True)
        else:
            self.rb_launcher_lib.setChecked(True)

        # ===== Путь к Java =====
        self.labels["java_path"] = QLabel()
        layout.addWidget(self.labels["java_path"])
        self.java_path_input = QLineEdit(self.config.get("java_path", ""))
        layout.addWidget(self.java_path_input)
        self.buttons["browse_java"] = QPushButton()
        layout.addWidget(self.buttons["browse_java"])
        self.buttons["browse_java"].clicked.connect(self.browse_java)

        self.java_path_input.setEnabled(self.rb_java.isChecked())
        self.buttons["browse_java"].setEnabled(self.rb_java.isChecked())
        self.rb_java.toggled.connect(self.java_path_input.setEnabled)
        self.rb_java.toggled.connect(self.buttons["browse_java"].setEnabled)

        # ===== Фоны страниц =====
        self.labels["page_bg"] = QLabel()
        layout.addWidget(self.labels["page_bg"])
        self.bg_buttons = {}
        self.bg_options = {
            "dark": "assets/bg_dark.png",
            "gray": "assets/bg_gray.png"
        }
        bg_layout = QHBoxLayout()
        for key, img in self.bg_options.items():
            btn = QPushButton()
            btn.setCheckable(True)
            btn.setIcon(QIcon(img))
            btn.setIconSize(QSize(120, 80))
            btn.setFixedSize(130, 90)
            btn.setStyleSheet("border: 2px solid transparent; border-radius: 8px;")
            btn.clicked.connect(lambda checked, k=key: self.select_bg(k))
            bg_layout.addWidget(btn)
            self.bg_buttons[key] = btn
        layout.addLayout(bg_layout)
        current_bg = self.config.get("page_bg", "dark")
        self.select_bg(current_bg)

        # ===== Кнопка сохранить =====
        self.buttons["save"] = QPushButton()
        layout.addWidget(self.buttons["save"])
        self.buttons["save"].clicked.connect(self.save_settings)

        self.setLayout(layout)
        self.update_texts()

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def update_texts(self):
        self.labels["theme"].setText(self.tr("Theme:"))
        self.labels["lang"].setText(self.tr("Language:"))
        self.labels["launch_mode"].setText(self.tr("Minecraft launch mode:"))
        self.rb_launcher_lib.setText(self.tr("minecraft-launcher-lib (default)"))
        self.rb_java.setText(self.tr("Java (specify path)"))
        self.labels["java_path"].setText(self.tr("Java path (if Java is selected):"))
        self.buttons["browse_java"].setText(self.tr("Browse Java path"))
        self.labels["page_bg"].setText(self.tr("Page backgrounds:"))
        self.buttons["save"].setText(self.tr("Save settings"))

        # если родитель имеет метод refresh_language, обновляем и его
        parent = self.parent()
        if parent and hasattr(parent, "refresh_language"):
            parent.refresh_language()

    def change_language(self, lang):
        self.config["language"] = lang
        self.update_texts()

    def select_bg(self, key):
        for k, btn in self.bg_buttons.items():
            if k == key:
                btn.setChecked(True)
                btn.setStyleSheet("border: 2px solid #4facfe; border-radius: 8px;")
            else:
                btn.setChecked(False)
                btn.setStyleSheet("border: 2px solid transparent; border-radius: 8px;")
        self.config["page_bg"] = key

    def browse_java(self):
        file, _ = QFileDialog.getOpenFileName(
            self, self.tr("Browse Java path"), "", "Executable Files (*.exe);;All Files (*)"
        )
        if file:
            self.java_path_input.setText(file)

    def save_settings(self):
        self.config["theme"] = self.theme_combo.currentText()
        self.config["language"] = self.lang_combo.currentText()
        self.config["launch_mode"] = "java" if self.rb_java.isChecked() else "launcher_lib"
        self.config["java_path"] = self.java_path_input.text()
        self.config["page_bg"] = self.config.get("page_bg", "dark")
        save_config(self.config)
        self.update_texts()


class ModDownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, save_path):
        super().__init__()
        self.url = url
        self.save_path = save_path

    def run(self):
        try:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0

                with open(self.save_path, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                self.progress.emit(int(downloaded * 100 / total))
            self.finished.emit(self.save_path)
        except Exception as e:
            self.finished.emit(f"ERROR: {e}")


class DiscordRPCThread(threading.Thread):
    def __init__(self, main_window):
        super().__init__()
        self.client_id = "1405145554027155456"
        self.rpc = None
        self.main_window = main_window
        self.running = True
        self.connected = False  # Флаг успешного подключения

    def run(self):
        try:
            self.rpc = Presence(self.client_id)
            try:
                self.rpc.connect()
                self.connected = True
                print("Discord RPC connected successfully.")
            except Exception as e:
                print(f"Discord RPC not connected: {e}")
                self.connected = False
                return  # Если не подключилось, выходим из потока

            while self.running:
                current_page = self.main_window.pages.currentIndex()
                page_names = ["Home", "Mods", "News", "Updates", "Servers", "Settings", "Minecraft"]
                details = f"На странице: {page_names[current_page]}"
                state = "Суперлаунчер 1.4.0.8"

                try:
                    self.rpc.update(
                        details=details,
                        state=state,
                        large_image="superlauncher",
                        small_image="minecraft",
                        start=time.time()
                    )
                except Exception as e:
                    print(f"Discord RPC update error: {e}")

                time.sleep(15)
        except Exception as e:
            print(f"Discord RPC thread error: {e}")

    def stop(self):
        self.running = False
        if self.rpc and self.connected:
            try:
                self.rpc.close()
                print("Discord RPC closed successfully.")
            except Exception as e:
                print(f"Error closing Discord RPC: {e}")


class ModsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config = load_config()

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)

        self.mods_dir = os.path.join(minecraft_directory, "mods")
        os.makedirs(self.mods_dir, exist_ok=True)

        # Заголовок
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 10px; color: white;")
        self.layout.addWidget(self.title)

        # Поиск
        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_mods)
        self.layout.addWidget(self.search_input)

        # Список результатов
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(64, 64))
        self.layout.addWidget(self.results_list)

        # Кнопки
        buttons_layout = QHBoxLayout()
        self.open_folder_button = QPushButton()
        self.open_folder_button.clicked.connect(self.open_mods_folder)
        buttons_layout.addWidget(self.open_folder_button)

        self.delete_all_button = QPushButton()
        self.delete_all_button.setStyleSheet("background-color: #d9534f; color: white;")
        self.delete_all_button.clicked.connect(self.delete_all_mods)
        buttons_layout.addWidget(self.delete_all_button)

        self.layout.addLayout(buttons_layout)

        self.load_featured_mods()
        self.update_texts()

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def update_texts(self):
        self.title.setText(f"🧩 {self.tr('Mods from Modrinth')}")
        self.search_input.setPlaceholderText(f"🔍 {self.tr('Search mod...')}")
        self.open_folder_button.setText(f"📂 {self.tr('Open mods folder')}")
        self.delete_all_button.setText(f"🗑 {self.tr('Delete all mods')}")

    def load_featured_mods(self):
        try:
            url = f"{MODRINTH_API}/search?limit=20&index=relevance"
            resp = requests.get(url)
            data = resp.json()
            self.results_list.clear()
            for hit in data["hits"]:
                item = QListWidgetItem(f"{hit['title']} — {hit.get('description', '')}")
                item.setData(Qt.ItemDataRole.UserRole, hit["project_id"])
                self.results_list.addItem(item)
            self.results_list.itemClicked.connect(self.show_mod_dialog)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def search_mods(self):
        query = self.search_input.text()
        if not query.strip():
            return
        try:
            url = f"{MODRINTH_API}/search?query={query}"
            resp = requests.get(url)
            data = resp.json()
            self.results_list.clear()
            for hit in data["hits"]:
                item = QListWidgetItem(f"{hit['title']} — {hit.get('description', '')}")
                item.setData(Qt.ItemDataRole.UserRole, hit["project_id"])
                self.results_list.addItem(item)
            self.results_list.itemClicked.connect(self.show_mod_dialog)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def show_mod_dialog(self, item):
        project_id = item.data(Qt.ItemDataRole.UserRole)
        try:
            versions_url = f"{MODRINTH_API}/project/{project_id}/version"
            resp = requests.get(versions_url)
            versions = resp.json()

            if not versions:
                QMessageBox.warning(self, self.tr("No available versions"),
                                    self.tr("No versions available"))
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(self.tr("Install mod"))
            layout = QVBoxLayout(dialog)

            version_box = QComboBox()
            version_loader_map = {}
            for v in versions:
                mc_versions = v["game_versions"]
                loaders = v["loaders"]
                if not mc_versions or not loaders:
                    continue
                display_text = f"{mc_versions[0]} | {loaders[0]}"
                version_loader_map[display_text] = v

            if not version_loader_map:
                QMessageBox.warning(self, self.tr("No supported builds"),
                                    self.tr("No supported builds"))
                return

            version_box.addItems(version_loader_map.keys())
            layout.addWidget(QLabel(self.tr("Minecraft version and loader:")))
            layout.addWidget(version_box)

            install_button = QPushButton(self.tr("Install mod"))
            layout.addWidget(install_button)

            install_button.clicked.connect(
                lambda: self.download_selected_mod(version_loader_map[version_box.currentText()], dialog)
            )

            dialog.exec()

        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def download_selected_mod(self, version_data, dialog):
        files = version_data["files"]
        for file in files:
            if file["filename"].endswith(".jar"):
                url = file["url"]
                filename = file["filename"]
                save_path = os.path.join(self.mods_dir, filename)
                dialog.close()
                self.start_download(url, save_path)
                return
        QMessageBox.warning(self, self.tr("File not found"),
                            self.tr("File not found"))

    def start_download(self, url, save_path):
        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle(self.tr("Downloading mod"))
        self.progress_dialog.setModal(True)

        dialog_layout = QVBoxLayout(self.progress_dialog)
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        dialog_layout.addWidget(self.progress_bar)

        self.progress_dialog.show()

        self.download_thread = ModDownloadThread(url, save_path)
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(self.on_download_finished)
        self.download_thread.start()

    def on_download_finished(self, result):
        self.progress_dialog.hide()
        if result.startswith("ERROR:"):
            QMessageBox.critical(self, self.tr("Error"), result)
        else:
            QMessageBox.information(self, self.tr("Done"),
                                    f"{self.tr('Mod installed successfully:')}\n{result}")

    def open_mods_folder(self):
        path = os.path.realpath(self.mods_dir)
        if sys.platform == "win32":
            os.startfile(path)
        elif sys.platform == "darwin":
            os.system(f"open \"{path}\"")
        else:
            os.system(f"xdg-open \"{path}\"")

    def delete_all_mods(self):
        confirm = QMessageBox.question(
            self, self.tr("Delete all mods"),
            self.tr("Are you sure you want to delete all mods?"),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            deleted = 0
            for file in os.listdir(self.mods_dir):
                if file.endswith(".jar"):
                    try:
                        os.remove(os.path.join(self.mods_dir, file))
                        deleted += 1
                    except Exception as e:
                        QMessageBox.warning(self, self.tr("Error"),
                                            f"{self.tr('Could not delete')} {file}: {e}")
            QMessageBox.information(self, self.tr("Done"),
                                    f"{self.tr('All mods deleted')}: {deleted}")


class NewsPage(QWidget):
    def __init__(self, parent=None, language="en"):
        super().__init__(parent)
        self.parent_window = parent
        self.language = language  # Текущий язык

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        # Заголовок
        self.title = QLabel()
        self.title.setStyleSheet("font-size: 26px; font-weight: bold; margin-bottom: 15px; color: white;")
        layout.addWidget(self.title)

        # Scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.scroll_area.setWidget(self.container)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(12)

        # Новости
        self.news_list = [
            ("2025-08-12 v1.4.0.7", "Добавлен Discord RPC"),
            ("2025-07-24 v1.4.0.5", "Добавлена поддержка скачивания модов из Modrind и настроек лаунчера"),
            ("2025-07-23 v1.4.0.4",
             "Добавлена возможность создавать и управлять локальными Minecraft-серверами прямо из лаунчера..."),
            ("2025-07-23 v1.4.0.3", "Добавлен новый дизайн и восстановлен код"),
            ("2025-06-26 v1.4.0.2", "Добавлен новый дизайн, но утерян код"),
            ("2025-06-26 v1.4.0.1", "Исправлены баги, но дизайн устаревший"),
            ("2025-06-26 v1.4.0.0", "Исправлены баги, но дизайн устаревший"),
            ("2025-06-26 v1.3", "Лаунчер выйдет из бета в следующем релизе")
        ]

        self.news_labels = []  # Сохраняем лейблы для обновления текста
        self.update_texts()
        self.populate_news()

    def _tr(self, text):
        return translations.get(self.language, {}).get(text, text)

    def update_texts(self):
        self.title.setText(self._tr("News"))

    def populate_news(self):
        # Очищаем контейнер перед заполнением
        for i in reversed(range(self.container_layout.count())):
            widget = self.container_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # Добавление новостей
        for date, text in self.news_list:
            translated_text = self._tr(text)
            news_label = QLabel(f"<b>{date}</b>: {translated_text}")
            news_label.setWordWrap(True)
            news_label.setStyleSheet("font-size: 16px; color: #c0c0c0;")
            self.container_layout.addWidget(news_label)
            self.news_labels.append(news_label)

        self.container_layout.addStretch()

    def set_language(self, language):
        self.language = language
        self.update_texts()
        self.populate_news()


CURRENT_VERSION = "v1.4.0.5"


class UpdateDownloadThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            with requests.get(self.url, stream=True) as r:
                r.raise_for_status()
                total_length = int(r.headers.get("content-length", 0))
                downloaded = 0
                with open(self.filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_length > 0:
                                percent = int(downloaded * 100 / total_length)
                                self.progress.emit(percent)
            self.finished.emit(str(self.filename))
        except Exception as e:
            self.finished.emit(f"ERROR: {str(e)}")


class UpdatesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        self.title = QLabel("🔄 Проверка обновлений")
        self.title.setStyleSheet("font-size:26px;font-weight:bold;color:white;")
        self.layout.addWidget(self.title)

        self.status_label = QLabel("Проверка доступных обновлений...")
        self.status_label.setStyleSheet("color:#c0c0c0;font-size:14px;")
        self.layout.addWidget(self.status_label)

        self.update_button = QPushButton("Скачать и установить обновление")
        self.update_button.setVisible(False)
        self.update_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.update_button.clicked.connect(self.download_latest)
        self.layout.addWidget(self.update_button)

        self.latest_version_info = None
        self.checked = False  # флаг, чтобы проверить только один раз

        QTimer.singleShot(100, self.check_for_updates)  # запуск проверки один раз после запуска UI

    def check_for_updates(self):
        if self.checked:
            return
        self.checked = True

        def task():
            try:
                url = "https://raw.githubusercontent.com/ludvig2457/SuperLauncher/main/versions.txt"
                r = requests.get(url, timeout=10)
                r.raise_for_status()
                lines = r.text.splitlines()

                versions = []
                for line in lines:
                    if "=" in line:
                        ver, link = line.split("=", 1)
                        versions.append((ver.strip(), link.strip()))

                if not versions:
                    QTimer.singleShot(0, lambda: self.status_label.setText("Версии не найдены."))
                    return

                # сортировка по семантической версии
                versions.sort(key=lambda x: version.parse(x[0]), reverse=True)
                latest_version, download_url = versions[0]

                if version.parse(latest_version) > version.parse(CURRENT_VERSION):
                    self.latest_version_info = (latest_version, download_url)
                    QTimer.singleShot(0, lambda: self.show_update_button(latest_version))
                else:
                    QTimer.singleShot(0, lambda: self.status_label.setText("У вас установлена последняя версия."))

            except Exception as e:
                QTimer.singleShot(0, lambda: self.status_label.setText(f"Ошибка: {e}"))

        from threading import Thread
        Thread(target=task, daemon=True).start()

    def show_update_button(self, version):
        self.status_label.setText(f"Доступна новая версия: {version}")
        self.update_button.setVisible(True)

    def download_latest(self):
        if not self.latest_version_info:
            return

        latest_version, download_url = self.latest_version_info
        downloads_path = Path(__file__).parent
        filename = downloads_path / f"SuperLauncher{latest_version}.exe"

        self.update_button.setEnabled(False)
        self.status_label.setText(f"Загрузка версии {latest_version}...")

        self.progress_dialog = QDialog(self)
        self.progress_dialog.setWindowTitle(f"Загрузка {latest_version}")
        layout = QVBoxLayout(self.progress_dialog)
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        self.progress_dialog.show()

        self.download_thread = UpdateDownloadThread(download_url, str(filename))
        self.download_thread.progress.connect(self.progress_bar.setValue)
        self.download_thread.finished.connect(lambda result: self.finish_update(result))
        self.download_thread.start()

    def finish_update(self, result):
        self.progress_dialog.hide()
        if result.startswith("ERROR:"):
            QMessageBox.critical(self, "Ошибка", result)
            self.update_button.setEnabled(True)
            return

        subprocess.Popen([str(result)], close_fds=True)
        QApplication.quit()


class CreateServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()  # Загружаем текущие настройки (например, язык)

        self.setWindowTitle(self.tr("Create your own server"))
        self.setFixedSize(350, 220)

        layout = QFormLayout(self)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(self.tr("Server Name"))

        self.input_port = QLineEdit()
        self.input_port.setPlaceholderText(self.tr("Port (e.g., 25565)"))
        self.input_port.setText("25565")

        self.combo_version = QComboBox()
        self.combo_version.addItems(["1.20.4", "1.20.1", "1.19.4"])  # Можно расширить

        self.combo_core = QComboBox()
        self.combo_core.addItems(["Paper", "Purpur", "Vanilla"])

        layout.addRow(self.tr("Server Name") + ":", self.input_name)
        layout.addRow(self.tr("Port") + ":", self.input_port)
        layout.addRow(self.tr("Version") + ":", self.combo_version)
        layout.addRow(self.tr("Core") + ":", self.combo_core)

        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton(self.tr("Create"))
        self.btn_cancel = QPushButton(self.tr("Cancel"))
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)

        self.btn_create.clicked.connect(self.create_server)
        self.btn_cancel.clicked.connect(self.reject)

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.setWindowTitle(self.tr("Create your own server"))
        self.input_name.setPlaceholderText(self.tr("Server Name"))
        self.input_port.setPlaceholderText(self.tr("Port (e.g., 25565)"))
        # Обновляем подписи полей
        layout: QFormLayout = self.layout()
        layout.labelForField(self.input_name).setText(self.tr("Server Name") + ":")
        layout.labelForField(self.input_port).setText(self.tr("Port") + ":")
        layout.labelForField(self.combo_version).setText(self.tr("Version") + ":")
        layout.labelForField(self.combo_core).setText(self.tr("Core") + ":")
        self.btn_create.setText(self.tr("Create"))
        self.btn_cancel.setText(self.tr("Cancel"))

    def create_server(self):
        name = self.input_name.text().strip()
        port = self.input_port.text().strip()
        version = self.combo_version.currentText()
        core = self.combo_core.currentText()

        if not name or not port.isdigit():
            QMessageBox.warning(self, self.tr("Error"), self.tr("Please enter a valid server name and port (number)."))
            return

        self.server_name = name
        self.server_port = int(port)
        self.server_version = version
        self.server_core = core
        self.accept()


class DownloadThread(QThread):
    progress_changed = pyqtSignal(int)  # проценты
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, core, version, save_path):
        super().__init__()
        self.core = core
        self.version = version
        self.save_path = save_path

    def run(self):
        try:
            url = self.get_jar_url(self.core, self.version)
            r = requests.get(url, stream=True)
            r.raise_for_status()

            total_length = r.headers.get('content-length')
            if total_length is None:
                with open(self.save_path, 'wb') as f:
                    f.write(r.content)
                self.progress_changed.emit(100)
            else:
                total_length = int(total_length)
                downloaded = 0
                with open(self.save_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            percent = int(downloaded * 100 / total_length)
                            self.progress_changed.emit(percent)

            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))

    def get_jar_url(self, core, version):
        core = core.lower()
        if core == "paper":
            builds_url = f"https://api.papermc.io/v2/projects/paper/versions/{version}"
            resp = requests.get(builds_url)
            resp.raise_for_status()
            build = resp.json()["builds"][-1]
            return f"https://api.papermc.io/v2/projects/paper/versions/{version}/builds/{build}/downloads/paper-{version}-{build}.jar"

        elif core == "purpur":
            builds_url = f"https://api.purpurmc.org/v2/purpur/{version}"
            resp = requests.get(builds_url)
            resp.raise_for_status()
            build = resp.json()["builds"][-1]
            return f"https://api.purpurmc.org/v2/purpur/{version}/{build}/download"

        elif core == "vanilla":
            manifest = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json").json()
            version_data = next((v for v in manifest["versions"] if v["id"] == version), None)
            if not version_data:
                raise Exception(f"Версия {version} не найдена")
            version_json = requests.get(version_data["url"]).json()
            return version_json["downloads"]["server"]["url"]

        else:
            raise Exception(f"Ядро {core} не поддерживается")


class ServerControlDialog(QDialog):
    def __init__(self, server_name, server_path, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.server_path = server_path
        self.process = None
        self.playit_process = None

        self.setWindowTitle(self.tr("Manage server") + f" '{server_name}'")
        self.setFixedSize(350, 300)

        layout = QVBoxLayout(self)

        self.label = QLabel(self.tr("Managing server: ") + server_name)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.label)

        # Чекбоксы
        self.checkbox_eula = QCheckBox(self.tr("I accept the EULA license agreement"))
        layout.addWidget(self.checkbox_eula)

        self.checkbox_offline = QCheckBox(self.tr("Enable offline mode (pirate)"))
        layout.addWidget(self.checkbox_offline)

        self.checkbox_playit = QCheckBox(self.tr("Use playit.gg (tunnel)"))
        layout.addWidget(self.checkbox_playit)

        # Кнопка сохранить настройки
        self.btn_save_settings = QPushButton(self.tr("Save settings"))
        self.btn_save_settings.clicked.connect(self.save_settings)
        layout.addWidget(self.btn_save_settings)

        # Кнопки управления сервером
        self.btn_start = QPushButton(self.tr("Start server"))
        self.btn_stop = QPushButton(self.tr("Stop server"))
        self.btn_close = QPushButton(self.tr("Close"))

        layout.addWidget(self.btn_start)
        layout.addWidget(self.btn_stop)
        layout.addWidget(self.btn_close)

        self.btn_start.clicked.connect(self.start_server)
        self.btn_stop.clicked.connect(self.stop_server)
        self.btn_close.clicked.connect(self.close)

        self.update_buttons()
        self.load_settings()

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.setWindowTitle(self.tr("Manage server"))
        self.label.setText(self.tr("Managing server: ") + os.path.basename(self.server_path))
        self.checkbox_eula.setText(self.tr("I accept the EULA license agreement"))
        self.checkbox_offline.setText(self.tr("Enable offline mode (pirate)"))
        self.checkbox_playit.setText(self.tr("Use playit.gg (tunnel)"))
        self.btn_save_settings.setText(self.tr("Save settings"))
        self.btn_start.setText(self.tr("Start server"))
        self.btn_stop.setText(self.tr("Stop server"))
        self.btn_close.setText(self.tr("Close"))

    def load_settings(self):
        eula_path = os.path.join(self.server_path, "eula.txt")
        self.checkbox_eula.setChecked(
            os.path.isfile(eula_path) and "eula=true" in open(eula_path, "r", encoding="utf-8").read().lower())

        prop_path = os.path.join(self.server_path, "server.properties")
        online_mode = True
        if os.path.isfile(prop_path):
            with open(prop_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("online-mode="):
                        online_mode = line.strip().split("=")[1].lower() == "true"
                        break
        self.checkbox_offline.setChecked(not online_mode)
        self.checkbox_playit.setChecked(False)

    def save_settings(self):
        eula_path = os.path.join(self.server_path, "eula.txt")
        try:
            with open(eula_path, "w", encoding="utf-8") as f:
                f.write(f"eula={'true' if self.checkbox_eula.isChecked() else 'false'}\n")
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save eula.txt") + f":\n{e}")
            return

        prop_path = os.path.join(self.server_path, "server.properties")
        props = {}
        if os.path.isfile(prop_path):
            try:
                with open(prop_path, "r", encoding="utf-8") as f:
                    for line in f:
                        if "=" in line:
                            k, v = line.strip().split("=", 1)
                            props[k] = v
            except Exception:
                pass
        props["online-mode"] = "false" if self.checkbox_offline.isChecked() else "true"

        try:
            with open(prop_path, "w", encoding="utf-8") as f:
                for k, v in props.items():
                    f.write(f"{k}={v}\n")
                if not props:
                    f.write(f"online-mode={'false' if self.checkbox_offline.isChecked() else 'true'}\n")
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save server.properties") + f":\n{e}")
            return

        QMessageBox.information(self, self.tr("Success"), self.tr("Settings saved!"))

    def update_buttons(self):
        running = self.process is not None and self.process.poll() is None
        self.btn_start.setEnabled(not running)
        self.btn_stop.setEnabled(running)

    def download_and_install_playit(self):
        import requests, tempfile

        msi_url = "https://github.com/playit-cloud/playit-agent/releases/download/v0.15.26/playit-windows-x86_64-signed.msi"
        temp_dir = tempfile.gettempdir()
        msi_path = os.path.join(temp_dir, "playit-agent.msi")

        if not os.path.isfile(msi_path):
            try:
                response = requests.get(msi_url, stream=True)
                response.raise_for_status()
                with open(msi_path, "wb") as f:
                    for chunk in response.iter_content(8192):
                        if chunk:
                            f.write(chunk)
                os.system(f'powershell -Command "Unblock-File -Path \'{msi_path}\'"')
            except Exception as e:
                QMessageBox.critical(self, self.tr("Download error"),
                                     self.tr("Failed to download playit MSI") + f":\n{e}")
                return False

        try:
            result = subprocess.run(["msiexec", "/i", msi_path, "/quiet", "/qn"], capture_output=True, text=True,
                                    shell=False)
            if result.returncode != 0:
                msg = QMessageBox(self)
                msg.setIcon(QMessageBox.Icon.Critical)
                msg.setWindowTitle(self.tr("Installation error"))
                msg.setText(self.tr(
                    "Installation failed with code") + f" {result.returncode}:\n{result.stderr.strip()}\n\n" + self.tr(
                    "Try opening the file manually:"))

                btn_copy = QPushButton(self.tr("Copy MSI path"))
                btn_copy.clicked.connect(lambda: QApplication.clipboard().setText(msi_path))
                layout = msg.layout()
                layout.addWidget(btn_copy, layout.rowCount(), 0, 1, layout.columnCount())
                msg.exec()
                return False

            QMessageBox.information(self, self.tr("Installation"), self.tr("Playit-agent installed successfully."))
            return True
        except Exception as e:
            QMessageBox.critical(self, self.tr("Installation error"), self.tr("Failed to install playit") + f":\n{e}")
            return False

    def start_playit(self):
        import os, subprocess
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\playit\playit.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\playit\playit.exe"),
            os.path.join(self.server_path, "playit.exe"),
        ]
        playit_exe = next((p for p in possible_paths if os.path.isfile(p)), None)
        if not playit_exe and not self.download_and_install_playit():
            QMessageBox.warning(self, "playit.gg", self.tr("playit.exe not found after installation"))
            return False

        try:
            self.playit_process = subprocess.Popen([playit_exe], cwd=os.path.dirname(playit_exe))
            return True
        except Exception as e:
            QMessageBox.critical(self, self.tr("Playit error"), str(e))
            return False

    def stop_playit(self):
        if self.playit_process and self.playit_process.poll() is None:
            try:
                self.playit_process.terminate()
                self.playit_process.wait(5)
            except Exception:
                self.playit_process.kill()
            finally:
                self.playit_process = None

    def start_server(self):
        import os, subprocess
        if self.process is None or self.process.poll() is not None:
            if not self.checkbox_eula.isChecked():
                QMessageBox.warning(self, "EULA", self.tr("You must accept the EULA!"))
                return

            bat_path = os.path.join(self.server_path, "start.bat")
            if not os.path.isfile(bat_path):
                QMessageBox.warning(self, self.tr("Error"), self.tr("start.bat not found!"))
                return

            try:
                self.process = subprocess.Popen(["cmd.exe", "/k", "start.bat"], cwd=self.server_path, shell=True)
                if self.checkbox_playit.isChecked() and not self.start_playit():
                    QMessageBox.warning(self, "playit.gg", self.tr("Playit tunnel will not be started."))
                QMessageBox.information(self, self.tr("Server"), self.tr("Server started."))
                self.update_buttons()
            except Exception as e:
                QMessageBox.critical(self, self.tr("Start error"), str(e))
        else:
            QMessageBox.information(self, self.tr("Info"), self.tr("Server is already running."))
            self.update_buttons()

    def stop_server(self):
        if self.process and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(5)
                self.stop_playit()
                QMessageBox.information(self, self.tr("Server"), self.tr("Server stopped."))
            except Exception:
                self.process.kill()
                self.stop_playit()
                QMessageBox.information(self, self.tr("Server"), self.tr("Server forcefully stopped."))
            finally:
                self.process = None
                self.update_buttons()
        else:
            QMessageBox.information(self, self.tr("Info"), self.tr("Server is not running."))
            self.update_buttons()


class ServersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent  # для возможности доступа к родителю при переводе
        self.config = load_config()  # для текущего языка

        self.servers_file = "servers_list.json"
        self.servers_list = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        # Заголовок
        self.title_label = QLabel(self.tr("🖧 Minecraft Servers"))
        self.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; margin-bottom: 15px; color: white;"
        )
        self.layout.addWidget(self.title_label)

        # Кнопка создания сервера
        self.btn_create_server = QPushButton(self.tr("Create your own server"))
        self.btn_create_server.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_create_server.setStyleSheet(
            "padding: 8px; font-weight: bold; background-color: #4facfe; color: black; border-radius: 8px;"
        )
        self.btn_create_server.clicked.connect(self.open_create_server_dialog)
        self.layout.addWidget(self.btn_create_server)

        # Форма добавления сервера вручную
        form_layout = QHBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(self.tr("Server Name"))
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText(self.tr("IP or domain"))

        self.btn_add_server = QPushButton(self.tr("Add server"))
        self.btn_add_server.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_server.clicked.connect(self.add_server)

        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_ip)
        form_layout.addWidget(self.btn_add_server)
        self.layout.addLayout(form_layout)

        # Прогрессбар
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        # Скролл для серверов
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.scroll_area.setWidget(self.container)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(12)

        self.load_servers()
        self.update_servers_ui()

    # --- Перевод ---
    def tr(self, key: str) -> str:
        # если есть родитель с tr — используем его
        if self.parent_window and hasattr(self.parent_window, "tr"):
            return self.parent_window.tr(key)
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.title_label.setText(self.tr("🖧 Minecraft Servers"))
        self.btn_create_server.setText(self.tr("Create your own server"))
        self.input_name.setPlaceholderText(self.tr("Server Name"))
        self.input_ip.setPlaceholderText(self.tr("IP or domain"))
        self.btn_add_server.setText(self.tr("Add server"))
        self.update_servers_ui()

    # --- Методы сервера ---
    def open_create_server_dialog(self):
        dialog = CreateServerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.server_name
            port = dialog.server_port
            version = dialog.server_version
            core = dialog.server_core
            ip = f"localhost:{port}"

            server_path = os.path.join("servers", name)
            os.makedirs(server_path, exist_ok=True)

            self.progress_bar.setValue(0)
            self.progress_bar.show()

            self.download_thread = DownloadThread(core, version, os.path.join(server_path, "server.jar"))
            self.download_thread.progress_changed.connect(self.progress_bar.setValue)
            self.download_thread.finished.connect(lambda: self.on_download_finished(name, ip, server_path))
            self.download_thread.error.connect(self.on_download_error)
            self.download_thread.start()

    def on_download_finished(self, name, ip, server_path):
        self.progress_bar.hide()
        self.generate_start_bat(server_path)

        self.servers_list.append({"name": name, "ip": ip, "managed": True})
        self.save_servers()
        self.update_servers_ui()

        QMessageBox.information(
            self,
            self.tr("Done"),
            f"{self.tr('Server')} '{name}' {self.tr('successfully created!')}"
        )

    def on_download_error(self, error_message):
        self.progress_bar.hide()
        QMessageBox.critical(self, self.tr("Error"), error_message)

    def generate_start_bat(self, path):
        with open(os.path.join(path, "start.bat"), "w", encoding="utf-8") as f:
            f.write("""@echo off
java -Xmx2G -Xms2G -jar server.jar nogui
pause
""")

    # --- Работа с JSON ---
    def load_servers(self):
        try:
            with open(self.servers_file, "r", encoding="utf-8") as f:
                self.servers_list = json.load(f)
        except Exception:
            self.servers_list = []

    def save_servers(self):
        try:
            with open(self.servers_file, "w", encoding="utf-8") as f:
                json.dump(self.servers_list, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print("Error saving servers:", e)

    # --- Добавление сервера вручную ---
    def add_server(self):
        name = self.input_name.text().strip()
        ip = self.input_ip.text().strip()

        if not name or not ip:
            QMessageBox.warning(
                self,
                self.tr("Error"),
                self.tr("Please fill in server name and IP.")
            )
            return

        self.servers_list.append({"name": name, "ip": ip, "managed": False})
        self.save_servers()
        self.update_servers_ui()

        self.input_name.clear()
        self.input_ip.clear()

    # --- Обновление UI серверов ---
    def update_servers_ui(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for server in self.servers_list:
            self.add_server_widget(server['name'], server['ip'], server.get('managed', False))

        self.container_layout.addStretch()

    def add_server_widget(self, name, ip, managed):
        container = QWidget()
        layout = QHBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)

        server_label = QLabel(f"<b>{name}</b> — <span style='color:#4facfe;'>{ip}</span>")
        server_label.setWordWrap(True)
        server_label.setStyleSheet("font-size: 16px; color: #c0c0c0;")
        layout.addWidget(server_label)
        layout.addStretch()

        if managed:
            btn_manage = QPushButton(self.tr("Manage"))
            btn_manage.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_manage.setStyleSheet("padding: 4px 12px; font-weight: bold;")
            server_path = os.path.join("servers", name)
            btn_manage.clicked.connect(lambda _, n=name, p=server_path: ServerControlDialog(n, p, self).exec())
            layout.addWidget(btn_manage)

        btn_delete = QPushButton(self.tr("Delete"))
        btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_delete.setStyleSheet(
            "background-color: #fe4c4c; color: white; border-radius: 5px; padding: 3px 8px;"
        )
        btn_delete.clicked.connect(lambda _, n=name, m=managed: self.delete_server(n, m))
        layout.addWidget(btn_delete)

        self.container_layout.addWidget(container)

    # --- Удаление сервера ---
    def delete_server(self, server_name, managed):
        reply = QMessageBox.question(
            self,
            self.tr("Confirm deletion"),
            f"{self.tr('Are you sure you want to delete the server')} '{server_name}'? {self.tr('This action cannot be undone.')}",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if reply == QMessageBox.StandardButton.Yes:
            self.servers_list = [s for s in self.servers_list if s['name'] != server_name]
            self.save_servers()
            self.update_servers_ui()

            if managed:
                server_path = os.path.join("servers", server_name)
                if os.path.exists(server_path) and os.path.isdir(server_path):
                    try:
                        shutil.rmtree(server_path)
                    except Exception as e:
                        QMessageBox.critical(self, self.tr("Error"), f"{self.tr('Failed to delete folder')}:\n{e}")

# =========== ЗАМЕНИТЬ ВЕСЬ КЛАСС MainWindow НА ЭТОТ ===========
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SuperLauncher 2026 Edition v2.0.0 🎄")
        self.setWindowIcon(QIcon("assets/icon.png"))

        # Устанавливаем начальное разрешение 1080x720
        # Но разрешаем растягивание
        self.resize(1080, 720)
        self.setMinimumSize(800, 600)  # Минимальный размер
        self.setMaximumSize(1920, 1080)  # Максимальный размер
        
        # Новые системы
        self.account_system = AccountSystem()
        self.holiday_theme = HolidayTheme()
        self.gift_system = GiftSystem(self.account_system)
        self.skins_manager = SkinsManager(self.account_system)
        self.builds_manager = BuildsManager()
        self.custom_ui = CustomizableUI()
        self.platform_info = CrossPlatformSupport.get_platform_info()
        
        # Применяем праздничную тему
        if self.holiday_theme.current_holiday:
            self.holiday_theme.apply_holiday_style(self)
        
        # Включаем прозрачность
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")
        
        # Центральный виджет
        central_widget = GlassFrame()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)
        
        # Боковая панель (создаем после всех страниц)
        self.pages = QStackedWidget()
        self.pages.setStyleSheet("""
            QStackedWidget {
                background: rgba(30, 30, 40, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                margin: 5px;
            }
        """)
        
        # Сначала создаем ВСЕ страницы в правильном порядке
        self.create_all_pages()
        
        # Теперь создаем сайдбар, который будет знать о страницах
        self.sidebar = ModernSidebar(self)
        self.update_sidebar_for_holiday()
        
        # Проверяем соответствие
        self.check_pages_consistency()
        
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)
        
        # Потоки
        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        
        # Discord RPC
        self.discord_rpc_thread = DiscordRPCThread(self)
        self.discord_rpc_thread.start()
        
        # Статусбар с дополнительной информацией
        self.setup_status_bar()
        
        # Проверка входа
        self.check_auto_login()
        
        # Таймер для проверки подарков
        self.gift_timer = QTimer()
        self.gift_timer.timeout.connect(self.check_for_gifts)
        self.gift_timer.start(60000)  # Каждую минуту
        
        # Применяем настройки UI
        self.custom_ui.apply_to_widget(self)
        
        # Показываем приветственное сообщение
        QTimer.singleShot(1000, self.show_welcome_message)
    
    def create_all_pages(self):
        """Создает все страницы в правильном порядке"""
        # Создаем временный список для страниц
        pages_list = []
        
        # 0 - Главная
        pages_list.append(self.create_home_page())
        
        # 1 - Аккаунт
        pages_list.append(self.create_account_page())
        
        # 2 - Подарки
        pages_list.append(self.create_gifts_page())
        
        # 3 - Моды
        pages_list.append(ModsPage(self))
        
        # 4 - Сборки
        pages_list.append(self.create_builds_page())
        
        # 5 - Скины
        pages_list.append(self.create_skins_page())
        
        # 6 - Новости
        pages_list.append(NewsPage(self))
        
        # 7 - Обновления
        pages_list.append(UpdatesPage())
        
        # 8 - Серверы
        pages_list.append(ServersPage(self))
        
        # 9 - Настройки
        self.settings_page = SettingsPage(self)
        pages_list.append(self.settings_page)
        
        # 10 - Minecraft
        minecraft_page = MinecraftLauncherPage()
        # Заменяем кнопку запуска на анимированную
        if hasattr(minecraft_page, 'start_button'):
            old_button = minecraft_page.start_button
            new_button = AnimatedButton("🎮 Играть")
            new_button.setFixedHeight(50)
            new_button.setStyleSheet("font-size: 18px; font-weight: bold;")
            new_button.clicked.connect(self.launch_game)
            
            layout = minecraft_page.layout()
            for i in range(layout.count()):
                item = layout.itemAt(i)
                if item.widget() == old_button:
                    layout.removeWidget(old_button)
                    old_button.deleteLater()
                    layout.insertWidget(i, new_button)
                    minecraft_page.start_button = new_button
                    break
        pages_list.append(minecraft_page)
        
        # Добавляем все страницы в QStackedWidget
        for page in pages_list:
            self.pages.addWidget(page)
        
        print(f"✅ Создано {len(pages_list)} страниц")
    
    def check_pages_consistency(self):
        """Проверка соответствия кнопок и страниц"""
        button_count = len(self.sidebar.nav_buttons)
        page_count = self.pages.count()
        
        if button_count != page_count:
            print(f"⚠️ Несоответствие: {button_count} кнопок, {page_count} страниц")
            # Автоматическая корректировка
            if button_count < page_count:
                print(f"Добавляем {page_count - button_count} кнопок...")
            elif button_count > page_count:
                print(f"Удаляем {button_count - page_count} лишних кнопок...")
            return False
        
        print(f"✅ Все в порядке: {button_count} кнопок, {page_count} страниц")
        return True
    
    def update_sidebar_for_holiday(self):
        """Обновление боковой панели для праздников"""
        if self.holiday_theme.current_holiday:
            assets = self.holiday_theme.get_holiday_assets()
            if assets:
                # Обновляем иконки в сайдбаре
                holiday_icons = {
                    "home": "🎄",
                    "account": "🎅",
                    "gifts": "🎁",
                    "mods": "🧩",
                    "builds": "📦",
                    "skins": "🖼️",
                    "news": "❄️",
                    "updates": "🌟",
                    "servers": "🦌",
                    "settings": "🔔",
                    "minecraft": "⛄"
                }
                
                # Обновляем тексты кнопок
                for i, (icon_key, btn) in enumerate(zip(holiday_icons.keys(), self.sidebar.nav_buttons)):
                    new_icon = holiday_icons.get(icon_key, btn.property("full_text")[:2])
                    old_text = btn.property("full_text")
                    # Сохраняем текст после иконки
                    text_part = old_text[2:] if len(old_text) > 2 else ""
                    btn.setProperty("full_text", f"  {new_icon}{text_part}")
                    btn.setProperty("short_text", f"  {new_icon}")
                    
                    # Обновляем отображаемый текст
                    if self.sidebar.is_expanded:
                        btn.setText(btn.property("full_text"))
                    else:
                        btn.setText(btn.property("short_text"))
    
    def create_home_page(self):
        """Создание главной страницы для 1080x720"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)  # Уменьшаем отступы
        layout.setSpacing(12)  # Уменьшаем расстояние
        
        # Новогодний счетчик - уменьшаем
        self.countdown_widget = NewYearCountdown()
        layout.addWidget(self.countdown_widget)
        
        # Заголовок - уменьшаем
        title_label = GradientLabel("🎄 SuperLauncher 2026 🎄")
        title_label.setStyleSheet("""
            font-size: 28px;  # Было 36px
            margin: 8px 0;  # Уменьшаем отступы
            font-weight: bold;
            text-align: center;
        """)
        layout.addWidget(title_label)
        
        # НА ЭТО:
        user_info_widget = self.create_user_info_widget_720p()  # Без self.
        layout.addWidget(user_info_widget)
        
        # И также:
        quick_actions = self.create_quick_actions_720p()  # Без self.
        layout.addWidget(quick_actions)
        
        layout.addStretch()
        return page

    # В классе MainWindow (примерно строка 4012) ЗАМЕНИТЕ:

    def create_user_info_widget_720p(self):
        """Виджет информации о пользователе для 720p"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(10)
        
        # Аватар
        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("""
            font-size: 36px;
            padding: 8px;
            background-color: rgba(255, 255, 255, 0.1);
            border-radius: 50%;
            min-width: 60px;
            min-height: 60px;
            text-align: center;
        """)
        layout.addWidget(self.avatar_label)
        
        # Информация о пользователе
        user_info_widget = QWidget()
        user_info_layout = QVBoxLayout(user_info_widget)
        user_info_layout.setContentsMargins(0, 0, 0, 0)
        user_info_layout.setSpacing(5)
        
        self.username_label = QLabel("Гость")
        self.username_label.setStyleSheet("font-size: 16px; font-weight: bold; color: white;")
        user_info_layout.addWidget(self.username_label)
        
        self.user_status_label = QLabel("Не авторизован")
        self.user_status_label.setStyleSheet("font-size: 12px; color: #aaa;")
        user_info_layout.addWidget(self.user_status_label)
        
        layout.addWidget(user_info_widget)
        layout.addStretch()
        
        # Кнопка входа
        self.login_button = QPushButton("Войти / Зарегистрироваться")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 6px 12px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
        """)
        self.login_button.clicked.connect(self.show_login_dialog)
        layout.addWidget(self.login_button)
        
        return widget

    def create_quick_actions_720p(self):
        """Быстрые действия для 720p"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(8)
        
        title = QLabel("🚀 Быстрые действия")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: white; margin-bottom: 8px;")
        layout.addWidget(title)
        
        grid_widget = QWidget()
        grid_layout = QGridLayout(grid_widget)
        grid_layout.setContentsMargins(0, 0, 0, 0)
        grid_layout.setSpacing(8)
        
        actions = [
            ("🎮", "Быстрый запуск", self.launch_game),
            ("🎁", "Подарок", self.claim_daily_gift),
            ("🛒", "Скины", lambda: self.pages.setCurrentIndex(5)),
            ("📦", "Сборки", lambda: self.pages.setCurrentIndex(4)),
            ("⚙️", "Настройки", lambda: self.pages.setCurrentIndex(9)),
            ("🆘", "Помощь", self.show_help),
        ]
        
        row, col = 0, 0
        for icon, text, callback in actions:
            btn = QPushButton(f"{icon}\n{text}")
            btn.setFixedSize(120, 80)
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn.setStyleSheet("""
                QPushButton {
                    font-size: 12px;
                    padding: 6px;
                    border-radius: 8px;
                    background-color: rgba(79, 172, 254, 0.2);
                    color: white;
                    border: 1px solid rgba(79, 172, 254, 0.3);
                }
                QPushButton:hover {
                    background-color: rgba(79, 172, 254, 0.4);
                    border: 1px solid rgba(79, 172, 254, 0.6);
                }
            """)
            btn.clicked.connect(callback)
            grid_layout.addWidget(btn, row, col)
            
            col += 1
            if col > 2:
                col = 0
                row += 1
        
        layout.addWidget(grid_widget)
        return widget
    
    def create_stats_widget(self):
        """Создание виджета статистики"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Заголовок
        title = QLabel("📊 Статистика")
        title.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # Контейнер для статистики
        stats_container = QWidget()
        stats_layout = QHBoxLayout(stats_container)
        stats_layout.setContentsMargins(0, 0, 0, 0)
        stats_layout.setSpacing(10)
        
        stats = [
            ("📈", "Прогресс", [
                ("Уровень:", "1"),
                ("Опыт:", "0/1000"),
                ("Подарки:", "0")
            ]),
            ("🏆", "Достижения", [
                ("Новичок:", "✅"),
                ("Исследователь:", "❌"),
                ("Коллекционер:", "❌")
            ]),
            ("🎯", "Активность", [
                ("Игровое время:", "0ч"),
                ("Запусков:", "0"),
                ("Серверов:", "0")
            ])
        ]
        
        for icon, title_text, items in stats:
            frame = QFrame()
            frame.setStyleSheet("""
                QFrame {
                    background-color: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    border-radius: 10px;
                    padding: 15px;
                }
            """)
            frame_layout = QVBoxLayout(frame)
            frame_layout.setSpacing(5)
            
            # Заголовок блока
            block_title = QLabel(f"{icon} {title_text}")
            block_title.setStyleSheet("font-weight: bold; font-size: 16px; color: #4facfe;")
            frame_layout.addWidget(block_title)
            
            # Элементы статистики
            for label, value in items:
                item_widget = QWidget()
                item_layout = QHBoxLayout(item_widget)
                item_layout.setContentsMargins(0, 0, 0, 0)
                
                label_widget = QLabel(label)
                label_widget.setStyleSheet("color: #aaaaaa;")
                
                value_widget = QLabel(value)
                value_widget.setStyleSheet("color: white; font-weight: bold;")
                
                item_layout.addWidget(label_widget)
                item_layout.addStretch()
                item_layout.addWidget(value_widget)
                
                frame_layout.addWidget(item_widget)
            
            frame_layout.addStretch()
            stats_layout.addWidget(frame)
        
        layout.addWidget(stats_container)
        return widget
    
    def create_account_page(self):
        """Создание страницы аккаунта"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("👤 Мой Аккаунт")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: white;")
        layout.addWidget(title)
        
        # Информация об аккаунте
        info_group = QGroupBox("Информация об аккаунте")
        info_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        info_layout = QVBoxLayout()
        
        # Данные пользователя
        user_data = [
            ("Имя пользователя:", "Гость"),
            ("Email:", "Не указан"),
            ("Уровень:", "1"),
            ("Опыт:", "0"),
            ("Дата регистрации:", "Не зарегистрирован")
        ]
        
        for label, value in user_data:
            row_widget = QWidget()
            row_layout = QHBoxLayout(row_widget)
            row_layout.setContentsMargins(10, 5, 10, 5)
            
            label_widget = QLabel(label)
            label_widget.setStyleSheet("color: #aaaaaa; font-size: 14px;")
            label_widget.setMinimumWidth(150)
            
            value_widget = QLabel(value)
            value_widget.setStyleSheet("color: white; font-size: 14px; font-weight: bold;")
            
            row_layout.addWidget(label_widget)
            row_layout.addWidget(value_widget)
            row_layout.addStretch()
            
            info_layout.addWidget(row_widget)
        
        info_group.setLayout(info_layout)
        layout.addWidget(info_group)
        
        # Лицензии
        license_group = QGroupBox("Лицензии")
        license_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        license_layout = QVBoxLayout()
        
        self.license_label = QLabel("Статус: Бесплатная версия")
        self.license_label.setStyleSheet("color: white; font-size: 14px; padding: 10px;")
        license_layout.addWidget(self.license_label)
        
        # Поле для ввода ключа
        key_widget = QWidget()
        key_layout = QHBoxLayout(key_widget)
        key_layout.setContentsMargins(10, 5, 10, 5)
        
        self.license_input = QLineEdit()
        self.license_input.setPlaceholderText("Введите ключ лицензии...")
        self.license_input.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 5px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        
        self.activate_license_btn = QPushButton("Активировать")
        self.activate_license_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.activate_license_btn.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #aaaaaa;
            }
        """)
        self.activate_license_btn.clicked.connect(self.activate_license)
        
        key_layout.addWidget(self.license_input)
        key_layout.addWidget(self.activate_license_btn)
        license_layout.addWidget(key_widget)
        
        # Информация о лицензиях
        license_info = QLabel("• Standard: Все основные функции\n• Premium: Дополнительные темы и скины\n• Ultimate: Полный доступ ко всему")
        license_info.setStyleSheet("color: #aaaaaa; font-size: 12px; padding: 10px; background-color: rgba(255, 255, 255, 0.05); border-radius: 5px;")
        license_layout.addWidget(license_info)
        
        license_group.setLayout(license_layout)
        layout.addWidget(license_group)
        
        # Кнопки управления
        button_widget = QWidget()
        button_layout = QHBoxLayout(button_widget)
        button_layout.setContentsMargins(0, 10, 0, 0)
        
        btn_logout = QPushButton("Выйти из аккаунта")
        btn_logout.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_logout.setStyleSheet("""
            QPushButton {
                background-color: #ff5555;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #ff4444;
            }
        """)
        btn_logout.clicked.connect(self.logout_user)
        
        btn_delete = QPushButton("Удалить аккаунт")
        btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_delete.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 85, 85, 0.3);
                color: #ff5555;
                border: 1px solid #ff5555;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 85, 85, 0.5);
            }
        """)
        btn_delete.clicked.connect(self.delete_account)
        
        button_layout.addWidget(btn_logout)
        button_layout.addStretch()
        button_layout.addWidget(btn_delete)
        
        layout.addWidget(button_widget)
        layout.addStretch()
        
        return page
    
    def create_gifts_page(self):
        """Создание страницы подарков"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("🎁 Подарки и Награды")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: white;")
        layout.addWidget(title)
        
        # Ежедневный подарок
        daily_group = QGroupBox("🎯 Ежедневный подарок")
        daily_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #FFD700;
                border: 2px solid #FFD700;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
                background-color: rgba(255, 215, 0, 0.05);
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        daily_layout = QVBoxLayout()
        
        # Виджет ежедневного подарка
        daily_gift_widget = QWidget()
        daily_gift_layout = QHBoxLayout(daily_gift_widget)
        daily_gift_layout.setContentsMargins(15, 15, 15, 15)
        
        # Иконка подарка
        gift_icon = QLabel("🎁")
        gift_icon.setStyleSheet("font-size: 64px;")
        daily_gift_layout.addWidget(gift_icon)
        
        # Информация о подарке
        gift_info = QWidget()
        gift_info_layout = QVBoxLayout(gift_info)
        gift_info_layout.setSpacing(5)
        
        self.daily_gift_status = QLabel("Готово к получению!")
        self.daily_gift_status.setStyleSheet("font-size: 18px; font-weight: bold; color: #FFD700;")
        gift_info_layout.addWidget(self.daily_gift_status)
        
        gift_desc = QLabel("Заходите ежедневно, чтобы получать новые подарки!")
        gift_desc.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        gift_desc.setWordWrap(True)
        gift_info_layout.addWidget(gift_desc)
        
        daily_gift_layout.addWidget(gift_info)
        daily_gift_layout.addStretch()
        
        daily_layout.addWidget(daily_gift_widget)
        
        # Кнопка получения
        self.claim_daily_btn = QPushButton("🎉 Получить ежедневный подарок!")
        self.claim_daily_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.claim_daily_btn.setStyleSheet("""
            QPushButton {
                background-color: #FFD700;
                color: #333333;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #FFC800;
            }
            QPushButton:disabled {
                background-color: #666666;
                color: #aaaaaa;
            }
        """)
        self.claim_daily_btn.clicked.connect(self.claim_daily_gift)
        daily_layout.addWidget(self.claim_daily_btn)
        
        daily_group.setLayout(daily_layout)
        layout.addWidget(daily_group)
        
        # Полученные подарки
        received_group = QGroupBox("📜 История подарков")
        received_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        self.gifts_list = QListWidget()
        self.gifts_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                font-size: 14px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(79, 172, 254, 0.3);
            }
        """)
        
        # Заполняем тестовыми данными
        test_gifts = [
            "🎁 25.12.2024: Новогодний скин",
            "🌟 24.12.2024: 500 XP",
            "🎄 23.12.2024: Праздничная тема",
            "✨ 22.12.2024: Редкий ресурс-пак"
        ]
        
        for gift in test_gifts:
            item = QListWidgetItem(gift)
            self.gifts_list.addItem(item)
        
        received_layout = QVBoxLayout()
        received_layout.addWidget(self.gifts_list)
        received_group.setLayout(received_layout)
        layout.addWidget(received_group)
        
        layout.addStretch()
        return page
    
    def create_skins_page(self):
        """Создание страницы скинов"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("🖼️ Скины и Оформление")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: white;")
        layout.addWidget(title)
        
        # Текущий скин
        current_group = QGroupBox("🎯 Текущий скин")
        current_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        current_layout = QHBoxLayout()
        current_layout.setContentsMargins(15, 15, 15, 15)
        
        self.current_skin_preview = QLabel("👤")
        self.current_skin_preview.setFixedSize(120, 120)
        self.current_skin_preview.setStyleSheet("""
            border: 3px solid #4facfe;
            border-radius: 10px;
            font-size: 72px;
            text-align: center;
            background-color: rgba(255, 255, 255, 0.1);
        """)
        current_layout.addWidget(self.current_skin_preview)
        
        skin_info = QWidget()
        skin_info_layout = QVBoxLayout(skin_info)
        skin_info_layout.setSpacing(10)
        
        self.current_skin_name = QLabel("Стандартный")
        self.current_skin_name.setStyleSheet("font-size: 20px; font-weight: bold; color: white;")
        skin_info_layout.addWidget(self.current_skin_name)
        
        skin_desc = QLabel("Базовый скин по умолчанию")
        skin_desc.setStyleSheet("color: #aaaaaa; font-size: 14px;")
        skin_desc.setWordWrap(True)
        skin_info_layout.addWidget(skin_desc)
        
        # Кнопка применения
        btn_apply = QPushButton("Применить скин")
        btn_apply.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
        """)
        btn_apply.clicked.connect(lambda: self.apply_skin("default"))
        skin_info_layout.addWidget(btn_apply)
        
        skin_info_layout.addStretch()
        current_layout.addWidget(skin_info)
        current_layout.addStretch()
        
        current_group.setLayout(current_layout)
        layout.addWidget(current_group)
        
        # Библиотека скинов
        skins_group = QGroupBox("📚 Библиотека скинов")
        skins_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        # Создаем сетку для скинов
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: transparent;
            }
        """)
        
        skins_container = QWidget()
        self.skins_grid = QGridLayout(skins_container)
        self.skins_grid.setContentsMargins(10, 10, 10, 10)
        self.skins_grid.setSpacing(15)
        
        # Добавляем тестовые скины
        test_skins = [
            ("👤", "Стандартный", "Бесплатно", True),
            ("🎅", "Санта", "500 XP", False),
            ("⛄", "Снеговик", "300 XP", False),
            ("🦌", "Олень", "400 XP", False),
            ("🎄", "Ёлка", "250 XP", False),
            ("🌟", "Звезда", "600 XP", False),
            ("❄️", "Снежинка", "350 XP", False),
            ("🎁", "Подарок", "450 XP", False)
        ]
        
        row, col = 0, 0
        for icon, name, price, unlocked in test_skins:
            skin_widget = self.create_skin_widget(icon, name, price, unlocked)
            self.skins_grid.addWidget(skin_widget, row, col)
            
            col += 1
            if col > 3:  # 4 колонки
                col = 0
                row += 1
        
        scroll.setWidget(skins_container)
        
        skins_layout = QVBoxLayout()
        skins_layout.addWidget(scroll)
        skins_group.setLayout(skins_layout)
        layout.addWidget(skins_group)
        
        # Кнопка загрузки своего скина
        btn_upload = QPushButton("📤 Загрузить свой скин")
        btn_upload.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_upload.setStyleSheet("""
            QPushButton {
                background-color: rgba(79, 172, 254, 0.2);
                color: #4facfe;
                border: 2px dashed #4facfe;
                border-radius: 8px;
                padding: 15px;
                font-size: 16px;
                font-weight: bold;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: rgba(79, 172, 254, 0.3);
            }
        """)
        btn_upload.clicked.connect(self.upload_custom_skin)
        layout.addWidget(btn_upload)
        
        layout.addStretch()
        return page
    
    def create_skin_widget(self, icon, name, price, unlocked):
        """Создание виджета скина"""
        widget = QFrame()
        widget.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 10px;
                padding: 10px;
            }
            QFrame:hover {
                border: 1px solid #4facfe;
                background-color: rgba(79, 172, 254, 0.1);
            }
        """)
        widget.setFixedSize(180, 180)
        
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Иконка скина
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 48px; text-align: center;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Название
        name_label = QLabel(name)
        name_label.setStyleSheet("font-weight: bold; font-size: 14px; color: white; text-align: center;")
        name_label.setWordWrap(True)
        layout.addWidget(name_label)
        
        # Цена/статус
        status_label = QLabel("Разблокирован" if unlocked else price)
        status_label.setStyleSheet(f"""
            color: {'#4facfe' if unlocked else '#FFD700'};
            font-size: 12px;
            text-align: center;
        """)
        layout.addWidget(status_label)
        
        # Кнопка
        btn_text = "Применить" if unlocked else "Разблокировать"
        btn = QPushButton(btn_text)
        btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {'#4facfe' if unlocked else 'rgba(255, 215, 0, 0.2)'};
                color: {'white' if unlocked else '#FFD700'};
                border: none;
                border-radius: 5px;
                padding: 5px;
                font-size: 12px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: {'#3a9bed' if unlocked else 'rgba(255, 215, 0, 0.3)'};
            }}
        """)
        
        if unlocked:
            btn.clicked.connect(lambda: self.apply_skin(name))
        else:
            btn.clicked.connect(lambda: self.unlock_skin(name, price))
        
        layout.addWidget(btn)
        
        return widget
    
    def create_builds_page(self):
        """Создание страницы сборок"""
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        title = QLabel("📦 Сборки и Модпаки")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: white;")
        layout.addWidget(title)
        
        # Поиск сборок
        search_widget = QWidget()
        search_layout = QHBoxLayout(search_widget)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(10)
        
        self.builds_search = QLineEdit()
        self.builds_search.setPlaceholderText("Введите название сборки...")
        self.builds_search.setStyleSheet("""
            QLineEdit {
                background-color: rgba(255, 255, 255, 0.1);
                border: 1px solid rgba(255, 255, 255, 0.3);
                border-radius: 8px;
                padding: 10px;
                color: white;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #4facfe;
            }
        """)
        
        self.builds_search_btn = QPushButton("Поиск")
        self.builds_search_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.builds_search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
        """)
        self.builds_search_btn.clicked.connect(self.search_builds)
        
        search_layout.addWidget(self.builds_search)
        search_layout.addWidget(self.builds_search_btn)
        layout.addWidget(search_widget)
        
        # Список сборок
        builds_group = QGroupBox("🔍 Доступные сборки")
        builds_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        self.builds_list = QListWidget()
        self.builds_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                font-size: 14px;
                min-height: 200px;
            }
            QListWidget::item {
                padding: 12px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:selected {
                background-color: rgba(79, 172, 254, 0.3);
            }
        """)
        
        # Добавляем тестовые сборки
        test_builds = [
            "Better Minecraft [1.20.1] - 500K+ загрузок",
            "RLCraft [1.12.2] - 1M+ загрузок",
            "All The Mods 9 [1.20.1] - 300K+ загрузок",
            "Medieval Minecraft [1.19.2] - 150K+ загрузок",
            "SkyFactory 4 [1.12.2] - 800K+ загрузок",
            "StoneBlock 3 [1.18.2] - 400K+ загрузок"
        ]
        
        for build in test_builds:
            item = QListWidgetItem(build)
            self.builds_list.addItem(item)
        
        builds_layout = QVBoxLayout()
        builds_layout.addWidget(self.builds_list)
        
        # Кнопки для сборок
        builds_buttons = QWidget()
        builds_buttons_layout = QHBoxLayout(builds_buttons)
        builds_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        btn_install = QPushButton("⬇️ Установить сборку")
        btn_install.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_install.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
        """)
        btn_install.clicked.connect(self.install_selected_build)
        
        btn_info = QPushButton("ℹ️ Информация")
        btn_info.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_info.setStyleSheet("""
            QPushButton {
                background-color: rgba(79, 172, 254, 0.2);
                color: #4facfe;
                border: 1px solid #4facfe;
                border-radius: 5px;
                padding: 10px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(79, 172, 254, 0.3);
            }
        """)
        btn_info.clicked.connect(self.show_build_info)
        
        builds_buttons_layout.addWidget(btn_install)
        builds_buttons_layout.addWidget(btn_info)
        builds_buttons_layout.addStretch()
        
        builds_layout.addWidget(builds_buttons)
        builds_group.setLayout(builds_layout)
        layout.addWidget(builds_group)
        
        # Установленные сборки
        installed_group = QGroupBox("📁 Установленные сборки")
        installed_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                color: #4facfe;
                border: 2px solid #4facfe;
                border-radius: 10px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
            }
        """)
        
        self.installed_builds_list = QListWidget()
        self.installed_builds_list.setStyleSheet("""
            QListWidget {
                background-color: rgba(255, 255, 255, 0.05);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 5px;
                color: white;
                font-size: 14px;
                min-height: 150px;
            }
            QListWidget::item {
                padding: 10px;
                border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            }
            QListWidget::item:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Тестовые установленные сборки
        test_installed = [
            "Vanilla [1.20.1]",
            "My Custom Pack [1.19.2]"
        ]
        
        for build in test_installed:
            item = QListWidgetItem(build)
            self.installed_builds_list.addItem(item)
        
        installed_layout = QVBoxLayout()
        installed_layout.addWidget(self.installed_builds_list)
        
        # Кнопки для установленных сборок
        installed_buttons = QWidget()
        installed_buttons_layout = QHBoxLayout(installed_buttons)
        installed_buttons_layout.setContentsMargins(0, 10, 0, 0)
        
        btn_play = QPushButton("🎮 Запустить")
        btn_play.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_play.setStyleSheet("""
            QPushButton {
                background-color: #4facfe;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #3a9bed;
            }
        """)
        btn_play.clicked.connect(self.play_installed_build)
        
        btn_remove = QPushButton("🗑️ Удалить")
        btn_remove.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_remove.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 85, 85, 0.2);
                color: #ff5555;
                border: 1px solid #ff5555;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: rgba(255, 85, 85, 0.3);
            }
        """)
        btn_remove.clicked.connect(self.remove_installed_build)
        
        installed_buttons_layout.addWidget(btn_play)
        installed_buttons_layout.addWidget(btn_remove)
        installed_buttons_layout.addStretch()
        
        installed_layout.addWidget(installed_buttons)
        installed_group.setLayout(installed_layout)
        layout.addWidget(installed_group)
        
        layout.addStretch()
        return page
    
    def setup_status_bar(self):
        """Настройка статусбара"""
        status_bar = self.statusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: rgba(30, 30, 40, 0.9);
                color: white;
                border-top: 1px solid rgba(255, 255, 255, 0.1);
            }
        """)
        
        # Информация о пользователе
        self.status_user_label = QLabel("👤 Гость")
        self.status_user_label.setStyleSheet("padding: 5px; font-size: 12px;")
        status_bar.addWidget(self.status_user_label)
        
        # Разделитель
        status_bar.addWidget(QLabel("|"))
        
        # Версия лаунчера
        version_label = QLabel(f"SuperLauncher {CURRENT_VERSION}")
        version_label.setStyleSheet("padding: 5px; font-size: 12px; color: #aaaaaa;")
        status_bar.addWidget(version_label)
        
        # Разделитель
        status_bar.addWidget(QLabel("|"))
        
        # Время
        self.status_time_label = QLabel()
        self.status_time_label.setStyleSheet("padding: 5px; font-size: 12px;")
        status_bar.addPermanentWidget(self.status_time_label)
        
        # Таймер обновления времени
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        self.update_time()
    
    def update_time(self):
        """Обновление времени в статусбаре"""
        current_time = datetime.datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.status_time_label.setText(f"🕒 {current_time}")
    
    def show_welcome_message(self):
        """Показать приветственное сообщение"""
        if self.holiday_theme.current_holiday:
            holiday_name = {
                "christmas": "Рождеством",
                "new_year": "Новым Годом",
                "new_year_eve": "Новым Годом"
            }.get(self.holiday_theme.current_holiday, "")
            
            if holiday_name:
                QMessageBox.information(
                    self,
                    f"🎄 С {holiday_name}!",
                    f"SuperLauncher 2026 желает вам счастливого {holiday_name.lower()}!\n\n"
                    f"Заходите ежедневно за подарками и участвуйте в праздничных ивентах!"
                )
    
    def check_auto_login(self):
        """Проверка автоматического входа"""
        # Можно добавить сохранение сессии
        pass
    
    def show_login_dialog(self):
        """Показать диалог входа"""
        dialog = LoginDialog(self.account_system, self)
        if dialog.exec():
            user = dialog.get_user()
            if user:
                self.update_user_info(user)
                self.check_for_gifts()
    
    def update_user_info(self, user):
        """Обновление информации о пользователе"""
        self.username_label.setText(user["username"])
        self.user_status_label.setText(f"Уровень {user.get('level', 1)} • {user.get('xp', 0)} XP")
        self.login_button.setText("Выйти")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.logout_user)
        
        self.status_user_label.setText(f"👤 {user['username']} | Ур. {user.get('level', 1)}")
    
    def logout_user(self):
        """Выход пользователя"""
        self.account_system.logout()
        self.username_label.setText("Гость")
        self.user_status_label.setText("Не авторизован")
        self.login_button.setText("Войти / Зарегистрироваться")
        self.login_button.clicked.disconnect()
        self.login_button.clicked.connect(self.show_login_dialog)
        
        self.status_user_label.setText("👤 Гость")
    
    def delete_account(self):
        """Удаление аккаунта"""
        reply = QMessageBox.question(
            self,
            "Удаление аккаунта",
            "Вы уверены, что хотите удалить аккаунт? Это действие нельзя отменить.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Удаление аккаунта",
                "Функция удаления аккаунта находится в разработке."
            )
    
    def check_for_gifts(self):
        """Проверка доступных подарков"""
        if self.account_system.current_user:
            gift, message = self.gift_system.get_daily_gift()
            if gift:
                GiftNotification(gift, self).exec()
    
    def claim_daily_gift(self):
        """Получение ежедневного подарка"""
        if not self.account_system.current_user:
            self.show_login_dialog()
            return
        
        gift, message = self.gift_system.get_daily_gift()
        if gift:
            GiftNotification(gift, self).exec()
        else:
            QMessageBox.information(self, "Подарки", message)
    
    def apply_skin(self, skin_name):
        """Применение скина"""
        if not self.account_system.current_user:
            QMessageBox.warning(self, "Ошибка", "Требуется вход в аккаунт")
            return
        
        success, message = self.skins_manager.apply_skin_to_minecraft(skin_name.lower().replace(" ", "_"))
        if success:
            self.current_skin_name.setText(skin_name)
            QMessageBox.information(self, "Успех", message)
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def unlock_skin(self, skin_name, price):
        """Разблокировка скина"""
        if not self.account_system.current_user:
            QMessageBox.warning(self, "Ошибка", "Требуется вход в аккаунт")
            return
        
        skin_id = skin_name.lower().replace(" ", "_")
        user = self.account_system.current_user
        
        success, message = self.skins_manager.unlock_skin(skin_id, user)
        if success:
            QMessageBox.information(self, "Успех", message)
            # Обновляем страницу скинов
            self.pages.setCurrentIndex(5)  # Переходим на страницу скинов
        else:
            QMessageBox.warning(self, "Ошибка", message)
    
    def upload_custom_skin(self):
        """Загрузка кастомного скина"""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Выберите изображение скина")
        file_dialog.setNameFilter("Изображения (*.png *.jpg *.jpeg)")
        
        if file_dialog.exec():
            files = file_dialog.selectedFiles()
            if files:
                image_path = files[0]
                success, result = self.skins_manager.upload_custom_skin(image_path)
                if success:
                    QMessageBox.information(self, "Успех", f"Скин загружен! ID: {result}")
                else:
                    QMessageBox.warning(self, "Ошибка", result)
    
    def activate_license(self):
        """Активация лицензии"""
        license_key = self.license_input.text().strip()
        if not license_key:
            QMessageBox.warning(self, "Ошибка", "Введите ключ лицензии")
            return
        
        if not self.account_system.current_user:
            QMessageBox.warning(self, "Ошибка", "Требуется вход в аккаунт")
            return
        
        success, message = self.account_system.activate_license(
            license_key,
            self.account_system.current_user["user_id"]
        )
        
        if success:
            QMessageBox.information(self, "Успех", message)
            self.license_label.setText(f"Статус: {self.account_system.current_user.get('license_tier', 'free').upper()}")
        else:
            QMessageBox.critical(self, "Ошибка", message)
    
    def search_builds(self):
        """Поиск сборок"""
        query = self.builds_search.text()
        if not query.strip():
            QMessageBox.warning(self, "Предупреждение", "Введите поисковый запрос")
            return
        
        # Здесь будет реальный поиск
        QMessageBox.information(
            self,
            "Поиск",
            f"Поиск сборок по запросу: '{query}'\n\n"
            "В реальном приложении здесь будет отображен\n"
            "результат поиска из Modrinth API."
        )
    
    def install_selected_build(self):
        """Установка выбранной сборки"""
        current_item = self.builds_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите сборку для установки")
            return
        
        build_name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Установка сборки",
            f"Установить сборку:\n\n{build_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Установка",
                f"Начинаем установку сборки:\n\n{build_name}\n\n"
                "В реальном приложении здесь будет процесс\n"
                "скачивания и установки сборки."
            )
    
    def show_build_info(self):
        """Показать информацию о сборке"""
        current_item = self.builds_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите сборку для просмотра информации")
            return
        
        build_name = current_item.text()
        QMessageBox.information(
            self,
            "Информация о сборке",
            f"Название: {build_name}\n\n"
            "Здесь будет подробная информация о сборке:\n"
            "- Версия Minecraft\n"
            "- Модификации\n"
            "- Описание\n"
            "- Автор\n"
            "- Рейтинг"
        )
    
    def play_installed_build(self):
        """Запуск установленной сборки"""
        current_item = self.installed_builds_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите сборку для запуска")
            return
        
        build_name = current_item.text()
        QMessageBox.information(
            self,
            "Запуск сборки",
            f"Запускаем сборку:\n\n{build_name}\n\n"
            "В реальном приложении здесь будет запуск\n"
            "Minecraft с выбранной сборкой модов."
        )
    
    def remove_installed_build(self):
        """Удаление установленной сборки"""
        current_item = self.installed_builds_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Предупреждение", "Выберите сборку для удаления")
            return
        
        build_name = current_item.text()
        reply = QMessageBox.question(
            self,
            "Удаление сборки",
            f"Удалить сборку:\n\n{build_name}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            QMessageBox.information(
                self,
                "Удаление",
                f"Сборка '{build_name}' будет удалена.\n\n"
                "В реальном приложении здесь будет процесс\n"
                "удаления файлов сборки."
            )
    
    def show_help(self):
        """Показать справку"""
        QMessageBox.information(
            self,
            "Помощь",
            "SuperLauncher 2026 - Новогоднее издание\n\n"
            "🎮 Быстрый запуск: Нажмите кнопку 'Играть' на странице Minecraft\n"
            "🎁 Подарки: Заходите ежедневно за бесплатными наградами\n"
            "👤 Аккаунт: Создайте аккаунт для синхронизации и доступа к премиум функциям\n"
            "🖼️ Скины: Разблокируйте и применяйте уникальные скины\n"
            "📦 Сборки: Устанавливайте готовые сборки модов\n"
            "🧩 Моды: Ищите и устанавливайте моды из Modrinth\n"
            "📢 Новости: Следите за обновлениями лаунчера\n"
            "🔄 Обновления: Обновляйте лаунчер до последней версии\n"
            "🖧 Серверы: Создавайте и управляйте Minecraft-серверами\n"
            "⚙️ Настройки: Настройте лаунчер под себя\n\n"
            "Поддержка: https://ludvig2457.github.io"
        )
    
    def show_stats(self):
        """Показать статистику"""
        QMessageBox.information(
            self,
            "Статистика",
            "Ваша статистика:\n\n"
            "• Уровень: 1\n"
            "• Опыт: 0/1000\n"
            "• Игровое время: 0 часов\n"
            "• Запусков: 0\n"
            "• Получено подарков: 0\n"
            "• Разблокировано скинов: 1\n"
            "• Установлено сборок: 0"
        )
    
    def show_social(self):
        """Показать социальные функции"""
        QMessageBox.information(
            self,
            "Социальное",
            "Социальные функции:\n\n"
            "• Друзья (в разработке)\n"
            "• Группы (в разработке)\n"
            "• Общие сборки (в разработке)\n"
            "• Рейтинги (в разработке)\n\n"
            "Эти функции появятся в следующих обновлениях!"
        )
    
    # Существующие методы
    def tr(self, key: str) -> str:
        lang = "ru"
        if hasattr(self, "settings_page") and self.settings_page:
            lang = self.settings_page.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)
    
    def on_button_clicked(self, button):
        idx = self.sidebar.nav_buttons.index(button)
        if idx < self.pages.count():
            self.pages.setCurrentIndex(idx)
            for i, btn in enumerate(self.sidebar.nav_buttons):
                btn.setChecked(i == idx)
        else:
            print(f"⚠️ Ошибка: страница с индексом {idx} не существует")
    
    def update_progress(self, value, max_value, label):
        minecraft_page = self.pages.widget(10)  # Minecraft страница теперь 10
        if hasattr(minecraft_page, 'start_progress'):
            minecraft_page.start_progress.setMaximum(max_value)
            minecraft_page.start_progress.setValue(value)
            minecraft_page.start_progress_label.setText(label)
    
    def state_update(self, running):
        minecraft_page = self.pages.widget(10)  # Minecraft страница теперь 10
        if hasattr(minecraft_page, 'start_button'):
            minecraft_page.start_button.setDisabled(running)
        if hasattr(minecraft_page, 'start_progress'):
            minecraft_page.start_progress.setVisible(running)
            minecraft_page.start_progress_label.setVisible(running)
    
    def apply_settings(self):
        if hasattr(self, "settings_page"):
            theme = self.settings_page.config.get("theme", "dark")
            # Обновляем тему
            self.custom_ui.apply_to_widget(self)
    
    def launch_game(self):
        minecraft_page = self.pages.widget(10)  # Minecraft страница теперь 10
        if hasattr(self, "settings_page"):
            config = self.settings_page.config
            version = minecraft_page.version_select.currentText()
            username = minecraft_page.username.text() or "player"
            
            # Если пользователь авторизован, используем его имя
            if self.account_system.current_user:
                username = self.account_system.current_user["username"]
            
            if config.get("launch_mode") == "java" and config.get("java_path"):
                java_path = config["java_path"]
                print(f"Запуск через Java: {java_path}")
            else:
                self.launch_thread.launch_setup_signal.emit(version, username)
                self.launch_thread.start()
    
    def closeEvent(self, event):
        if hasattr(self, "discord_rpc_thread") and self.discord_rpc_thread:
            self.discord_rpc_thread.stop()
        super().closeEvent(event)

if __name__ == "__main__":
    import sys
    from PyQt6.QtWidgets import QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
