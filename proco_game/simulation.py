'''
this is a slightly different variation of above method `make_world_2`;
instead of having different arguments for consumer and producer, all
the args. are in a dictionary arg. d
'''

from .world import *


# variables are used for random generation of arguments
## producer initialization
SIZE_SPACE = np.linspace(1, 1000, 1000)
TOTAL_SURFACE_AREA_SPACE = np.linspace(1000, 10 ** 6, 1000)
NETWORTH_SPACE = np.linspace(10 **4, 10 ** 7, 1000)

## producer controller variables
COST_ROT_THRESHOLD_SPACE = np.linspace(0.0, 1, 100)
COST_TAX_THRESHOLD_SPACE = np.linspace(0.0, 1, 100)
COST_RISK_THRESHOLD_SPACE = np.linspace(0.0, 1, 100)
COST_STUNT_THRESHOLD_SPACE = np.linspace(0.0, 1, 100)

# consumer initialization
WEALTH_SPACE = np.linspace(10 ** 3.5, 10 ** 6.5, 1000)

# consumer controller variables
GREED_SPACE = np.linspace(0.0, 1, 100)
FOCUS_SPACE = np.linspace(0.0, 1, 100)
SPEND_SPACE = np.linspace(0.0, 1, 100)
INVEST_SPACE = np.linspace(0.0, 1, 100)


def make_world_specified(d, consumer = None, producer = None, model = None):

    if consumer is None:
        # no model, just consumer
        if model is None:
            consumer = Consumer(d['wealth'])
        else:
            consumer = SmartConsumer(d['wealth'], model = model)

    consumer.GREED = d['GREED']
    consumer.FOCUS = d['FOCUS']
    consumer.SPEND = d['SPEND']
    consumer.INVEST = d['INVEST']

    # clear logs
    consumer.clear_logs()

    # producer will have
    # identical surface area, depth 0, layer-0 and net worth
    if producer is None:
        producerInfo = np.zeros((int(d['size']), 5))
        producerInfo[:, 0] = d['totalSurfaceArea'] / d['size']
        producerInfo[:, 2] = d['netWorth'] / d['size']
        producerInfo[:, 3] = d['netWorth'] / d['size']
        producerInfo[:, 4] = np.arange(d['size'])
        producer = ModelProducer(producerInfo)
    else:
        print("* Using given producer :\t", producer)

    producer.COST_ROT_THRESHOLD = d['COST_ROT_THRESHOLD']
    producer.COST_TAX_THRESHOLD = d['COST_TAX_THRESHOLD']
    producer.COST_RISK_THRESHOLD = d['COST_RISK_THRESHOLD']
    producer.COST_STUNT_THRESHOLD = d['COST_STUNT_THRESHOLD']

    # clear producer logs
    producer.clear_logs()

    w = World(producer, consumer)
    return w


'''
method generates a dictionary of random arguments used for
making a World; this is a helper method for above `make_world_specified`
'''
def make_random_arguments():

    d = {}
    d['size'] = int(random.choice(SIZE_SPACE))
    d['totalSurfaceArea'] = random.choice(TOTAL_SURFACE_AREA_SPACE)
    d['netWorth'] = random.choice(NETWORTH_SPACE)
    d['COST_ROT_THRESHOLD'] = random.choice(COST_ROT_THRESHOLD_SPACE)
    d['COST_TAX_THRESHOLD'] = random.choice(COST_TAX_THRESHOLD_SPACE)
    d['COST_RISK_THRESHOLD'] = random.choice(COST_RISK_THRESHOLD_SPACE)
    d['COST_STUNT_THRESHOLD'] = random.choice(COST_RISK_THRESHOLD_SPACE)
    d['wealth'] = random.choice(WEALTH_SPACE)
    d['GREED'] = random.choice(GREED_SPACE)
    d['FOCUS'] = random.choice(FOCUS_SPACE)
    d['SPEND'] = random.choice(SPEND_SPACE)
    d['INVEST'] = random.choice(INVEST_SPACE)
    return d


'''
description :
- method runs n matches between consumer and producer. Option to pick either
  SmartConsumer or Consumer. Goes against randomly constructed producers.

arguments :
- c : Consumer (if user wants to play) or None (SmartConsumer)
- n : number of matches against producer.
'''
def test_smart_consumer(c = None, n = 100):

    def reset_spec(c, d):
        c.GREED = d['GREED']
        c.FOCUS = d['FOCUS']
        c.SPEND = d['SPEND']
        c.INVEST = d['INVEST']
        return c

    model = None
    d = {}
    # spectator mode : watch smart consumer
    if c is None:
        model = pickle.load(open(CMODEL_FILE, 'rb'))
    else:
        d['GREED'] = c.GREED
        d['FOCUS'] = c.FOCUS
        d['SPEND'] = c.SPEND
        d['INVEST'] = c.INVEST

    scoreboard = {'CONSUMER' : 0, 'PRODUCER' : 0, None : 0}

    d = make_random_arguments()
    
    # smart consumer if there is a model
    w = make_world_specified(d, consumer = c, producer = None, model = model)

    for _ in range(n):

        w.move_n(n = None)
        scoreboard[w.winner] += 1

        # reset arguments for consumer if not smart
        if c:
            c = reset_spec(c, d)

        # make random arguments for the next world
        d = make_random_arguments()

        w = make_world_specified(d, consumer = c, producer = None, model = model)

        # clear logs for consumer
        w.co.clear_logs()



    print("scoreboard\n")
    print(scoreboard)
    return scoreboard
