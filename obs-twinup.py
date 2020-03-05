#!/usr/bin/env python

import json
import obspython as obs
import urllib3

url_api = ""
headers_api = {}
account_id = ""
source_lf = ""
source_st = ""
source_sc = ""
http = urllib3.PoolManager()

def update_last_follower():
    global url_api
    global headers_api
    global account_id
    global source_lf
    source = obs.obs_get_source_by_name(source_lf)
    if source is not None:
        request = http.request("GET", url_api + "users/follows?first=1&to_id=" + account_id, headers = headers_api)
        username = json.loads(request.data.decode("utf-8"))["data"][0]["from_name"]
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", username)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def update_stream_title(title):
    global source_st
    source = obs.obs_get_source_by_name(source_st)
    if source is not None:
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", title)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def update_stream_category(game_id):
    global url_api
    global headers_api
    global source_sc
    source = obs.obs_get_source_by_name(source_sc)
    if source is not None:
        request = http.request("GET", url_api + "games?id=" + game_id, headers = headers_api)
        category = json.loads(request.data.decode("utf-8"))["data"][0]["name"]
        settings = obs.obs_data_create()
        obs.obs_data_set_string(settings, "text", category)
        obs.obs_source_update(source, settings)
        obs.obs_data_release(settings)
        obs.obs_source_release(source)

def update_stream_infos():
    global url_api
    global headers_api
    global account_id
    request = http.request("GET", url_api + "streams?first=1&user_id=" + account_id, headers = headers_api)
    response = json.loads(request.data.decode("utf-8"))["data"]
    if len(response) == 1:
        update_stream_title(response[0]["title"])
        update_stream_category(response[0]["game_id"])
        
def update_infos():
    update_last_follower()
    update_stream_infos()

def update_pressed(props, prop):
    update_infos()

# ------------------------------------------------------------------------------

def script_defaults(settings):
    obs.obs_data_set_default_string(settings, "url", "https://api.twitch.tv/helix/")
    obs.obs_data_set_default_int(settings, "interval", 30)

def script_description():
    return "Updates some text sources with last twitch follower, stream title and stream category.\n\nBy kholo"

def script_properties():
    props = obs.obs_properties_create()
    obs.obs_properties_add_text(props, "url", "Twitch API URL", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "client", "Twitch Client ID", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_text(props, "account", "Twitch Account ID", obs.OBS_TEXT_DEFAULT)
    obs.obs_properties_add_int(props, "interval", "Update Interval (seconds)", 5, 3600, 1)
    p1 = obs.obs_properties_add_list(props, "source_lf", "Source: Last follower", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    p2 = obs.obs_properties_add_list(props, "source_st", "Source: Stream title", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    p3 = obs.obs_properties_add_list(props, "source_sc", "Source: Stream category", obs.OBS_COMBO_TYPE_EDITABLE, obs.OBS_COMBO_FORMAT_STRING)
    sources = obs.obs_enum_sources()
    if sources is not None:
        for source in sources:
            source_id = obs.obs_source_get_id(source)
            if source_id != "text_gdiplus" and source_id != "text_ft2_source" and source_id != "text_gdiplus_v2" and source_id != "text_ft2_source_v2":
                continue
            name = obs.obs_source_get_name(source)
            obs.obs_property_list_add_string(p1, name, name)
            obs.obs_property_list_add_string(p2, name, name)
            obs.obs_property_list_add_string(p3, name, name)
    obs.obs_properties_add_button(props, "update", "Update Now", update_pressed)
    return props

def script_update(settings):
    global url_api
    global headers_api
    global account_id
    global source_lf
    global source_st
    global source_sc
    url_api = obs.obs_data_get_string(settings, "url")
    headers_api = {"Client-ID": obs.obs_data_get_string(settings, "client_id")}
    account_id = obs.obs_data_get_string(settings, "account_id")
    interval = obs.obs_data_get_int(settings, "interval")
    source_lf = obs.obs_data_get_string(settings, "source_lf")
    source_st = obs.obs_data_get_string(settings, "source_st")
    source_sc = obs.obs_data_get_string(settings, "source_sc")
    obs.timer_remove(update_infos)
    if url_api != "" and headers_api != {} and account_id != "" and source_lf != "" and source_st != "" and source_sc != "":
        obs.timer_add(update_infos, interval * 1000)
