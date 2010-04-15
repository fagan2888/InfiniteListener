"""
Similar code from the BostonHackDay project

Simple code that Ron can launch on the NYU cluster.

T. Bertin-Mahieux (2010) Columbia University
tb2332@columbia.edu
"""


import os
import sys
import glob
import multiprocessing

import numpy as np
import scipy as sp
import scipy.io

import initializer
import trainer



featsDir = os.path.expanduser('~/projects/ismir10-patterns/beatFeats')
#testFeatsDir = os.path.expanduser('~/projects/ismir10-patterns/uspop_mat')
#outputDir = os.path.expanduser('~/projects/ismir10-patterns/experiments')
outputDir = ''
assert outputDir != '','SET OUTPUT DIR TO SOMETHING!!!!'


def do_experiment(experiment_dir,beats=0,bars=0,nCodes=0,nIter=1e7,
                  partialbar=0,keyInv=False,songKeyInv=True,lrate=1e-3,
                  mat_dir=''):
    """
    Main function to run an experiment, train a model and save to dir.
    """

    # check for 'done' file
    if os.path.exists(os.path.join(experiment_dir,'DONE.txt')):
        return

    # if experiment folder does not exist, create it
    if not os.path.exists(experiment_dir):
        print 'creating experiment dir:',experiment_dir
        os.mkdir(experiment_dir)

    # ec = exit code for training, 0 = ok, >0 = bad
    ec = 1

    # check if saved model exists
    alldirs = glob.glob(os.path.join(experiment_dir,'*'))
    alldirs = filter(lambda x: os.path.isdir(x), alldirs)
    alldirs = filter(lambda x: os.path.split(x)[-1][:4] == 'exp_',alldirs)
    continue_training = len(alldirs) > 0

    # continue from saved model
    if continue_training:
        # find most recent saved mdoel, and continue!
        # ec = exit_code, 0 if due to StopIteration, >0 otherwise
        savedmodel = np.sort(alldirs)[-1]
        ec = trainer.train(savedmodel)

    # no prior saved model
    if not continue_training:
        #initialize and save codebook
        codebook = initializer.initialize(nCodes, pSize=beats, usebars=bars,
                                          keyInv=keyInv, songKeyInv=songKeyInv,
                                          positive=True, do_resample=True,
                                          partialbar=partialbar, nThreads=4,
                                          oracle='MAT', artistsdb='',
                                          matdir=mat_dir)
        codebook_fname = os.path.join(experiment_dir,'codebook.mat')
        scipy.io.savemat(codebook_fname,{'codebook':codebook})
        print 'after initialization, codebook saved to:',codebook_fname

        # train (from scratch)
        # ec = exit_code, 0 if due to StopIteration, >0 otherwise
        ec = trainer.train(codebook_fname, expdir=experiment_dir, pSize=beats,
                           usebars=bars, keyInv=keyInv, songKeyInv=songKeyInv,
                           positive=True, do_resample=True,
                           partialbar=partialbar, lrate=lrate, nThreads=4,
                           oracle='MAT', artistsdb='',
                           matdir=mat_dir, nIterations=nIter, useModel='VQ')

    # write done file
    if ec == 0:
        f = open(os.path.join(experiment_dir,'DONE.txt'),'w')
        f.write('experiment appear to be done\n')
        f.close()


def do_experiment_wrapper(args):
    """
    launch experiments given params
    Receives a pair: args and argsdict!
    """
    args,argsdict = args
    return do_experiment(*args,**argsdict)



experiment_args = []
# experiment set 1
args1 = [os.path.join(outputDir,'set1exp1')]
argsd1 = {'mat_dir':featsDir,'beats':4,'bars':1,'nCodes':100}
experiment_args.append( [(args1,argsd1),] )
# EXPERIMENT SET 2
# redo the distortion rate experiment: double pSize, square codebook size
#1
args1 = [os.path.join(outputDir,'set2exp1')]
argsd1 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':2,'partialbar':1}
args2 = [os.path.join(outputDir,'set2exp2')]
argsd2 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':4,'partialbar':2}
args3 = [os.path.join(outputDir,'set2exp3')]
argsd3 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':16}
args4 = [os.path.join(outputDir,'set2exp4')]
argsd4 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':8,'bars':2,'nCodes':256}
#2
args5 = [os.path.join(outputDir,'set2exp5')]
argsd5 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':3,'partialbar':1}
args6 = [os.path.join(outputDir,'set2exp6')]
argsd6 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':9,'partialbar':2}
args7 = [os.path.join(outputDir,'set2exp7')]
argsd7 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':81}
args8 = [os.path.join(outputDir,'set2exp8')]
argsd8 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':8,'bars':2,'nCodes':6561}
#3
args9 = [os.path.join(outputDir,'set2exp9')]
argsd9 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':2,'partialbar':2}
args10 = [os.path.join(outputDir,'set2exp10')]
argsd10 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':4}
args11 = [os.path.join(outputDir,'set2exp11')]
argsd11 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':8,'bars':2,'nCodes':16}
args12 = [os.path.join(outputDir,'set2exp12')]
argsd12 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':16,'bars':4,'nCodes':256}
#4
args13 = [os.path.join(outputDir,'set2exp13')]
argsd13 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':2}
args14 = [os.path.join(outputDir,'set2exp14')]
argsd14 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':8,'bars':2,'nCodes':4}
args15 = [os.path.join(outputDir,'set2exp15')]
argsd15 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':16,'bars':4,'nCodes':16}
args16 = [os.path.join(outputDir,'set2exp16')]
argsd16 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':32,'bars':8,'nCodes':256}
#5
args17 = [os.path.join(outputDir,'set2exp17')]
argsd17 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':7,'partialbar':1}
args18 = [os.path.join(outputDir,'set2exp18')]
argsd18 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':49,'partialbar':2}
args19 = [os.path.join(outputDir,'set2exp19')]
argsd19 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':2401}
#6
args20 = [os.path.join(outputDir,'set2exp20')]
argsd20 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':7,'partialbar':2}
args21 = [os.path.join(outputDir,'set2exp21')]
argsd21 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':4,'bars':1,'nCodes':49}
args22 = [os.path.join(outputDir,'set2exp22')]
argsd22 = {'mat_dir':featsDir,'keyInv':False,'songKeyInv':True,
          'beats':8,'bars':2,'nCodes':2401}
# add to exp args
tmp = []
for k in range(1,23):
    tmp.append(eval( '(args'+str(int(k))+',argsd'+str(int(k))+')' ))
experiment_args.append(tmp)


def die_with_usage():
    """
    HELP MENU
    """
    print 'code to launch experiments on NYU cluster'
    print 'usage:'
    print '  python for_ron.py -go <num proc> <exp set> <sub exp (opt)>'
    sys.exit(0)



if __name__ == '__main__':

    # help menu
    if len(sys.argv) < 4:
        die_with_usage()

    # setup
    nprocesses = int(sys.argv[2])
    pool = multiprocessing.Pool(processes=nprocesses)
    # Python indexes from 0, the argument indexes from 1.
    experiment_set_number = int(sys.argv[3]) - 1
    args = experiment_args[experiment_set_number]
    try:
        args = [args[int(sys.argv[4]) - 1]] # subset exp? nice ;)
    except IndexError:
        pass

    # launch experiments
    pool.map(do_experiment_wrapper, args)
