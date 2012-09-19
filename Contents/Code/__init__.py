# -*- coding: utf-8 -*-

RE_FLASHVARS    = Regex("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'", Regex.DOTALL)
RE_SWFURL       = Regex("avodSwfUrl = '(.*?)'\;")
RE_IDENT_IP	= Regex('<fcs><ip>(.+?)</ip></fcs>')


import operator
import time

NAME = "Amazon Video on Demand"
ICON = "icon-default.png"
ART = "art-default.jpg"

ASSOC_TAG = "plco09-20"
FIRMWARE = 'WIN%2010,0,181,14%20PlugIn'
DEVICEID = 'A36VLPLQERSUGW1347221081338B0029Z3EH0'

TV_LIST = "/s/ref=sr_nr_n_1?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&ie=UTF8&qid=1334413870&rnid=2858778011"

STREAM_URL = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingUrlSets?format=json&version=1&asin=%s&deviceTypeID=%s&xws-fa-ov=false&token=%s&firmware=%s&customerID=%s&deviceID=%s' # % (values['asin'], values['deviceTypeID'], values['token'], FIRMWARE, values['customerID'], DEVICEID)

####################################################################################################
def Start():
        Plugin.AddPrefixHandler("/video/amazonvod", MainMenu, NAME, ICON, ART)

        Plugin.AddViewGroup("List", viewMode="List", mediaType="items")

        ObjectContainer.title1 = NAME
        ObjectContainer.art = R(ART)
        ObjectContainer.view_group = "List"
        
        DirectoryObject.thumb = R(ICON)

####################################################################################################
def MainMenu():
    oc = ObjectContainer()

    usedSelections={'genre':False, 'network':False}
    
    oc.add(DirectoryObject(key=Callback(MovieList), title="Movies"))

    oc.add(DirectoryObject(key=Callback(TVList, url=TV_LIST, usedSelections=usedSelections), title="TV"))

    oc.add(DirectoryObject(key=Callback(SearchMenu), title="Search"))
    
    oc.add(DirectoryObject(key=Callback(Library), title="Your Library"))

    oc.add(PrefsObject(title=L("Preferences"), thumb=R(ICON)))
    
    return oc

####################################################################################################
def SearchMenu():
    oc = ObjectContainer()

    oc.add(InputDirectoryObject(key=Callback(Search, tvSearch=False), title="Search Movies", summary="Search Amazon Prime for Movies", thumb=R(ICON)))
    oc.add(InputDirectoryObject(key=Callback(Search), title="Search TV Shows", summary="Search Amazon Prime for TV Shows", thumb=R(ICON)))
    
    return oc

####################################################################################################
def Search(query, url = None, tvSearch=True):
    string = "/s/ref=sr_nr_n_0?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Ck%3A"

    string += String.Quote(query, usePlus=True)
    
    if tvSearch:
        string += "%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&keywords="
    else:
        string += "%2Cp_85%3A2470955011%2Cn%3A2858905011&bbn=2858778011&keywords="
    
    string += String.Quote(query, usePlus=True)

    if tvSearch:
        return ResultsList(None, url=string, onePage=True)
    else:
        return ResultsList(None, url=string, onePage=True, tvList = False)


####################################################################################################
def Login():
    x = HTTP.Request('https://www.amazon.com/?tag=%s' % ASSOC_TAG, errors='replace')
    x = HTTP.Request('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG, errors='replace')
    cookies = HTTP.CookiesForURL('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG)

    sessId = None
        
    params = {
        'path': '/gp/homepage.html',
        'useRedirectOnSuccess': '1',
        'protocol': 'https',
        'sessionId': sessId,
        'action': 'sign-in',
        'password': Prefs['password'],
        'email': Prefs['username'],
        'x': '62',
        'y': '11'
    }
    x = HTTP.Request('https://www.amazon.com/gp/flex/sign-in/select.html?ie=UTF8&protocol=https&tag=%s' % ASSOC_TAG,values=params,errors='replace', immediate=True).headers

####################################################################################################
def Library():
    Login()
    oc = ObjectContainer()
    
    oc.add(DirectoryObject(key=Callback(LibrarySpecific, movies=True), title="Movies"))
    oc.add(DirectoryObject(key=Callback(LibrarySpecific, movies=False), title="TV"))
    
    return oc

####################################################################################################    
def LibrarySpecific(movies=True):
    if movies:
        url = "https://www.amazon.com/gp/video/library/movie?show=all"
    else:
        url = "https://www.amazon.com/gp/video/library/tv?show=all"
    
    element = HTML.ElementFromURL(url)
    
    purchasedList = element.xpath('//*[@class="lib-item"]')
    videos = list()
    seasons = list()
    
    for i in range(0, len(purchasedList)):
        asin = purchasedList[i].xpath('//@asin')[0]
        imageLink = purchasedList[i].xpath('//div/a/img/@src')[0]
        title = purchasedList[i].xpath('//*[@class="title"]/a/text()')[0]
        
        if purchasedList[i].xpath('//div/@type')[0] == "movie":    
            videos.append((title, asin, imageLink))
        else:
            seasons.append((title, asin, imageLink))
        
    oc = ObjectContainer()
    
    for i in range(0, len(videos)):
        url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1]
        if movies:
                video = GetVideoObject(
                                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
                                video_type='movie',
                                title=videos[i][0],
                                thumb=videos[i][0]
                                )
                oc.add(video)

        else:
                video = GetVideoObject(
                                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
                                video_type='episode',
                                title=videos[i][0],
                                thumb=videos[i][0]
                                )
                oc.add(video)
    
    for i in range(0, len(seasons)):
        oc.add(DirectoryObject(Key=Callback(TVIndividualSeason, url="https://www.amazon.com/gp/product/" + seasons[i][1]),
                title=seasons[i][0],
                thumb=Resource.ContentsOfURLWithFallback(url=seasons[i][2], fallback=ICON)))

    return oc
    
####################################################################################################
def MovieList(url=None, usedSelections = None):
    oc = ObjectContainer()

    oc.add(InputDirectoryObject(key=Callback(Search, tvSearch=False), title="Search Movies", summary="Search Amazon Prime for Movies", thumb=R(ICON)))

    return oc

####################################################################################################    
def TVList(url=None, usedSelections = None):

    oc = ObjectContainer()
    
    shownUnorganized = False
    
    tvPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    links = tvPage.xpath("//div[@id='refinements']//h2[. = 'TV Show']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'TV Show'])]/li/a/@href")    

    if (len(links) > 0):
        tvShowsLink = links[len(links)-1]
        
        if "sr_sa_p_lbr_tv_series_brow" in tvShowsLink:
            oc.add(DirectoryObject(key=Callback(TVShows, url=tvShowsLink), title="Shows"))
        else:
            oc.add(DirectoryObject(key=Callback(TVShowsNotNice, url=url), title="Shows"))

    else:
        oc.add(DirectoryObject(key=Callback(ResultsList, url=url, onePage=True), title="All TV Shows (Unorganized)"))
        shownUnorganized = True
        
            
    if not usedSelections['genre']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Genre']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Genre'])]/li/a/@href")
        if len(links) > 0:
            genresLink = links[len(links)-1]
        
            if "sr_sa_p_n_theme_browse-bin" in genresLink:
                oc.add(DirectoryObject(key=Callback(TVSubCategories, url=genresLink, category="Genre", usedSelections=usedSelections), title="Genres"))
            else:
                oc.add(DirectoryObject(key=Callback(TVNotNiceSubCategories, url=url, category="Genre", usedSelections=usedSelections), title="Genres"))
            
            
            
    if not usedSelections['network']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Content Provider']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Content Provider'])]/li/a/@href")
        if len(links) > 0:
            networksLink = links[len(links)-1]

            if "sr_sa_p_studio" in networksLink:
                oc.add(DirectoryObject(key=Callback(TVSubCategories, url=networksLink, category="Content Provider", usedSelections=usedSelections), title="Networks"))
            else:
                oc.add(DirectoryObject(key=Callback(TVNotNiceSubCategories, url=url, category="Content Provider", usedSelections=usedSelections), title="Networks"))
    

    if not shownUnorganized:
        oc.add(DirectoryObject(key=Callback(ResultsList, url=url, onePage=True), title="All TV Shows (Unorganized)"))

    return oc
    
####################################################################################################    
def TVSubCategories(url=None, category=None, usedSelections=None):
    if category=='Content Provider':
        usedSelections['network'] = True
        
    if category=='Genre':
        usedSelections['genre'] = True
    
    
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfGenresLinks = tvGenrePage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfGenres = tvGenrePage.xpath("//*[@class='c3_ref refList']//a")
    listOfGenresNames = listOfGenres[0].xpath("//*[@class='refinementLink']/text()")
        
    oc = ObjectContainer()
    
    for i in range(0, len(listOfGenresLinks)):
        oc.add(DirectoryObject(key=Callback(TVList, usedSelections=usedSelections, url=listOfGenresLinks[i]), title=listOfGenresNames[i]))

    return oc

####################################################################################################
def TVNotNiceSubCategories(url=None, category=None, usedSelections=None):
    if category=='Content Provider':
        usedSelections['network'] = True
        
    if category=='Genre':
        usedSelections['genre'] = True


    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    genreList = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + category + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + category + "'])]//*[@class='refinementLink']/text()")
    
    genreLinks = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + category + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + category + "'])]/li/a/@href")
    
    pairs = list()    
    
    for i in range(0, len(genreList)):
        pairs.append((genreList[i], genreLinks[i]))
        
    sortedPairs = sorted(pairs, key=operator.itemgetter(0))
              
    oc = ObjectContainer()
        
    for i in range(0, len(genreList)):
        oc.add(DirectoryObject(key=Callback(TVList, usedSelection=usedSelection, url=sortedPairs[i][1]), title=sortedPairs[i][0]))
    
    return oc

####################################################################################################
def TVShows(url=None):  
    tvShowPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfShowsLinks = tvShowPage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfShows = tvShowPage.xpath("//*[@class='c3_ref refList']//a")
    
    oc = ObjectContainer()
    
    if len(listOfShows) > 0:
        listOfShowsNames = listOfShows[0].xpath("//*[@class='refinementLink']/text()")
    
        for i in range(0, len(listOfShowsLinks)):
            oc.add(DirectoryObject(key=Callback(ResultsList, url=listOfShowsLinks[i], sort=True), title=listOfShowsNames[i]))
    
    return oc
    
####################################################################################################
def TVShowsNotNice(url=None):   
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    showList = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]//*[@class='refinementLink']/text()")
    
    showLinks = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]/li/a/@href")
    
    pairs = list()
    
    
    for i in range(0, len(showList)):
        pairs.append((showList[i], showLinks[i]))
        
    sortedPairs = sorted(pairs, key=operator.itemgetter(0))
              
    oc = ObjectContainer()
        
    for i in range(0, len(showList)):
        oc.add(DirectoryObject(key=Callback(TVList, url=sortedPairs[i][1]), title=sortedPairs[i][0]))
    
    return oc

####################################################################################################
def ResultsList(url = None, onePage=False, tvList = True, sort=False):     
    
    oc = ObjectContainer()

    seasonsPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    seasons = list()
    
    newURL = ""
    
    if (len(seasonsPage.xpath('//*[@class="pagnNext"]')) > 0) and not onePage:
        nextLoopQuit = False
    else:
        nextLoopQuit = True

    
    while True:
        if len(seasonsPage.xpath("//*[@id='atfResults' or @id='btfResults']")) > 0:
            listOfSeasons = seasonsPage.xpath("//*[@id='atfResults' or @id='btfResults']")[0]
    
            listOfSeasonsNames = listOfSeasons.xpath('//*[@class="title"]/a/text()')
            listOfSeasonsLinks = listOfSeasons.xpath('//*[@class="title"]/a/@href')
            listOfSeasonsImages = listOfSeasons.xpath('//*[@class="image"]/a/img/@src')
            
            Log(listOfSeasonsLinks[0].partition('/ref=sr_')[0].rpartition('/dp/')[2])

            for i in range(0, len(listOfSeasonsNames)):
                seasons.append((listOfSeasonsNames[i], listOfSeasonsLinks[i], listOfSeasonsImages[i], listOfSeasonsLinks[i].partition('/ref=sr_')[0].rpartition('/dp/')[2]))

           
            try:
                newURL = seasonsPage.xpath('//*[@id="pagnNextLink"]')[0].xpath('@href')[0]        
            except:
                break
                
            if nextLoopQuit:
                break
        
            
            seasonsPage = HTML.ElementFromURL("http://www.amazon.com" + newURL) 
            
            if (len(seasonsPage.xpath('//*[@class="pagnNext"]')) > 0):
                nextLoopQuit = False
            else:
                nextLoopQuit = True
        else:
            return ObjectContainer(header=NAME, message="Sorry, no results.")
    
    sortedSeasonPairs = seasons
    
    if sort:
        sortedSeasonPairs = sorted(seasons, key=operator.itemgetter(0))


    if tvList:
        for i in range(0, len(sortedSeasonPairs)):
            oc.add(DirectoryObject(key=Callback(TVIndividualSeason, url=sortedSeasonPairs[i][1]), title=sortedSeasonPairs[i][0], thumb=Resource.ContentsOfURLWithFallback(url=sortedSeasonPairs[i][2], fallback=ICON)))
    else:
        for i in range(0, len(sortedSeasonPairs)):
                video = GetVideoObject(
                                url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + sortedSeasonPairs[i][3],
                                video_type='episode',
                                title=sortedSeasonPairs[i][0],
                                thumb=sortedSeasonPairs[i][2]
                                )
                oc.add(video)  

    if onePage and len(newURL) > 0:
        oc.add(DirectoryObject(key=Callback(ResultsList, url=newURL, onePage = True), title="Next Page"))

    return oc
    
####################################################################################################    
def TVIndividualSeason(url = None):
    episodesPage = HTML.ElementFromURL(url)
    
    listOfEpisodesTable = episodesPage.xpath('//*[@class="episodeRow" or @class="episodeRow current"]')
    
    listOfEpisodesTitles = list()
    listOfEpisodesASIN = list()
    listOfEpisodesSummaries = list()
    
    for i in range(0, len(listOfEpisodesTable)):
        listOfEpisodesTitles.append(listOfEpisodesTable[i].xpath('td/div/text()')[0])
        listOfEpisodesASIN.append(listOfEpisodesTable[i].xpath('@asin')[0])
        listOfEpisodesSummaries.append(listOfEpisodesTable[i].xpath('td/div/text()')[1])

    oc = ObjectContainer()
    
    for i in range(0, len(listOfEpisodesTable)):
        video = GetVideoObject(url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + listOfEpisodesASIN[i], video_type='episode', title=listOfEpisodesTitles[i],
                               summary=listOfEpisodesSummaries[i])
        oc.add(video)

    return oc

####################################################################################################
def GetVideoObject(url, video_type, title='', summary='', thumb='None'):
        if video_type == "episode":
                return EpisodeObject(
                        key = url,
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
                        key = url,
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

####################################################################################################
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

        #rtmp_url = streams[-1]['url']
	
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

####################################################################################################
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

####################################################################################################