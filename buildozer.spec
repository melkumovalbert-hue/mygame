[app]
title = SpaceShooter
package.name = spaceshooter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,mp3,ogg
version = 0.1

requirements = python3==3.11.9,hostpython3==3.11.9,pygame,android,sdl2,sdl2_image,sdl2_mixer,sdl2_ttf,png,jpeg

orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

android.permissions = INTERNET,VIBRATE

[buildozer]
log_level = 2
warn_on_root = 0
