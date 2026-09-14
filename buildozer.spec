[app]

title = Space Dodger
package.name = spacedodger
package.domain = org.albert
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 0.1
requirements = python3,pygame
orientation = portrait
fullscreen = 0

# Версии для правильной сборки без ошибок
android.api = 33
android.minapi = 21
android.ndk = 25b

[buildozer]
log_level = 2
warn_on_root = 1

[app.android]
android.accept_sdk_license = True
