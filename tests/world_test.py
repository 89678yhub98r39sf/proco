"""
from .consumer_test import *
from ..src.world import *
"""

from .consumer_test import *
from .context.proco.world import *


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


'''
description :
- makes a default world.
'''
def make_world():
    c = make_consumer()
    p = make_model_producer_default()
    return World(p, c)

'''
description :
- constructs a world with specified args. for producer and consumer
'''
def make_world_2(producerInit, producerArgs, consumerInit, consumerArgs):

    c = Consumer(consumerInit)
    c.GREED = consumerArgs['GREED']
    c.FOCUS = consumerArgs['FOCUS']
    c.SPEND = consumerArgs['SPEND']
    c.INVEST = consumerArgs['INVEST']
    for k in c.SELF_LOG_X.keys():
        c.SELF_LOG_X[k] = []

    for k in c.SELF_LOG_Y.keys():
        c.SELF_LOG_Y[k] = []

    # producer will have
    # identical surface area, depth 0, layer-0 and net worth
    producerInfo = np.zeros((producerInit['size'], 5))
    producerInfo[:, 0] = producerInit['totalSurfaceArea'] / producerInit['size']
    producerInfo[:, 2] = producerInit['netWorth'] / producerInit['size']
    producerInfo[:, 3] = producerInit['netWorth'] / producerInit['size']
    producerInfo[:, 4] = np.arange(producerInit['size'])

    p = ModelProducer(producerInfo)
    p.COST_ROT_THRESHOLD = producerArgs['COST_ROT_THRESHOLD']
    p.COST_TAX_THRESHOLD = producerArgs['COST_TAX_THRESHOLD']
    p.COST_RISK_THRESHOLD = producerArgs['COST_RISK_THRESHOLD']
    p.COST_STUNT_THRESHOLD = producerArgs['COST_STUNT_THRESHOLD']
    for k in p.SELF_LOG_X.keys():
        p.SELF_LOG_X[k] = []

    for k in p.SELF_LOG_Y.keys():
        p.SELF_LOG_Y[k] = []

    # world
    w = World(p, c)
    return w

'''
this is a slightly different variation of above method `make_world_2`;
instead of having different arguments for consumer and producer, all
the args. are in a dictionary arg. d
'''
def make_world_specified(d, consumer = None, producer = None, model = None):

    #----
    """
    print()
    print('\t\t**world attributes')
    print(d)
    """
    #-----

    if consumer is None:
        # no model, just consumer
        if model is None:
            consumer = Consumer(d['wealth'])
        else:
            consumer = SmartConsumer(d['wealth'], model = model)
    ##else:
    ##    print("* Using given consumer :\t", consumer)


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
tests average runs given producer and consumer arguments.

prints a scoreboard and the average number of rounds per world at the end
of the run.
'''
def test_average_runs(n = 1):

    producerInit = {'size' : 100,  'totalSurfaceArea' : 20 * 100, 'netWorth' : 10 ** 4}
    producerArgs = {'COST_ROT_THRESHOLD' : 0.5, 'COST_TAX_THRESHOLD' : 0.5, 'COST_RISK_THRESHOLD' : 0.5, 'COST_STUNT_THRESHOLD' : 0.5}

    consumerInit = 10 ** 4
    consumerArgs = {'GREED' : 0.2, 'FOCUS' : 0.5, 'SPEND' : 0.5, 'INVEST' : 0.5}

    scoreboard = {'CONSUMER' : 0, 'PRODUCER' : 0, None : 0}
    rounds = np.array([])

    for i in range(n):

        print("run {}".format(i))
        w = make_world_2(producerInit, producerArgs, consumerInit, consumerArgs)

        w.move_n(n = None)

        scoreboard[w.winner] += 1
        rounds = np.append(rounds, w.round)

    print("scoreboard")
    print(scoreboard)
    print()
    print()
    print("average rounds :\t", np.mean(rounds))

'''
method is to test how the world moves.
'''
def test_move_n():

    # clear log files
    open(LOGFILE_C, 'w')
    open(LOGFILE_P, 'w')

    w = make_world()
        # base
    w.move_n(n = 50)

    print("-------------------------------------")
    print("WINNER :\t", w.winner)
    print("NUMBER OF ROUNDS :\t", w.round)
    print("-------------------------------------")
    return

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
    # smart consumer
    w = make_world_specified(d, consumer = c, producer = None, model = model)
    # default consumer
    ##w = make_world_specified(d, consumer = None, producer = None, model = None)

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
