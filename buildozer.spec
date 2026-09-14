[app]
title = SpaceShooter
package.name = spaceshooter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3
version = 0.1

requirements = python3,kivy

orientation = portrait
osx.python_version = 3
osx.kivy_version = 1.9.1
fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_licenses = True
android.archs = arm64-v8a

[buildozer]
log_level = 1
warn_on_root = 12
