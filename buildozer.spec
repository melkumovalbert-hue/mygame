[app]
title = SpaceShooter
package.name = spaceshooter
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,wav,mp3,ogg
version = 0.1

requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.5.2,android

orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.accept_sdk_license = True
android.archs = arm64-v8a

android.permissions = VIBRATE

[buildozer]
log_level = 2
warn_on_root = 0
