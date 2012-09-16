# -*- coding: utf-8 -*-
#import re
import operator
import urllib
import time
import cookielib
from base64 import b64decode

NAME = "Amazon Video on Demand"
ICON = "icon-default.png"
ART = "art-default.jpg"

ASSOC_TAG = "plco09-20"

TV_LIST = "/s/ref=sr_nr_n_1?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&ie=UTF8&qid=1334413870&rnid=2858778011"

####################################################################################################
def Start():
	Plugin.AddPrefixHandler("/video/amazonvod", MainMenu, NAME, ICON, ART)

	Plugin.AddViewGroup("List", viewMode="List", mediaType="items")


	#MediaContainer.title1 = NAME
	#MediaContainer.art = R(ART)
	#MediaContainer.viewGroup = "List"
	ObjectContainer.title1 = NAME
	ObjectContainer.art = R(ART)
	ObjectContainer.view_group = "List"
	

	#DirectoryItem.thumb = R(ICON)
	DirectoryObject.thumb = R(ICON)

####################################################################################################
def MainMenu():
    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()

    usedSelections={'genre':False, 'network':False}
    
    #dir.Append(Function(DirectoryItem(MovieList, "Movies")))
    oc.add(DirectoryObject(key=Callback(MovieList), title="Movies"))

    #dir.Append(Function(DirectoryItem(TVList, "TV"), url="/s/ref=sr_nr_n_1?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&ie=UTF8&qid=1334413870&rnid=2858778011", usedSelections=usedSelections))
    oc.add(DirectoryObject(key=Callback(TVList, url=TV_LIST, usedSelections=usedSelections), title="TV"))

    #dir.Append(Function(DirectoryItem(SearchMenu, "Search")))
    
    #dir.Append(Function(DirectoryItem(Library, "Your Library")))
    oc.add(DirectoryObject(key=Callback(Library), title="Your Library"))

    #dir.Append(PrefsItem(L('Preferences'), thumb=R(ICON)))
    oc.add(PrefsObject(title=L("Preferences"), thumb=R(ICON)))
    
    #return dir
    return oc

####################################################################################################
#def SearchMenu(sender):
def SearchMenu():
    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()
    #dir.Append(Function(InputDirectoryItem(Search, "Search Movies", "Search Amazon Prime for Movies", thumb = R(ICON)), tvSearch=False))
    oc.add(InputDirectoryObject(key=Callback(Search, tvSearch=False), title="Search Movies", summary="Search Amazon Prime for Movies", thumb=R(ICON)))
    #dir.Append(Function(InputDirectoryItem(Search, "Search TV Shows", "Search Amazon Prime for TV Shows", thumb = R(ICON))))
    oc.add(InputDirectoryObject(key=Callback(Search), title="Search TV Shows", summary="Search Amazon Prime for TV Shows", thumb=R(ICON)))
    
    #return dir
    return oc

####################################################################################################
#def Search(sender, query, url = None, tvSearch=True):
def Search(query, url = None, tvSearch=True):
    string = "/s/ref=sr_nr_n_0?rh=n%3A2625373011%2Cn%3A%212644981011%2Cn%3A%212644982011%2Cn%3A2858778011%2Ck%3A"


    #string += urllib.quote_plus(query)
    string += String.Quote(query, usePlus=True)
    
    if tvSearch:
        string += "%2Cp_85%3A2470955011%2Cn%3A2864549011&bbn=2858778011&keywords="
    else:
        string += "%2Cp_85%3A2470955011%2Cn%3A2858905011&bbn=2858778011&keywords="
    
    #string += urllib.quote_plus(query)
    string += String.Quote(query, usePlus=True)

    if tvSearch:
        return ResultsList(None, url=string, onePage=True)
    else:
        return ResultsList(None, url=string, onePage=True, tvList = False)


####################################################################################################
def Login():
    x = HTTP.Request('https://www.amazon.com/?tag=%s' % ASSOC_TAG, errors='replace')
    x = HTTP.Request('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG, errors='replace')
    cookies = HTTP.GetCookiesForURL('https://www.amazon.com/gp/sign-in.html?tag=%s' % ASSOC_TAG)

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
    x = HTTP.Request('https://www.amazon.com/gp/flex/sign-in/select.html?ie=UTF8&protocol=https&tag=%s' % ASSOC_TAG,values=params,errors='replace')

####################################################################################################
#def Library(sender):
def Library():
    Login()
    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()
    
    #dir.Append(Function(DirectoryItem(LibrarySpecific, "Movies"), movies=True))
    oc.add(DirectoryObject(key=Callback(LibrarySpecific, movies=True), title="Movies"))
    #dir.Append(Function(DirectoryItem(LibrarySpecific, "TV"), movies=False)) 
    oc.add(DirectoryObject(key=Callback(LibrarySpecific, movies=False), title="TV"))
    
    #return dir
    return oc

####################################################################################################    
#def LibrarySpecific(sender, movies=True):
def LibrarySpecific(movies=True):
    #pageList = HTTP.Request("https://www.amazon.com/gp/video/library")
    if movies:
        #pageList = HTTP.Request("https://www.amazon.com/gp/video/library/movie?show=all")
	url = "https://www.amazon.com/gp/video/library/movie?show=all"
    else:
        #pageList = HTTP.Request("https://www.amazon.com/gp/video/library/tv?show=all")
	url = "https://www.amazon.com/gp/video/library/tv?show=all"
    
    #element = HTML.ElementFromString(pageList.content)
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
        

    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()
    
    for i in range(0, len(videos)):
        #dir.Append(
        #        WebVideoItem(
        #        url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
        #        title = videos[i][0],
        #        thumb=Callback(Thumb, url=videos[i][2] )
        #        )
        #    )
	if movies:
		oc.add(MovieObject(
			url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
			title=videos[i][0],
			thumb=Resource.ContentsOfURLWithFallback(url=videos[i][0], fallback=ICON)
			)
		)
	else:
		oc.add(EpisodeObject(
			url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + videos[i][1],
			title=videos[i][0],
			thumb=Resource.ContentsOfURLWithFallback(url=videos[i][0], fallback=ICON)
			)
		)
    
    for i in range(0, len(seasons)):
        #dir.Append(Function(DirectoryItem(TVIndividualSeason, title=seasons[i][0], thumb=Callback(Thumb, url=seasons[i][2] )), url="https://www.amazon.com/gp/product/" + seasons[i][1]))
	oc.add(DirectoryObject(Key=Callback(TVIndividualSeason, url="https://www.amazon.com/gp/product/" + seasons[i][1]),
		title=seasons[i][0],
		thumb=Resource.ContentsOfURLWithFallback(url=seasons[i][2], fallback=ICON)))

    #return dir
    return oc
    
####################################################################################################
#def MovieList(sender, url=None, usedSelections = None):
def MovieList(url=None, usedSelections = None):
    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()

    #dir.Append(Function(InputDirectoryItem(Search, "Search Movies", "Search Amazon Prime for Movies", thumb = R(ICON)), tvSearch=False))
    oc.add(InputDirectoryObject(key=Callback(Search, tvSearch=False), title="Search Movies", summary="Search Amazon Prime for Movies", thumb=R(ICON)))

    #return dir
    return oc

####################################################################################################    
#def TVList(sender, url=None, usedSelections = None):
def TVList(url=None, usedSelections = None):

    #dir = MediaContainer(viewMode="List")
    oc = ObjectContainer()
    
    shownUnorganized = False
    
    tvPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    links = tvPage.xpath("//div[@id='refinements']//h2[. = 'TV Show']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'TV Show'])]/li/a/@href")    

    if (len(links) > 0):
        tvShowsLink = links[len(links)-1]
        
        if "sr_sa_p_lbr_tv_series_brow" in tvShowsLink:
            #dir.Append(Function(DirectoryItem(TVShows, "Shows"), url=tvShowsLink))
	    oc.add(DirectoryObject(key=Callback(TVShows, url=tvShowsLink), title="Shows"))
        else:
            #dir.Append(Function(DirectoryItem(TVShowsNotNice, "Shows"), url=url))
	    oc.add(DirectoryObject(key=Callback(TVShowsNotNice, url=url), title="Shows"))

    else:
        #dir.Append(Function(DirectoryItem(ResultsList, "All TV Shows (Unorganized)"), url=url, onePage=True))
	oc.add(DirectoryObject(key=Callback(ResultsList, url=url, onePage=True), title="All TV Shows (Unorganized)"))
        shownUnorganized = True
        
            
    if not usedSelections['genre']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Genre']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Genre'])]/li/a/@href")
        if len(links) > 0:
            genresLink = links[len(links)-1]
        
            if "sr_sa_p_n_theme_browse-bin" in genresLink:
                #dir.Append(Function(DirectoryItem(TVSubCategories, "Genres"), url=genresLink, category="Genre", usedSelections=usedSelections ))
		oc.add(DirectoryObject(key=Callback(TVSubCategories, url=genresLink, category="Genre", usedSelections=usedSelections), title="Genres"))
            else:
                #dir.Append(Function(DirectoryItem(TVNotNiceSubCategories, "Genres"), url=url, category="Genre", usedSelections=usedSelections ))
		oc.add(DirectoryObject(key=Callback(TVNotNiceSubCategories, url=url, category="Genre", usedSelections=usedSelections), title="Genres"))
            
            
            
    if not usedSelections['network']:
        links = tvPage.xpath("//div[@id='refinements']//h2[. = 'Content Provider']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = 'Content Provider'])]/li/a/@href")
        if len(links) > 0:
            networksLink = links[len(links)-1]

            if "sr_sa_p_studio" in networksLink:
                #dir.Append(Function(DirectoryItem(TVSubCategories, "Networks"), url=networksLink, category="Content Provider", usedSelections=usedSelections ))
		oc.add(DirectoryObject(key=Callback(TVSubCategories, url=networksLink, category="Content Provider", usedSelections=usedSelections), title="Networks"))
            else:
                #dir.Append(Function(DirectoryItem(TVNotNiceSubCategories, "Networks"), url=url, category="Content Provider", usedSelections=usedSelections ))
		oc.add(DirectoryObject(key=Callback(TVNotNiceSubCategories, url=url, category="Content Provider", usedSelections=usedSelections), title="Networks"))
    

    if not shownUnorganized:
        #dir.Append(Function(DirectoryItem(ResultsList, "All TV Shows (Unorganized)"), url=url, onePage=True))
	oc.add(DirectoryObject(key=Callback(ResultsList, url=url, onePage=True), title="All TV Shows (Unorganized)"))

        
        
   
        
    #return dir
    return oc
    
####################################################################################################    
#def TVSubCategories(sender, url=None, category=None, usedSelections=None):
def TVSubCategories(url=None, category=None, usedSelections=None):
    if category=='Content Provider':
        usedSelections['network'] = True
        
    if category=='Genre':
        usedSelections['genre'] = True
    
    
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfGenresLinks = tvGenrePage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfGenres = tvGenrePage.xpath("//*[@class='c3_ref refList']//a")
    listOfGenresNames = listOfGenres[0].xpath("//*[@class='refinementLink']/text()")
    
    
    #dir = MediaContainer(viewMode="list")
    oc = ObjectContainer()
    
    for i in range(0, len(listOfGenresLinks)):
        #dir.Append(Function(DirectoryItem(TVList, title=listOfGenresNames[i]), usedSelections=usedSelections, url=listOfGenresLinks[i]))
	oc.add(DirectoryObjecy(key=Callback(TVList, usedSelections=usedSelections, url=listOfGenresLinks[i]), title=listOfGenresNames[i]))
    
    #return dir
    return oc

####################################################################################################
#def TVNotNiceSubCategories(sender, url=None, category=None, usedSelections=None):
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
              
    #dir = MediaContainer(viewMode="list")
    oc = ObjectContainer()
        
    for i in range(0, len(genreList)):
        #dir.Append(Function(DirectoryItem(TVList, title=sortedPairs[i][0]), usedSelection=usedSelection, url=sortedPairs[i][1]))
	oc.add(DirectoryObject(key=Callback(TVList, usedSelection=usedSelection, url=sortedPairs[i][1]), title=sortedPairs[i][0]))
    
    #return dir
    return oc

####################################################################################################
#def TVShows(sender, url=None):
def TVShows(url=None):	
    tvShowPage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    listOfShowsLinks = tvShowPage.xpath("//*[@class='c3_ref refList']//a/@href")
    listOfShows = tvShowPage.xpath("//*[@class='c3_ref refList']//a")
    
    #dir = MediaContainer(viewMode="list")
    oc = ObjectContainer()
    
    if len(listOfShows) > 0:
        listOfShowsNames = listOfShows[0].xpath("//*[@class='refinementLink']/text()")
    

        
    
        for i in range(0, len(listOfShowsLinks)):
            #dir.Append(Function(DirectoryItem(ResultsList, title=listOfShowsNames[i]), url=listOfShowsLinks[i], sort=True))
	    oc.add(DirectoryObject(key=Callback(ResultsList, url=listOfShowsLinks[i], sort=True), title=listOfShowsNames[i]))
    
    #return dir
    return oc
    
####################################################################################################
#def TVShowsNotNice(sender, url=None):
def TVShowsNotNice(url=None):	
    tvGenrePage = HTML.ElementFromURL("http://www.amazon.com" + url)
    
    showList = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]//*[@class='refinementLink']/text()")
    
    showLinks = tvGenrePage.xpath("//div[@id='refinements']//h2[. = '" + "TV Show" + "']/following-sibling::ul[1 = count(preceding-sibling::h2[1] | ../h2[. = '" + "TV Show" + "'])]/li/a/@href")
    
    pairs = list()
    
    
    for i in range(0, len(showList)):
        pairs.append((showList[i], showLinks[i]))
        
    sortedPairs = sorted(pairs, key=operator.itemgetter(0))
              
    #dir = MediaContainer(viewMode="list")
    oc = ObjectContainer()
        
    for i in range(0, len(showList)):
        #dir.Append(Function(DirectoryItem(TVList, title=sortedPairs[i][0]), url=sortedPairs[i][1]))
	oc.add(DirectoryObject(key=Callback(TVList, url=sortedPairs[i][1]), title=sortedPairs[i][0]))
    
    #return dir
    return oc

####################################################################################################
#def ResultsList(sender, url = None, onePage=False, tvList = True, sort=False):
def ResultsList(url = None, onePage=False, tvList = True, sort=False):     
    
    #dir = MediaContainer(viewMode="list")
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
            #return MessageContainer("Sorry, no results.", "")
	    return ObjectContainer(header=NAME, message="Sorry, no results.")
    
    sortedSeasonPairs = seasons
    
    if sort:
        sortedSeasonPairs = sorted(seasons, key=operator.itemgetter(0))


    if tvList:
        for i in range(0, len(sortedSeasonPairs)):
            #dir.Append(Function(DirectoryItem(TVIndividualSeason, title=sortedSeasonPairs[i][0], thumb=Callback(Thumb, url=sortedSeasonPairs[i][2] )), url=sortedSeasonPairs[i][1]))
	    oc.add(DirectoryObject(key=Callback(TVIndividualSeason, url=sortedSeasonPairs[i][1]), title=sortedSeasonPairs[i][0], thumb=Resource.ContentsOfURLWithFallback(url=sortedSeasonPairs[i][2], fallback=ICON)))
    else:
        for i in range(0, len(sortedSeasonPairs)):
            #dir.Append(
            #WebVideoItem(
            #    url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + sortedSeasonPairs[i][3],
            #    title = sortedSeasonPairs[i][0],
            #    thumb=Callback(Thumb, url=sortedSeasonPairs[i][2] )
            #    )
            #)
	    oc.add(
		EpisodeObject(
			url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + sortedSeasonPairs[i][3],
			title = sortedSeasonPairs[i][0],
			thumb=Resource.ContentsOfURLWithFallback(url=sortedSeasonPairs[i][2], fallback=ICON)
		)
	    )
            

    if onePage and len(newURL) > 0:
        #dir.Append(Function(DirectoryItem(ResultsList, title="Next Page"), url=newURL, onePage = True))
	oc.add(DirectoryObject(key=Callback(ResultsList, url=newURL, onePage = True), title="Next Page"))

    #return dir
    return oc
    
####################################################################################################    
#def TVIndividualSeason(sender, url = None):
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

    #dir = MediaContainer(viewMode="list")
    oc = ObjectContainer()
    
    for i in range(0, len(listOfEpisodesTable)):
        #dir.Append(
        #    WebVideoItem(
        #        url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + listOfEpisodesASIN[i],
        #        title = listOfEpisodesTitles[i],
        #        summary = listOfEpisodesSummaries[i]
        #        )
        #    )
	oc.add(
		EpisodeObject(
			url="http://www.amazon.com/gp/video/streaming/mini-mode.html?asin=" + listOfEpisodesASIN[i],
		        title = listOfEpisodesTitles[i],
		        summary = listOfEpisodesSummaries[i],
			thumb = R(ICON) ###Check to see if there's an episode/season/series thumb accessible###
		)
	)
    
    
    #return dir
    return oc

####################################################################################################
#def Thumb(url):
#    try:
#        data = HTTP.Request(url, cacheTime = CACHE_1MONTH).content
#        return DataObject(data, 'image/jpeg')
#    except:
#        return Redirect(R(ICON))


'''
def GETSTREAMS(getstream):
    data = common.getURL(getstream,'atv-ps.amazon.com',useCookie=True)
    print data
    rtmpdata = demjson.decode(data)
    print rtmpdata
    try:
        drm = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['drm']
        if drm <> 'NONE':
            xbmcgui.Dialog().ok('DRM Detected','This video uses %s DRM' % drm)
    except:pass
    sessionId = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['sessionId']
    cdn = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['cdn']
    rtmpurls = rtmpdata['message']['body']['urlSets']['streamingURLInfoSet'][0]['streamingURLInfo']
    title = rtmpdata['message']['body']['metadata']['title'].replace('[HD]','')
    return rtmpurls, sessionId, cdn, title


def PLAYVIDEO():
    if not os.path.isfile(common.COOKIEFILE):
        common.mechanizeLogin()
    #try:
    swfUrl, values, owned = GETFLASHVARS(common.args.url)
    #if not owned:
    #    return PLAYTRAILER_RESOLVE() 
    values['deviceID'] = values['customerID'] + str(int(time.time() * 1000)) + values['asin']
    getstream  = 'https://atv-ps.amazon.com/cdp/catalog/GetStreamingUrlSets'
    #getstream  = 'https://atv-ext.amazon.com/cdp/cdp/catalog/GetStreamingUrlSets'
    getstream += '?asin='+values['asin']
    getstream += '&deviceTypeID='+values['deviceTypeID']
    getstream += '&firmware=WIN%2010,0,181,14%20PlugIn'
    getstream += '&customerID='+values['customerID']
    getstream += '&deviceID='+values['deviceID']
    getstream += '&token='+values['token']
    getstream += '&xws-fa-ov=false'
    getstream += '&format=json'
    getstream += '&version=1'
    try:
        rtmpurls, streamSessionID, cdn, title = GETSTREAMS(getstream)
    except:
        return PLAYTRAILER_RESOLVE()
    if cdn == 'limelight':
        xbmcgui.Dialog().ok('Limelight CDN','Limelight uses swfverfiy2. Playback may fail.')
    if rtmpurls <> False:
        basertmp, ip = PLAY(rtmpurls,swfUrl=swfUrl,title=title)
    if streamSessionID <> False:
        epoch = str(int(time.mktime(time.gmtime()))*1000)
        USurl =  'https://atv-ps.amazon.com/cdp/usage/UpdateStream'
        USurl += '?device_type_id='+values['deviceTypeID']
        USurl += '&deviceTypeID='+values['deviceTypeID']
        USurl += '&streaming_session_id='+streamSessionID
        USurl += '&operating_system='
        USurl += '&timecode=45.003'
        USurl += '&flash_version=WIN%2010,3,181,14%20PlugIn'
        USurl += '&asin='+values['asin']
        USurl += '&token='+values['token']
        USurl += '&browser='+urllib.quote_plus(values['userAgent'])
        USurl += '&server_id='+ip
        USurl += '&client_version='+swfUrl.split('/')[-1]
        USurl += '&unique_browser_id='+values['UBID']
        USurl += '&device_id='+values['deviceID']
        USurl += '&format=json'
        USurl += '&version=1'
        USurl += '&page_type='+values['pageType']
        USurl += '&start_state=Video'
        USurl += '&amazon_session_id='+values['sessionID']
        USurl += '&event=STOP'
        USurl += '&firmware=WIN%2010,3,181,14%20PlugIn'
        USurl += '&customerID='+values['customerID']
        USurl += '&deviceID='+values['deviceID']
        USurl += '&source_system=http://www.amazon.com'
        USurl += '&http_referer=ecx.images-amazon.com'
        USurl += '&event_timestamp='+epoch
        USurl += '&encrypted_customer_id='+values['customerID']
        print common.getURL(USurl,'atv-ps.amazon.com',useCookie=True)

        epoch = str(int(time.mktime(time.gmtime()))*1000)
        surl =  'https://atv-ps.amazon.com/cdp/usage/ReportStopStreamEvent'
        surl += '?deviceID='+values['deviceID']
        surl += '&source_system=http://www.amazon.com'
        surl += '&format=json'
        surl += '&event_timestamp='+epoch
        surl += '&encrypted_customer_id='+values['customerID']
        surl += '&http_referer=ecx.images-amazon.com'
        surl += '&device_type_id='+values['deviceTypeID']
        surl += '&download_bandwidth=9926.295518207282'
        surl += '&device_id='+values['deviceTypeID']
        surl += '&from_mode=purchased'
        surl += '&operating_system='
        surl += '&version=1'
        surl += '&flash_version=LNX%2010,3,181,14%20PlugIn'
        surl += '&url='+urllib.quote_plus(basertmp)
        surl += '&streaming_session_id='+streamSessionID
        surl += '&browser='+urllib.quote_plus(values['userAgent'])
        surl += '&server_id='+ip
        surl += '&client_version='+swfUrl.split('/')[-1]
        surl += '&unique_browser_id='+values['UBID']
        surl += '&amazon_session_id='+values['sessionID']
        surl += '&page_type='+values['pageType']
        surl += '&start_state=Video'
        surl += '&token='+values['token']
        surl += '&to_timecode=3883'
        surl += '&streaming_bit_rate=348'
        surl += '&new_streaming_bit_rate=2500'
        surl += '&asin='+values['asin']
        surl += '&deviceTypeID='+values['deviceTypeID']
        surl += '&firmware=WIN%2010,3,181,14%20PlugIn'
        surl += '&customerID='+values['customerID']
        print common.getURL(surl,'atv-ps.amazon.com',useCookie=True)
        if values['pageType'] == 'movie':
            import movies as moviesDB
            moviesDB.watchMoviedb(values['asin'])
        if values['pageType'] == 'tv':
            import tv as tvDB
            tvDB.watchEpisodedb(values['asin'])

def GETFLASHVARS(pageurl):
    showpage = common.getURL(pageurl,useCookie=True)
    flashVars = re.compile("'flashVars', '(.*?)' \+ new Date\(\)\.getTime\(\)\+ '(.*?)'",re.DOTALL).findall(showpage)
    flashVars =(flashVars[0][0] + flashVars[0][1]).split('&')
    swfUrl = re.compile("avodSwfUrl = '(.*?)'\;").findall(showpage)[0]
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
    return swfUrl, values, owned
        
def PLAY(rtmpurls,swfUrl,Trailer=False,resolve=True,title=False):
    print rtmpurls
    quality = [0,2500,1328,996,664,348]
    lbitrate = quality[int(common.addon.getSetting("bitrate"))]
    mbitrate = 0
    streams = []
    for data in rtmpurls:
        url = data['url']
        bitrate = int(data['bitrate'])
        if lbitrate == 0:
            streams.append([bitrate,url])
        elif bitrate >= mbitrate and bitrate <= lbitrate:
            mbitrate = bitrate
            rtmpurl = url
    if lbitrate == 0:        
        quality=xbmcgui.Dialog().select('Please select a quality level:', [str(stream[0])+'kbps' for stream in streams])
        if quality!=-1:
            rtmpurl = streams[quality][1]
    protocolSplit = rtmpurl.split("://")
    pathSplit   = protocolSplit[1].split("/")
    hostname    = pathSplit[0]
    appName     = protocolSplit[1].split(hostname + "/")[1].split('/')[0]    
    streamAuth  = rtmpurl.split(appName+'/')[1].split('?')
    stream      = streamAuth[0].replace('.mp4','')
    auth        = streamAuth[1]
    identurl = 'http://'+hostname+'/fcs/ident'
    ident = common.getURL(identurl)
    ip = re.compile('<fcs><ip>(.+?)</ip></fcs>').findall(ident)[0]
    basertmp = 'rtmpe://'+ip+':1935/'+appName+'?_fcs_vhost='+hostname+'&ovpfv=2.1.4&'+auth
    finalUrl = basertmp
    finalUrl += " playpath=" + stream 
    finalUrl += " pageurl=" + common.args.url
    finalUrl += " swfurl=" + swfUrl + " swfvfy=true"
    if Trailer and not resolve:
        finalname = Trailer+' Trailer'
        item = xbmcgui.ListItem(finalname,path=finalUrl)
        item.setInfo( type="Video", infoLabels={ "Title": finalname})
        item.setProperty('IsPlayable', 'true')
        xbmc.Player().play(finalUrl,item)
    else:
        item = xbmcgui.ListItem(path=finalUrl)
        #item.setInfo( type="Video", infoLabels={ "Title": title})
        xbmcplugin.setResolvedUrl(pluginhandle, True, item)
    return basertmp, ip
'''