"""
A set of functions to complement pyechonest
Mainly, do URL calls, get XML, parse it

For help on XML with Python, check:
http://diveintopython.org/xml_processing/index.html


T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu
"""


import os
import sys
import time
import copy
import xml
from xml.dom import minidom
import urllib
import numpy as np

try:
    _api_dev_key = os.environ['ECHO_NEST_API_KEY']
except:
    _api_dev_key = os.environ['ECHONEST_API_KEY']


def do_xml_call(url):
    """
    Calls echonest with a given command, expect XML document
    Return XML object
    """
    # open stream
    stream = urllib.urlopen(url)
    # directly parse it to XML
    xmldoc = minidom.parse(stream).documentElement
    # close stream
    stream.close()
    # done, return xml document
    return xmldoc

    # SLOW METHOD, BY CREATING A FILE:
    # call the url, save the output to file
    filename,httpmesage = urllib.urlretrieve(url)
    # open the file
    f = open(filename,'r')
    # parse it to xml
    xmldoc = minidom.parse(f).documentElement
    # close the file
    f.close()
    # return xml object
    return xmldoc


def do_dict_call(url):
    """
    Calls EchoNest with a given command, expect the string
    representation of a python dictionary.
    Used by alpha API calls like search_tracks
    Returns dictionary
    """
    # call the url, save the output to file
    filename,httpmessage = urllib.urlretrieve(url)
    # open the file
    f = open(filename,'r')
    # read the line (hope there is only one...)
    data = f.readline().strip()
    # close the file
    f.close()
    # eval
    d = eval(data)
    # return dictionary
    return d


def check_xml_success(xmldoc):
    """
    Check an XML document received from the EchoNest
    Return True if success, otherwise
    """
    status = xmldoc.getElementsByTagName('status')[0]
    code = xmldoc.getElementsByTagName('code')[0]
    value = code.firstChild
    assert value.__class__.__name__ == 'Text'
    if value.data == '0':
        return True # succes
    return False # failure

    

def get_audio(artist_id,max_results=15):
    """
    Get the audio given an artist EchoNest id.
    artist_id example: ARH6W4X1187B99274F

    INPUT:
    - artist_id    something like: ARH6W4X1187B99274F
    - max_results  max number  of results (must be <= 15)

    Returns two list, or two None if error
    RETURN:
       titles,artist    one list + one string
       None,?           if problem, none + <none or artist>

    This one is actually easy with pyechonest.
    This is a debugging case.
    """
    # build call
    url = 'http://developer.echonest.com/api/get_audio?api_key='
    url += _api_dev_key
    url += '&id=music://id.echonest.com/~/AR/'
    url += artist_id
    url += '&rows=' + str(int(max_results))
    url += '&version=3'
    # call, get XML
    xmldoc = do_xml_call(url)
    # check success
    if not check_xml_success(xmldoc):
        return None,None
    # get artist name
    artist_name = xmldoc.getElementsByTagName('artist')[0].firstChild.firstChild.data
    # get all audio
    results = xmldoc.getElementsByTagName('results')[0]
    nAudio = int(results.getAttribute('shown'))
    if nAudio == 0:
        return None,artist_name
    # we have positive results
    titles = []
    docs = results.getElementsByTagName('doc')
    for doc in docs:
        title = doc.getElementsByTagName('title')[0].firstChild.data
        titles.append(title)
    # done, return lists
    return titles,artist_name
    


def search_tracks(artist,title='',max_results=100):
    """
    Search for songs that match a query.
    Query based on artist and title (one of the two or both).

    INPUT:
       - artist, or approximation
       - title of the song, or approximation (optional)
       - max_results, number of results (must be <= 100)

    RETURN:
       tids, titles, aids, artists    4 lists! or None, None, None, None

    Not sure that addind a song title changes much the result...
    This code relies on an alpha call to EchoNest API, it will
    get deprecated!
    """
    # build call
    url = 'http://developer.echonest.com/api/alpha_search_tracks?'
    url += 'api_key=' + _api_dev_key
    try:
        url += '&artist='+urllib.quote(artist)
    except TypeError:
        url += '&artist='+artist
    if title != '':
        url += '&title='+urllib.quote(title)
    url += '&version=3'
    url += '&results=' + str(int(max_results))
    # call, get XML
    d = do_dict_call(url)
    # check success
    if not d['status'] == 'ok':
        return None, None, None, None
    results = d['results']
    if len(results) == 0:
        return None, None, None, None
    # get results info
    tids = []
    titles = []
    aids = []
    artists = []
    for res in results:
        tids.append(res['trackID'])
        titles.append(res['title'])
        aids.append(res['artistID'])
        artists.append(res['artist'])
    # done
    return tids, titles, aids, artists

    

def get_beats(track_id):
    """ SEE GET_BEATS_BARS """
    return get_beats_bars(track_id,'beat')

def get_bars(track_id):
    """ SEE GET_BEATS_BARS """
    return get_beats_bars(track_id,'bar')

def get_beats_bars(track_id,elem):
    """
    Get bars or beats from a given track ID
    typical track id: TRCPOLF12548893D42

    elem can be 'bar' or 'beat'

    RETURN
        bstarts        array or None
    """
    assert elem=='bar' or elem=='beat', 'wrong element, only "bar" or "beat"'
    # build call
    url = 'http://developer.echonest.com/api/'
    if elem == 'bar':
        url += 'get_bars?api_key='
    elif elem == 'beat':
        url += 'get_beats?api_key='
    url += _api_dev_key
    url += '&id=music://id.echonest.com/~/TR/' + track_id
    url += '&version=3'
    # call, get XML
    xmldoc = do_xml_call(url)
    # check success
    if not check_xml_success(xmldoc):
        return None
    result = []
    bs = xmldoc.getElementsByTagName(elem) # elem = 'bar' or 'beat'
    for b in bs:
        result.append(float(b.firstChild.data))
    # done
    return result


def get_duration(track_id):
    """
    Get the duration of a given track id
    RETURN
       float or None
    """
    # build call
    url = 'http://developer.echonest.com/api/get_duration?api_key='
    url += _api_dev_key
    url += '&id=music://id.echonest.com/~/TR/' + track_id
    url += '&version=3'
    # call, get XML
    xmldoc = do_xml_call(url)
    # check success
    if not check_xml_success(xmldoc):
        return None
    duration = xmldoc.getElementsByTagName('duration')[0].firstChild.data
    return float(duration)


def get_segments(track_id):
    """
    Get the segments of a given track id
    RETURN
      segstart, chroma     array, np.array 12x1    or None, None
    """
    # build call
    url = 'http://developer.echonest.com/api/get_segments?api_key='
    url += _api_dev_key
    url += '&id=music://id.echonest.com/~/TR/' + track_id
    url += '&version=3'
    # call, get XML
    xmldoc = do_xml_call(url)
    # check success
    if not check_xml_success(xmldoc):
        return None, None
    # get all segments
    segments = xmldoc.getElementsByTagName('segment')
    if len(segments) == 0:
        return None, None
    # to return
    segstart = []
    chromas = np.zeros([12,len(segments)])
    for segidx in range(len(segments)):
        segment = segments[segidx]
        # get start time
        segstart.append(float(segment.getAttribute('start')))
        # get chromas
        pitches = segment.getElementsByTagName('pitch')
        assert len(pitches) == 12
        for k in range(12):
            chromas[k,segidx] = float(pitches[k].firstChild.data)
    # done
    return segstart, chromas


def get_our_analysis(track_id):
    """
    Get the analysis we need from a given track ID:
    - segment starts
    - segment chromas
    - beatstart
    - barstart
    - duration

    Return them in order, or 5 None if one of them fails
    """
    # duration
    duration = get_duration(track_id)
    if duration == None:
        return None,None,None,None,None
    # beats
    beatstart = get_beats(track_id)
    if beatstart == None:
        return None,None,None,None,None
    # bars
    barstart = get_bars(track_id)
    if barstart == None:
        return None,None,None,None,None
    # segments
    segstart, chromas = get_segments(track_id)
    if segstart == None or chromas == None:
        return None,None,None,None,None
    # done, return
    return segstart, chromas, beatstart, barstart, duration

    

def die_with_usage():
    """
    HELP MENU
    """
    print 'library, set of function to complement pyechonest'
    print 'to test/debug, launch:'
    print '    python en_extras.py -go'
    sys.exit(0)


    
if __name__ == '__main__' :

    if len(sys.argv) < 2:
        die_with_usage()


    # DEBUGGING
    call1 = 'http://developer.echonest.com/api/get_audio?api_key=5ZAOMB3BUR8QUN4PE&id=musicbrainz:artist:6fe07aa5-fec0-4eca-a456-f29bff451b04&rows=2&version=3'

    # do a call, get XML
    xmldoc = do_xml_call(call1)

    # call for all audio for a given artist
    artist_id = 'ARH6W4X1187B99274F'
    titles, artist_name = get_audio(artist_id)
    print 'after get_audio with',artist_name,'id, got:'
    for t in titles:
        print '   ',t

    # get info on the first track from previous call
    print 'calling first song, title=',titles[0],', artist=',artist_name
    tids,titles2,aids,artists = search_tracks(artist_name,title=titles[0])
    print 'got tracks:'
    for k in range(len(tids)):
        print '   ',titles2[k],'by',artists[k]
    print 'first song id:',tids[0]

    # get bars with that id
    print get_bars(tids[0])
    # get beats with that id
    print get_beats(tids[0])
    # get duration with that id
    print 'duration:',get_duration(tids[0])
    # get segments with that id
    segstart, chromas = get_segments(tids[0])
    print 'some chromas:',chromas[:,int(chromas.shape[1]/2)]
    # get our analysis with that id
    tstart = time.time()
    a,b,c,d,e = get_our_analysis(tids[0])
    print 'duration still:', e, ', obtained in',time.time()-tstart,'seconds.'
    