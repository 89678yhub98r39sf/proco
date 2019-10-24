'''
this script runs n randomized worlds and collects their data into base
data files `con` and `prod`;

these files will be used to train consumer and producer.
'''

from ..tests.world_test import *

def run_n_worlds(n = 5000):

    for _ in range(n):
        d = make_random_arguments()
        w = make_world_specified(d, consumer = None, producer = None, model = None)
        w.move_n()


# collect data
'''
run_n_worlds()
'''

# clean data for consumer training
"""
df = pd.read_csv(CON)

    # get consumer moves that result in
    ## (not enough samples) positive change in wealth
    ## new investments
##df1 = df[df['delta_wealth'] >= 1]
df1 = df[df['new_investments'] >= 1]
df1.to_csv(CONSUMER_TRAINING)
"""

# get producer data
"""
    # get producer moves that result in positive growth
df = pd.read_csv(PROD)
df2 = df[df['delta_networth'] >= 1]

df2.to_csv(PRODUCER_TRAINING)
"""
