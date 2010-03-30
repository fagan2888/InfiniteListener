"""
Program to analyze a saved model of the InfiniteListener project.
Takes a saving directory and outputs basic stats.

T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu
"""


import os
import os.path
import glob
import sys
import time
import pickle

from trainer import StatLog


def unpickle(filename):
    """
    Unpickle from a filename
    """
    f = open(filename)
    unpickler = pickle.Unpickler(f)
    res = unpickler.load()
    f.close()
    return res



def stop_time(folder):
    """
    Find the stop time in seconds of the savedmodel from the folder name.
    Returns stop time in seconds.
    """
    # tail of folder name
    tail = os.path.split(folder)[-1]
    # remove exp_
    stime = tail[4:]
    # get time
    timeformat = "%Y_%m_%d_AT_%Hh%Mm%Ss"
    res = time.strptime(stime,timeformat)
    # return time in seconds
    return time.mktime(res)


def start_time(folder):
    """
    Find the start time in seconds of the savedmodel from the file 'starttime_'.
    Returns start time in seconds.
    """
    files = glob.glob(os.path.join(folder,'starttime_*.txt'))
    assert len(files) == 1,'Too many startime in folder: %s'%folder
    startfile = files[0]
    # tail of folder name
    tail = os.path.split(startfile)[-1]
    # remove exp_ and .txt
    stime = tail[len('starttime_'):]
    stime = stime[:-len('.txt')]
    # get time
    timeformat = "%Y_%m_%d_AT_%Hh%Mm%Ss"
    res = time.strptime(stime,timeformat)
    # return time in seconds
    return time.mktime(res)


def pretty_print_secs(seconds):
    """
    Return a string to print elapsed time in a comprehensible way.
    """
    seconds = int(seconds) # drop decimals
    # seconds
    secs = seconds % 60
    res = str(secs) + ' seconds'
    seconds = seconds - secs
    if seconds == 0:
        return res
    minutes = seconds / 60
    # min
    mins = minutes % 60
    res = str(mins) + ' mins ' + res
    minutes = minutes - mins
    if minutes == 0:
        return res
    hours = minutes / 60
    # hrs
    hrs = hours % 24
    res = str(hrs) + ' h ' + res
    hours = hours - hrs
    if hours == 0:
        return res
    days = hours / 24
    # days
    res = str(days) + ' days ' + res
    return res
    

def print_traceback(folder):
    """
    Print the original folder and the followers
    """
    if not os.path.isdir(folder):
        print 'missing folder in print_traceback:',folder
        return
    statlog = unpickle(os.path.join(folder,'stats.p'))
    params = unpickle(os.path.join(folder,'params.p'))    
    if not statlog.fromscratch:
        assert params['savedmodel'] != '','No saved model in traceback'
        print_traceback(params['savedmodel'])
    print folder
    return


def traceback_stats(folder):
    """
    Recursively compute number iterations and number patterns seen.
    Also time ran in seconds.
    RETURN
       nIters
       nPatterns
       totalTime
    """
    if not os.path.isdir(folder):
        print 'missing folder in traceback_stats:',folder
        return 0,0,0
    statlog = unpickle(os.path.join(folder,'stats.p'))
    params = unpickle(os.path.join(folder,'params.p'))
    stoptime = stop_time(folder)
    starttime = start_time(folder)
    totalTime = stoptime - starttime
    nIters = statlog.nIterations
    nPatterns = statlog.nPatternUsed
    if not statlog.fromscratch:
        assert params['savedmodel'] != '','No saved model in traceback'
        nIters2,nPatterns2, totalTime2 = traceback_stats(params['savedmodel'])
        nIters += nIters2
        nPatterns += nPatterns2
        totalTime += totalTime2
    return nIters, nPatterns, totalTime

    

def die_with_usage():
    """
    HELP MENU
    """
    print 'display basic statistics about a saved model'
    print 'usage:'
    print '   python analyze_saved_model.py ~/exps/saveddir'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 2:
        die_with_usage

    savedmodel = sys.argv[1]
    assert os.path.isdir(savedmodel),'%s is not a directory.'%savedmodel
    
    # load stat, params
    statlog = unpickle(os.path.join(savedmodel,'stats.p'))
    params = unpickle(os.path.join(savedmodel,'params.p'))

    # traceback
    print '*** TRACEBACK ********************'
    print 'folders from oldest to most recent'
    print_traceback(savedmodel)
    print '**********************************'

    # stats: nIters, nPatterns
    nIters, nPatterns, totalTime = traceback_stats(savedmodel)
    print 'ran for:', pretty_print_secs(totalTime)
    print 'number of iterations:', nIters
    print 'number of patterns seen:', nPatterns
    
    # params
    print 'PARAMS:'
    for k in params.keys():
        print '   ',k,' = ',params[k]
