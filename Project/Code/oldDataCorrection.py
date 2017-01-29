from h5py import File
import numpy as np
import preproc
import classification
import visualize
file = '../Data/calibration_subject_4.hdf5'

with File(file, 'r') as f:
    for i in f: print(i)

    events = f['events'].value
    rawData = f['rawData'].value
    cap  = f['cap'].value


uniques = np.unique(events[:, 0])
data = {}
ev   = {}
for unique in uniques:
    eventIdx = np.where(events[:, 0] == unique)
    data[unique] = rawData[eventIdx, ...].squeeze()
    ev[unique]   = events[eventIdx,...].squeeze()
dataIM = data['target']
eventsIM = ev['target']

eventsERN = ev['feedback']
dataERN = data['feedback']

procDataIM, _  = preproc.stdPreproc(dataIM, [0,30], 250)
procDataERN, _ = preproc.stdPreproc(dataERN,[0,30], 250)
print(procDataIM.shape, eventsIM.shape)

# visualize.plotERP(procDataIM, eventsIM, cap, fSample = 250)
classification.SVM(procDataIM, eventsIM, fft = 1)
classification.SVM(procDataERN[:, :120,:], eventsERN, fft = 0)