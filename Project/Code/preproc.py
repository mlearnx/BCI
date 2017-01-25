from __future__ import division, print_function
import numpy as np
import scipy
import sklearn
from pylab import *
from h5py import File
def detrend(data, dim = 1, type = "linear"):
    '''Removes trends from the data.

    Applies the scipy.scipy.signal.detrend function to the data, this numpy function
    offers to types of detrending:

    linear - the result of a linear least-squares fit to data is subtracted
    from the data.
    constant - the mean of the data is subtracted from the data.

    Parameters
    ----------
    data : list of datapoints (numpy arrays) or a single numpy array.
    dim : the axis along which detrending needs to be applied
    type : a string that indicates the type of detrending should either
    be "linear" or "constant"

    Returns
    -------
    out : a clone of data on wich the detrending algorithm has been applied

    Examples
    --------
    >>> data, events = f250tc.getData(0,100)
    >>> data = preproc.detrend(data,type="constant")
    >>> data = bufhelp.gatherdata("start",10,"stop")
    >>> data = preproc.detrend(data)
    '''


    X = scipy.signal.detrend(data, axis=dim)

    return X
def badChannelRemoval(data, x = 3):
    '''
    assumes data is event, time, channels
    returns array of data that should be analyzed
    '''
    std = np.std(data)
    # filter with x standard deviations
    events, time, badChans = np.where(abs(data) <  x * std) # bug fixed, i did the  reverse selection!
    # set all channels to useablewith File(fileCalibration) as f:
                # testData = np.array(testData)
                # f.create_dataset('test', data = testData)

    useable = np.ones(data.shape[-1], dtype = bool)

    # if there is an outlier dont use that channel
    useable[np.unique(badChans)] = True
    return useable


def butterFilter(data, band, N = 2, hdr = 100, dim = 1, filter_type = 'lowpass'):
    '''
    Simple butter worth filter
    filter defaults to the first axis (assumes time)
    '''
    if type(hdr) == int:
        fs = hdr
    else:
        fs = hdr.fSample
    band = np.array(band) / float(fs)
    if len(band) == 2:
        filter_type = 'bandpass'

    b, a = scipy.signal.butter(N = N, Wn = band, btype = filter_type)
    fdata = scipy.signal.filtfilt(b,a, data, method = 'gust', axis = dim)
    return fdata


import numpy as np

def plotERP(binnedData, cap):
    '''
    Takes as input a dictionary mapping the event value to the corresponding data
    Data should have format trials x time x channels
    '''
    erps  = []  # erp stoarage
    label = []  # labels for plotting
    # get the labels and erp data
    for eventType, eventData in binnedData.iteritems():
        if eventType == 'negative' or eventType == 'positive':
            label.append(eventType)
            erps.append(mean(eventData, 0))
    nChans = eventData.shape[-1]
    erps = np.array(erps)

    if nChans % 2 == 0:
        nRows = nCols =  nChans / 2
    else:
        nRows = (nChans + 1) // 2
    nCols = nChans// nRows

    fig, axs = subplots(nrows = int(nRows),
                        ncols = int(nCols), sharex = 'all', sharey = 'all')
    fig.add_subplot(111, frameon=False)

    t = np.linspace(0, 600, erps.shape[1]) # manual edit
    print(t.shape)
    # plot erps per channel
    for idx, ax in enumerate(axs.flatten()):
        [ax.plot(t, erp[:,idx]) for erp in erps]
        ax.set_title(cap[idx, 0])  # first index is the name


    ax.legend(label, ncol = erp.shape[0],
            loc = 'upper center', bbox_to_anchor = (-.15, -.5)) # centers under all subplots
    ylab = 'mV'
    xlab = 'Time[ms]'
    xlabel(xlab, fontsize = 20)
    ylabel(ylab, fontsize = 20)
    tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    # fig.text(.05, .5, ylab, rotation = 90, fontsize = 20) # ylabel
    # fig.text(.5 - 1/(float(2*len(xlab))), .06, xlab, fontsize = 20)
    print(1/float(len(xlab)))
    # savefig('../Figures/ERP_Lisa.png')
    show()


def eventSeparator(data, events):
    '''
    Returns dictionary of key = event value, item = data corresponding to key
    '''
    uniqueEvents  = np.unique(events[:, 1])
    eventStorage  = {}
    for i, event in enumerate(uniqueEvents):
        idx                   = np.where(events[:,1] == event)  # find corresponding indices
        eventStorage[event]   = data[idx, :, :].squeeze()       # squeeze out the 0 dimension
    return eventStorage



def car(data):
  '''
  Return a common average reference (CAR) spatial filter for n channels.
  The common average reference is a re-referencing scheme that is
  commonly used when no dedicated reference is given. Since the
  average signal is subtracted from each sensor's signal, it reduces
  signals that are common to all sensors, such as far-away noise.
  Parameters
  ----------
  n : int
    The number of sensors to filer.
  Returns
  -------
  W : array
    Spatial filter matrix of shape (n, n) where n is the number of
    sensors. Each row of W is single spatial filter.
  Examples
  --------
  >>> car(4)
  array([[ 0.75, -0.25, -0.25, -0.25],
         [-0.25,  0.75, -0.25, -0.25],
         [-0.25, -0.25,  0.75, -0.25],
         [-0.25, -0.25, -0.25,  0.75]])
  '''
  n = data.shape[-1]
  W = np.eye(n) - 1 / float(n)
  return  data.dot(W)

def stdPreproc(data, band,  hdr, cap = None):
    '''
    Function performs:
            Detrends the data
            Removes bad channels
            Filters the data
    '''

    data        = detrend(data)                       # detrend
    # plotERP(data, events, cap)
    # data        = scipy.signal.detrend(data,          # re-referencing
    #                              axis = 2,
    #                              type = 'constant')
    # tmp = data.reshape(data.shape[0], -1)
    data        = car(data)                     # spatial filter
    useable     = badChannelRemoval(data)       # remove bad channels
    data        = data[:, :, useable]           # remove the bad channels
    tmp = sklearn.preprocessing.normalize(data.flatten(), axis = 0)
    data = tmp.reshape(data.shape)

    data        = butterFilter(data,            # temporal filter
                               band = band,
                               hdr = hdr)

    if cap != None:
        print('Removing channels :\n', cap[useable == False])

    return data

def rickerWavelet(binnedData, nWavelet = 20):
    sizeOfWavelets = logspace(.1, 1.7, nWavelet) # this goes to about 50 hz, more weighting on the lower end
    convolutedData = {}
    for type, data in binnedData.iteritems():
        cw = scipy.signal.cwt(data.flatten(), scipy.signal.ricker, sizeOfWavelets)
        cw = cw.reshape(cw.shape[0], data.shape[0], data.shape[1], data.shape[2])   # algorithm expects 1 d array
        convolutedData[type] = cw                                                  # reshape back

    # make figure for negative positive
    fig, axs = subplots(5,2)
    for i, (ax, sensor) in enumerate(zip(axs.flatten(), cap)):
        pos = convolutedData['positive'][:, :, i]
        neg = convolutedData['negative'][:, :, i]
        pos = mean(pos, 1)
        neg = mean(neg, 1)
        im  = ax.imshow( (pos - neg), origin = 'lower',
                  extent = [0, 600, sizeOfWavelets[0], sizeOfWavelets[-1]])
        # print(im)
        colorbar(im, ax = ax)# cax = ax)
        ax.set_title(sensor[0])
    subplots_adjust(hspace = .5)
    fig.suptitle('Pos - neg')
    labels = ['feet', 'left hand', 'right hand', 'rest']
    # make figure for negative positive
    fig, axs = subplots(5,2)
    fig.add_subplot(111)
    for i, (ax, sensor) in enumerate(zip(axs.flatten(), cap)):
        feet      = convolutedData['feet'][:, :, i]
        leftHand  = convolutedData['left hand'][:, :, i]
        rightHand = convolutedData['right hand'][:, :, i]
        rest      = convolutedData['rest'][:, :, i]


        # feet = mean(feet, 1)
        # leftHand = mean(leftHand, 1)
        # rightHand  = mean(rightHand, 1)
        # rest      = mean(rest, 1)
        print(feet.shape)
        data = [feet, leftHand, rightHand, rest]
        for idx, datai in enumerate(data):
            ax.imshow(datai[:,i], origin = 'lower',
            extent = [0, 600, sizeOfWavelets[0], sizeOfWavelets[-1]])

        ax.set_title(sensor[0])
    ax.legend(labels, ncol = len(labels),
            loc = 'upper center', bbox_to_anchor = (-.15, -.5)) # centers under all subplots
    ylab = 'mV'
    xlab = 'Time[ms]'
    xlabel(xlab, fontsize = 20)
    ylabel(ylab, fontsize = 20)
    tick_params(labelcolor='none', top='off', bottom='off', left='off', right='off')
    subplots_adjust(hspace = .5)
    show()







if __name__ == '__main__':
    from scipy import signal
    from h5py import File
    import sklearn.preprocessing
    with File('../Data/calibration_subject_4.hdf5', 'r') as f:
        rawData = f['rawData'].value
        procData = f['processedData'].value
        events  = f['events'].value
        cap     = f['cap'].value

        procData = stdPreproc(rawData, [0, 40], 250 )
        # procData = stdPreproc(rawData,[0, 40], 250, cap)
        # procData = stdPreproc(tmp, [0, 50], 100)
        binnedData = eventSeparator(procData, events)
        plotERP(binnedData, cap)
        # rickerWavelet(binnedData)
        print(binnedData['feet'].shape)
        # plotERP(binnedData, cap)
        # rickerWavelet(binnedData)


        # plotERP(test, events, )
