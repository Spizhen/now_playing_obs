# Now Playing script for OBS (for Windows OS only)

Now Playing - это скрипт для OBS, написанный на Python, который обновляет слои, которые вы укажете в настройках OBS в рельном времени текущей песней, воспроизводимой медиаплеером.

Работает только с ОС Windows!

## Требования

- [OBS (Open Broadcaster Software)](https://obsproject.com/ru)
- [Python](https://www.python.org/) 3.11.7 (другие версии не тестировались)
- [Python Windows SDK](https://pypi.org/project/winsdk/)

## Установка и настройка (подробно)

- Скачиваем и устанавливаем Python для Windows ([get here](https://www.python.org/downloads/release/python-3117/)). После запуска установщика обязательно поставьте галочку `Add Python to PATH`, далее можно воспользоваться стандартной установкой. После завершения установки необъодимо перезагрузить компьютер, чтобы OBS в дальнейшем понимал, что Python устанволен в системе.
- Далее нужно установить `winsdk`. Для этого нужно открыть комнадную строку. Самый простой способ нажать `Win + R`, написать `cmd.exe` и нажать кнопку `OK`. После этого откроется командная строка Windows. Копируем `pip install winsdk`, в командной строке в любом месте жмем правую кнопку мыши и жмем энтер. Если все прошло успешно, вы увидите сообщение `Successfully installed winsdk`.
- Теперь надо получить путь установки Python (понадобится при настройке OBS). Для этого в этом же окне вставьте (правой мышью) следующий текст `python -c "import sys; import os; print(os.path.dirname(sys.executable))"` и нажмите ентер. Если все прошло успешно, вы увидите похожее сообщение `C:\Users\username\AppData\Local\Programs\Python\Python311`. Скопируйте его (тоже правой мышью), оно понадобится нам чуть позже.
- Открываем OBS. Создаем два текстовых слоя (Текст GDI+) и один слой Изображение. Ставим и настраиваем их как нужно на свой вкус (можно потом).
- Жмем `Сервис -> Скрипты`. Переходим во вторую вкладку `Настройки Python` и в строке путь установки, вставляем скопированный текст из командной строки. Если все прошло успешно, под строкой пути будет написано "Загружена версия Pytnon 3.xx". Возвращаемся на первую вкладку.
- Скачиваем проект и распаковываем его куда-нибудь на ПК, но куда-нибудь подальше, чтобы не удалить случайно, например в "Мои Документы". Возвращаемся в OBS и жмем плюсик. Находим папку куда разархивировали проект и выбираем файл `GSMT_NowPlaying.py`.
- Если скрипт загрузился, справа появятся настройки скрипта.
- Тут вам нужно выбрать папку куда будет загружаться обложка песни. Текстовый слой для заголовка, текстовый слой для исполнителя, и слой Изображения для обложки. Ставим галочку Enabled, закрываем окно.
- Включаем музыку. Готово!

## Связанные проекты

- [now_playing](https://github.com/rsp4jack/now_playing) with Pywin32
- [now playing for Rainmeter](https://forum.rainmeter.net/viewtopic.php?t=37088&start=50#p219668)

## Лицензия

[MIT](https://choosealicense.com/licenses/mit/)