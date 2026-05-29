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
from minecraft_launcher_lib import fabric as fabric_loader
from minecraft_launcher_lib import forge as forge_loader
from minecraft_launcher_lib import quilt as quilt_loader
# neoforge пока недоступен в этой версии minecraft_launcher_lib

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
    QGridLayout, QGroupBox, QTabWidget, QProgressDialog
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
    "assets/skins", "assets/icons",
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
        "RAM allocation:": "Выделение ОЗУ:",
        "JVM arguments:": "JVM аргументы:",

        # --- MinecraftPage ---
        "Play": "Играть",
        "Username": "Имя пользователя",
        "No versions available": "Версии недоступны",

        # --- ModsPage ---
        "Mods from": "Моды из",
        "Modrinth": "Modrinth",
        "CurseForge": "CurseForge",
        "Select file:": "Выберите файл:",
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
        "RAM (GB):": "ОЗУ (ГБ):",
        "Console": "Консоль",
        "Plugins": "Плагины",
        "Backup": "Бэкап",
        "Search": "Поиск",
        "Install": "Установить",
        "Uninstall": "Удалить",
        "Open folder": "Открыть папку",
        "Server console": "Консоль сервера",
        "Enter command...": "Введите команду...",
        "Send": "Отправить",
        "Online mode": "Online-mode",
        "Offline mode": "Оффлайн режим",
        "Max players": "Макс. игроков",
        "MOTD": "MOTD",
        "Create Backup": "Создать бэкап",
        "Restore": "Восстановить",
        "Backup created": "Бэкап создан",
        "Backup restored": "Бэкап восстановлен",
        "Downloading plugin...": "Загрузка плагина...",
        "Plugin installed": "Плагин установлен",
        "Search plugins...": "Поиск плагинов...",
        "No plugins found": "Плагины не найдены",
        "Backups": "Бэкапы",
        "Restore backup": "Восстановить бэкап",
        "Are you sure?": "Вы уверены?",
        "Install plugin": "Установка плагина",
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
        "RAM allocation:": "RAM allocation:",
        "JVM arguments:": "JVM arguments:",

        # --- MinecraftPage ---
        "Play": "Play",
        "Username": "Username",
        "No versions available": "No versions available",

        # --- ModsPage ---
        "Mods from": "Mods from",
        "Modrinth": "Modrinth",
        "CurseForge": "CurseForge",
        "Select file:": "Select file:",
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
        "RAM (GB):": "RAM (GB):",
        "Console": "Console",
        "Plugins": "Plugins",
        "Backup": "Backup",
        "Search": "Search",
        "Install": "Install",
        "Uninstall": "Uninstall",
        "Open folder": "Open folder",
        "Server console": "Server console",
        "Enter command...": "Enter command...",
        "Send": "Send",
        "Online mode": "Online mode",
        "Offline mode": "Offline mode",
        "Max players": "Max players",
        "MOTD": "MOTD",
        "Create Backup": "Create Backup",
        "Restore": "Restore",
        "Backup created": "Backup created",
        "Backup restored": "Backup restored",
        "Downloading plugin...": "Downloading plugin...",
        "Plugin installed": "Plugin installed",
        "Search plugins...": "Search plugins...",
        "No plugins found": "No plugins found",
        "Backups": "Backups",
        "Restore backup": "Restore backup",
        "Are you sure?": "Are you sure?",
        "Install plugin": "Install plugin",
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
        "max_ram": 4096,
        "jvm_args": "",
        "language": "ru",
        "theme": "dark",
        "launch_mode": "launcher_lib",
        "curseforge_api_key": ""
    }


def save_config(config):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print("Ошибка сохранения настроек:", e)


MODRINTH_API = "https://api.modrinth.com/v2"
CURSEFORGE_API = "https://api.curseforge.com/v1"

_cf_api_key_cache = None
def get_cf_api_key():
    global _cf_api_key_cache
    if _cf_api_key_cache is None:
        cfg = load_config()
        _cf_api_key_cache = cfg.get("curseforge_api_key", "")
    return _cf_api_key_cache

def invalidate_cf_api_key_cache():
    global _cf_api_key_cache
    _cf_api_key_cache = None

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

    def search_modrinth(self, query="", limit=20):
        try:
            params = {
                "limit": limit,
                "index": "downloads",
                "facets": '[["project_type:modpack"]]'
            }
            if query:
                params["query"] = query
            resp = requests.get(f"{self.modrinth_api}/search", params=params, timeout=15,
                                headers={"User-Agent": "SuperLauncher/2.0"})
            data = resp.json()
            modpacks = []
            for hit in data.get("hits", []):
                modpacks.append({
                    "id": hit["project_id"], "slug": hit.get("slug"),
                    "name": hit["title"], "description": hit.get("description", ""),
                    "icon_url": hit.get("icon_url"), "downloads": hit.get("downloads", 0),
                    "author": hit.get("author", "Unknown"),
                    "versions": hit.get("versions", []), "loaders": hit.get("loaders", []),
                    "source": "modrinth"
                })
            return modpacks
        except Exception as e:
            print(f"Modrinth search error: {e}")
            return []

    def search_curseforge(self, query="", limit=30):
        try:
            params = {
                "gameId": 432, "classId": 4471, "searchFilter": query,
                "pageSize": limit, "sortField": 2, "sortOrder": "desc"
            }
            resp = requests.get(f"{self.curseforge_api}/mods/search", params=params,
                                headers={"x-api-key": get_cf_api_key(), "Accept": "application/json"}, timeout=15)
            data = resp.json()
            modpacks = []
            for mod in data.get("data", []):
                modpacks.append({
                    "id": mod["id"], "name": mod.get("name", ""),
                    "description": mod.get("summary", ""),
                    "icon_url": (mod.get("logo") or {}).get("url"),
                    "downloads": mod.get("downloadCount", 0),
                    "author": (mod.get("authors") or [{}])[0].get("name", "Unknown") if mod.get("authors") else "Unknown",
                    "source": "curseforge"
                })
            return modpacks
        except Exception as e:
            print(f"CurseForge search error: {e}")
            return []

    def get_modpack_versions(self, project_id, source="modrinth"):
        if source == "modrinth":
            try:
                resp = requests.get(f"{self.modrinth_api}/project/{project_id}/version", timeout=15,
                                    headers={"User-Agent": "SuperLauncher/2.0"})
                return resp.json()
            except:
                return []
        else:
            try:
                resp = requests.get(f"{self.curseforge_api}/mods/{project_id}/files",
                                    headers={"x-api-key": get_cf_api_key(), "Accept": "application/json"}, timeout=15)
                data = resp.json()
                return data.get("data", [])
            except:
                return []

    def backup_mods(self, mc_dir):
        mods_dir = os.path.join(mc_dir, "mods")
        if not os.path.exists(mods_dir):
            return
        import time
        backup = os.path.join(mc_dir, f"mods_backup_{int(time.time())}")
        shutil.copytree(mods_dir, backup)
        return backup

    def restore_mods(self, mc_dir):
        import glob, re
        backups = sorted(glob.glob(os.path.join(mc_dir, "mods_backup_*")))
        if not backups:
            return False
        backup = backups[-1]
        mods_dir = os.path.join(mc_dir, "mods")
        if os.path.exists(mods_dir):
            shutil.rmtree(mods_dir, ignore_errors=True)
        shutil.copytree(backup, mods_dir)
        shutil.rmtree(backup, ignore_errors=True)
        return True

    def deduplicate_mods(self, mc_dir):
        mods_dir = os.path.join(mc_dir, "mods")
        if not os.path.isdir(mods_dir):
            return
        import re

        def _parse_version(ver_str):
            parts = ver_str.replace("-", ".").split(".")
            nums = []
            for p in parts:
                try:
                    nums.append(int(p))
                except ValueError:
                    nums.append(0)
            return tuple(nums)

        def _read_meta(path):
            with zipfile.ZipFile(path, 'r') as z:
                if "META-INF/mods.toml" in z.namelist():
                    text = z.read("META-INF/mods.toml").decode("utf-8", errors="replace")
                    m = re.search(r'^\s*modId\s*=\s*"([^"]+)"', text, re.MULTILINE)
                    v = re.search(r'^\s*version\s*=\s*"([^"]+)"', text, re.MULTILINE)
                    return (m.group(1), v.group(1) if v else "0") if m else None
                if "fabric.mod.json" in z.namelist():
                    data = json.loads(z.read("fabric.mod.json"))
                    mid = data.get("id")
                    return (mid, data.get("version", "0")) if mid else None
                if "quilt.mod.json" in z.namelist():
                    data = json.loads(z.read("quilt.mod.json"))
                    mid = data.get("quilt_loader", {}).get("id")
                    return (mid, data.get("version", "0") or "0") if mid else None
            return None

        entries = []
        for fn in os.listdir(mods_dir):
            if not fn.endswith(".jar"):
                continue
            path = os.path.join(mods_dir, fn)
            try:
                meta = _read_meta(path)
                if meta:
                    mid, ver = meta
                    # loader_priority: 0=Forge (mods.toml), 1=Fabric, 2=Quilt
                    with zipfile.ZipFile(path, 'r') as z:
                        if "META-INF/mods.toml" in z.namelist():
                            lp = 0
                        elif "fabric.mod.json" in z.namelist():
                            lp = 1
                        else:
                            lp = 2
                    entries.append((mid, fn, path, ver, lp))
            except Exception:
                pass

        mod_groups = {}
        for mid, fn, path, ver, lp in entries:
            mod_groups.setdefault(mid, []).append((fn, path, ver, lp))

        removed = 0
        for mid, group in mod_groups.items():
            if len(group) > 1:
                group.sort(key=lambda x: (x[3], tuple(-n for n in _parse_version(x[2]))))
                for fn, path, ver, lp in group[1:]:
                    try:
                        os.remove(path)
                        removed += 1
                        loader_name = ["Forge", "Fabric", "Quilt"][lp]
                        print(f"Удалён дубликат: {fn} (modId={mid}, версия={ver}, {loader_name})")
                    except Exception:
                        pass
        if removed:
            print(f"Дедупликация завершена: удалено {removed} дубликатов модов")

    # Известные конфликтные Fabric-моды, которые ломают RegistryDataLoader через Sinytra Connector
    CONFLICTING_MODS = {
        "betterend": "BetterEnd (Fabric) — ломает загрузку регистров через Connector",
        "bclib": "BCLib (Fabric, библиотека BetterEnd) — конфликтует с fabric-registry-sync-v0",
        "betterendisland": "BetterEnd Island (Fabric) — зависит от BCLib",
    }

    def detect_conflicting_mods(self, mc_dir):
        import re
        mods_dir = os.path.join(mc_dir, "mods")
        if not os.path.isdir(mods_dir):
            return []
        found = []
        for fn in os.listdir(mods_dir):
            if not fn.endswith(".jar"):
                continue
            path = os.path.join(mods_dir, fn)
            try:
                with zipfile.ZipFile(path, 'r') as z:
                    if "fabric.mod.json" in z.namelist():
                        data = json.loads(z.read("fabric.mod.json"))
                        mid = data.get("id", "")
                        if mid in self.CONFLICTING_MODS:
                            found.append((fn, mid, self.CONFLICTING_MODS[mid]))
                    elif "META-INF/mods.toml" in z.namelist():
                        text = z.read("META-INF/mods.toml").decode("utf-8", errors="replace")
                        m = re.search(r'^\s*modId\s*=\s*"([^"]+)"', text, re.MULTILINE)
                        if m:
                            mid = m.group(1)
                            if mid in self.CONFLICTING_MODS:
                                found.append((fn, mid, self.CONFLICTING_MODS[mid]))
            except Exception:
                pass
        return found

    def download_file(self, url, save_path, callback=None):
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))
        written = 0
        with open(save_path, "wb") as f:
            for chunk in resp.iter_content(8192):
                if chunk:
                    f.write(chunk)
                    written += len(chunk)
                    if callback and total > 0:
                        callback(int(written * 100 / total))
        if callback and total > 0:
            callback(100)

    def _install_modrinth_pack(self, version_data, mc_dir, callback=None):
        files = version_data.get("files", [])
        if not files:
            return None, "Нет файлов для скачивания"
        primary = next((f for f in files if f.get("primary")), files[0])
        if not primary.get("url"):
            return None, "Нет ссылки на файл"

        ver_num = version_data.get("version_number", "?")
        import tempfile, zipfile, json as j, shutil
        tmp = tempfile.mkdtemp(prefix="mrpack-")
        try:
            mrpack_path = os.path.join(tmp, primary["filename"])
            if callback:
                callback(0)
            print(f"Бекап старых модов перед установкой сборки...")
            self.backup_mods(mc_dir)
            self.download_file(primary["url"], mrpack_path, callback)

            if callback:
                callback(50)

            with zipfile.ZipFile(mrpack_path, 'r') as z:
                z.extractall(tmp)

            index_path = os.path.join(tmp, "modrinth.index.json")
            if not os.path.exists(index_path):
                return None, "modrinth.index.json не найден в .mrpack"
            with open(index_path, encoding="utf-8") as f:
                idx = j.load(f)

            deps = idx.get("dependencies", {})
            mc_version = deps.get("minecraft", "unknown")
            loader_type = "vanilla"
            for k in deps:
                if k in ("fabric-loader", "quilt-loader"):
                    loader_type = k.replace("-loader", "")
                elif k == "forge":
                    loader_type = "forge"
                elif k == "neoforge":
                    loader_type = "neoforge"

            pack_name = idx.get("name", version_data.get("name", "modpack")).strip()
            safe_name = "".join(c for c in pack_name if c.isalnum() or c in " _-")

            idx_files = idx.get("files", [])
            total_files = len(idx_files)
            installed = []
            for i, entry in enumerate(idx_files):
                path = entry.get("path", "")
                downloads = entry.get("downloads", [])
                if not path or not downloads:
                    continue
                target = os.path.normpath(os.path.join(mc_dir, path))
                if not target.startswith(os.path.normpath(mc_dir) + os.sep):
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if not os.path.exists(target):
                    try:
                        self.download_file(downloads[0], target, callback)
                    except Exception:
                        if os.path.exists(target):
                            os.remove(target)
                        pass
                installed.append(target)
                if callback and total_files > 0:
                    callback(50 + int(40 * (i + 1) / total_files))

            for odir in ("overrides", "client-overrides"):
                sdir = os.path.join(tmp, odir)
                if os.path.exists(sdir):
                    for root, dirs, flist in os.walk(sdir):
                        rel = os.path.relpath(root, sdir)
                        for fn in flist:
                            src = os.path.join(root, fn)
                            dst = os.path.join(mc_dir, rel, fn)
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            installed.append(dst)

            if callback:
                callback(95)
            self.deduplicate_mods(mc_dir)
            if callback:
                callback(100)
            return safe_name, {"mc_version": mc_version, "loader": loader_type,
                               "_source": "modrinth", "_version_id": ver_num,
                               "_installed_files": installed}
        except Exception as e:
            return None, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def _install_curseforge_pack(self, version_data, mc_dir, callback=None):
        dl_url = version_data.get("downloadUrl", "")
        if not dl_url:
            try:
                resp = requests.get(
                    f"{self.curseforge_api}/mods/{version_data['modId']}/files/{version_data['id']}/download-url",
                    headers={"x-api-key": get_cf_api_key(), "Accept": "application/json"}, timeout=15)
                dl_url = resp.json().get("data", "")
            except Exception:
                pass
        if not dl_url:
            return None, "CurseForge: не удалось получить ссылку"

        import tempfile, zipfile, json as j, shutil
        tmp = tempfile.mkdtemp(prefix="cfpack-")
        try:
            filename = version_data.get("fileName", "pack.zip")
            zip_path = os.path.join(tmp, filename)
            if callback:
                callback(0)
            print(f"Бекап старых модов перед установкой сборки...")
            self.backup_mods(mc_dir)
            self.download_file(dl_url, zip_path, callback)

            if callback:
                callback(30)

            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(tmp)

            manifest_path = os.path.join(tmp, "manifest.json")
            installed = []
            if not os.path.exists(manifest_path):
                mc_version = "unknown"
                loader_type = "vanilla"
                for root, dirs, flist in os.walk(tmp):
                    for fn in flist:
                        if fn.endswith((".jar", ".litemod")):
                            rel = os.path.relpath(os.path.join(root, fn), tmp)
                            dst = os.path.join(mc_dir, rel)
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(os.path.join(root, fn), dst)
                            installed.append(dst)
                if callback:
                    callback(100)
                return "curseforge-pack", {"mc_version": mc_version, "loader": loader_type, "_source": "curseforge", "_version_id": str(version_data.get("id", "")), "_installed_files": installed}

            with open(manifest_path, encoding="utf-8") as f:
                manifest = j.load(f)

            mc_version = manifest.get("minecraft", {}).get("version", "unknown")
            loader_data = manifest.get("minecraft", {}).get("modLoaders", [{}])[0] if manifest.get("minecraft", {}).get("modLoaders") else {}
            loader_id = loader_data.get("id", "")
            loader_type = "forge"
            if "fabric" in loader_id.lower():
                loader_type = "fabric"
            elif "quilt" in loader_id.lower():
                loader_type = "quilt"
            elif "neoforge" in loader_id.lower():
                loader_type = "neoforge"

            cf_files = manifest.get("files", [])
            for i, fentry in enumerate(cf_files):
                project_id = fentry.get("projectID", 0)
                file_id = fentry.get("fileID", 0)
                fpath = fentry.get("filePathOverride", fentry.get("path", ""))
                if not fpath:
                    continue
                try:
                    fresp = requests.get(
                        f"{self.curseforge_api}/mods/{project_id}/files/{file_id}/download-url",
                        headers={"x-api-key": get_cf_api_key(), "Accept": "application/json"}, timeout=15)
                    furl = fresp.json().get("data", "")
                    if furl:
                        target = os.path.normpath(os.path.join(mc_dir, fpath))
                        if not target.startswith(os.path.normpath(mc_dir) + os.sep):
                            continue
                        os.makedirs(os.path.dirname(target), exist_ok=True)
                        if not os.path.exists(target):
                            try:
                                self.download_file(furl, target, callback)
                            except Exception:
                                if os.path.exists(target):
                                    os.remove(target)
                                pass
                        installed.append(target)
                except Exception:
                    pass
                if callback and cf_files:
                    callback(30 + int(60 * (i + 1) / len(cf_files)))

            for odir in ("overrides",):
                sdir = os.path.join(tmp, odir)
                if os.path.exists(sdir):
                    for root, dirs, flist in os.walk(sdir):
                        rel = os.path.relpath(root, sdir)
                        for fn in flist:
                            src = os.path.join(root, fn)
                            dst = os.path.join(mc_dir, rel, fn)
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            installed.append(dst)

            if callback:
                callback(95)
            self.deduplicate_mods(mc_dir)
            if callback:
                callback(100)
            return manifest.get("name", "curseforge-pack"), {"mc_version": mc_version, "loader": loader_type, "_source": "curseforge", "_version_id": str(version_data.get("id", "")), "_installed_files": installed}
        except Exception as e:
            return None, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def download_and_install(self, version_data, source, install_base, callback=None):
        if source == "modrinth":
            return self._install_modrinth_pack(version_data, install_base, callback)
        elif source == "curseforge":
            return self._install_curseforge_pack(version_data, install_base, callback)
        return None, "Неизвестный источник"

    def create_install_config(self, pack_folder, source, version_id, mc_versions, loaders):
        os.makedirs(pack_folder, exist_ok=True)
        config = {
            "type": f"{source}_modpack",
            "source": source,
            "version_id": version_id,
            "mc_versions": mc_versions if isinstance(mc_versions, list) else [mc_versions],
            "loaders": loaders if isinstance(loaders, list) else [loaders],
            "install_path": pack_folder,
            "installed_at": datetime.datetime.now().isoformat()
        }
        with open(os.path.join(pack_folder, "superlauncher_config.json"), "w", encoding="utf-8") as f:
            json.dump(config, f, indent=2)

    def get_installed_packs(self, install_base):
        installed = []
        if os.path.exists(install_base):
            for folder in os.listdir(install_base):
                cfg = os.path.join(install_base, folder, "superlauncher_config.json")
                if os.path.exists(cfg):
                    try:
                        with open(cfg, encoding="utf-8") as f:
                            conf = json.load(f)
                            conf["name"] = folder
                            installed.append(conf)
                    except:
                        pass
        return installed

    def _install_local_mrpack(self, mrpack_path, mc_dir, callback=None):
        import tempfile, zipfile, json as j, shutil
        tmp = tempfile.mkdtemp(prefix="import-")
        try:
            if callback:
                callback(0)
            print(f"Бекап старых модов перед импортом сборки...")
            self.backup_mods(mc_dir)
            with zipfile.ZipFile(mrpack_path, 'r') as z:
                z.extractall(tmp)
            if callback:
                callback(10)
            index_path = os.path.join(tmp, "modrinth.index.json")
            if not os.path.exists(index_path):
                return None, "modrinth.index.json не найден"
            with open(index_path, encoding="utf-8") as f:
                idx = j.load(f)
            deps = idx.get("dependencies", {})
            mc_version = deps.get("minecraft", "unknown")
            loader_type = "vanilla"
            for k in deps:
                if k in ("fabric-loader", "quilt-loader"):
                    loader_type = k.replace("-loader", "")
                elif k == "forge":
                    loader_type = "forge"
                elif k == "neoforge":
                    loader_type = "neoforge"
            pack_name = idx.get("name", "imported").strip()
            safe_name = "".join(c for c in pack_name if c.isalnum() or c in " _-")
            idx_files = idx.get("files", [])
            installed = []
            for i, entry in enumerate(idx_files):
                path = entry.get("path", "")
                downloads = entry.get("downloads", [])
                if not path or not downloads:
                    continue
                target = os.path.normpath(os.path.join(mc_dir, path))
                if not target.startswith(os.path.normpath(mc_dir) + os.sep):
                    continue
                os.makedirs(os.path.dirname(target), exist_ok=True)
                if not os.path.exists(target):
                    try:
                        self.download_file(downloads[0], target, callback)
                    except Exception:
                        if os.path.exists(target):
                            os.remove(target)
                        pass
                installed.append(target)
                if callback and idx_files:
                    callback(10 + int(80 * (i + 1) / len(idx_files)))
            for odir in ("overrides", "client-overrides"):
                sdir = os.path.join(tmp, odir)
                if os.path.exists(sdir):
                    for root, dirs, flist in os.walk(sdir):
                        rel = os.path.relpath(root, sdir)
                        for fn in flist:
                            src = os.path.join(root, fn)
                            dst = os.path.join(mc_dir, rel, fn)
                            os.makedirs(os.path.dirname(dst), exist_ok=True)
                            shutil.copy2(src, dst)
                            installed.append(dst)
            if callback:
                callback(95)
            self.deduplicate_mods(mc_dir)
            if callback:
                callback(100)
            return safe_name, {"mc_version": mc_version, "loader": loader_type, "_installed_files": installed}
        except Exception as e:
            return None, str(e)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    
    def _cf_cache_path(self, mc_dir, slug, mc_ver, loader_type):
        cache_dir = os.path.join(mc_dir, "cache", "curseforge")
        os.makedirs(cache_dir, exist_ok=True)
        return os.path.join(cache_dir, f"{slug}_{mc_ver}_{loader_type}.jar")

    def download_curseforge_mods_from_modlist(self, mc_dir, callback=None, mc_ver=None, loader_type="forge"):
        import re, hashlib
        from concurrent.futures import ThreadPoolExecutor, as_completed
        modlist_path = os.path.join(mc_dir, "modlist.html")
        if not os.path.exists(modlist_path):
            return 0, "modlist.html не найден"
        with open(modlist_path, encoding="utf-8") as f:
            html = f.read()
        urls = re.findall(r'href="(https://www\.curseforge\.com/minecraft/[^"]+)"', html)
        if not urls:
            return 0, "Нет CurseForge ссылок в modlist.html"
        total = len(urls)
        if not mc_ver:
            mc_ver = "1.20.1"
        loader_map = {"forge": 1, "fabric": 4, "quilt": 5, "neoforge": 6}
        mod_loader_type = loader_map.get(loader_type.lower(), 1)
        cf_key = get_cf_api_key()

        # Подготовка списка задач: (slug, dest_dir, cache_path)
        tasks = []
        for url in urls:
            parts = url.split("/")
            cat = parts[-2] if len(parts) >= 2 else "mc-mods"
            slug = parts[-1] if parts else ""
            if not slug:
                continue
            dest_dir = os.path.join(mc_dir, "mods")
            if "texture" in cat:
                dest_dir = os.path.join(mc_dir, "resourcepacks")
            elif "shader" in cat:
                dest_dir = os.path.join(mc_dir, "shaderpacks")
            os.makedirs(dest_dir, exist_ok=True)
            exists = any(slug.replace("-", "").lower() in f.replace("-", "").lower()
                         for f in os.listdir(dest_dir) if f.endswith((".jar", ".zip")))
            if exists:
                continue
            cache_path = self._cf_cache_path(mc_dir, slug, mc_ver, loader_type)
            if os.path.exists(cache_path):
                # копируем из кэша
                fname = os.path.basename(cache_path)
                import shutil
                shutil.copy2(cache_path, os.path.join(dest_dir, fname))
                print(f"✓ {slug} (из кэша)")
                continue
            tasks.append((slug, dest_dir, cache_path))

        if not tasks:
            if callback:
                callback(100)
            return 0, "Всё уже скачано"

        completed = [0]
        lock = __import__("threading").Lock()
        results = {"downloaded": 0, "skipped": 0}

        def process_one(slug, dest_dir, cache_path):
            try:
                search = requests.get(
                    f"{self.curseforge_api}/mods/search?gameId=432&slug={slug}",
                    headers={"x-api-key": cf_key, "Accept": "application/json"}, timeout=10)
                if search.status_code != 200:
                    return False, slug, "search fail"
                mods_list = search.json().get("data", [])
                if not mods_list:
                    return False, slug, "not found"
                mod_id = mods_list[0]["id"]
                files_resp = requests.get(
                    f"{self.curseforge_api}/mods/{mod_id}/files?gameVersion={mc_ver}&modLoaderType={mod_loader_type}",
                    headers={"x-api-key": cf_key, "Accept": "application/json"}, timeout=10)
                if files_resp.status_code != 200:
                    return False, slug, "files list fail"
                files_data = files_resp.json().get("data", [])
                if not files_data:
                    return False, slug, "no files"
                file_id = files_data[0]["id"]
                dl_resp = requests.get(
                    f"{self.curseforge_api}/mods/{mod_id}/files/{file_id}/download-url",
                    headers={"x-api-key": cf_key, "Accept": "application/json"}, timeout=10)
                if dl_resp.status_code != 200:
                    return False, slug, "dl-url fail"
                dl_url = dl_resp.json().get("data", "")
                if not dl_url:
                    return False, slug, "no dl-url"
                fname = files_data[0].get("fileName", f"{slug}.jar")
                save_path = os.path.join(dest_dir, fname)
                dl_resp2 = requests.get(dl_url, timeout=60, stream=True)
                if dl_resp2.status_code != 200:
                    return False, slug, "download fail"
                with open(save_path, "wb") as f:
                    for chunk in dl_resp2.iter_content(65536):
                        if chunk:
                            f.write(chunk)
                # кэшируем
                import shutil
                shutil.copy2(save_path, cache_path)
                return True, slug, fname
            except Exception as e:
                return False, slug, str(e)

        max_workers = min(5, len(tasks))
        with ThreadPoolExecutor(max_workers=max_workers) as pool:
            futures = {pool.submit(process_one, slug, d, c): slug for slug, d, c in tasks}
            for fut in as_completed(futures):
                ok, slug, info = fut.result()
                with lock:
                    completed[0] += 1
                    if callback:
                        callback(int(90 * completed[0] / len(tasks)))
                    if ok:
                        results["downloaded"] += 1
                        print(f"✓ {slug} -> {info}")
                    else:
                        results["skipped"] += 1
                        print(f"× {slug}: {info}")

        if callback:
            callback(100)
        return (results["downloaded"],
                f"Загружено: {results['downloaded']}/{len(tasks)}, пропущено: {results['skipped']}")

# =========== ДОБАВИТЬ ПОСЛЕ BuildsManager ===========
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


class AIRequestThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, api_url, api_key, model, system_prompt, messages):
        super().__init__()
        self.api_url = api_url
        self.api_key = api_key
        self.model = model
        self.system_prompt = system_prompt
        self.messages = messages

    def run(self):
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            body = [{"role": "system", "content": self.system_prompt}] + self.messages if self.system_prompt else self.messages
            payload = {"model": self.model, "messages": body, "max_tokens": 2048}
            url = self.api_url.rstrip("/") + "/chat/completions"
            resp = requests.post(url, headers=headers, json=payload, timeout=120)
            resp.raise_for_status()
            data = resp.json()
            choice = data.get("choices", [{}])[0]
            content = choice.get("message", {}).get("content", "")
            self.finished.emit(("ok", content))
        except Exception as e:
            self.finished.emit(("error", str(e)))


class AIAgentPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config = load_config()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)

        title = QLabel("🤖 AI Агент")
        title.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        layout.addWidget(title)

        settings_frame = QFrame()
        settings_frame.setStyleSheet("QFrame { background: rgba(255,255,255,0.05); border-radius: 8px; padding: 8px; }")
        slayout = QVBoxLayout(settings_frame)

        row1 = QHBoxLayout()
        row1.addWidget(QLabel("API URL:"))
        self.api_url = QLineEdit(self.config.get("ai_api_url", "https://api.openai.com/v1"))
        self.api_url.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px;")
        row1.addWidget(self.api_url)
        slayout.addLayout(row1)

        row2 = QHBoxLayout()
        row2.addWidget(QLabel("API Key:"))
        self.api_key = QLineEdit(self.config.get("ai_api_key", ""))
        self.api_key.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px;")
        row2.addWidget(self.api_key)
        slayout.addLayout(row2)

        row3 = QHBoxLayout()
        row3.addWidget(QLabel("Модель:"))
        self.model_combo = QComboBox()
        models = ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude-sonnet-4", "claude-haiku-4"]
        self.model_combo.addItems(models + ["custom"])
        self.model_combo.setCurrentText(self.config.get("ai_model", "gpt-4o-mini"))
        self.model_combo.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 4px; padding: 3px;")
        self.model_combo.currentTextChanged.connect(self._on_model_changed)
        row3.addWidget(self.model_combo)
        self.custom_model = QLineEdit()
        self.custom_model.setPlaceholderText("custom model")
        self.custom_model.hide()
        self.custom_model.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px;")
        row3.addWidget(self.custom_model)
        slayout.addLayout(row3)

        row4 = QVBoxLayout()
        row4.addWidget(QLabel("System prompt:"))
        self.system_prompt = QTextEdit()
        self.system_prompt.setPlainText(self.config.get("ai_system_prompt",
            "You are a helpful Minecraft assistant. Help with mods, modpacks, servers, and gameplay."))
        self.system_prompt.setMaximumHeight(60)
        self.system_prompt.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 4px; padding: 4px;")
        row4.addWidget(self.system_prompt)
        slayout.addLayout(row4)

        btn_save = QPushButton("💾 Сохранить настройки")
        btn_save.setStyleSheet("background: #4facfe; color: white; border: none; border-radius: 4px; padding: 6px;")
        btn_save.clicked.connect(self._save_settings)
        slayout.addWidget(btn_save)
        layout.addWidget(settings_frame)

        self.chat_list = QListWidget()
        self.chat_list.setStyleSheet("""
            QListWidget { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1);
                border-radius: 8px; color: white; font-size: 13px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid rgba(255,255,255,0.05); }
        """)
        layout.addWidget(self.chat_list, 1)

        input_layout = QHBoxLayout()
        self.input_text = QTextEdit()
        self.input_text.setPlaceholderText("Напиши сообщение...")
        self.input_text.setMaximumHeight(60)
        self.input_text.setStyleSheet("background: #2f2f2f; color: white; border: 1px solid #444; border-radius: 8px; padding: 6px;")
        input_layout.addWidget(self.input_text)

        btn_send = QPushButton("➤")
        btn_send.setFixedSize(50, 50)
        btn_send.setStyleSheet("background: #4facfe; color: white; border: none; border-radius: 8px; font-size: 20px;")
        btn_send.clicked.connect(self._send_message)
        input_layout.addWidget(btn_send)
        layout.addLayout(input_layout)

        self.input_text.installEventFilter(self)

        self._add_message("system", "Привет! Я AI ассистент по Minecraft. Задавай любые вопросы о модах, сборках и игре!")

    def _on_model_changed(self, text):
        self.custom_model.setVisible(text == "custom")

    def _save_settings(self):
        config = load_config()
        config["ai_api_url"] = self.api_url.text()
        config["ai_api_key"] = self.api_key.text()
        config["ai_model"] = self.model_combo.currentText()
        config["ai_system_prompt"] = self.system_prompt.toPlainText()
        save_config(config)
        QMessageBox.information(self, "Готово", "Настройки AI сохранены")

    def _add_message(self, role, text):
        icons = {"user": "🧑", "assistant": "🤖", "system": "ℹ️"}
        prefix = f"{icons.get(role, 'ℹ️')} {role.capitalize()}"
        if role == "user":
            prefix = "🧑 Вы"
        elif role == "assistant":
            prefix = "🤖 AI"
        item = QListWidgetItem(f"{prefix}: {text}")
        item.setData(Qt.ItemDataRole.UserRole, {"role": role, "text": text})
        self.chat_list.addItem(item)
        self.chat_list.scrollToBottom()

    def _remove_last_system(self):
        for i in range(self.chat_list.count() - 1, -1, -1):
            item = self.chat_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and data.get("role") == "system" and data.get("text") == "Думаю...":
                self.chat_list.takeItem(i)
                break

    def eventFilter(self, obj, event):
        if obj == self.input_text and event.type() == QEvent.Type.KeyPress:
            if event.key() == Qt.Key.Key_Return and not (event.modifiers() & Qt.KeyboardModifier.ShiftModifier):
                self._send_message()
                return True
        return super().eventFilter(obj, event)

    def _send_message(self):
        text = self.input_text.toPlainText().strip()
        if not text:
            return
        self.input_text.clear()
        self._add_message("user", text)
        self._add_message("system", "Думаю...")
        self._do_request()

    def _do_request(self):
        messages = []
        for i in range(self.chat_list.count()):
            item = self.chat_list.item(i)
            data = item.data(Qt.ItemDataRole.UserRole)
            if data and data.get("role") in ("user", "assistant"):
                messages.append({"role": data["role"], "content": data["text"]})
        url = self.api_url.text().strip()
        key = self.api_key.text().strip()
        model = self.model_combo.currentText()
        if model == "custom":
            model = self.custom_model.text().strip()
        system = self.system_prompt.toPlainText().strip()
        if not key:
            self._add_message("system", "❌ API ключ не указан. Введи его в настройках выше.")
            return
        thread = AIRequestThread(url, key, model, system, messages)
        thread.finished.connect(self._on_response)
        thread.start()

    def _on_response(self, result):
        self._remove_last_system()
        status, content = result
        if status == "ok" and content:
            self._add_message("assistant", content)
        else:
            error = content or "Неизвестная ошибка"
            self._add_message("system", f"❌ Ошибка: {error[:200]}")


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
            ("🧩", "Моды", "#96ceb4"),
            ("📦", "Сборки", "#feca57"),
            ("🖼️", "Скины", "#ff9ff3"),
            ("📢", "Новости", "#54a0ff"),
            ("🔄", "Обновления", "#5f27cd"),
            ("🖧", "Серверы", "#ff9f43"),
            ("⚙️", "Настройки", "#00d2d3"),
            ("⛏️", "Minecraft", "#1dd1a1"),
            ("🤖", "AI Агент", "#a855f7")
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
    launch_setup_signal = pyqtSignal(str, str, str)  # version_id, username, loader_type
    progress_update_signal = pyqtSignal(int, int, str)
    state_update_signal = pyqtSignal(bool)
    error_signal = pyqtSignal(str)  # error message for UI

    def __init__(self):
        super().__init__()
        self.launch_setup_signal.connect(self.launch_setup)
        self.version_id = ''
        self.username = ''
        self.loader_type = 'vanilla'
        self.max_ram = 4096
        self.min_ram = 1024
        self.java_path = ''
        self.jvm_args = ''
        self.progress = 0
        self.progress_max = 100
        self.progress_label = ''

    def launch_setup(self, version_id, username, loader_type):
        self.username = username
        self.loader_type = loader_type
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
            callback = {
                'setStatus': self.update_progress_label,
                'setProgress': self.update_progress,
                'setMax': self.update_progress_max
            }

            # 1. Устанавливаем загрузчик
            loader = self.loader_type.lower()
            if loader == "vanilla":
                install_minecraft_version(version=self.version_id,
                    minecraft_directory=minecraft_directory, callback=callback)
            elif loader == "fabric":
                fabric_loader.install_fabric(minecraft_version=self.version_id,
                    minecraft_directory=minecraft_directory, callback=callback)
            elif loader == "forge":
                forge_version = forge_loader.find_forge_version(self.version_id)
                if not forge_version:
                    raise Exception(f"Forge версия не найдена для {self.version_id}")
                forge_loader.install_forge_version(forge_version,
                    minecraft_directory, callback=callback)
            elif loader == "quilt":
                quilt_loader.install_quilt(minecraft_version=self.version_id,
                    minecraft_directory=minecraft_directory, callback=callback)
            elif loader == "neoforge":
                self._nf_installed_version = self._install_neoforge(callback)
            elif loader == "optifine":
                self._install_optifine()
            else:
                install_minecraft_version(version=self.version_id,
                    minecraft_directory=minecraft_directory, callback=callback)

            # 2. Готовим опции запуска
            if self.username == '':
                self.username = generate_username()[0]

            options = {
                'username': self.username,
                'uuid': str(uuid1()),
                'token': '',
                'jvmArguments': [
                    f'-Xmx{self.max_ram}M',
                    f'-Xms{self.min_ram}M',
                    '-XX:+UnlockExperimentalVMOptions',
                    '-XX:+UseG1GC',
                    '-XX:G1NewSizePercent=20',
                    '-XX:G1ReservePercent=20',
                    '-XX:MaxGCPauseMillis=50',
                    '-XX:G1HeapRegionSize=32M',
                ],
                'launcherName': 'SuperLauncher',
                'launcherVersion': '2.0',
            }

            if self.java_path and os.path.exists(self.java_path):
                options['executablePath'] = self.java_path

            if self.jvm_args:
                extra_args = self.jvm_args.split()
                options['jvmArguments'].extend(extra_args)

            # 3. Определяем ID версии для запуска (у Forge/Fabric он может отличаться)
            launch_version = self.version_id
            if loader == "forge":
                forge_ver = forge_loader.find_forge_version(self.version_id)
                if forge_ver:
                    launch_version = forge_loader.forge_to_installed_version(forge_ver)
            elif loader == "fabric":
                launch_version = f"fabric-loader-{fabric_loader.get_latest_loader_version()}-{self.version_id}"
            elif loader == "quilt":
                launch_version = f"quilt-loader-{self.version_id}"
            elif loader == "neoforge":
                launch_version = getattr(self, '_nf_installed_version', self.version_id)
                if launch_version == self.version_id:
                    raise Exception("NeoForge: не удалось определить версию для запуска")

            cmd = get_minecraft_command(
                version=launch_version,
                minecraft_directory=minecraft_directory,
                options=options
            )
            print("Запускаем команду:", cmd)
            proc = subprocess.Popen(cmd, cwd=minecraft_directory)
            proc.wait()
            print(f"Процесс Minecraft завершился с кодом: {proc.returncode}")
        except Exception as e:
            print("Ошибка при запуске Minecraft:", e)
            import traceback
            traceback.print_exc()
            self.error_signal.emit(str(e))
        finally:
            self.state_update_signal.emit(False)

    def _install_optifine(self):
        """Установка OptiFine через прямое скачивание и запуск установщика"""
        import urllib.request
        import zipfile

        optifine_dir = os.path.join(minecraft_directory, "mods", "optifine")
        os.makedirs(optifine_dir, exist_ok=True)

        # Парсим страницу OptiFine
        self.update_progress_label("Поиск OptiFine...")
        try:
            import requests as req
            resp = req.get("https://optifine.net/downloads", timeout=10)
            html = resp.text
            # Ищем ссылку на версию
            import re
            pattern = rf'/downloads/[^"]*{re.escape(self.version_id)}[^"]*\.jar'
            match = re.search(pattern, html)
            if not match:
                raise Exception(f"OptiFine для {self.version_id} не найден")
            dl_path = match.group(0)
            dl_url = f"https://optifine.net{dl_path}"

            jar_path = os.path.join(optifine_dir, f"OptiFine_{self.version_id}.jar")
            if not os.path.exists(jar_path):
                self.update_progress_label("Скачивание OptiFine...")
                urllib.request.urlretrieve(dl_url, jar_path)

            # Запускаем установщик OptiFine
            self.update_progress_label("Запуск установщика OptiFine...")
            java_exe = self.java_path or "java"
            subprocess.run([java_exe, "-jar", jar_path], cwd=optifine_dir, check=True)

            # После установки OptiFine версия будет как optifine_версия
            self.version_id = f"{self.version_id}_optifine"
            self.update_progress_label("OptiFine установлен!")
        except Exception as e:
            print(f"Ошибка установки OptiFine: {e}")
            raise

    def _install_neoforge(self, callback):
        NF_API = "https://maven.neoforged.net/api/maven/versions/releases/net/neoforged/neoforge"
        NF_MAVEN = "https://maven.neoforged.net/releases/net/neoforged/neoforge"
        self.update_progress_label("Поиск NeoForge...")
        try:
            r = requests.get(NF_API, timeout=15)
            r.raise_for_status()
            versions = r.json()["versions"]
        except Exception:
            self.update_progress_label("API NeoForge недоступен, пробуем GitHub...")
            try:
                r = requests.get("https://api.github.com/repos/neoforged/NeoForge/releases?per_page=50", timeout=15)
                r.raise_for_status()
                versions = []
                for rel in r.json():
                    tag = rel.get("tag_name", "")
                    parts = tag.split("-")
                    if len(parts) == 2:
                        versions.append(parts[1])
            except Exception:
                raise Exception("NeoForge недоступен (maven + GitHub). Проверь интернет или VPN.")

        ver_parts = self.version_id.split(".")
        mc_major = ver_parts[1]
        mc_minor = ver_parts[2] if len(ver_parts) > 2 else ""
        compatible = []
        for v in versions:
            vp = v.split(".")
            if len(vp) < 2:
                continue
            if vp[0] == mc_major and (not mc_minor or vp[1] == mc_minor):
                compatible.append(v)
        if not compatible:
            compatible = [v for v in versions if v.split(".")[0] == mc_major and len(v.split(".")) > 1]
        if not compatible:
            raise Exception(f"NeoForge не найдена для {self.version_id}")
        loader_ver = compatible[-1]

        installer_url = f"{NF_MAVEN}/{loader_ver}/neoforge-{loader_ver}-installer.jar"
        self.update_progress_label(f"Скачивание NeoForge {loader_ver}...")
        temp_dir = tempfile.mkdtemp(prefix="neoforge-")
        installer_path = os.path.join(temp_dir, "neoforge-installer.jar")
        try:
            dl_resp = requests.get(installer_url, timeout=60, stream=True)
            dl_resp.raise_for_status()
            total = int(dl_resp.headers.get("content-length", 0))
            written = 0
            with open(installer_path, "wb") as f:
                for chunk in dl_resp.iter_content(8192):
                    f.write(chunk)
                    written += len(chunk)
                    if total > 0:
                        self.update_progress(int(written * 100 / total))
            self.update_progress_label("Запуск установщика NeoForge...")
            java_exe = self.java_path or "java"
            subprocess.run(
                [java_exe, "-jar", installer_path, "--install-client", minecraft_directory],
                check=True, timeout=120,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)

        installed_ver = f"neoforge-{loader_ver}"
        install_minecraft_version(installed_ver, minecraft_directory, callback=callback)
        return installed_ver


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
        self.parent_window = parent
        self.config = load_config()

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

        # Выбор загрузчика
        self.loader_select = QComboBox()
        self.loader_select.addItems(["Vanilla", "Fabric", "Forge", "Quilt", "OptiFine", "NeoForge"])
        self.loader_select.setStyleSheet("""
            background-color: #2f2f2f;
            color: white;
            border: 1px solid #444;
            border-radius: 5px;
            padding: 3px;
        """)

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
        layout.addWidget(self.loader_select)
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

        # ===== ОЗУ =====
        self.ram_label = QLabel()
        layout.addWidget(self.ram_label)
        ram_layout = QHBoxLayout()
        self.ram_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_slider.setRange(1024, 32768)
        self.ram_slider.setValue(self.config.get("max_ram", 4096))
        self.ram_slider.setTickInterval(1024)
        self.ram_slider.setSingleStep(512)
        self.ram_value_label = QLabel(f'{self.ram_slider.value()} MB')
        self.ram_slider.valueChanged.connect(lambda v: self.ram_value_label.setText(f'{v} MB'))
        ram_layout.addWidget(self.ram_slider)
        ram_layout.addWidget(self.ram_value_label)
        layout.addLayout(ram_layout)

        # ===== JVM аргументы =====
        self.jvm_label = QLabel()
        layout.addWidget(self.jvm_label)
        self.jvm_input = QLineEdit(self.config.get("jvm_args", ""))
        self.jvm_input.setPlaceholderText("-XX:+UseG1GC -XX:+UnlockExperimentalVMOptions")
        layout.addWidget(self.jvm_input)

        # ===== CurseForge API ключ =====
        self.labels["curseforge_key"] = QLabel()
        layout.addWidget(self.labels["curseforge_key"])
        self.cf_key_input = QLineEdit(self.config.get("curseforge_api_key", ""))
        self.cf_key_input.setPlaceholderText("Введите CurseForge API ключ...")
        layout.addWidget(self.cf_key_input)
        self.buttons["test_cf_key"] = QPushButton()
        layout.addWidget(self.buttons["test_cf_key"])
        self.buttons["test_cf_key"].clicked.connect(self.test_cf_key)

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
        self.labels["curseforge_key"].setText(self.tr("CurseForge API Key:"))
        self.buttons["test_cf_key"].setText(self.tr("Test key"))
        self.labels["page_bg"].setText(self.tr("Page backgrounds:"))
        self.buttons["save"].setText(self.tr("Save settings"))
        self.ram_label.setText(self.tr("RAM allocation:"))
        self.jvm_label.setText(self.tr("JVM arguments:"))

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

    def test_cf_key(self):
        key = self.cf_key_input.text().strip()
        if not key:
            QMessageBox.warning(self, "Ошибка", "Введите API ключ")
            return
        try:
            resp = requests.get(
                f"{CURSEFORGE_API}/mods/search?gameId=432&classId=6&pageSize=1",
                headers={"x-api-key": key, "Accept": "application/json"}, timeout=10)
            if resp.status_code == 200:
                QMessageBox.information(self, "Успех", "✅ Ключ работает! CurseForge API отвечает.")
            else:
                QMessageBox.critical(self, "Ошибка",
                    f"❌ Ключ не работает. HTTP {resp.status_code}: {resp.text[:200]}")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"❌ Не удалось проверить ключ:\n{e}")

    def save_settings(self):
        self.config["theme"] = self.theme_combo.currentText()
        self.config["language"] = self.lang_combo.currentText()
        self.config["launch_mode"] = "java" if self.rb_java.isChecked() else "launcher_lib"
        self.config["java_path"] = self.java_path_input.text()
        self.config["page_bg"] = self.config.get("page_bg", "dark")
        self.config["max_ram"] = self.ram_slider.value()
        self.config["jvm_args"] = self.jvm_input.text()
        self.config["curseforge_api_key"] = self.cf_key_input.text().strip()
        save_config(self.config)
        invalidate_cf_api_key_cache()
        self.update_texts()


class IconLoadThread(QThread):
    icon_data = pyqtSignal(object, bytes)

    def __init__(self, items):
        super().__init__()
        self.items = items

    def run(self):
        for item, icon_url in self.items:
            try:
                resp = requests.get(icon_url, timeout=5)
                if resp.status_code == 200:
                    self.icon_data.emit(item, resp.content)
            except Exception:
                pass


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
    MOD_SOURCES = ["Modrinth", "CurseForge"]

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

        # Источник и поиск в одной строке
        search_row = QHBoxLayout()

        self.source_combo = QComboBox()
        self.source_combo.addItems(self.MOD_SOURCES)
        self.source_combo.setStyleSheet("""
            background-color: #2f2f2f; color: white;
            border: 1px solid #444; border-radius: 5px; padding: 3px;
        """)
        search_row.addWidget(self.source_combo)

        self.search_input = QLineEdit()
        self.search_input.returnPressed.connect(self.search_mods)
        self.search_input.setStyleSheet("""
            background-color: #2f2f2f; color: white;
            border: 1px solid #444; border-radius: 5px; padding: 5px;
        """)
        search_row.addWidget(self.search_input, 1)
        self.layout.addLayout(search_row)

        # Список результатов
        self.results_list = QListWidget()
        self.results_list.setIconSize(QSize(64, 64))
        self.results_list.setStyleSheet("""
            background-color: #2f2f2f; color: white;
            border: 1px solid #444; border-radius: 5px;
        """)
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
        src = self.source_combo.currentText()
        self.title.setText(f"🧩 {self.tr('Mods from')} {src}")
        self.search_input.setPlaceholderText(f"🔍 {self.tr('Search mod...')}")
        self.open_folder_button.setText(f"📂 {self.tr('Open mods folder')}")
        self.delete_all_button.setText(f"🗑 {self.tr('Delete all mods')}")

    def _connect_item_clicked(self):
        try:
            self.results_list.itemClicked.disconnect(self.show_mod_dialog)
        except TypeError:
            pass
        self.results_list.itemClicked.connect(self.show_mod_dialog)

    def _load_icons_bg(self, items_with_urls):
        if not hasattr(self, "_icon_thread") or not self._icon_thread.isRunning():
            self._icon_thread = IconLoadThread(items_with_urls)
            self._icon_thread.icon_data.connect(self._on_icon_data)
            self._icon_thread.start()

    def _on_icon_data(self, item, data):
        try:
            pm = QPixmap()
            pm.loadFromData(data)
            if not pm.isNull():
                item.setIcon(QIcon(pm.scaled(32, 32, Qt.AspectRatioMode.KeepAspectRatio,
                                              Qt.TransformationMode.SmoothTransformation)))
        except Exception:
            pass

    def load_featured_mods(self):
        try:
            url = f"{MODRINTH_API}/search?limit=20&index=downloads"
            resp = requests.get(url, headers={"User-Agent": "SuperLauncher/2.0"}, timeout=10)
            data = resp.json()
            self.results_list.clear()
            icon_items = []
            for hit in data["hits"]:
                desc = hit.get("description", "")[:80]
                downloads = hit.get("downloads", 0)
                item = QListWidgetItem(f"{hit['title']} ⬇{downloads} — {desc}")
                item.setData(Qt.ItemDataRole.UserRole, ("modrinth", hit["project_id"]))
                self.results_list.addItem(item)
                if hit.get("icon_url"):
                    icon_items.append((item, hit["icon_url"]))
            self._connect_item_clicked()
            if icon_items:
                self._load_icons_bg(icon_items)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def search_mods(self):
        query = self.search_input.text()
        if not query.strip():
            return
        source = self.source_combo.currentText()
        if source == "Modrinth":
            self._search_modrinth(query)
        else:
            self._search_curseforge(query)

    def _search_modrinth(self, query):
        try:
            url = f"{MODRINTH_API}/search?query={query}&limit=30&index=relevance"
            resp = requests.get(url, headers={"User-Agent": "SuperLauncher/2.0"}, timeout=10)
            data = resp.json()
            self.results_list.clear()
            icon_items = []
            for hit in data["hits"]:
                if hit.get("project_type") != "mod":
                    continue
                desc = hit.get("description", "")[:80]
                downloads = hit.get("downloads", 0)
                item = QListWidgetItem(f"{hit['title']} ⬇{downloads} — {desc}")
                item.setData(Qt.ItemDataRole.UserRole, ("modrinth", hit["project_id"]))
                self.results_list.addItem(item)
                if hit.get("icon_url"):
                    icon_items.append((item, hit["icon_url"]))
            self._connect_item_clicked()
            if icon_items:
                self._load_icons_bg(icon_items)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def _search_curseforge(self, query):
        try:
            params = {
                "gameId": 432,
                "classId": 6,
                "searchFilter": query,
                "pageSize": 30,
                "sortField": 2,
                "sortOrder": "desc"
            }
            resp = requests.get(
                f"{CURSEFORGE_API}/mods/search",
                params=params,
                headers={
                    "x-api-key": get_cf_api_key(),
                    "Accept": "application/json"
                },
                timeout=15
            )
            data = resp.json()
            self.results_list.clear()
            icon_items = []
            for mod in data.get("data", []):
                name = mod.get("name", "Unknown")
                summary = mod.get("summary", "")[:80]
                downloads = mod.get("downloadCount", 0)
                item = QListWidgetItem(f"{name} ⬇{downloads} — {summary}")
                item.setData(Qt.ItemDataRole.UserRole, ("curseforge", mod["id"]))
                self.results_list.addItem(item)
                logo = mod.get("logo", {})
                if logo and logo.get("url"):
                    icon_items.append((item, logo["url"]))
            self._connect_item_clicked()
            if icon_items:
                self._load_icons_bg(icon_items)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), f"CurseForge: {e}")

    def show_mod_dialog(self, item):
        source, mod_id = item.data(Qt.ItemDataRole.UserRole)
        if source == "modrinth":
            self._show_modrinth_dialog(mod_id)
        else:
            self._show_curseforge_dialog(mod_id)

    def _show_modrinth_dialog(self, project_id):
        try:
            versions_url = f"{MODRINTH_API}/project/{project_id}/version"
            resp = requests.get(versions_url, headers={"User-Agent": "SuperLauncher/2.0"})
            versions = resp.json()

            if not versions:
                QMessageBox.warning(self, self.tr("No available versions"),
                                    self.tr("No versions available"))
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(self.tr("Install mod"))
            dialog.setMinimumWidth(400)
            layout = QVBoxLayout(dialog)

            version_box = QComboBox()
            version_loader_map = {}
            for v in versions:
                mc_versions = v.get("game_versions", [])
                loaders = v.get("loaders", [])
                if not mc_versions or not loaders:
                    continue
                ver_num = v.get("version_number", "?")
                display_text = f"{mc_versions[0]} | {loaders[0]} | {ver_num}"
                version_loader_map[display_text] = v

            if not version_loader_map:
                QMessageBox.warning(self, self.tr("No supported builds"),
                                    self.tr("No supported builds"))
                return

            version_box.addItems(version_loader_map.keys())
            layout.addWidget(QLabel(self.tr("Minecraft version and loader:")))
            layout.addWidget(version_box)

            install_button = QPushButton(self.tr("Install mod"))
            install_button.setStyleSheet("""
                background-color: #4facfe; color: white;
                border: none; border-radius: 5px; padding: 8px; font-weight: bold;
            """)
            layout.addWidget(install_button)

            install_button.clicked.connect(
                lambda: self._download_from_modrinth(version_loader_map[version_box.currentText()], dialog)
            )

            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def _download_from_modrinth(self, version_data, dialog):
        files = version_data.get("files", [])
        for file in files:
            if file.get("filename", "").endswith(".jar"):
                url = file["url"]
                filename = file["filename"]
                save_path = os.path.join(self.mods_dir, filename)
                dialog.close()
                self.start_download(url, save_path)
                return
        QMessageBox.warning(self, self.tr("File not found"), self.tr("File not found"))

    def _show_curseforge_dialog(self, mod_id):
        try:
            resp = requests.get(
                f"{CURSEFORGE_API}/mods/{mod_id}/files",
                headers={
                    "x-api-key": get_cf_api_key(),
                    "Accept": "application/json"
                },
                timeout=10
            )
            data = resp.json()
            files = data.get("data", [])

            if not files:
                QMessageBox.warning(self, self.tr("No available versions"),
                                    self.tr("No versions available"))
                return

            dialog = QDialog(self)
            dialog.setWindowTitle(self.tr("Install mod"))
            dialog.setMinimumWidth(500)
            layout = QVBoxLayout(dialog)

            file_box = QComboBox()
            file_map = {}
            LOADER_NAMES = {1: "Forge", 2: "Cauldron", 3: "LiteLoader", 4: "Fabric", 5: "Quilt", 6: "NeoForge"}
            for f in files[:30]:
                display_name = f.get("displayName", f.get("fileName", "?"))
                mc_ver = "?"
                file_loader = "?"
                for sgv in f.get("sortableGameVersions", []):
                    gv_type = sgv.get("gameVersionTypeId")
                    gv_name = sgv.get("gameVersionName", "")
                    if gv_type == 1:
                        mc_ver = gv_name
                    elif gv_type == 2:
                        file_loader = LOADER_NAMES.get(int(gv_name), gv_name) if gv_name.isdigit() else gv_name
                if mc_ver == "?":
                    mc_ver = next((v for v in f.get("gameVersions", []) if v and v[0].isdigit()), "?")
                dl_count = f.get("downloadCount", 0)
                release_type = {1: "Release", 2: "Beta", 3: "Alpha"}.get(f.get("releaseType"), "")
                label = f"{mc_ver} | {file_loader} | {display_name} ⬇{dl_count}"
                if release_type:
                    label += f" [{release_type}]"
                file_map[label] = f
                file_box.addItem(label)

            layout.addWidget(QLabel(self.tr("Select file:")))
            layout.addWidget(file_box)

            install_button = QPushButton(self.tr("Install mod"))
            install_button.setStyleSheet("""
                background-color: #f1642e; color: white;
                border: none; border-radius: 5px; padding: 8px; font-weight: bold;
            """)
            layout.addWidget(install_button)

            install_button.clicked.connect(
                lambda: self._download_from_curseforge(file_map[file_box.currentText()], dialog)
            )

            dialog.exec()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), f"CurseForge: {e}")

    def _download_from_curseforge(self, file_data, dialog):
        file_id = file_data.get("id")
        mod_id = file_data.get("modId")
        try:
            resp = requests.get(
                f"{CURSEFORGE_API}/mods/{mod_id}/files/{file_id}/download-url",
                headers={
                    "x-api-key": get_cf_api_key(),
                    "Accept": "application/json"
                },
                timeout=10
            )
            data = resp.json()
            dl_url = data.get("data", "")
            if not dl_url:
                # fallback: build URL manually
                filename = file_data.get("fileName", "mod.jar")
                dl_url = f"https://media.forgecdn.net/files/{file_id // 1000}/{file_id % 1000}/{filename}"

            filename = file_data.get("fileName", "mod.jar")
            save_path = os.path.join(self.mods_dir, filename)
            dialog.close()
            self.start_download(dl_url, save_path)
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), f"CurseForge download: {e}")

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


class UpdateDownloadThread(QThread):
    progress = pyqtSignal(int)
    speed = pyqtSignal(str)
    finished = pyqtSignal(str)

    def __init__(self, url, filename):
        super().__init__()
        self.url = url
        self.filename = filename

    def run(self):
        try:
            with requests.get(self.url, stream=True, timeout=30) as r:
                r.raise_for_status()
                total = int(r.headers.get("content-length", 0))
                downloaded = 0
                start = time.time()
                with open(self.filename, "wb") as f:
                    for chunk in r.iter_content(chunk_size=65536):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total > 0:
                                pct = int(downloaded * 100 / total)
                                self.progress.emit(pct)
                                elapsed = time.time() - start
                                if elapsed > 0:
                                    speed_bps = downloaded / elapsed
                                    if speed_bps > 1048576:
                                        speed_str = f"{speed_bps/1048576:.1f} MB/s"
                                    else:
                                        speed_str = f"{speed_bps/1024:.0f} KB/s"
                                    eta = (total - downloaded) / speed_bps if speed_bps > 0 else 0
                                    self.speed.emit(f"{speed_str} | ETA: {eta:.0f}s")
            self.finished.emit(str(self.filename))
        except Exception as e:
            self.finished.emit(f"ERROR: {str(e)}")


class UpdatesPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.releases = []
        self.download_url = None
        self.download_version = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # === HEADER ===
        header = QHBoxLayout()
        self.title = QLabel("🔄 Обновления")
        self.title.setStyleSheet("font-size: 26px; font-weight: bold; color: white;")
        header.addWidget(self.title)
        header.addStretch()

        self.btn_refresh = QPushButton("⟳ Проверить")
        self.btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_refresh.setStyleSheet(
            "QPushButton { background: #4facfe; color: white; border: none; "
            "border-radius: 6px; padding: 8px 18px; font-weight: bold; }"
            "QPushButton:hover { background: #3a8ed9; }")
        self.btn_refresh.clicked.connect(self.check_for_updates)
        header.addWidget(self.btn_refresh)
        layout.addLayout(header)

        # === CURRENT VERSION CARD ===
        self.version_card = QFrame()
        self.version_card.setStyleSheet(
            "QFrame { background: rgba(79, 172, 254, 0.1); border: 1px solid rgba(79,172,254,0.3); "
            "border-radius: 12px; padding: 16px; }")
        vc_layout = QHBoxLayout(self.version_card)
        vc_layout.setContentsMargins(16, 12, 16, 12)

        vc_icon = QLabel("📦")
        vc_icon.setStyleSheet("font-size: 32px;")
        vc_layout.addWidget(vc_icon)

        vc_info = QVBoxLayout()
        vc_info.setSpacing(2)
        vc_title = QLabel("Текущая версия")
        vc_title.setStyleSheet("color: #888; font-size: 12px;")
        vc_info.addWidget(vc_title)
        self.vc_version = QLabel(CURRENT_VERSION)
        self.vc_version.setStyleSheet("color: white; font-size: 22px; font-weight: bold;")
        vc_info.addWidget(self.vc_version)
        vc_layout.addLayout(vc_info)
        vc_layout.addStretch()

        self.vc_status = QLabel()
        self.vc_status.setStyleSheet("color: #4caf50; font-size: 13px; font-weight: bold;")
        vc_layout.addWidget(self.vc_status)

        self.vc_channel = QLabel()
        self.vc_channel.setStyleSheet("color: #888; font-size: 12px;")
        vc_layout.addWidget(self.vc_channel)

        layout.addWidget(self.version_card)

        # === UPDATE AVAILABLE CARD ===
        self.update_card = QFrame()
        self.update_card.setVisible(False)
        self.update_card.setStyleSheet(
            "QFrame { background: rgba(76, 175, 80, 0.1); border: 1px solid rgba(76,175,80,0.4); "
            "border-radius: 12px; padding: 16px; }")
        uc_layout = QVBoxLayout(self.update_card)
        uc_layout.setContentsMargins(16, 12, 16, 12)
        uc_layout.setSpacing(8)

        uc_header = QHBoxLayout()
        self.uc_icon = QLabel("⬆")
        self.uc_icon.setStyleSheet("font-size: 28px;")
        uc_header.addWidget(self.uc_icon)
        self.uc_title = QLabel()
        self.uc_title.setStyleSheet("color: #4caf50; font-size: 18px; font-weight: bold;")
        uc_header.addWidget(self.uc_title)
        uc_header.addStretch()
        self.uc_badge = QLabel()
        self.uc_badge.setStyleSheet(
            "background: #4caf50; color: white; padding: 2px 10px; "
            "border-radius: 4px; font-size: 11px; font-weight: bold;")
        uc_header.addWidget(self.uc_badge)
        uc_layout.addLayout(uc_header)

        self.uc_changelog = QLabel()
        self.uc_changelog.setWordWrap(True)
        self.uc_changelog.setStyleSheet("color: #ccc; font-size: 13px; padding: 4px 0;")
        uc_layout.addWidget(self.uc_changelog)

        uc_actions = QHBoxLayout()
        self.btn_download = QPushButton("⬇ Скачать и установить")
        self.btn_download.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_download.setStyleSheet(
            "QPushButton { background: #4caf50; color: white; border: none; "
            "border-radius: 6px; padding: 10px 24px; font-weight: bold; font-size: 14px; }"
            "QPushButton:hover { background: #43a047; }"
            "QPushButton:disabled { background: #555; }")
        self.btn_download.clicked.connect(self.start_download)
        uc_actions.addWidget(self.btn_download)

        self.btn_skip = QPushButton("Пропустить")
        self.btn_skip.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_skip.setStyleSheet(
            "QPushButton { background: transparent; color: #888; border: 1px solid #555; "
            "border-radius: 6px; padding: 10px 16px; font-size: 13px; }"
            "QPushButton:hover { color: white; border-color: #888; }")
        self.btn_skip.clicked.connect(lambda: self.update_card.setVisible(False))
        uc_actions.addWidget(self.btn_skip)
        uc_actions.addStretch()
        uc_layout.addLayout(uc_actions)

        # progress bar + speed
        self.download_progress = QProgressBar()
        self.download_progress.setVisible(False)
        self.download_progress.setStyleSheet(
            "QProgressBar { border: 1px solid #4caf50; border-radius: 6px; text-align: center; "
            "height: 22px; background: #1a1a2e; color: white; }"
            "QProgressBar::chunk { background: qlineargradient(x1:0,y1:0,x2:1,y2:0, "
            "stop:0 #4caf50, stop:1 #81c784); border-radius: 5px; }")
        uc_layout.addWidget(self.download_progress)

        self.download_speed = QLabel()
        self.download_speed.setVisible(False)
        self.download_speed.setStyleSheet("color: #888; font-size: 11px;")
        uc_layout.addWidget(self.download_speed)

        layout.addWidget(self.update_card)

        # === RELEASE NOTES / VERSION HISTORY ===
        notes_label = QLabel("📋 История версий")
        notes_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; margin-top: 8px;")
        layout.addWidget(notes_label)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.release_list = QListWidget()
        self.release_list.setStyleSheet(
            "QListWidget { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); "
            "border-radius: 8px; padding: 4px; color: white; font-size: 13px; }"
            "QListWidget::item { padding: 8px; border-radius: 4px; }"
            "QListWidget::item:hover { background: rgba(255,255,255,0.08); }"
            "QListWidget::item:selected { background: rgba(79,172,254,0.3); }")
        self.release_list.currentRowChanged.connect(self.on_release_selected)
        splitter.addWidget(self.release_list)

        self.release_notes = QTextEdit()
        self.release_notes.setReadOnly(True)
        self.release_notes.setStyleSheet(
            "QTextEdit { background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.1); "
            "border-radius: 8px; padding: 12px; color: #ccc; font-size: 13px; }")
        splitter.addWidget(self.release_notes)

        splitter.setSizes([250, 450])
        layout.addWidget(splitter, stretch=1)

        self.status_label = QLabel("Нажмите «Проверить» для поиска обновлений")
        self.status_label.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(self.status_label)

        QTimer.singleShot(500, self.check_for_updates)

    def check_for_updates(self):
        self.btn_refresh.setEnabled(False)
        self.btn_refresh.setText("⟳ Поиск...")
        self.status_label.setText("Проверка обновлений...")

        def task():
            try:
                # GitHub Releases API — все релизы
                url = "https://api.github.com/repos/Ludvig2457Ultra/SuperLauncherMC/releases?per_page=20"
                resp = requests.get(url, timeout=15,
                    headers={"Accept": "application/vnd.github.v3+json"})
                if resp.status_code != 200:
                    QTimer.singleShot(0, lambda: self.status_label.setText(
                        f"Ошибка API GitHub: {resp.status_code}"))
                    return

                data = resp.json()
                releases = []
                for r in data:
                    tag = r.get("tag_name", "")
                    name = r.get("name", tag)
                    body = r.get("body", "") or ""
                    published = r.get("published_at", "")[:10]
                    prerelease = r.get("prerelease", False)
                    assets = r.get("assets", [])
                    dl_url = ""
                    for a in assets:
                        if a.get("name", "").endswith(".exe"):
                            dl_url = a.get("browser_download_url", "")
                            break
                    if not dl_url:
                        for a in assets:
                            if a.get("name", "").endswith(".py"):
                                dl_url = a.get("browser_download_url", "")
                                break
                    try:
                        v = packaging_version.parse(tag)
                    except Exception:
                        continue
                    releases.append({
                        "tag": tag, "name": name, "body": body,
                        "date": published, "prerelease": prerelease,
                        "dl_url": dl_url, "version": v
                    })

                releases.sort(key=lambda x: x["version"], reverse=True)
                self.releases = releases

                # Fill list
                QTimer.singleShot(0, self.populate_release_list)

                # Check for new version
                current_v = packaging_version.parse(CURRENT_VERSION)
                for r in releases:
                    if r["version"] > current_v and r["dl_url"]:
                        self.download_url = r["dl_url"]
                        self.download_version = r["tag"]
                        QTimer.singleShot(0, lambda v=r: self.show_update(v))
                        return

                QTimer.singleShot(0, self.show_up_to_date)

            except Exception as e:
                QTimer.singleShot(0, lambda: self.status_label.setText(f"Ошибка: {e}"))
            finally:
                QTimer.singleShot(0, lambda: self.btn_refresh.setEnabled(True))
                QTimer.singleShot(0, lambda: self.btn_refresh.setText("⟳ Проверить"))

        from threading import Thread
        Thread(target=task, daemon=True).start()

    def populate_release_list(self):
        self.release_list.blockSignals(True)
        self.release_list.clear()
        for r in self.releases:
            badge = " 🔧" if r["prerelease"] else ""
            text = f"{r['tag']}{badge}  {r['date']}"
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, r["tag"])
            if r["prerelease"]:
                item.setForeground(QColor("#ff9800"))
            else:
                item.setForeground(QColor("white"))
            self.release_list.addItem(item)
        self.release_list.blockSignals(False)
        if self.releases:
            self.release_list.setCurrentRow(0)

    def on_release_selected(self, row):
        if row < 0 or row >= len(self.releases):
            return
        r = self.releases[row]
        body = r.get("body", "Нет описания.")
        # Strip HTML, keep markdown-ish
        import html
        safe_body = html.escape(body)
        # Simple markdown-like rendering
        lines = safe_body.split("\n")
        html_lines = []
        for line in lines:
            if line.startswith("## "):
                html_lines.append(f"<h3 style='color:#4facfe;'>{line[3:]}</h3>")
            elif line.startswith("### "):
                html_lines.append(f"<h4 style='color:#81c784;'>{line[4:]}</h4>")
            elif line.startswith("- ") or line.startswith("* "):
                html_lines.append(f"• {line[2:]}")
            elif line.startswith("**") and line.endswith("**"):
                html_lines.append(f"<b>{line[2:-2]}</b>")
            else:
                html_lines.append(line)
        html_content = "<br>".join(html_lines)
        header = f"<h2 style='color:white;'>{r['tag']}</h2>"
        meta = f"<p style='color:#888; font-size:12px;'>{r['date']}" + \
               (" | 🔧 Предрелиз</p>" if r["prerelease"] else "</p>")
        self.release_notes.setHtml(header + meta + "<hr>" + html_content)

    def show_update(self, release):
        self.update_card.setVisible(True)
        self.uc_title.setText(f"Доступна версия {release['tag']}")
        self.uc_badge.setText("НОВОЕ")
        # First line of body as summary
        body = release.get("body", "")
        summary = body.split("\n")[0] if body else "Обновление доступно для скачивания."
        if len(summary) > 120:
            summary = summary[:117] + "..."
        self.uc_changelog.setText(summary)
        self.vc_status.setText(f"⬆ Доступно обновление: {release['tag']}")
        self.vc_status.setStyleSheet("color: #4caf50; font-size: 13px; font-weight: bold;")

    def show_up_to_date(self):
        self.vc_status.setText("✓ Установлена последняя версия")
        self.vc_status.setStyleSheet("color: #4caf50; font-size: 13px; font-weight: bold;")
        self.status_label.setText(f"Последняя проверка: {datetime.datetime.now().strftime('%H:%M:%S')}")

    def start_download(self):
        if not self.download_url or not self.download_version:
            return

        filename = Path(__file__).parent / f"SuperLauncher_{self.download_version}.exe"
        self.btn_download.setEnabled(False)
        self.btn_download.setText("⏳ Загрузка...")
        self.download_progress.setVisible(True)
        self.download_progress.setValue(0)
        self.download_speed.setVisible(True)
        self.download_speed.setText("Подготовка...")
        self.status_label.setText(f"Загрузка {self.download_version}...")

        self.dl_thread = UpdateDownloadThread(self.download_url, str(filename))
        self.dl_thread.progress.connect(self.download_progress.setValue)
        self.dl_thread.speed.connect(self.download_speed.setText)
        self.dl_thread.finished.connect(self.on_download_finished)
        self.dl_thread.start()

    def on_download_finished(self, result):
        self.download_progress.setVisible(False)
        self.download_speed.setVisible(False)
        self.btn_download.setEnabled(True)
        self.btn_download.setText("⬇ Скачать и установить")

        if result.startswith("ERROR:"):
            QMessageBox.critical(self, "Ошибка", result)
            self.status_label.setText("Ошибка загрузки")
            return

        reply = QMessageBox.question(self, "Обновление",
            f"Версия {self.download_version} загружена.\n"
            "Запустить установку? Текущий лаунчер закроется.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            subprocess.Popen([result], close_fds=True)
            QApplication.quit()


class CreateServerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.setWindowTitle(self.tr("Create your own server"))
        self.setFixedSize(400, 300)

        layout = QFormLayout(self)

        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(self.tr("Server Name"))

        self.input_port = QLineEdit()
        self.input_port.setPlaceholderText(self.tr("Port (e.g., 25565)"))
        self.input_port.setText("25565")

        self.combo_version = QComboBox()
        self.combo_version.setMinimumContentsLength(12)

        self.combo_core = QComboBox()
        self.combo_core.addItems(["Paper", "Purpur", "Vanilla", "Fabric", "Quilt"])
        self.combo_core.currentTextChanged.connect(self.on_core_changed)

        self.ram_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_slider.setMinimum(1)
        self.ram_slider.setMaximum(16)
        self.ram_slider.setValue(4)
        self.ram_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ram_slider.setTickInterval(1)
        self.ram_slider.valueChanged.connect(self.on_ram_changed)
        self.ram_label = QLabel(f"4 {self.tr('RAM (GB):')}")
        self.ram_label.setStyleSheet("font-size: 12px; color: #ccc;")

        ram_widget = QWidget()
        ram_layout = QVBoxLayout(ram_widget)
        ram_layout.setContentsMargins(0, 0, 0, 0)
        ram_layout.addWidget(self.ram_slider)
        ram_layout.addWidget(self.ram_label)

        layout.addRow(self.tr("Server Name") + ":", self.input_name)
        layout.addRow(self.tr("Port") + ":", self.input_port)
        layout.addRow(self.tr("Version") + ":", self.combo_version)
        layout.addRow(self.tr("Core") + ":", self.combo_core)
        layout.addRow(self.tr("RAM (GB):") + ":", ram_widget)

        btn_layout = QHBoxLayout()
        self.btn_create = QPushButton(self.tr("Create"))
        self.btn_cancel = QPushButton(self.tr("Cancel"))
        btn_layout.addWidget(self.btn_create)
        btn_layout.addWidget(self.btn_cancel)
        layout.addRow(btn_layout)

        self.btn_create.clicked.connect(self.create_server)
        self.btn_cancel.clicked.connect(self.reject)

        self.fetch_versions()

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.setWindowTitle(self.tr("Create your own server"))
        layout = self.layout()
        self.input_name.setPlaceholderText(self.tr("Server Name"))
        self.input_port.setPlaceholderText(self.tr("Port (e.g., 25565)"))
        if layout.labelForField(self.input_name):
            layout.labelForField(self.input_name).setText(self.tr("Server Name") + ":")
        if layout.labelForField(self.input_port):
            layout.labelForField(self.input_port).setText(self.tr("Port") + ":")
        if layout.labelForField(self.combo_version):
            layout.labelForField(self.combo_version).setText(self.tr("Version") + ":")
        if layout.labelForField(self.combo_core):
            layout.labelForField(self.combo_core).setText(self.tr("Core") + ":")
        if layout.labelForField(self.ram_slider):
            layout.labelForField(self.ram_slider).setText(self.tr("RAM (GB):") + ":")
        self.btn_create.setText(self.tr("Create"))
        self.btn_cancel.setText(self.tr("Cancel"))
        self.on_ram_changed(self.ram_slider.value())

    def on_ram_changed(self, val):
        self.ram_label.setText(f"{val} GB")

    def on_core_changed(self, core):
        self.fetch_versions()

    def fetch_versions(self):
        self.combo_version.clear()
        self.combo_version.addItem(self.tr("Loading..."))
        from threading import Thread
        core = self.combo_core.currentText().lower()

        def task():
            try:
                versions = []
                if core in ("paper", "purpur"):
                    if core == "paper":
                        resp = requests.get("https://api.papermc.io/v2/projects/paper", timeout=10)
                        versions = resp.json().get("versions", [])
                    elif core == "purpur":
                        resp = requests.get("https://api.purpurmc.org/v2/purpur", timeout=10)
                        versions = list(resp.json().get("versions", {}).keys())
                    versions = sorted(versions, key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")], reverse=True)
                elif core in ("vanilla", "fabric", "quilt"):
                    resp = requests.get("https://launchermeta.mojang.com/mc/game/version_manifest.json", timeout=10)
                    manifest = resp.json()
                    versions = [v["id"] for v in manifest["versions"] if v["type"] == "release"]
                    versions.sort(key=lambda x: [int(p) if p.isdigit() else p for p in x.split(".")], reverse=True)
                if versions:
                    self.combo_version.clear()
                    self.combo_version.addItems(versions)
                else:
                    self.combo_version.clear()
                    self.combo_version.addItem("1.20.4")
            except Exception:
                self.combo_version.clear()
                self.combo_version.addItems(["1.20.4", "1.20.1", "1.19.4"])

        Thread(target=task, daemon=True).start()

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
        self.ram_gb = self.ram_slider.value()
        self.accept()


class DownloadThread(QThread):
    progress_changed = pyqtSignal(int)
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

        elif core == "fabric":
            loader_ver = requests.get("https://meta.fabricmc.net/v2/versions/loader", timeout=10).json()
            installer_ver = requests.get("https://meta.fabricmc.net/v2/versions/installer", timeout=10).json()
            loader = loader_ver[0]["version"]
            installer = installer_ver[0]["version"]
            return f"https://meta.fabricmc.net/v2/versions/loader/{version}/{loader}/{installer}/server/jar"

        elif core == "quilt":
            meta = requests.get("https://meta.quiltmc.org/v3/versions/loader", timeout=10).json()
            loader = meta[0]["version"]
            installer = requests.get("https://meta.quiltmc.org/v3/versions/installer", timeout=10).json()[0]["version"]
            return f"https://meta.quiltmc.org/v3/downloads/installer/installer-{installer}.jar"

        else:
            raise Exception(f"Ядро {core} не поддерживается")


class PluginInstallThread(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, slug, game_version, loader, plugins_folder):
        super().__init__()
        self.slug = slug
        self.game_version = game_version
        self.loader = loader
        self.plugins_folder = plugins_folder

    def run(self):
        try:
            url = f"{MODRINTH_API}/project/{self.slug}/version"
            headers = {"User-Agent": "SuperLauncher/2.0"}
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            versions = resp.json()

            loaders_to_try = [self.loader]
            if self.loader == "paper":
                loaders_to_try.append("bukkit")
            elif self.loader == "purpur":
                loaders_to_try.extend(["bukkit", "paper"])
            elif self.loader == "bukkit":
                loaders_to_try.extend(["paper", "purpur"])

            match = None
            for v in versions:
                gv = v.get("game_versions", [])
                loaders = v.get("loaders", [])
                if (not self.game_version or self.game_version in gv) and any(l in loaders for l in loaders_to_try):
                    match = v
                    break
            if not match:
                self.error.emit(f"No version found for {self.game_version or 'any'} / {self.loader}")
                return

            files = match.get("files", [])
            if not files:
                self.error.emit("No files in version")
                return

            file_info = files[0]
            dl_url = file_info.get("url")
            filename = file_info.get("filename", f"{self.slug}.jar")
            save_path = os.path.join(self.plugins_folder, filename)

            r = requests.get(dl_url, stream=True, timeout=30)
            r.raise_for_status()
            total = int(r.headers.get("content-length", 0))
            downloaded = 0
            with open(save_path, "wb") as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if total > 0:
                            self.progress.emit(int(downloaded * 100 / total))
            self.finished.emit(save_path)
        except Exception as e:
            self.error.emit(str(e))


class ServerProcessThread(QThread):
    output_line = pyqtSignal(str)
    started = pyqtSignal()
    stopped = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, server_path, start_command, ram_gb=4):
        super().__init__()
        self.server_path = server_path
        self.start_command = start_command
        self.ram_gb = ram_gb
        self.process = None
        self._running = False

    def run(self):
        bat_path = os.path.join(self.server_path, "start.bat")
        try:
            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(f"""@echo off
java -Xmx{self.ram_gb}G -Xms{self.ram_gb}G -jar server.jar nogui
""")
            self.process = subprocess.Popen(
                bat_path, cwd=self.server_path, shell=True,
                stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                text=True, encoding="utf-8", errors="replace"
            )
            self._running = True
            self.started.emit()
            for line in iter(self.process.stdout.readline, ""):
                if not self._running:
                    break
                if line:
                    self.output_line.emit(line.rstrip("\r\n"))
            self.process.wait()
        except Exception as e:
            self.error.emit(str(e))
        finally:
            self._running = False
            self.stopped.emit()

    def start_server(self):
        if not self.isRunning():
            self.start()

    def stop_server(self):
        self._running = False
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write("stop\n")
                self.process.stdin.flush()
            except Exception:
                pass
            try:
                self.process.wait(timeout=10)
            except Exception:
                try:
                    self.process.kill()
                except Exception:
                    pass

    def send_command(self, cmd):
        if self.process and self.process.poll() is None:
            try:
                self.process.stdin.write(cmd + "\n")
                self.process.stdin.flush()
            except Exception:
                pass


class ServerControlDialog(QDialog):
    def __init__(self, server_name, server_path, ram_gb=4, server_version='', server_core='', parent=None):
        super().__init__(parent)
        self.config = load_config()
        self.server_name = server_name
        self.server_path = server_path
        self.ram_gb = ram_gb
        self.server_version = server_version
        self.server_core = server_core
        self.server_thread = ServerProcessThread(server_path, "", ram_gb)
        self.playit_process = None
        self.plugin_install_thread = None

        self.setWindowTitle(self.tr("Manage server") + f" '{server_name}'")
        self.resize(700, 500)
        self.setMinimumSize(600, 400)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)

        main_layout = QVBoxLayout(self)
        self.tabs = QTabWidget()
        main_layout.addWidget(self.tabs)

        # -- Console tab --
        self.console_tab = QWidget()
        console_layout = QVBoxLayout(self.console_tab)

        btn_row = QHBoxLayout()
        self.btn_start = QPushButton(self.tr("Start server"))
        self.btn_start.setStyleSheet("background-color: #4caf50; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        self.btn_stop = QPushButton(self.tr("Stop server"))
        self.btn_stop.setStyleSheet("background-color: #f44336; color: white; font-weight: bold; padding: 6px 16px; border-radius: 4px;")
        self.btn_stop.setEnabled(False)
        btn_row.addWidget(self.btn_start)
        btn_row.addWidget(self.btn_stop)
        btn_row.addStretch()
        console_layout.addLayout(btn_row)

        self.console_output = QTextEdit()
        self.console_output.setReadOnly(True)
        self.console_output.setStyleSheet("""
            background-color: #1a1a2e; color: #00ff00;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 12px; border: 1px solid #333; border-radius: 4px;
        """)
        console_layout.addWidget(self.console_output)

        cmd_row = QHBoxLayout()
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText(self.tr("Enter command..."))
        self.cmd_input.returnPressed.connect(self.send_console_command)
        self.btn_send = QPushButton(self.tr("Send"))
        self.btn_send.clicked.connect(self.send_console_command)
        cmd_row.addWidget(self.cmd_input)
        cmd_row.addWidget(self.btn_send)
        console_layout.addLayout(cmd_row)

        self.tabs.addTab(self.console_tab, self.tr("Console"))

        self.btn_start.clicked.connect(self.start_server)
        self.btn_stop.clicked.connect(self.stop_server)

        # -- Settings tab --
        self.settings_tab = QWidget()
        settings_layout = QVBoxLayout(self.settings_tab)

        self.checkbox_eula = QCheckBox(self.tr("I accept the EULA"))
        self.checkbox_offline = QCheckBox(self.tr("Enable offline mode (cracked)"))
        self.checkbox_playit = QCheckBox(self.tr("Use playit.gg (tunnel)"))

        self.spin_max_players = QSpinBox()
        self.spin_max_players.setRange(1, 100)
        self.spin_max_players.setValue(20)

        self.motd_edit = QLineEdit("A SuperLauncher Server")

        self.ram_slider = QSlider(Qt.Orientation.Horizontal)
        self.ram_slider.setMinimum(1)
        self.ram_slider.setMaximum(16)
        self.ram_slider.setValue(self.ram_gb)
        self.ram_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ram_slider.setTickInterval(1)
        self.ram_slider.valueChanged.connect(lambda v: setattr(self, 'ram_gb', v))

        form = QFormLayout()
        form.addRow(self.tr("EULA") + ":", self.checkbox_eula)
        form.addRow(self.tr("Offline mode") + ":", self.checkbox_offline)
        form.addRow(self.tr("Max players") + ":", self.spin_max_players)
        form.addRow(self.tr("MOTD") + ":", self.motd_edit)
        form.addRow(self.tr("RAM (GB):") + ":", self.ram_slider)
        form.addRow(self.tr("playit.gg") + ":", self.checkbox_playit)
        settings_layout.addLayout(form)

        self.btn_save_settings = QPushButton(self.tr("Save settings"))
        self.btn_save_settings.setStyleSheet("padding: 6px 16px; font-weight: bold; background-color: #4facfe; color: black; border-radius: 4px;")
        self.btn_save_settings.clicked.connect(self.save_settings)
        settings_layout.addWidget(self.btn_save_settings)
        settings_layout.addStretch()

        self.tabs.addTab(self.settings_tab, self.tr("Settings"))

        # -- Plugins tab --
        self.plugins_tab = QWidget()
        plugins_layout = QVBoxLayout(self.plugins_tab)

        search_row = QHBoxLayout()
        self.plugin_search_input = QLineEdit()
        self.plugin_search_input.setPlaceholderText(self.tr("Search plugins..."))
        self.btn_plugin_search = QPushButton(self.tr("Search"))
        self.btn_plugin_search.clicked.connect(self.search_plugins)
        search_row.addWidget(self.plugin_search_input)
        search_row.addWidget(self.btn_plugin_search)
        plugins_layout.addLayout(search_row)

        self.plugin_results = QListWidget()
        plugins_layout.addWidget(QLabel(self.tr("Search results:")))
        plugins_layout.addWidget(self.plugin_results)

        install_row = QHBoxLayout()
        self.btn_plugin_install = QPushButton(self.tr("Install"))
        self.btn_plugin_install.clicked.connect(self.install_selected_plugin)
        install_row.addWidget(self.btn_plugin_install)
        install_row.addStretch()
        plugins_layout.addLayout(install_row)

        plugins_layout.addWidget(QLabel(self.tr("Installed plugins:")))
        self.installed_plugins_list = QListWidget()
        plugins_layout.addWidget(self.installed_plugins_list)

        uninstall_row = QHBoxLayout()
        self.btn_plugin_uninstall = QPushButton(self.tr("Uninstall"))
        self.btn_plugin_uninstall.clicked.connect(self.uninstall_plugin)
        uninstall_row.addWidget(self.btn_plugin_uninstall)
        uninstall_row.addStretch()
        plugins_layout.addLayout(uninstall_row)

        self.tabs.addTab(self.plugins_tab, self.tr("Plugins"))
        self.refresh_installed_plugins()

        # -- Backup tab --
        self.backup_tab = QWidget()
        backup_layout = QVBoxLayout(self.backup_tab)

        self.btn_create_backup = QPushButton(self.tr("Create Backup"))
        self.btn_create_backup.setStyleSheet("padding: 8px; font-weight: bold; background-color: #ff9800; color: black; border-radius: 4px;")
        self.btn_create_backup.clicked.connect(self.create_backup)
        backup_layout.addWidget(self.btn_create_backup)

        backup_layout.addWidget(QLabel(self.tr("Backups:")))
        self.backup_list = QListWidget()
        backup_layout.addWidget(self.backup_list)

        self.btn_restore_backup = QPushButton(self.tr("Restore"))
        self.btn_restore_backup.clicked.connect(self.restore_backup)
        backup_layout.addWidget(self.btn_restore_backup)

        self.tabs.addTab(self.backup_tab, self.tr("Backup"))
        self.refresh_backups()

        self.server_thread.output_line.connect(self.on_server_output)
        self.server_thread.started.connect(self.on_server_started)
        self.server_thread.stopped.connect(self.on_server_stopped)
        self.server_thread.error.connect(self.on_server_error)

        self.load_settings()

    def tr(self, key: str) -> str:
        lang = self.config.get("language", "ru")
        return translations.get(lang, {}).get(key, key)

    def refresh_language(self):
        self.setWindowTitle(self.tr("Manage server") + f" '{self.server_name}'")
        self.tabs.setTabText(0, self.tr("Console"))
        self.tabs.setTabText(1, self.tr("Settings"))
        self.tabs.setTabText(2, self.tr("Plugins"))
        self.tabs.setTabText(3, self.tr("Backup"))
        self.btn_start.setText(self.tr("Start server"))
        self.btn_stop.setText(self.tr("Stop server"))
        self.cmd_input.setPlaceholderText(self.tr("Enter command..."))
        self.btn_send.setText(self.tr("Send"))
        self.checkbox_eula.setText(self.tr("I accept the EULA"))
        self.checkbox_offline.setText(self.tr("Enable offline mode (cracked)"))
        self.checkbox_playit.setText(self.tr("Use playit.gg (tunnel)"))
        self.btn_save_settings.setText(self.tr("Save settings"))
        self.plugin_search_input.setPlaceholderText(self.tr("Search plugins..."))
        self.btn_plugin_search.setText(self.tr("Search"))
        self.btn_plugin_install.setText(self.tr("Install"))
        self.btn_plugin_uninstall.setText(self.tr("Uninstall"))
        self.btn_create_backup.setText(self.tr("Create Backup"))
        self.btn_restore_backup.setText(self.tr("Restore"))

    def load_settings(self):
        eula_path = os.path.join(self.server_path, "eula.txt")
        self.checkbox_eula.setChecked(
            os.path.isfile(eula_path) and "eula=true" in open(eula_path, "r", encoding="utf-8").read().lower())

        prop_path = os.path.join(self.server_path, "server.properties")
        online_mode = True
        max_players = 20
        motd = "A SuperLauncher Server"
        if os.path.isfile(prop_path):
            with open(prop_path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("online-mode="):
                        online_mode = line.strip().split("=")[1].lower() == "true"
                    elif line.startswith("max-players="):
                        try:
                            max_players = int(line.strip().split("=")[1])
                        except Exception:
                            pass
                    elif line.startswith("motd="):
                        motd = line.strip().split("=", 1)[1] if "=" in line else motd
        self.checkbox_offline.setChecked(not online_mode)
        self.spin_max_players.setValue(max_players)
        self.motd_edit.setText(motd)
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
        props["max-players"] = str(self.spin_max_players.value())
        props["motd"] = self.motd_edit.text()

        try:
            with open(prop_path, "w", encoding="utf-8") as f:
                for k, v in props.items():
                    f.write(f"{k}={v}\n")
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to save server.properties") + f":\n{e}")
            return

        self.ram_gb = self.ram_slider.value()
        QMessageBox.information(self, self.tr("Success"), self.tr("Settings saved!"))

    def start_server(self):
        if self.server_thread.isRunning():
            return
        if not self.checkbox_eula.isChecked():
            QMessageBox.warning(self, "EULA", self.tr("You must accept the EULA!"))
            return
        self.save_settings()
        self.console_output.clear()
        self.console_output.append(self.tr("Starting server..."))
        if self.checkbox_playit.isChecked():
            self.start_playit()
        self.server_thread.ram_gb = self.ram_gb
        self.server_thread.start_server()

    def stop_server(self):
        if not self.server_thread.isRunning():
            return
        self.console_output.append(self.tr("Stopping server..."))
        self.server_thread.stop_server()
        self.stop_playit()

    def send_console_command(self):
        cmd = self.cmd_input.text().strip()
        if cmd:
            self.server_thread.send_command(cmd)
            self.console_output.append(f"> {cmd}")
            self.cmd_input.clear()

    def on_server_output(self, line):
        self.console_output.append(line)
        scrollbar = self.console_output.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())

    def on_server_started(self):
        self.btn_start.setEnabled(False)
        self.btn_stop.setEnabled(True)
        self.console_output.append(self.tr("Server started."))

    def on_server_stopped(self):
        self.btn_start.setEnabled(True)
        self.btn_stop.setEnabled(False)
        self.console_output.append(self.tr("Server stopped."))

    def on_server_error(self, msg):
        self.console_output.append(f"[ERROR] {msg}")
        QMessageBox.critical(self, self.tr("Error"), msg)

    # --- playit.gg ---
    def download_and_install_playit(self):
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
                QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to download playit MSI") + f":\n{e}")
                return False
        try:
            result = subprocess.run(["msiexec", "/i", msi_path, "/quiet", "/qn"], capture_output=True, text=True, shell=False)
            if result.returncode != 0:
                QMessageBox.critical(self, self.tr("Error"), self.tr("Installation failed"))
                return False
            return True
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), self.tr("Failed to install playit") + f":\n{e}")
            return False

    def start_playit(self):
        possible_paths = [
            os.path.expandvars(r"%ProgramFiles%\playit\playit.exe"),
            os.path.expandvars(r"%ProgramFiles(x86)%\playit\playit.exe"),
            os.path.join(self.server_path, "playit.exe"),
        ]
        playit_exe = next((p for p in possible_paths if os.path.isfile(p)), None)
        if not playit_exe and not self.download_and_install_playit():
            return False
        try:
            self.playit_process = subprocess.Popen([playit_exe], cwd=os.path.dirname(playit_exe))
            return True
        except Exception:
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

    # --- Plugins ---
    def search_plugins(self):
        query = self.plugin_search_input.text().strip()
        if not query:
            return
        self.plugin_results.clear()
        from threading import Thread

        category_map = {"paper": "paper", "purpur": "purpur", "vanilla": "bukkit", "fabric": "fabric", "quilt": "quilt"}
        cat = category_map.get(self.server_core.lower(), "bukkit")

        def task():
            try:
                # Modrinth AND facets with project_type:mod + categories:bukkit returns 0 results,
                # so only use project_type filter for fabric/quilt where it works.
                if cat in ("fabric", "quilt"):
                    facets = f'[["project_type:mod"],["categories:{cat}"]]'
                else:
                    facets = f'[["categories:{cat}"]]'
                url = f"{MODRINTH_API}/search?query={urllib.parse.quote(query)}&facets={urllib.parse.quote(facets)}&limit=30"
                resp = requests.get(url, headers={"User-Agent": "SuperLauncher/2.0"}, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                hits = data.get("hits", [])
                if not hits:
                    self.plugin_results.addItem(self.tr("No plugins found"))
                    return
                for hit in hits:
                    title = hit.get("title", "?")
                    slug = hit.get("slug", "")
                    downloads = hit.get("downloads", 0)
                    summary = hit.get("description", "")
                    if len(summary) > 80:
                        summary = summary[:77] + "..."
                    item_text = f"{title} ({slug}) - {downloads} downloads"
                    item = QListWidgetItem(item_text)
                    item.setData(Qt.ItemDataRole.UserRole, slug)
                    self.plugin_results.addItem(item)
            except Exception as e:
                self.plugin_results.addItem(self.tr("Error") + f": {e}")

        Thread(target=task, daemon=True).start()

    def install_selected_plugin(self):
        item = self.plugin_results.currentItem()
        if not item:
            return
        slug = item.data(Qt.ItemDataRole.UserRole)
        if not slug:
            return

        plugins_folder = os.path.join(self.server_path, "plugins")
        os.makedirs(plugins_folder, exist_ok=True)

        loader_map = {"paper": "bukkit", "purpur": "bukkit", "vanilla": "bukkit", "fabric": "fabric", "quilt": "quilt"}
        loader = loader_map.get(self.server_core.lower(), "bukkit")
        version = self.server_version if self.server_version else ""

        self.plugin_install_thread = PluginInstallThread(slug, version, loader, plugins_folder)
        self.plugin_install_thread.finished.connect(lambda p: QMessageBox.information(
            self, self.tr("Install plugin"), self.tr("Plugin installed") + f": {os.path.basename(p)}"))
        self.plugin_install_thread.finished.connect(lambda p: self.refresh_installed_plugins())
        self.plugin_install_thread.error.connect(lambda e: QMessageBox.critical(
            self, self.tr("Error"), self.tr("Downloading plugin...") + f"\n{e}"))
        self.plugin_install_thread.start()

    def refresh_installed_plugins(self):
        self.installed_plugins_list.clear()
        plugins_folder = os.path.join(self.server_path, "plugins")
        if os.path.isdir(plugins_folder):
            for f in sorted(os.listdir(plugins_folder)):
                if f.endswith(".jar"):
                    self.installed_plugins_list.addItem(f)

    def uninstall_plugin(self):
        item = self.installed_plugins_list.currentItem()
        if not item:
            return
        filename = item.text()
        reply = QMessageBox.question(self, self.tr("Uninstall"),
                                     f"{self.tr('Are you sure?')}\n{filename}",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        filepath = os.path.join(self.server_path, "plugins", filename)
        try:
            os.remove(filepath)
            self.refresh_installed_plugins()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    # --- Backups ---
    def create_backup(self):
        backup_dir = os.path.join(self.server_path, "backups")
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"backup_{timestamp}.zip")

        try:
            with zipfile.ZipFile(backup_path, "w", zipfile.ZIP_DEFLATED) as zf:
                for folder_name in ["world", "world_nether", "world_the_end", "plugins", ""]:
                    folder_path = os.path.join(self.server_path, folder_name)
                    if not os.path.isdir(folder_path):
                        continue
                    for root, dirs, files in os.walk(folder_path):
                        if "backups" in root.split(os.sep):
                            continue
                        for fname in files:
                            fpath = os.path.join(root, fname)
                            arcname = os.path.relpath(fpath, self.server_path)
                            zf.write(fpath, arcname)
            QMessageBox.information(self, self.tr("Backup"), self.tr("Backup created") + f":\n{backup_path}")
            self.refresh_backups()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))

    def refresh_backups(self):
        self.backup_list.clear()
        backup_dir = os.path.join(self.server_path, "backups")
        if os.path.isdir(backup_dir):
            for f in sorted(os.listdir(backup_dir), reverse=True):
                if f.endswith(".zip"):
                    self.backup_list.addItem(f)

    def restore_backup(self):
        item = self.backup_list.currentItem()
        if not item:
            return
        filename = item.text()
        reply = QMessageBox.question(self, self.tr("Restore backup"),
                                     f"{self.tr('Are you sure?')}\n{filename}",
                                     QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply != QMessageBox.StandardButton.Yes:
            return
        backup_path = os.path.join(self.server_path, "backups", filename)
        try:
            with zipfile.ZipFile(backup_path, "r") as zf:
                zf.extractall(self.server_path)
            QMessageBox.information(self, self.tr("Restore backup"), self.tr("Backup restored"))
            self.refresh_installed_plugins()
        except Exception as e:
            QMessageBox.critical(self, self.tr("Error"), str(e))


class ServersPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.config = load_config()

        self.servers_file = "servers_list.json"
        self.servers_list = []

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(15, 15, 15, 15)
        self.layout.setSpacing(10)

        self.title_label = QLabel(self.tr("🖧 Minecraft Servers"))
        self.title_label.setStyleSheet(
            "font-size: 26px; font-weight: bold; margin-bottom: 15px; color: white;"
        )
        self.layout.addWidget(self.title_label)

        self.btn_create_server = QPushButton(self.tr("Create your own server"))
        self.btn_create_server.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_create_server.setStyleSheet(
            "padding: 8px; font-weight: bold; background-color: #4facfe; color: black; border-radius: 8px;"
        )
        self.btn_create_server.clicked.connect(self.open_create_server_dialog)
        self.layout.addWidget(self.btn_create_server)

        form_layout = QHBoxLayout()
        self.input_name = QLineEdit()
        self.input_name.setPlaceholderText(self.tr("Server Name"))
        self.input_ip = QLineEdit()
        self.input_ip.setPlaceholderText(self.tr("IP or domain"))

        self.btn_add_server = QPushButton(self.tr("Add server"))
        self.btn_add_server.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.btn_add_server.setStyleSheet(
            "padding: 6px 12px; font-weight: bold; background-color: #4CAF50; color: white; border-radius: 5px;"
        )
        self.btn_add_server.clicked.connect(self.add_server)

        form_layout.addWidget(self.input_name)
        form_layout.addWidget(self.input_ip)
        form_layout.addWidget(self.btn_add_server)
        self.layout.addLayout(form_layout)

        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.hide()
        self.layout.addWidget(self.progress_bar)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("QScrollArea { border: none; background: transparent; }")
        self.layout.addWidget(self.scroll_area)

        self.container = QWidget()
        self.container.setStyleSheet("background: transparent;")
        self.scroll_area.setWidget(self.container)
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.setContentsMargins(0, 0, 0, 0)
        self.container_layout.setSpacing(8)

        self.load_servers()
        self.update_servers_ui()

    def tr(self, key: str) -> str:
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

    def open_create_server_dialog(self):
        dialog = CreateServerDialog(self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            name = dialog.server_name
            port = dialog.server_port
            version = dialog.server_version
            core = dialog.server_core
            ram_gb = dialog.ram_gb
            ip = f"localhost:{port}"

            server_path = os.path.join("servers", name)
            os.makedirs(server_path, exist_ok=True)

            self.progress_bar.setValue(0)
            self.progress_bar.show()

            self.download_thread = DownloadThread(core, version, os.path.join(server_path, "server.jar"))
            self.download_thread.progress_changed.connect(self.progress_bar.setValue)
            self.download_thread.finished.connect(lambda: self.on_download_finished(name, ip, server_path, ram_gb, version, core))
            self.download_thread.error.connect(self.on_download_error)
            self.download_thread.start()

    def on_download_finished(self, name, ip, server_path, ram_gb=4, version='', core=''):
        self.progress_bar.hide()
        self.generate_start_bat(server_path, ram_gb)

        self.servers_list.append({"name": name, "ip": ip, "managed": True, "ram_gb": ram_gb, "version": version, "core": core})
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

    def generate_start_bat(self, path, ram_gb=4):
        with open(os.path.join(path, "start.bat"), "w", encoding="utf-8") as f:
            f.write(f"""@echo off
java -Xmx{ram_gb}G -Xms{ram_gb}G -jar server.jar nogui
""")

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

    def update_servers_ui(self):
        while self.container_layout.count():
            item = self.container_layout.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        for server in self.servers_list:
            self.add_server_widget(server['name'], server['ip'], server.get('managed', False), server.get('ram_gb', 4), server.get('version', ''), server.get('core', ''))

        self.container_layout.addStretch()

    def add_server_widget(self, name, ip, managed, ram_gb=4, version='', core=''):
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background: rgba(40, 40, 55, 0.9);
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 10px;
                padding: 8px;
            }
        """)
        card_layout = QHBoxLayout(card)
        card_layout.setContentsMargins(12, 8, 12, 8)
        card_layout.setSpacing(10)

        icon_label = QLabel("🖧")
        icon_label.setStyleSheet("font-size: 24px;")
        card_layout.addWidget(icon_label)

        info_widget = QWidget()
        info_layout = QVBoxLayout(info_widget)
        info_layout.setContentsMargins(0, 0, 0, 0)
        info_layout.setSpacing(2)

        name_label = QLabel(f"<b>{name}</b>")
        name_label.setStyleSheet("font-size: 16px; color: white;")
        info_layout.addWidget(name_label)

        ip_label = QLabel(f"<span style='color:#4facfe;'>{ip}</span>")
        ip_label.setStyleSheet("font-size: 13px;")
        info_layout.addWidget(ip_label)

        badge_text = self.tr("Managed") if managed else self.tr("Manual")
        badge_color = "#4caf50" if managed else "#ff9800"
        badge = QLabel(f"<span style='background:{badge_color}; color:white; padding:2px 8px; border-radius:3px; font-size:11px;'>{badge_text}</span>")
        badge.setStyleSheet("font-size: 11px;")
        info_layout.addWidget(badge)

        card_layout.addWidget(info_widget)
        card_layout.addStretch()

        btn_style = "padding: 5px 12px; font-weight: bold; border-radius: 5px; font-size: 12px;"

        if managed:
            btn_console = QPushButton(self.tr("Console"))
            btn_console.setStyleSheet(f"{btn_style} background-color: #4facfe; color: black;")
            btn_console.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            server_path = os.path.join("servers", name)
            btn_console.clicked.connect(lambda checked, n=name, p=server_path, r=ram_gb, v=version, c=core: self.open_console(n, p, r, v, c))
            card_layout.addWidget(btn_console)

            btn_open = QPushButton(self.tr("Open folder"))
            btn_open.setStyleSheet(f"{btn_style} background-color: #607d8b; color: white;")
            btn_open.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            btn_open.clicked.connect(lambda checked, p=server_path: os.startfile(p) if hasattr(os, 'startfile') else None)
            card_layout.addWidget(btn_open)

        btn_delete = QPushButton(self.tr("Delete"))
        btn_delete.setStyleSheet(f"{btn_style} background-color: #f44336; color: white;")
        btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        btn_delete.clicked.connect(lambda checked, n=name, m=managed: self.delete_server(n, m))
        card_layout.addWidget(btn_delete)

        self.container_layout.addWidget(card)

    def open_console(self, server_name, server_path, ram_gb=4, version='', core=''):
        dialog = ServerControlDialog(server_name, server_path, ram_gb, version, core, self)
        dialog.exec()

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
        self.setWindowTitle("SuperLauncher 2026 Edition v2.0.0")
        self.setWindowIcon(QIcon("assets/icon.png"))

        self.resize(1080, 720)
        self.setMinimumSize(800, 600)
        self.setMaximumSize(1920, 1080)

        self.account_system = AccountSystem()
        self.skins_manager = SkinsManager(self.account_system)
        self.builds_manager = BuildsManager()
        self.custom_ui = CustomizableUI()
        self.platform_info = CrossPlatformSupport.get_platform_info()

        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        central_widget = GlassFrame()
        self.setCentralWidget(central_widget)

        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(0)

        self.pages = QStackedWidget()
        self.pages.setStyleSheet("""
            QStackedWidget {
                background: rgba(30, 30, 40, 0.9);
                border: 1px solid rgba(255, 255, 255, 0.1);
                border-radius: 20px;
                margin: 5px;
            }
        """)

        self.create_all_pages()

        self.sidebar = ModernSidebar(self)

        self.check_pages_consistency()

        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.pages)

        self.launch_thread = LaunchThread()
        self.launch_thread.state_update_signal.connect(self.state_update)
        self.launch_thread.progress_update_signal.connect(self.update_progress)
        self.launch_thread.error_signal.connect(self.show_launch_error)

        self.discord_rpc_thread = DiscordRPCThread(self)
        self.discord_rpc_thread.start()

        self.setup_status_bar()

        self.check_auto_login()

        self.custom_ui.apply_to_widget(self)
    
    def create_all_pages(self):
        pages_list = []

        # 0 - Главная
        pages_list.append(self.create_home_page())

        # 1 - Аккаунт
        pages_list.append(self.create_account_page())

        # 2 - Моды
        pages_list.append(ModsPage(self))

        # 3 - Сборки
        pages_list.append(self.create_builds_page())

        # 4 - Скины
        pages_list.append(self.create_skins_page())

        # 5 - Новости
        pages_list.append(NewsPage(self))

        # 6 - Обновления
        pages_list.append(UpdatesPage())

        # 7 - Серверы
        pages_list.append(ServersPage(self))

        # 8 - Настройки
        self.settings_page = SettingsPage(self)
        pages_list.append(self.settings_page)

        # 9 - Minecraft
        minecraft_page = MinecraftLauncherPage()
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

        # 10 - AI Агент
        self.ai_page = AIAgentPage(self)
        pages_list.append(self.ai_page)

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
    

    def create_home_page(self):
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(12)

        title_label = GradientLabel("SuperLauncher 2026")
        title_label.setStyleSheet("""
            font-size: 28px;
            margin: 8px 0;
            font-weight: bold;
            text-align: center;
        """)
        layout.addWidget(title_label)

        user_info_widget = self.create_user_info_widget_720p()
        layout.addWidget(user_info_widget)

        quick_actions = self.create_quick_actions_720p()
        layout.addWidget(quick_actions)

        layout.addStretch()
        return page

    # В классе MainWindow (примерно строка 4012) ЗАМЕНИТЕ:

    def create_user_info_widget_720p(self):
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

        self.avatar_label = QLabel("👤")
        self.avatar_label.setStyleSheet("font-size: 36px; padding: 8px;"
            "background-color: rgba(255, 255, 255, 0.1); border-radius: 50%;"
            "min-width: 60px; min-height: 60px; text-align: center;")
        layout.addWidget(self.avatar_label)

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

        self.login_button = QPushButton("Войти / Зарегистрироваться")
        self.login_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.login_button.setStyleSheet("background-color: #4facfe; color: white; border: none;"
            "border-radius: 6px; padding: 6px 12px; font-weight: bold; font-size: 12px;")
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
            ("🛒", "Скины", lambda: self.pages.setCurrentIndex(4)),
            ("📦", "Сборки", lambda: self.pages.setCurrentIndex(3)),
            ("⚙️", "Настройки", lambda: self.pages.setCurrentIndex(8)),
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
        page = QWidget()
        layout = QVBoxLayout(page)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        self.builds_manager = BuildsManager()

        title = QLabel("📦 Сборки и Модпаки")
        title.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: white;")
        layout.addWidget(title)

        # Источник + поиск
        search_row = QHBoxLayout()
        self.builds_source = QComboBox()
        self.builds_source.addItems(["Modrinth", "CurseForge"])
        self.builds_source.setStyleSheet("background-color: #2f2f2f; color: white; border: 1px solid #444; border-radius: 5px; padding: 3px;")
        search_row.addWidget(self.builds_source)

        self.builds_search = QLineEdit()
        self.builds_search.setPlaceholderText("Введите название сборки...")
        self.builds_search.setStyleSheet("background-color: #2f2f2f; color: white; border: 1px solid #444; border-radius: 5px; padding: 8px;")
        self.builds_search.returnPressed.connect(self.search_builds)
        search_row.addWidget(self.builds_search, 1)

        self.builds_search_btn = QPushButton("Поиск")
        self.builds_search_btn.setStyleSheet("background-color: #4facfe; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold;")
        self.builds_search_btn.clicked.connect(self.search_builds)
        search_row.addWidget(self.builds_search_btn)

        import_btn = QPushButton("📂 .mrpack")
        import_btn.setStyleSheet("background-color: #2f2f2f; color: white; border: 1px solid #444; border-radius: 5px; padding: 8px 10px;")
        import_btn.clicked.connect(self.import_mrpack)
        search_row.addWidget(import_btn)

        layout.addLayout(search_row)

        # Доступные сборки
        builds_group = QGroupBox("🔍 Доступные сборки")
        builds_group.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #4facfe;
                border: 1px solid #4facfe; border-radius: 8px; margin-top: 8px; padding-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px; }
        """)
        self.builds_list = QListWidget()
        self.builds_list.setStyleSheet("""
            QListWidget { background-color: #2f2f2f; border: 1px solid #444; border-radius: 5px; color: white; font-size: 14px; }
            QListWidget::item { padding: 10px; border-bottom: 1px solid #444; }
            QListWidget::item:hover { background-color: #3a3a3a; }
            QListWidget::item:selected { background-color: rgba(79,172,254,0.3); }
        """)
        self.builds_list.itemDoubleClicked.connect(self.install_selected_build)
        b_group_layout = QVBoxLayout()
        b_group_layout.addWidget(self.builds_list)
        b_btns = QHBoxLayout()
        btn_install = QPushButton("⬇️ Установить")
        btn_install.setStyleSheet("background-color: #4facfe; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold;")
        btn_install.clicked.connect(self.install_selected_build)
        btn_info = QPushButton("ℹ️ Инфо")
        btn_info.setStyleSheet("background-color: #2f2f2f; color: #4facfe; border: 1px solid #4facfe; border-radius: 5px; padding: 8px 15px;")
        btn_info.clicked.connect(self.show_build_info)
        b_btns.addWidget(btn_install)
        b_btns.addWidget(btn_info)
        b_btns.addStretch()
        b_group_layout.addLayout(b_btns)
        builds_group.setLayout(b_group_layout)
        layout.addWidget(builds_group, 1)

        # Установленные сборки
        installed_group = QGroupBox("📁 Установленные")
        installed_group.setStyleSheet("""
            QGroupBox { font-size: 14px; font-weight: bold; color: #4facfe;
                border: 1px solid #4facfe; border-radius: 8px; margin-top: 8px; padding-top: 12px; }
            QGroupBox::title { subcontrol-origin: margin; left: 10px; padding: 0 8px; }
        """)
        self.installed_builds_list = QListWidget()
        self.installed_builds_list.setStyleSheet("""
            QListWidget { background-color: #2f2f2f; border: 1px solid #444; border-radius: 5px; color: white; font-size: 14px; }
            QListWidget::item { padding: 8px; border-bottom: 1px solid #444; }
        """)
        i_group_layout = QVBoxLayout()
        i_group_layout.addWidget(self.installed_builds_list)
        i_btns = QHBoxLayout()
        btn_play = QPushButton("🎮 Запустить")
        btn_play.setStyleSheet("background-color: #4facfe; color: white; border: none; border-radius: 5px; padding: 8px 15px; font-weight: bold;")
        btn_play.clicked.connect(self.play_installed_build)
        btn_remove = QPushButton("🗑️ Удалить")
        btn_remove.setStyleSheet("background-color: #d9534f; color: white; border: none; border-radius: 5px; padding: 8px 15px;")
        btn_remove.clicked.connect(self.remove_installed_build)
        btn_restore = QPushButton("🔄 Восст. моды")
        btn_restore.setStyleSheet("background-color: #5bc0de; color: white; border: none; border-radius: 5px; padding: 8px 15px;")
        btn_restore.clicked.connect(self.restore_mods_backup)
        btn_dlcf = QPushButton("📥 Докачать моды")
        btn_dlcf.setStyleSheet("background-color: #f0ad4e; color: white; border: none; border-radius: 5px; padding: 8px 15px;")
        btn_dlcf.clicked.connect(self.download_missing_cf_mods)
        btn_clear_cache = QPushButton("🧹 Очистить кэш")
        btn_clear_cache.setStyleSheet("background-color: #6c757d; color: white; border: none; border-radius: 5px; padding: 8px 15px;")
        btn_clear_cache.clicked.connect(self.clear_builds_cache)
        i_btns.addWidget(btn_play)
        i_btns.addWidget(btn_remove)
        i_btns.addWidget(btn_restore)
        i_btns.addWidget(btn_dlcf)
        i_btns.addWidget(btn_clear_cache)
        i_btns.addStretch()
        i_group_layout.addLayout(i_btns)
        installed_group.setLayout(i_group_layout)
        layout.addWidget(installed_group)

        self.refresh_installed_builds()
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
            self.pages.setCurrentIndex(4)  # Переходим на страницу скинов
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
    
    def refresh_installed_builds(self):
        builds_dir = os.path.join(minecraft_directory, "builds")
        self.installed_builds_list.clear()
        for pack in self.builds_manager.get_installed_packs(builds_dir):
            name = pack.get("name", "?")
            mc = (pack.get("mc_versions") or ["?"])[0]
            src = pack.get("source", "?")
            item = QListWidgetItem(f"{name} [{mc}] ({src})")
            item.setData(Qt.ItemDataRole.UserRole, pack)
            self.installed_builds_list.addItem(item)

    def search_builds(self):
        query = self.builds_search.text().strip()
        source = self.builds_source.currentText()
        self.builds_list.clear()
        try:
            if source == "Modrinth":
                results = self.builds_manager.search_modrinth(query)
            else:
                results = self.builds_manager.search_curseforge(query)
            for mp in results:
                name = mp.get("name", "?")
                desc = mp.get("description", "")[:80]
                dl = mp.get("downloads", 0)
                source_label = mp.get("source", "")
                item = QListWidgetItem(f"{name} ⬇{dl} — {desc} [{source_label}]")
                item.setData(Qt.ItemDataRole.UserRole, mp)
                self.builds_list.addItem(item)
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", str(e))

    def _select_version(self, versions, source):
        if not versions:
            return None
        dialog = QDialog(self)
        dialog.setWindowTitle("Выберите версию")
        dialog.setMinimumWidth(400)
        layout = QVBoxLayout(dialog)
        combo = QComboBox()
        ver_map = {}
        if source == "modrinth":
            for v in versions:
                mc = ", ".join(v.get("game_versions", []))
                loaders = ", ".join(v.get("loaders", []))
                ver_num = v.get("version_number", "?")
                label = f"{ver_num} | MC: {mc} | {loaders}"
                ver_map[label] = v
                combo.addItem(label)
        else:
            LOADER_NAMES = {1: "Forge", 2: "Cauldron", 3: "LiteLoader", 4: "Fabric", 5: "Quilt", 6: "NeoForge"}
            for f in versions[:30]:
                mc = next((v for v in f.get("gameVersions", []) if v[0].isdigit()), "?")
                loader_name = "?"
                for sgv in f.get("sortableGameVersions", []):
                    if sgv.get("gameVersionTypeId") == 2:
                        gv_name = sgv.get("gameVersionName", "")
                        loader_name = LOADER_NAMES.get(int(gv_name), gv_name) if gv_name.isdigit() else gv_name
                dn = f.get("displayName", f.get("fileName", "?"))
                dlc = f.get("downloadCount", 0)
                label = f"{mc} | {loader_name} | {dn} ⬇{dlc}"
                ver_map[label] = f
                combo.addItem(label)
        layout.addWidget(QLabel("Выберите версию:"))
        layout.addWidget(combo)
        btn = QPushButton("Установить")
        btn.setStyleSheet("background-color: #4facfe; color: white; border: none; border-radius: 5px; padding: 8px; font-weight: bold;")
        layout.addWidget(btn)
        result = [None]
        def on_install():
            result[0] = ver_map[combo.currentText()]
            dialog.accept()
        btn.clicked.connect(on_install)
        dialog.exec()
        return result[0]

    def _clean_build_files(self, name):
        builds_dir = os.path.join(minecraft_directory, "builds", name)
        manifest_path = os.path.join(builds_dir, "installed_files.json")
        if os.path.exists(manifest_path):
            try:
                with open(manifest_path, encoding="utf-8") as f:
                    files = json.load(f)
                for fp in files:
                    if os.path.exists(fp) and fp.startswith(os.path.normpath(minecraft_directory) + os.sep):
                        try:
                            os.remove(fp)
                            print(f"Удалён: {fp}")
                        except Exception:
                            pass
                dirs = sorted(set(os.path.dirname(f) for f in files), key=len, reverse=True)
                for d in dirs:
                    if os.path.isdir(d) and d.startswith(os.path.normpath(minecraft_directory) + os.sep):
                        try:
                            if not os.listdir(d):
                                os.rmdir(d)
                        except Exception:
                            pass
            except Exception as e:
                print(f"Ошибка очистки старых файлов: {e}")

    def _run_install_with_progress(self, title, install_fn, build_name=None):
        dialog = QProgressDialog(title, "", 0, 0, self)
        dialog.setWindowTitle(title)
        dialog.setCancelButton(None)
        dialog.setMinimumWidth(350)
        dialog.show()
        QApplication.processEvents()

        def prog(val):
            if dialog.wasCanceled():
                return
            dialog.setValue(val)
            if val > 0:
                dialog.setMaximum(100)
                dialog.setValue(val)
            QApplication.processEvents()

        if build_name:
            self._clean_build_files(build_name)

        try:
            name, result = install_fn(prog)
        except Exception as e:
            name, result = None, str(e)
        finally:
            dialog.close()

        if name:
            info = result or {}
            mc_ver = info.get("mc_version", "?")
            loader = info.get("loader", "?")
            build_dir = os.path.join(minecraft_directory, "builds", name)
            self.builds_manager.create_install_config(
                build_dir,
                info.get("_source", ""), info.get("_version_id", ""),
                [mc_ver], [loader])
            installed = info.get("_installed_files", [])
            if installed:
                try:
                    with open(os.path.join(build_dir, "installed_files.json"), "w", encoding="utf-8") as f:
                        json.dump(installed, f, ensure_ascii=False, indent=2)
                except Exception as e:
                    print(f"Ошибка сохранения манифеста файлов: {e}")
            conflicted = self.builds_manager.detect_conflicting_mods(minecraft_directory)
            if conflicted:
                msg = "⚠️ Найдены конфликтные моды для Sinytra Connector:\n\n"
                for fn, mid, desc in conflicted:
                    msg += f"• {fn} ({desc})\n"
                msg += "\nОни могут вызвать краш при создании мира. Удалить их?"
                if QMessageBox.warning(self, "Конфликтные моды", msg,
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                    for fn, mid, desc in conflicted:
                        try:
                            os.remove(os.path.join(minecraft_directory, "mods", fn))
                            print(f"Удалён конфликтный мод: {fn}")
                        except Exception as e:
                            print(f"Не удалось удалить {fn}: {e}")
            QMessageBox.information(self, "Готово",
                f"✅ Сборка '{name}' установлена!\nMinecraft: {mc_ver}\nЗагрузчик: {loader}")
            if QMessageBox.question(self, "Докачка модов",
                "Скачать недостающие моды с CurseForge?\n(моды, которые нельзя распространять через Modrinth)",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No) == QMessageBox.StandardButton.Yes:
                self._run_install_with_progress("Загрузка модов с CurseForge...",
                    lambda cb: self.builds_manager.download_curseforge_mods_from_modlist(
                        minecraft_directory, cb, mc_ver=mc_ver, loader_type=loader))
            # авто-очистка кэша CurseForge (старше 7 дней)
            import time
            cache_dir = os.path.join(minecraft_directory, "cache", "curseforge")
            if os.path.exists(cache_dir):
                now = time.time()
                cleaned = 0
                for fn in os.listdir(cache_dir):
                    fp = os.path.join(cache_dir, fn)
                    try:
                        if os.path.isfile(fp) and now - os.path.getmtime(fp) > 604800:
                            os.remove(fp)
                            cleaned += 1
                    except Exception:
                        pass
                if cleaned:
                    print(f"Автоочистка кэша: удалено {cleaned} устаревших файлов")
        else:
            QMessageBox.critical(self, "Ошибка", f"Не удалось установить сборку:\n{result}")
        self.refresh_installed_builds()
        self.statusBar().clearMessage()

    def install_selected_build(self):
        item = self.builds_list.currentItem()
        if not item:
            return
        mp = item.data(Qt.ItemDataRole.UserRole)
        if not mp:
            return
        source = mp.get("source", "modrinth")
        versions = self.builds_manager.get_modpack_versions(mp["id"], source)
        selected = self._select_version(versions, source)
        if not selected:
            return
        builds_dir = os.path.join(minecraft_directory, "builds")
        os.makedirs(builds_dir, exist_ok=True)
        ok = QMessageBox.question(self, "Установка", f"Установить '{mp['name']}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ok != QMessageBox.StandardButton.Yes:
            return
        self.statusBar().showMessage(f"Установка {mp['name']}...")
        self._run_install_with_progress(f"Установка {mp['name']}...",
            lambda cb: self.builds_manager.download_and_install(selected, source, minecraft_directory, cb),
            build_name=mp['name'])

    def import_mrpack(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выберите .mrpack", "", "Modpacks (*.mrpack *.zip)")
        if not path:
            return
        self.statusBar().showMessage("Импорт сборки...")
        self._run_install_with_progress("Импорт сборки...",
            lambda cb: self.builds_manager._install_local_mrpack(path, minecraft_directory, cb))

    def show_build_info(self):
        item = self.builds_list.currentItem()
        if not item:
            return
        mp = item.data(Qt.ItemDataRole.UserRole)
        if not mp:
            return
        QMessageBox.information(self, "Информация",
            f"Название: {mp.get('name', '?')}\n"
            f"Автор: {mp.get('author', '?')}\n"
            f"Скачиваний: {mp.get('downloads', 0)}\n"
            f"Источник: {mp.get('source', '?')}\n"
            f"Описание: {mp.get('description', '?')[:200]}")

    def play_installed_build(self):
        item = self.installed_builds_list.currentItem()
        if not item:
            return
        name = item.text().split(" [")[0]
        cfg_path = os.path.join(minecraft_directory, "builds", name, "superlauncher_config.json")
        mc_ver = "?"
        loader = "vanilla"
        if os.path.exists(cfg_path):
            try:
                with open(cfg_path, encoding="utf-8") as f:
                    conf = json.load(f)
                mc_vers = conf.get("mc_versions", [])
                if mc_vers:
                    mc_ver = mc_vers[0]
                loaders = conf.get("loaders", [])
                if loaders:
                    loader = loaders[0].lower()
            except:
                pass

        minecraft_page = self.pages.widget(10)
        idx = minecraft_page.version_select.findText(mc_ver)
        if idx >= 0:
            minecraft_page.version_select.setCurrentIndex(idx)
        loader_map = {"forge": "Forge", "fabric": "Fabric", "quilt": "Quilt", "neoforge": "NeoForge", "vanilla": "Vanilla"}
        loader_name = loader_map.get(loader, "Forge")
        idx2 = minecraft_page.loader_select.findText(loader_name)
        if idx2 >= 0:
            minecraft_page.loader_select.setCurrentIndex(idx2)

        self.pages.setCurrentIndex(9)
        reply = QMessageBox.question(self, "Запуск",
            f"Запуск сборки '{name}'\nMinecraft: {mc_ver}  |  Загрузчик: {loader_name}\n\n"
            f"Версия и загрузчик уже выбраны на странице Minecraft.\nЗапустить сейчас?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if reply == QMessageBox.StandardButton.Yes:
            self.launch_game()

    def remove_installed_build(self):
        item = self.installed_builds_list.currentItem()
        if not item:
            return
        ok = QMessageBox.question(self, "Удаление", f"Удалить '{item.text()}'?\nВсе файлы сборки в .minecraft будут удалены.",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ok != QMessageBox.StandardButton.Yes:
            return
        builds_dir = os.path.join(minecraft_directory, "builds")
        name = item.text().split(" [")[0]
        self._clean_build_files(name)
        target = os.path.join(builds_dir, name)
        if os.path.exists(target):
            import shutil
            shutil.rmtree(target, ignore_errors=True)
        self.builds_manager.restore_mods(minecraft_directory)
        self.refresh_installed_builds()
    
    def restore_mods_backup(self):
        ok = self.builds_manager.restore_mods(minecraft_directory)
        if ok:
            QMessageBox.information(self, "Готово", "Моды восстановлены из резервной копии.")
        else:
            QMessageBox.information(self, "Восстановление", "Резервной копии модов не найдено.")
    
    def download_missing_cf_mods(self):
        item = self.installed_builds_list.currentItem()
        mc_ver = None
        loader = "forge"
        if item:
            name = item.text().split(" [")[0]
            cfg_path = os.path.join(minecraft_directory, "builds", name, "superlauncher_config.json")
            if os.path.exists(cfg_path):
                try:
                    with open(cfg_path, encoding="utf-8") as f:
                        conf = json.load(f)
                    mc_vers = conf.get("mc_versions", [])
                    if mc_vers:
                        mc_ver = mc_vers[0]
                    loaders = conf.get("loaders", [])
                    if loaders:
                        loader = loaders[0].lower()
                except Exception:
                    pass
        self.statusBar().showMessage("Загрузка недостающих модов с CurseForge...")
        self._run_install_with_progress("Загрузка модов с CurseForge...",
            lambda cb: self.builds_manager.download_curseforge_mods_from_modlist(
                minecraft_directory, cb, mc_ver=mc_ver, loader_type=loader))
    
    def clear_builds_cache(self):
        cache_dir = os.path.join(minecraft_directory, "cache")
        if not os.path.exists(cache_dir):
            QMessageBox.information(self, "Кэш", "Кэш пуст.")
            return
        import shutil
        try:
            total = 0
            for root, dirs, files in os.walk(cache_dir):
                total += len(files)
            ok = QMessageBox.question(self, "Очистка кэша",
                f"Удалить {total} файлов из кэша?\nВсе скачанные моды будут загружены заново при следующей докачке.",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
            if ok != QMessageBox.StandardButton.Yes:
                return
            shutil.rmtree(cache_dir, ignore_errors=True)
            os.makedirs(cache_dir, exist_ok=True)
            QMessageBox.information(self, "Готово", f"Кэш очищен. Удалено {total} файлов.")
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Не удалось очистить кэш:\n{e}")
    
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
            "Поддержка: https://github.com/Ludvig2457Ultra/SuperLauncherMC"
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
    
    def show_launch_error(self, error_msg):
        QMessageBox.critical(self, "Ошибка запуска", f"Minecraft не запустился:\n{error_msg}")

    def apply_settings(self):
        if hasattr(self, "settings_page"):
            theme = self.settings_page.config.get("theme", "dark")
            # Обновляем тему
            self.custom_ui.apply_to_widget(self)
    
    def launch_game(self):
        minecraft_page = self.pages.widget(10)
        if hasattr(self, "settings_page"):
            config = self.settings_page.config
            version = minecraft_page.version_select.currentText()
            username = minecraft_page.username.text() or "player"
            loader_type = minecraft_page.loader_select.currentText().lower()

            if self.account_system.current_user:
                username = self.account_system.current_user["username"]

            # Передаём настройки в поток запуска
            self.launch_thread.max_ram = config.get("max_ram", 4096)
            self.launch_thread.min_ram = max(1024, config.get("max_ram", 4096) // 4)
            self.launch_thread.java_path = config.get("java_path", "")
            self.launch_thread.jvm_args = config.get("jvm_args", "")

            if config.get("launch_mode") == "java" and config.get("java_path"):
                self.launch_thread.java_path = config["java_path"]

            self.launch_thread.launch_setup_signal.emit(version, username, loader_type)
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