[app]
# Название игры
title = SpaceDodger

# Имя пакета (только маленькие буквы и без пробелов)
package.name = spacedodger

# Домен (можешь оставить так или вписать свой)
package.domain = org.твоеимя

# Путь к исходникам (точка означает текущую папку)
source.dir = .

# Разрешенные форматы файлов
source.include_exts = py,png,jpg,ttf,wav,ogg

# Версия приложения
version = 1.0

# Зависимости (самое главное для твоего кода)
requirements = python3,pygame

# Ориентация экрана (твоя игра вертикальная)
orientation = portrait
fullscreen = 1

# Архитектуры процессоров (поддерживает большинство современных телефонов, включая твой Redmi)
android.archs = arm64-v8a, armeabi-v7a

# Разрешить создание бэкапов
android.allow_backup = True
