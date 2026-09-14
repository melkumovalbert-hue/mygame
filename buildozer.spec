[app]
# Название игры
title = SpaceDodger

# Имя пакета (только строчные буквы)
package.name = spacedodger

# Домен приложения
package.domain = org.game

# Путь к исходному коду
source.dir = .

# Расширения файлов для включения
source.include_exts = py,png,jpg,ttf,wav,ogg

# Версия приложения
version = 1.0

# Зависимости Python
requirements = python3,pygame

# Настройки экрана
orientation = portrait
fullscreen = 1

# Поддержка архитектур для Android
android.archs = arm64-v8a, armeabi-v7a

# Разрешения и лицензии
android.allow_backup = True
android.accept_sdk_license = True
android.api = 33
android.minapi = 21
p4a.branch = master
