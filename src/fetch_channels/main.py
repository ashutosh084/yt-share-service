import requests
import traceback
import json

from fastapi import FastAPI

app = FastAPI()

def filter_channels(channels):
    try:
        return [channel for channel in channels["contents"]["twoColumnSearchResultsRenderer"]["primaryContents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"] if "channelRenderer" in channel]
    except Exception as e:
        traceback.print_exc()
        
def prepare_response(channels):
    try:
        return [{"channelId": channel.get("channelRenderer", {}).get("channelId"), 
                "thumbnail": channel.get("channelRenderer", {}).get("thumbnail", {}).get("thumbnails", [{}])[0].get("url"),
                "navigationEndpoint": channel.get("channelRenderer", {}).get("navigationEndpoint", {}).get("browseEndpoint", {}).get("canonicalBaseUrl", {})} for channel in channels]
    except Exception as e:
        traceback.print_exc()

def get_channels(url, q):

    try:
        with open("./src/fetch_channels/body.json") as f:
            body = json.load(f)
        with open("./src/fetch_channels/cookies.json") as c:
            cookies = json.load(c)
        body["query"] = q
        request = requests.post(url=url,json=body, cookies=cookies)
        return request.json()
    except Exception as e:
        traceback.print_exc()
        return e
    
def fetch_channels(q: str):
    try:
        url = f"https://www.youtube.com/youtubei/v1/search?prettyPrint=false"
        channels = get_channels(url, q)
        return prepare_response(filter_channels(channels))
    except Exception as e:
        traceback.print_exc()
        return e