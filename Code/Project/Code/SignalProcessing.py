#!/usr/bin/python
#rewritten script in python from the matlab adaptation
#  Author:  Casper van Elteren
from __future__ import print_function
import classification, preproc, time, FeedbackSignals
import numpy as np
from h5py import File, special_dtype
from pylab import *
# from bufferInterface import bufhelp
import bufhelp
import os
import csv


# connect to buffer
ftc, hdr = bufhelp.connect()

# get cap file
filepath = '../../resources/caps/cap_tmsi_mobita_im.txt'
capfile = np.loadtxt(filepath, dtype = str)
# print(capfile)
# print(type(capfile))
# SET THE SUBJECT
num = 3
# storage for the data
dataDir = '../Data/'

# fileTest  = dataDir + 'test_subjecet_{0}'.format(num)


# P300 occurs up to 500 ms after stimulus
# taking 100 ms more than expectation
trlen_ms = 600
run = True

# calibrationCatchEvents is list of [type, value]
calibrationCatchEvents = [\
'target', 'feet', 'target', 'right hand', 'target', 'left hand', 'feedback','positive','feedback','negative']
print("Waiting for start event.")
while run:
    e = bufhelp.waitforevent('start',1000, 0)

    # print(':',type(e))
    # print(e)
    if e is not None:
        while True:
            fileCalibration = dataDir + 'calibration_subject_{0}.hdf5'.format(num)
            if os.path.isfile(fileCalibration):
                num = raw_input('Please enter a new subject number ')
                fileCalibration = dataDir + 'calibration_subject_{0}.hdf5'.format(num)
            else:
                break
        print('Storing data in: \n\t ', fileCalibration)

        # print(e[0], e[1])
        # print('Found event')calibration
        if e.value == "calibration":
            print("Calibration phase")
            # catch events
            data, events, stopevents = bufhelp.gatherdata(\
                                        calibrationCatchEvents, \
                                        trlen_ms, ("calibration", "end"), \
                                        milliseconds=True, verbose = False)

            # convert to arrays and save to disk
            data            = np.array(data)
            dt              = special_dtype(vlen=bytes)
            ev              = np.array([(event.type, event.value) for event in events])
            # specify [lowerBound, upperBound] bandpass filter range
            filterBand      = [0, 60]
            processedData   = preproc.stdPreproc(data, filterBand, hdr)
            with File(fileCalibration,'w') as f:
                # f.create_dataset('targets', data = tmp)
                f.create_dataset('rawData', data = data)
                f.create_dataset('events', data = ev, dtype = dt)
                f.create_dataset('processedData', data = processedData)
                f.create_dataset('cap', data = capfile)
                # f.create_dataset()

            print("End calibration phase")

        elif e.value == "train":
            print("Training classifier")
            # linear detrend, filter, average across epochs
            # to be on the save side I picked a normal range;
            # there is some evidence that P300 is within the theta / alpha band
            # here I choose a wide band pass that would be able to catch it
            # and suppress high frequency noise.
            #model = classification.trainClassifier(fileCalibration, hdr.fSample)
            bufhelp.sendEvent("training","done")

        elif e.value =="test":
            print("Feedback phase")
            keep = True
            while keep:
                data, events, stopevents = bufhelp.gatherdata(["stimulus"],\
                                                            trlen_ms,[("run","end"),\
                                                            ('test', 'end')], \
                                                            milliseconds=True, verbose = False)
                if stopevents.type == 'test' and stopevents.value == 'end':
                    keep = False
                else:
                    # specify [lowerBound, upperBound] bandpass filter range
                    filterBand = [0, 60]
                    # linear detrend, filter, average across epochs
                    processedData = preproc.stdPreproc(data, filterBand, hdr)
                    pred = FeedbackSignals.genPrediction(processedData, model, events)
                    # sanity check
                    print('prediction', pred)
                    bufhelp.sendEvent("classifier.prediction", pred)
                    data = np.array(data)
                    ev              = np.array([(event.type, event.value) for event in events])
                    # save the test phase
                    with File(fileTest,'w') as f:
                        # f.create_dataset('targets', data = tmp)
                        f.create_dataset('rawData', data = data)
                        f.create_dataset('events', data = ev, dtype = dt)
                        f.create_dataset('processedData', data = processedData)
                        # f.create_dataset()

        elif e.value =="exit":
            run = False
        # print(e.value)
        print("Waiting for start event.")