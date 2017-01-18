import numpy as np
import sklearn
import sklearn.svm, sklearn.linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.multiclass import OneVsRestClassifier
from sklearn.preprocessing import MultiLabelBinarizer
from h5py import File
from pylab import *


def trainClassifier(file, fSample):
    erpTarget, erpStimulus, cat, labels = binarizeData(file, fSample)
    model = LogReg(cat, labels)
    return model


def LogReg(data, events):
    lr = LogisticRegression()
    lr.fit(data, events)
    return lr


def SVM(data, events, type = 'target'):
    idxOfType       = np.where(events[:, 0] == type)[0]
    eventType       = events[idxOfType, :]
    dataType        = data[idxOfType, :, :]

    reshapedDataType = dataType.reshape(dataType.shape[0],\
                                        dataType.shape[1] *
                                        dataType.shape[2])

    uniqueLabels         = sorted(list(set(eventType[:, 1])))
    label_to_int         = dict((l, i) for i, l in enumerate(uniqueLabels))
    int_to_char          = dict((i, l) for i, l in enumerate(uniqueLabels))
    convertedLabels      = []
    for label in eventType[:, 1]:
        convertedLabels.append([label_to_int[label]])

    tmp = np.array(convertedLabels)

    test = MultiLabelBinarizer().fit_transform(tmp)

    # print(test)
    # print(eventType[:,1])
    from sklearn import svm
    model = OneVsRestClassifier(
        svm.SVC(class_weight='balanced', probability=1))
    # print(eventType[:,1].shape)
    model.fit(reshapedDataType, test)
    # returns trained model
    return model, reshapedDataType, eventType




if __name__ == '__main__':
    from h5py import File
    from preproc import  stdPreproc
    with File('../Data/calibration_subject_4.hdf5') as f:
        for i in f:
            print(i)
        data = f['processedData'].value
        rawData = f['rawData'].value
        cap = f['cap'].value
        events = f['events'].value

    model, reshapedData, tmp = SVM(data, events)
    modelERN, _, eventTarget = SVM(data, events, type='feedback')

    out = modelERN.predict(reshapedData)
    print(out[:5], eventTarget[:5, 1])
    idx = 20
    # print(out[:idx], tmp[:idx,1])
    fig, ax = subplots()

    # print(model.predict_proba(reshapedData))
