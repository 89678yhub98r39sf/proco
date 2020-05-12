'''
this file is to train data to make smart consumers and producers.

files are :
* consumer_training
* producer_training


TODO : train producer
'''

from .consumer import *
from sklearn.multioutput import MultiOutputRegressor
from sklearn.ensemble import GradientBoostingRegressor



# read consumer training data
def train_consumer():
    cdf = pd.read_csv(CONSUMER_TRAINING)

    xs = ['risk', 'delta_risk', 'grat_payoff', 'delta_grat_payoff',\
        'inv_payoff', 'delta_inv_payoff', 'surface_area_risk_factor',\
        'delta_surface_area_risk_factor']

    ys = ['GREED', 'FOCUS', 'SPEND', 'INVEST']

    cx, cy = cdf[xs], cdf[ys]

    '''
    will use multi-output regressor
    '''
    model = MultiOutputRegressor(GradientBoostingRegressor(random_state=0)).fit(cx, cy)

    # clear CMODEL_FILE
    open(CMODEL_FILE, 'w').close()
    pickle.dump(model, open(CMODEL_FILE, 'wb'))
