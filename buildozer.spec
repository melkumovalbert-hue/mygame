[app]

# Название приложения
title = My Application

# Имя пакета
package.name = myapp

# Домен пакета
package.domain = org.example

# Исходные файлы (код Python, изображения и т.д.)
source.include_exts = py,png,jpg,kv,atlas

# Главная точка входа
source.main = main.py

# Версия приложения
version = 0.1

# Требования (например, kivy, python3)
requirements = python3,kivy

# Ориентация экрана
orientation = portrait

# Поддерживаемые архитектуры (для универсального APK или только arm64)
android.archs = arm64-v8a, armeabi-v7a

# ВАЖНО: Актуальные версии API и NDK для стабильной сборки
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33

# Автоматическое принятие лицензий Android SDK
android.accept_sdk_license = True

[buildozer]

# Уровень логирования (1 = информация, 2 = отладка)
log_level = 2

# Предупреждение о запуске от root (для контейнеров GitHub Actions)
warn_on_root = 1
