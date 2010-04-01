"""
Code to test a model trained by online learning.
Look at all the saved folders, and apply every save to the
given testset (load into memory).

T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu
"""

import os
import sys
import glob
import time
import copy
#import pickle
import numpy as np

from trainer import StatLog
import model as MODEL
import oracle_matfiles as ORACLE
import analyze_saved_model as ANALYZE


def print_write(s,fname):
    """
    Prints something and write it to file
    """
    print s
    f = open(fname,'a')
    f.write(s)
    f.write('\n')
    f.close()


def safe_traceback(folder):
    """
    Performs traceback, but returns [None] if an error is raised.
    """
    try:
        return ANALYZE.traceback(folder)
    except IOError:
        return [None]
        

def test_saved_model_folder(dirname,feats,output):
    """
    Test a saved model by loading it and applying to features.
    Output is the output file, used with print_write()
    """
    raise NotImplementedError


def test_saved_model_codebook(filename,feats,output):
    """
    Test a codebook by creating the simplest model we have,
    model.Model().
    Output is the output file, used with print_write()
    """
    raise NotImplementedError


def die_with_usage():
    """
    HELP MENU
    """
    print 'Test a set of saved model with a given dataset.'
    print 'Usage:'
    print 'python test_trained_models.py [FLAGS] <savedmodel> <matfilesdir> <output.txt>'
    print 'PARAMS:'
    print '  <savedmodel>   directory where an online model is saved'
    print '  <matfilesdir>  '
    print '  <output.txt>   '
    print 'FLAGS:'
    print '  -testone       test only the given saved model'
    print ''
    print 'T. Bertin-Mahieux (2010) Columbia University'
    print 'tb2332@columbia.edu'
    sys.exit(0)


if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # flags
    testone = False
    while True:
        if sys.argv[1] == '-testone':
            testone = True
        else:
            break
        sys.argv.pop(1)

    # params
    savedmodel = os.path.abspath(sys.argv[1])
    matfilesdir = os.path.abspath(sys.argv[2])
    output = os.path.abspath(sys.argv[3])
    print_write('saved model = '+ savedmodel,output)
    print_write('matfiles dir = '+ matfilesdir,output)
    print_write('output = '+output,output)


    #******************************************************************
    # gather in a set all models to try
    # also gather the number of iterations associated with each model
    if os.path.isfile(savedmodel):
        # WRONG CASE, matfile
        print_write('Cannot do it on just a codebook.',output)
        print_write('We dont know the params!.',output)
        sys.exit(0)
    elif testone:
        # load one things and move on
        print_write('Doing only one file.',output)
        all_to_test = [savedmodel]
    else:
        # main algorithm
        parentdir,tmp = os.path.split(savedmodel)
        # traceback
        tb = ANALYZE.traceback(savedmodel)
        print_write('*** TRACEBACK ****************',output)
        for f in tb:
            print_write(str(f),output)
        print_write('******************************',output)
        # find everything in parent folder, then just folders
        all_in_folder = glob.glob(os.path.join(parentdir,'*'))
        all_in_folder = filter(lambda x: os.path.isdir(x), all_in_folder)
        # keep those that have same origin
        leaves = filter(lambda x: safe_traceback(x)[0]==tb[0],all_in_folder)
        # everything to test, matfile at the end
        all_to_test = set()
        for f in tb:
            if os.path.isdir(f):
                all_to_test.add(f)
        for f in leaves:
            all_to_test.add(f)
        all_to_test = list(all_to_test)
        all_to_test.append(tb[0])
    print_write('all models to try:',output)
    for f in all_to_test:
        print_write(str(f),output)
    print_write('number of models to test: '+str(len(all_to_test)),output)
    

    #******************************************************************
    # get params
    params = ANALYZE.unpickle(os.path.join(savedmodel,'params.p'))
    # load data into memory
    oracle = ORACLE.OracleMatfiles(params,matfilesdir,oneFullIter=True)
    # get all features
    data = [x for x in oracle]
    print_write('retrieved '+str(len(data))+' tracks.',output)
    # get none none features
    data = filter(lambda x: x != None, data)
    print_write(str(len(data))+' tracks not None remaining.',output)
    # transform into numpy array
    data = np.concatenate(data)
    print_write(str(data.shape[0])+' patterns loaded.',output)
    # remove empty patterns
    data = data[np.where(np.sum(data,axis=1)>0)]
    print_write(str(data.shape[0])+' non-zero patterns loaded.',output)
    if data.shape[0] == 0:
        print_write('No patterns loaded, quit.',output)
        sys.exit(0)

    #******************************************************************
    # predict on every model

