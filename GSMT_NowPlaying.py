#!/usr/bin/env python
# ==============================================================================

import obspython as obs

import winsdk.windows.media.control as media_control
import winsdk.windows.storage.streams as streams
import asyncio
import os

enabled = False
check_frequency = 5  # ms
debug_mode = False

last_title = ""
title_layer = ""
artist_layer = ""
cover_layer = ""

cover = ""
show_cover = False
current_image = None
image_folder = os.path.dirname(__file__)

image_directory = ""


def script_defaults(settings):
    if debug_mode:
        print("Calling defaults settings")

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug_mode", debug_mode)
    obs.obs_data_set_default_int(settings, "check_frequency", check_frequency)
    obs.obs_data_set_default_bool(settings, "show_cover", show_cover)
    obs.obs_data_set_default_string(settings, "title_layer", title_layer)
    obs.obs_data_set_default_string(settings, "artist_layer", artist_layer)
    obs.obs_data_set_default_string(settings, "cover_layer", cover_layer)


def script_description():
    if debug_mode:
        print("Calling description")

    return (
        "<b>Now Playing</b>"
        + "<hr>"
        + "Подгружает информацию о воcпроизводимой музыке в выбранные источники ниже."
        + "<br/>"
        + "Информация подтягивается напрямую из медиаплеера Windows, в который попадает практически любой медиаконтент который в данный момент воспроизводится в системе."
        + "<hr>"
    )


def script_load(_):
    if debug_mode:
        print("Loaded script.")
    script_update(_)


def on_property_modified(props, property, settings):
    # hint: https://github.com/Mr-Mmhhmm-OBS/OBS-Event-Manager/tree/master

    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "cover_layer"), show_cover is True
    )
    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "image_directory_hint"), show_cover is True
    )
    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "image_directory"), show_cover is True
    )

    return True


def script_properties():
    if debug_mode:
        print("Loaded properties.")

    props = obs.obs_properties_create()

    obs.obs_properties_add_bool(props, "debug_mode", "Больше деталей в журнале")

    create_obs_field_selector(props, "title_layer", "Источник вывода названия", "text")
    create_obs_field_selector(
        props, "artist_layer", "Источник вывода исполнителя", "text"
    )

    p_show_cover = obs.obs_properties_add_bool(
        props, "show_cover", "Обновлять обложку "
    )
    obs.obs_property_set_modified_callback(p_show_cover, on_property_modified)

    warning_text = "Обязательное выберите папку хранения файла обложки!"

    obs.obs_property_set_long_description(
        p_show_cover,
        warning_text,
    )

    p_image_directory_hint = obs.obs_properties_add_text(
        props,
        "image_directory_hint",
        warning_text,
        obs.OBS_TEXT_INFO,
    )

    obs.obs_property_set_modified_callback(p_image_directory_hint, on_property_modified)

    p_image_directory = obs.obs_properties_add_path(
        props,
        "image_directory",
        "Папка, где хранится файл обложки",
        obs.OBS_PATH_DIRECTORY,
        "",
        "",
    )
    obs.obs_property_set_modified_callback(p_image_directory, on_property_modified)

    create_obs_field_selector(props, "cover_layer", "Источник вывода обложки", "image")

    obs.obs_properties_add_int_slider(
        props, "check_frequency", "Частота обновления (сек)", 1, 15, 1
    )

    obs.obs_properties_add_bool(props, "enabled", "Скрипт включен")

    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "cover_layer"), show_cover is True
    )
    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "image_directory"), show_cover is True
    )
    obs.obs_property_set_visible(
        obs.obs_properties_get(props, "image_directory_hint"), show_cover is True
    )

    return props


def create_obs_field_selector(props, field_code, field_name, field_type):
    p = obs.obs_properties_add_list(
        props,
        field_code,
        field_name,
        obs.OBS_COMBO_TYPE_EDITABLE,
        obs.OBS_COMBO_FORMAT_STRING,
    )

    sources = obs.obs_enum_sources()

    if sources:
        for source in sources:
            source_id = obs.obs_source_get_unversioned_id(source)
            if field_type == "text":
                if source_id in ("text_gdiplus", "text_ft2_source"):
                    name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(p, name, name)
            elif field_type == "image":
                if source_id in ("image_source"):
                    name = obs.obs_source_get_name(source)
                    obs.obs_property_list_add_string(p, name, name)
    obs.source_list_release(sources)
    return


def script_save(settings):
    if debug_mode:
        print("Saved properties.")

    script_update(settings)


def script_unload():
    if debug_mode:
        print("Unloaded script.")

    obs.timer_remove(get_song_info)


def script_update(settings):
    global enabled
    global debug_mode
    global check_frequency
    global show_cover
    global title_layer
    global artist_layer
    global cover_layer
    global image_directory

    check_frequency = check_frequency * 1000

    if debug_mode:
        print("Updated properties.")

    if (obs.obs_data_get_int(settings, "check_frequency") != check_frequency) or (
        obs.obs_data_get_bool(settings, "enabled") is False
    ):
        obs.timer_remove(get_song_info)

    if obs.obs_data_get_bool(settings, "enabled") is True:
        if not enabled:
            if debug_mode:
                print("Enabled song timer.")

        enabled = True
        check_frequency = obs.obs_data_get_int(settings, "check_frequency") * 1000
        obs.timer_add(get_song_info, check_frequency)
    else:
        if enabled:
            if debug_mode:
                print("Disabled song timer.")

        enabled = False
        check_frequency = obs.obs_data_get_int(settings, "check_frequency") * 1000
        obs.timer_remove(get_song_info)

    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    show_cover = obs.obs_data_get_bool(settings, "show_cover")
    title_layer = obs.obs_data_get_string(settings, "title_layer")
    artist_layer = obs.obs_data_get_string(settings, "artist_layer")
    cover_layer = obs.obs_data_get_string(settings, "cover_layer")
    image_directory = obs.obs_data_get_string(settings, "image_directory")

    if debug_mode:
        print("Selected image directory - " + image_directory)


def update_song(artist="", title="", cover=""):
    global image_directory
    global last_title

    if artist != "" or title != "":
        last_title = title + artist

        if debug_mode:
            print("Now Playing : " + artist + " / " + title)

        settings = obs.obs_data_create()

        # Обновляем только если источники существуют
        if title_layer:
            obs.obs_data_set_string(settings, "text", title)
            title_source = obs.obs_get_source_by_name(title_layer)
            if title_source:
                obs.obs_source_update(title_source, settings)
                obs.obs_source_release(title_source)

        if artist_layer:
            obs.obs_data_set_string(settings, "text", artist)
            artist_source = obs.obs_get_source_by_name(artist_layer)
            if artist_source:
                obs.obs_source_update(artist_source, settings)
                obs.obs_source_release(artist_source)

        if cover_layer and cover and image_directory:
            obs.obs_data_set_string(settings, "file", image_directory + "/" + cover)
            cover_source = obs.obs_get_source_by_name(cover_layer)
            if cover_source:
                obs.obs_source_update(cover_source, settings)
                obs.obs_source_release(cover_source)

        obs.obs_data_release(settings)


def get_song_info():
    try:
        load_data = get_current_playing_song()
        asyncio.run(load_data)
    except Exception as e:
        if debug_mode:
            print(f"Error in get_song_info: {e}")


async def get_current_playing_song():
    global show_cover
    global last_title
    global cover
    global image_directory

    # Инициализируем переменные по умолчанию
    artist = ""
    title = ""
    cover_file = ""

    try:
        if debug_mode:
            print("Check audio sessions ")

        # Get the current session manager
        sessions = (
            await media_control.GlobalSystemMediaTransportControlsSessionManager.request_async()
        )

        # Get the current session
        current_session = sessions.get_current_session()
        if current_session:
            # Get the media information
            media_info = await current_session.try_get_media_properties_async()

            if media_info:
                title = media_info.title if media_info.title else ""
                artist = media_info.artist if media_info.artist else ""

                if last_title != title + artist:
                    if show_cover is True and image_directory != "":
                        try:
                            # Attempt to get the thumbnail
                            thumbnail_ref = media_info.thumbnail
                            if thumbnail_ref:
                                stream_with_content = await thumbnail_ref.open_read_async()
                                size = stream_with_content.size
                                if size:
                                    reader = streams.DataReader(stream_with_content)
                                    await reader.load_async(size)
                                    data = reader.read_buffer(size)
                                    # Save the image data to a file
                                    file_name = f"thumb.png".replace("/", "_").replace("\\", "_")
                                    with open(image_directory + "/" + file_name, "wb") as file:
                                        file.write(data)

                                    if debug_mode:
                                        print(f"Album cover saved as {file_name}")
                                    cover_file = file_name
                                else:
                                    if debug_mode:
                                        print("No album cover available.")
                            else:
                                if debug_mode:
                                    print("No album cover available.")
                        except Exception as e:
                            if debug_mode:
                                print(f"Error saving cover: {e}")
            else:
                if debug_mode:
                    print("No media info available.")
        else:
            if debug_mode:
                print("No song is currently playing.")

    except Exception as e:
        if debug_mode:
            print(f"Error getting current playing song: {e}")

    # Обновляем информацию о песне
    try:
        update_song(artist, title, cover_file)
    except Exception as e:
        if debug_mode:
            print(f"Error updating song: {e}")