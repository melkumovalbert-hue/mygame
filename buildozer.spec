[app]

title = Космический уворотчик
package.name = kosmicheskiyuvorotchik
package.domain = org.albert

source.dir = .
source.include_exts = py,png,jpg,jpeg,wav,mp3,ogg,ttf

version = 1.0

requirements = python3==3.10.12,hostpython3==3.10.12,pygame==2.5.2

orientation = portrait
fullscreen = 1

android.api = 33
android.minapi = 21
android.ndk = 25b
android.ndk_api = 21
android.archs = arm64-v8a

android.permissions = VIBRATE

[buildozer]

log_level = 2
warn_on_root = 0
