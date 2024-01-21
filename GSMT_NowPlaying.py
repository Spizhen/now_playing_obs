#!/usr/bin/env python
# ==============================================================================
import site

import obspython as obs

import winsdk.windows.media.control as media_control
import winsdk.windows.storage.streams as streams
import asyncio
import os

site.main()

enabled = False
check_frequency = 1000  # ms
debug_mode = True

show_title = True
show_artist = True
show_cover = True

last_title = ""
title_layer = ""
artist_layer = ""
cover_layer = ""

current_image = None
image_folder = os.path.dirname(__file__)

image_directory = ""
retry_load_cover = False


def script_defaults(settings):
    if debug_mode:
        print("Calling defaults settings")

    obs.obs_data_set_default_bool(settings, "enabled", enabled)
    obs.obs_data_set_default_bool(settings, "debug_mode", debug_mode)
    obs.obs_data_set_default_int(settings, "check_frequency", check_frequency)
    # obs.obs_data_set_default_bool(settings, "show_title", show_title)
    # obs.obs_data_set_default_bool(settings, "show_artist", show_artist)
    # obs.obs_data_set_default_bool(settings, "show_cover", show_cover)
    obs.obs_data_set_default_string(settings, "title_layer", title_layer)
    obs.obs_data_set_default_string(settings, "artist_layer", artist_layer)
    obs.obs_data_set_default_string(settings, "cover_layer", cover_layer)


def script_description():
    if debug_mode:
        print("Calling description")

    return (
        "<b>Music Now Playing</b>"
        + "<hr>"
        + "Display current playing song from Windows Global System Media Transport"
        + "<br/>"
        + "<hr>"
    )


def script_load(_):
    if debug_mode:
        print("Loaded script.")


def script_properties():
    if debug_mode:
        print("Loaded properties.")

    props = obs.obs_properties_create()

    obs.obs_properties_add_path(
        props, "image_directory", "Directory for cover", obs.OBS_PATH_DIRECTORY, "", ""
    )

    create_obs_field_selector(props, "title_layer", "Layer with song title", "text")
    create_obs_field_selector(props, "artist_layer", "Layer with song artist", "text")
    create_obs_field_selector(props, "cover_layer", "Layer with song cover", "image")

    # obs.obs_properties_add_bool(props, "show_title", "Update song title")
    # obs.obs_properties_add_bool(props, "show_artist", "Update song artist")
    # obs.obs_properties_add_bool(props, "show_cover", "Update song cover")

    obs.obs_properties_add_int(
        props, "check_frequency", "Check frequency (ms)", 1000, 10000, 100
    )
    obs.obs_properties_add_bool(props, "debug_mode", "Debug Mode")
    obs.obs_properties_add_bool(props, "enabled", "Enabled")

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
    # global show_title
    # global show_artist
    # global show_cover
    global title_layer
    global artist_layer
    global cover_layer
    global image_directory

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
        obs.timer_add(get_song_info, check_frequency)
    else:
        if enabled:
            if debug_mode:
                print("Disabled song timer.")

        enabled = False
        obs.timer_remove(get_song_info)

    debug_mode = obs.obs_data_get_bool(settings, "debug_mode")
    # show_artist = obs.obs_data_get_bool(settings, "show_artist")
    # show_cover = obs.obs_data_get_bool(settings, "show_cover")
    # show_title = obs.obs_data_get_bool(settings, "show_title")
    title_layer = obs.obs_data_get_string(settings, "title_layer")
    artist_layer = obs.obs_data_get_string(settings, "artist_layer")
    cover_layer = obs.obs_data_get_string(settings, "cover_layer")
    image_directory = obs.obs_data_get_string(settings, "image_directory")
    check_frequency = obs.obs_data_get_int(settings, "check_frequency")


def update_song(artist="", title="", cover=""):
    global image_directory
    global last_title

    if artist != "" or title != "":
        last_title = title + artist

        if debug_mode:
            print("Now Playing : " + artist + " / " + title)

        settings = obs.obs_data_create()

        obs.obs_data_set_string(settings, "text", title)
        title = obs.obs_get_source_by_name(title_layer)
        obs.obs_source_update(title, settings)

        obs.obs_data_set_string(settings, "text", artist)
        artist = obs.obs_get_source_by_name(artist_layer)
        obs.obs_source_update(artist, settings)

        obs.obs_data_set_string(settings, "file", image_directory + "/" + cover)
        cover = obs.obs_get_source_by_name(cover_layer)
        obs.obs_source_update(cover, settings)

        obs.obs_data_release(settings)

        obs.obs_source_release(title)
        obs.obs_source_release(artist)
        obs.obs_source_release(cover)


def get_song_info():
    load_data = get_current_playing_song()
    asyncio.run(load_data)


async def get_current_playing_song():
    global last_title
    global retry_load_cover

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

        title = media_info.title
        artist = media_info.artist

        if retry_load_cover == False or (last_title != title + artist):
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
                    print(f"Album cover saved as {file_name}")
                    retry_load_cover = True
                    cover = file_name
                else:
                    print("No album cover available.")
                    retry_load_cover = False
            else:
                print("No album cover available.")
    else:
        print("No song is currently playing.")

    try:
        update_song(artist, title, cover)
    except:
        update_song()
    finally:
        retry_load_cover == False
