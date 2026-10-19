# strata-vpn-routing

Маршрутизация Strata VPN для Happ и Incy: **российские сервисы — без VPN, заблокированное — через VPN,
реклама, торрент-трекеры и телеметрия Windows — блок, всё неизвестное — через VPN.**
Файлы `geosite.dat` / `geoip.dat` собираются автоматически каждый день и перед публикацией
проверяются настоящим Xray.

## Ссылки для пользователей

После первой сборки в ветке [`release`](../../tree/release) лежат:

| Файл | Что это |
|---|---|
| `happ.txt` | ссылка `happ://routing/onadd/…` — добавить и включить профиль в Happ |
| `incy.txt` | ссылка `incy://routing/onadd/…` — то же для Incy |
| `strata-profile.json` | сам профиль |
| `geosite.dat`, `geoip.dat` | geo-файлы (профиль берёт их по адресу `https://cdn.jsdelivr.net/gh/Brandonbetterdays/strata-vpn-routing@release/…`) |
| `lists/*.txt` | развёрнутые списки доменов — посмотреть, что куда идёт |
| `SOURCES.txt` | из каких версий источников собрано |

Профиль ссылается на geo-файлы по постоянному адресу, поэтому **ссылку пользователям нужно выдать один раз**:
новые списки клиенты подхватывают сами (Happ обновляет geo-файлы не чаще раза в неделю — по его документации).
Новая ссылка нужна только если изменился сам профиль (`profile/strata.json`).

## Как устроено

```
data/                       списки доменов (формат v2fly domain-list-community)
  strata-direct             БЕЗ VPN  = strata-direct-custom + strata-cdn + российские категории roscomvpn
  strata-tunnel             ЧЕРЕЗ VPN = strata-tunnel-custom + category-geoblock-ru, youtube, telegram, github, …
  strata-ads                БЛОК     = strata-ads-custom + category-ads
  strata-block              БЛОК     = torrent + win-spy
  *-custom, strata-cdn      ВАШИ списки — правьте их
geoip/
  config.json               direct = российские IP (Loyalsoldier/geoip) + direct-custom.txt − direct-exclude.txt
profile/
  strata.json               профиль Happ/Incy (порядок: блок → VPN → напрямую)
  subscription-template.json клиентский шаблон подписки PasarGuard — тоже проверяется при каждой сборке
scripts/                    build.sh · make_profile.py · validate.py
.github/workflows/build.yml ежедневная сборка → проверка → публикация в ветку release
```

Сборка (`.github/workflows/build.yml`, каждый день в 05:30 МСК, при изменениях в `main` и вручную):
1. берёт свежие списки [roscomvpn-geosite](https://github.com/hydraponique/roscomvpn-geosite), добавляет наши
   и собирает `geosite.dat` официальным сборщиком [v2fly/domain-list-community](https://github.com/v2fly/domain-list-community);
2. собирает `geoip.dat` инструментом [Loyalsoldier/geoip](https://github.com/Loyalsoldier/geoip);
3. **проверяет** (`scripts/validate.py`): каждый код из профиля и шаблона подписки есть в файлах,
   категории не опустели и не уменьшились больше чем на 30%, `xray run -test` проходит с профилем и с шаблоном.
   Если проверка не прошла — ничего не публикуется, пользователи остаются на прошлой версии;
4. публикует в ветку `release` только если файлы изменились, ставит тег `ГГГГММДДЧЧММ`, сбрасывает кэш jsDelivr.

## Как добавить сайт

- Российский сервис открывается плохо через VPN → строка в `data/strata-direct-custom`.
- Сайт заблокирован или не пускает российские IP → строка в `data/strata-tunnel-custom`.
- Рекламный/трекинговый домен → `data/strata-ads-custom`.
- Российский сервис на зарубежном IP → адрес в `geoip/direct-custom.txt`.

Формат строки (v2fly): `domain:example.com` — домен и все поддомены; `full:www.example.com` — ровно этот адрес;
`keyword:example` — подстрока; `regexp:…` — регулярное выражение. Строки с `#` — комментарии.
После коммита в `main` сборка запустится сама; результат — во вкладке **Actions**.

Если сайт есть и в «напрямую», и в «через VPN», победит VPN (в профиле `ProxySites` проверяются раньше `DirectSites`).

## Старые файлы

`release/geosite.dat` и `release/geoip.dat` в ветке `main` — прежняя ручная версия. Новый профиль их не использует;
их можно удалить, когда убедитесь, что ни одна ссылка на них не ведёт.

## Источники и лицензии

См. [NOTICE.md](NOTICE.md).
