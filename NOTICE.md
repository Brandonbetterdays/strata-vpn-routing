# Источники и лицензии

Сборка использует данные и инструменты других проектов. Их лицензии — у них в репозиториях.

| Что | Откуда | Лицензия | Как используется |
|---|---|---|---|
| Списки доменов `category-ru`, `whitelist`, `category-geoblock-ru`, `youtube`, `telegram`, `github`, `google-play`, `google-deepmind`, `twitch-ads`, `category-ads`, `torrent`, `win-spy`, `private`, игровые/Apple/Microsoft | [hydraponique/roscomvpn-geosite](https://github.com/hydraponique/roscomvpn-geosite) | MIT (© V2Ray, файл LICENSE в репозитории) | скачиваются при каждой сборке и включаются в `geosite.dat` через `include:` |
| Сборщик `geosite.dat` | [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community) | MIT | запускается в CI, в репозиторий не копируется |
| Список российских IP (`text/ru.txt`) | [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip), ветка release | данные — CC BY-SA 4.0 | основа категорий `ru` и `direct` в `geoip.dat`; `geoip.dat` распространяется на тех же условиях (CC BY-SA 4.0) |
| Сборщик `geoip.dat` | Loyalsoldier/geoip | GPL-3.0 | запускается в CI, в репозиторий не копируется |
| Проверка | [XTLS/Xray-core](https://github.com/XTLS/Xray-core) | MPL-2.0 | `xray run -test` в CI |

This product includes GeoLite2 data created by MaxMind, available from [MaxMind](https://www.maxmind.com)
(требование Loyalsoldier/geoip к атрибуции, раздел License их README).

IP-списки [roscomvpn-geoip](https://github.com/hydraponique/roscomvpn-geoip) не используются: файла лицензии в том
репозитории нет.
