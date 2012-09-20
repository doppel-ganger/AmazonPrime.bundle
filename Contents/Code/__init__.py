#   Copyright 2012 Josh Kearney
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

RE_FLASHVARS    = Regex("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'", Regex.DOTALL)
RE_SWFURL       = Regex("avodSwfUrl = '(.*?)'\;")
RE_IDENT_IP	= Regex('<fcs><ip>(.+?)</ip></fcs>')

import operator
import time


NAME = "Amazon Prime Instant Videos"

ICON = "icon-default.png"
ICON_SEARCH = "icon-search.png"
ICON_PREFS = "icon-prefs.png"
ART = "art-default.jpg"

ASSOC_TAG = "plco09-20"
FIRMWARE = 'WIN%2010,0,181,14%20PlugIn'
DEVICEID = 'A36VLPLQERSUGW1347221081338B0029Z3EH0'

AMAZON_URL = "https://www.amazon.com"
#STREAM_URL = "http://www.amazon.com/gp/video/streaming/mini-mode.html?asin="
STREAM_URL = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingUrlSets?format=json&version=1&asin=%s&deviceTypeID=%s&xws-fa-ov=false&token=%s&firmware=%s&customerID=%s&deviceID=%s' # % (values['asin'], values['deviceTypeID'], values['token'], FIRMWARE, values['customerID'], DEVICEID)

LIBRARY_URL = AMAZON_URL + "/gp/video/library/%s?show=all"
MOVIES_URL = AMAZON_URL + "/s/ref=PIVHPBB_Categories_MostPopular?rh=n%3A2858905011%2Cp_85%3A2470955011"
TV_URL = AMAZON_URL + "/s/ref=lp_2864549011_nr_p_85_0?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Cn%3A2864549011%2Cp_85%3A2470955011"
SEARCH_URL = AMAZON_URL + "/s/ref=sr_nr_p_85_0?rh=i:aps,p_85:1&keywords=%s"


def Login():
    x = HTTP.Request(AMAZON_URL + "/?tag=%s" % ASSOC_TAG, errors="replace")
    x = HTTP.Request(AMAZON_URL + "/gp/sign-in.html?tag=%s" % ASSOC_TAG, errors="replace")

    cookies_url = AMAZON_URL + "/gp/sign-in.html?tag=%s" % ASSOC_TAG
    cookies = HTTP.CookiesForURL(cookies_url)

    params = {
        "path": "/gp/homepage.html",
        "useRedirectOnSuccess": "1",
        "protocol": "https",
        "sessionId": None,
        "action": "sign-in",
        "password": Prefs["password"],
        "email": Prefs["username"],
        "x": '62',
        "y": '11'
    }

    x = HTTP.Request(AMAZON_URL + "/gp/flex/sign-in/select.html?ie=UTF8&protocol=https&tag=%s" % ASSOC_TAG, values=params, errors="replace", immediate=True).headers


def Start():
    Plugin.AddPrefixHandler("/video/amazonprime", MainMenu, NAME, ICON, ART)
    Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

    ObjectContainer.title1 = NAME
    ObjectContainer.art = R(ART)
    ObjectContainer.view_group = "List"

    DirectoryObject.thumb = R(ICON)


def MainMenu():
    Login()

    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(Browse, video_type="movies", match_pattern="//div[contains(@id, \"result_\")]"), title="Browse Movies"))
    oc.add(DirectoryObject(key=Callback(Browse, video_type="tv", match_pattern="//div[contains(@id, \"result_\")]"), title="Browse TV"))
    oc.add(DirectoryObject(key=Callback(Library), title="Your Library"))
    oc.add(DirectoryObject(key=Callback(SearchMenu), title="Search", thumb=R(ICON_SEARCH)))
    oc.add(PrefsObject(title=L("Preferences"), thumb=R(ICON_PREFS)))

    return oc


def SearchMenu():
    oc = ObjectContainer()

    oc.add(InputDirectoryObject(key=Callback(Search, video_type="movies"), title="Search Movies", prompt="Search for a Movie", thumb=R(ICON_SEARCH)))
    oc.add(InputDirectoryObject(key=Callback(Search, video_type="tv"), title="Search TV", prompt="Search for a TV show", thumb=R(ICON_SEARCH)))

    return oc


def Browse(video_type, match_pattern, is_library=False, query=None):
    if query:
        query = query.replace(" ", "%20")
        browse_url = SEARCH_URL % query
    elif is_library:
        browse_url = LIBRARY_URL % video_type
    elif video_type == "movies":
        browse_url = MOVIES_URL
    else:
        browse_url = TV_URL

    html = HTML.ElementFromURL(browse_url)
    video_list = html.xpath(match_pattern)

    verify_ownership = True if is_library else False

    videos = []
    seasons = []

    # NOTE(jk0): Determine whether or not we're looking at movies or TV shows
    # which contain multiple episodes.
    for item in video_list:
        # TODO(jk0): Clean up this parsing mess.
        if is_library:
            item_asin = item.attrib["asin"].strip()
            item_title = list(item)[1][0].text.strip()
            item_image_link = list(item)[0][0][0].attrib["src"].strip()
        elif query:
            item_asin = item.attrib["name"].strip()
            item_title = list(item)[1][0][0].text.strip()
            item_image_link = list(item)[0][0][0].attrib["src"].strip()
        else:
            item_asin = item.attrib["name"].strip()
            item_title = list(item)[2][0][0].text.strip()
            item_image_link = list(item)[1][0][0].attrib["src"].strip()

        if video_type == "movies":
            videos.append((item_title, item_asin, item_image_link))
        else:
            seasons.append((item_title, item_asin, item_image_link))

    if query and (len(videos) == 0 and len(seasons) == 0):
        return MessageContainer("No Results", "No results were found for '%s'." % query)

    oc = ObjectContainer()

    # NOTE(jk0): Determine whether or not we're watching a movie or a TV show
    # since they require different video object types.
    for video in videos:
        video_url = STREAM_URL + video[1]

        if video_type == "movies":
            oc.add(GetVideoObject(url=video_url, video_type="movie", title=video[0], thumb_url=video[2]))
        else:
            oc.add(GetVideoObject(url=video_url, video_type="episode", title=video[0], thumb_url=video[2]))

    # NOTE(jk0): TV shows contain multiple episodes, so handle them
    # appropriately.
    for season in seasons:
        season_url = AMAZON_URL + "/gp/product/" + season[1]

        thumb = Resource.ContentsOfURLWithFallback(url=season[2], fallback=ICON)

        oc.add(DirectoryObject(key=Callback(TVSeason, season_url=season_url, season_thumb_url=season[2], verify_ownership=verify_ownership), title=season[0], thumb=thumb))

    return oc


def Library():
    oc = ObjectContainer()

    oc.add(DirectoryObject(key=Callback(Browse, video_type="movies", match_pattern="//*[@class=\"lib-item\"]", is_library=True), title="Movies"))
    oc.add(DirectoryObject(key=Callback(Browse, video_type="tv", match_pattern="//*[@class=\"lib-item\"]", is_library=True), title="TV"))

    return oc


def Search(query, video_type):
    return Browse(video_type=video_type, match_pattern="//div[contains(@id, \"result_\")]", query=query)


def TVSeason(season_url, season_thumb_url, verify_ownership):
    html = HTML.ElementFromURL(season_url)
    episode_list = html.xpath("//*[@class=\"episodeRow\" or @class=\"episodeRow current\"]")

    episodes = []

    for episode in episode_list:
        if not verify_ownership or list(episode)[7].text == "Owned":
            # TODO(jk0): Clean up this parsing mess.
            episode_asin = episode.xpath("@asin")[0].strip()
            episode_title = episode.xpath("td/div/text()")[0].strip()
            episode_summary = episode.xpath("td/div/text()")[1].strip()

            episodes.append((episode_asin, episode_title, episode_summary))

    oc = ObjectContainer()

    for episode in episodes:
        episode_url = STREAM_URL + episode[0]

        oc.add(GetVideoObject(url=episode_url, video_type="episode", title=episode[1], summary=episode[2], thumb_url=season_thumb_url))

    return oc


#def GetVideoObject(url, video_type, title=None, summary=None, thumb_url=None):
#    thumb = Resource.ContentsOfURLWithFallback(url=thumb_url, fallback=ICON)
#
#    if video_type == "episode":
#        return EpisodeObject(key=WebVideoURL(url), rating_key=url, title=title, summary=summary, thumb=thumb)
#    else:
#        return MovieObject(key=WebVideoURL(url), rating_key=url, title=title, summary=summary, thumb=thumb)
def GetVideoObject(url, video_type, title='', summary='', thumb='None'):
        if video_type == "episode":
                return EpisodeObject(
                        key = Callback(VideoDetails, url),
                        rating_key = url,
                        items=[
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=2500))],
                                        bitrate = 2500
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=1328))],
                                        bitrate = 1328
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=996))],
                                        bitrate = 996
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=664))],
                                        bitrate = 664
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=348))],
                                        bitrate = 348
                                )
                        ],
                        title = title,
                        summary = summary,
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
                )
        else:
                return MovieObject(
                        key = Callback(VideoDetails, url),
                        rating_key = url,
                        items=[
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=2500))],
                                        bitrate = 2500
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=1328))],
                                        bitrate = 1328
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=996))],
                                        bitrate = 996
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=664))],
                                        bitrate = 664
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=348))],
                                        bitrate = 348
                                )
                        ],
                        title = title,
                        summary = summary,
                        thumb = Resource.ContentsOfURLWithFallback(url=thumb, fallback=ICON)
                )

#This *looks* superfluous but is apparently the proper way to do it when working without an URL Service#
def VideoDetails(url):
    oc = ObjectContainer()

    oc.add(VideoClipObject(
        key = Callback(VideoDetails, url = url),
        rating_key = url,
        items=[
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=2500))],
                                        bitrate = 2500
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=1328))],
                                        bitrate = 1328
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=996))],
                                        bitrate = 996
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=664))],
                                        bitrate = 664
                                ),
                                MediaObject(
                                        parts = [PartObject(key=Callback(PlayVideo, url=url, bitrate=348))],
                                        bitrate = 348
                                )
                        ],

  return oc
  

@indirect
def PlayVideo(url, bitrate):
    BITRATES = [348, 664, 996, 1328, 2500]
	index = BITRATES.index(bitrate)
        swfUrl, values, owned, cookies = GetFlashVars(url)
        values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
        streamUrl =  STREAM_URL % (values['asin'], values['deviceTypeID'], values['token'], FIRMWARE, values['customerID'], DEVICEID)
        stream_data = JSON.ObjectFromURL(streamUrl, headers={'Cookie':cookies})
        streams = stream_data['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
	while index > -1:
		try:
			rtmp_url = streams[index]['url']
			try:
				if streams[index]['drm'] != '':
					Log('This video contains DRM and may not play.')
			except:
				pass
			break
		except:
			index = index -1
	
	protocolSplit = rtmp_url.split("://")
	pathSplit   = protocolSplit[1].split("/")
	hostname    = pathSplit[0]
	appName     = protocolSplit[1].split(hostname + "/")[1].split('/')[0]    
	streamAuth  = rtmp_url.split(appName+'/')[1].split('?')
	stream      = streamAuth[0].replace('.mp4','')
	auth        = streamAuth[1]
	identurl = 'http://'+hostname+'/fcs/ident'
	ident = HTTP.Request(identurl).content
	ip = RE_IDENT_IP.findall(ident)[0]
	basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
	
    return IndirectResponse(VideoClipObject, key=RTMPVideoURL(url=basertmp, clip=stream, swf_url=swfUrl))


def GetFlashVars(url):
        Login()
        cookies = HTTP.CookiesForURL(url)
        cookies = cookies + ' x-main="MZsjMdQ1GEH@1rVszcqrPHY4Gh91Wl@v";'
        showpage = HTTP.Request(url, headers={'Cookie':cookies}, follow_redirects=False).content
        flashVars = RE_FLASHVARS.findall(showpage)
        flashVars =(flashVars[0][0] + flashVars[0][1]).split('&')
        swfUrl = RE_SWFURL.findall(showpage)[0]
        values={'token'          :'',
                'deviceTypeID'   :'A13Q6A55DBZB7M',
                'version'        :'1',
                'firmware'       :'1',       
                'customerID'     :'',
                'format'         :'json',
                'deviceID'       :'',
                'asin'           :''      
                }
        if '<div class="avod-post-purchase">' in showpage:
                owned=True
        else:
                owned=False
        for item in flashVars:
                item = item.split('=')
                if item[0]      == 'token':
                        values[item[0]]         = item[1]
                elif item[0]    == 'customer':
                        values['customerID']    = item[1]
                elif item[0]    == 'ASIN':
                        values['asin']          = item[1]
                elif item[0]    == 'pageType':
                        values['pageType']      = item[1]        
                elif item[0]    == 'UBID':
                        values['UBID']          = item[1]
                elif item[0]    == 'sessionID':
                        values['sessionID']     = item[1]
                elif item[0]    == 'userAgent':
                        values['userAgent']     = item[1]
        return swfUrl, values, owned, cookies
