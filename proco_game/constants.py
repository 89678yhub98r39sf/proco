from math import ceil, sqrt, log, factorial
import numpy as np
import random
import os
import copy
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys
import pickle
from collections import defaultdict



# get path of data folder
scriptDir = os.path.dirname(__file__) #<-- absolute dir the script is in
relPath = "data"
dataPath = os.path.join(scriptDir, relPath)

# a random number ;)
random.seed()

#----------------------------------------------------
    # standardize rounding error
ROUNDING_DEPTH = 4

# world variables
RF = 2
TAX = 0.08

# occurrence of risk
RISK = 0.15
# starting ratio of cost / worth

    # issue : too small
    # TODO : this is arbitrary
RISK_EFFECTS =  round(RISK * 100, ROUNDING_DEPTH)

# files collect all data during runs
CON = os.path.join(dataPath, 'con')
PROD = os.path.join(dataPath, 'con')

# files are data samples used for training
CONSUMER_TRAINING = os.path.join(dataPath, 'consumer_training')
PRODUCER_TRAINING = os.path.join(dataPath, 'producer_training')

# files are pickled models for consumer and producer
CMODEL_FILE = os.path.join(dataPath, 'consumer_model')
LOGFILE_P = os.path.join(dataPath, 'log_producer.txt')
LOGFILE_C = os.path.join(dataPath, 'log_consumer.txt')


#----------------------------------------------------

'''
normalizes value w.r.t. start and end of range
'''
def normalize_value(value,rStart, rEnd):
    # l-->r
    if rStart <= rEnd:
        assert value >= rStart and value <= rEnd, "invalid range!"
    # r --> l
    else:
        assert value <= rStart and value >= rEnd, "invalid range!"

    diffRange = rEnd - rStart
    diffV = value - rStart
    return round(diffV / diffRange, ROUNDING_DEPTH)


'''
description :
- controller variables have abs. value between 0 and 1 inclusive
'''
def check_controller_variable(value):

    if abs(value) > 1:
        if value < 0:
            value = -1
        else:
            value = 1
        return value

    return value

'''
description :
- method is used for error-free division; division-by-zero will result in 0.

arguments :
- num : float, numerator
- denum : float, denumerator
- safety : float, the value to use for denumerator in the event
           that it is zero.

NOTE : logic is not well-thought out.
'''
def safe_divide(num, denum, safety = 0):
    if type(denum) is not np.ndarray:
        if round(denum, 3) - 0.1 == 0:
            if safety != 0:
                return num / safety
            return 0

        if denum == 0:
            if type(num) is np.ndarray:
                return np.zeros(num.shape)
            return 0

        z = num / denum

        if np.isinf(z):
            return 0

        if np.isnan(z):
            return 0

        return z

    else:
        z = num / denum

        if type(z) is np.ndarray:
            z[np.isnan(z)] = 0
            z[np.isinf(z)] = 0

        return z

'''
description :
- searches for elements in list in another list

arguments :
- l1 : contains elements to be searched for
- l2 : list to be searched

return :
- dict, key is element from l1, value is list containing their indices
'''
def search_list_in_list(l1, l2):
    dicto = defaultdict(list) #dictionary stores all the relevant coordinates
                          #so you don't have to search for them later
    for ind, ele in enumerate(l2):
        if ele in l1:
            dicto[ele].append(ind)
    return dicto

'''
description :
- method builds on top of above
-       checks values (for sync) to make sure no dups
- converts values to integer values

arguments :
- l1 : list w/ elements to search in l2
- l2 : list to search in
'''
def search_list_in_list0(l1, l2, throwErr = True):

    d = search_list_in_list(l1, l2)

    r = []
    for e in l1:
        if e in d:
            r.append(d[e][0])
        else:
            if throwErr:
                raise ValueError("Missing value during search!")
    return r
