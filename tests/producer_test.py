'''
from ..src.model_producer import *
'''

from .context.proco.model_producer import * 
# TODO : account for id column


#----- generator functions

# TODO : shabby maker
def make_producer(n = None):

    if n == None:
        n = random.randrange(5, 11)

    sa = np.random.randint(5, 500, size = (n, 1))
    ##d = np.random.randint(1, 20, size = (n, 1))
    d = np.zeros((n, 1))

    l0 = np.random.randint(5, 100, size = (n, 1))
    w = np.random.randint(100, 1000, size= (n, 1))
    ids = np.arange(n).reshape((n, 1))

    x = np.hstack((sa, d, l0, w, ids))

    x = np.array(x, dtype = "float64")
    p = Producer(x)
    return p

'''
description :
- makes default model producer w/ net worth equal to `nw`,
  depth is 0 and surface area set to some number for each unit.
'''
def make_model_producer_default(numUnits = 100, surfaceArea = 100, nw = 10 ** 7):

    unitWorth = nw / numUnits
    x = np.zeros((numUnits, 5))
    ids = np.arange(numUnits)
    x[:, 4] = ids # set ids
    x[:, 0] += surfaceArea # set sa
    x[:, 3] += unitWorth # set unit worth
    x[:, 2] += unitWorth
    p = ModelProducer(x)
    return p

def make_unit(id = 1):

    sa = random.randrange(5, 500)
    d = random.randrange(1, 11)
    l0 = random.randrange(5, 500)
    w = random.randrange(500, 5000)

    x = np.array([sa, d, l0, w, id], dtype = "float64")
    return x

def make_bad_unit0(id = 1):

    sa = random.randrange(5, 500)
    d = 0
    l0 = random.randrange(-500, -5)
    w = l0

    x = np.array([sa, d, l0, w, id], dtype = "float64")
    return x

'''
used for testing `recalibrate_networth`
'''
def make_bad_unit_negworth(id = 1):

    sa = random.randrange(5, 500)
    d = random.randrange(1, 20)
    l0 = random.randrange(250, 500)
    w = random.randrange(-250, 1)
    return np.array([sa, d, l0, w, id], dtype = "float64")

#--------
'''
test pos. and neg.


+ : log down
- : log up (more than +!)
'''
def test_reproduce_unitworth_depth():

    # testing changes in shape
    results = {'depths': [], 'percent_increase' : []}
    ##unitWorth = 10000
    p = make_producer()
    ##p.producerInfo[0] = make_bad_unit_negworth()
    x = p.producerInfo[0]

    d = 0
    x[1] = 0
    while d < 32:
        y = Producer.reproduce_unitworth(x, 2)
        results['depths'].append(d)
        results['percent_increase'].append(y / x[3])
        d += 0.1
        x[1] = d

    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'depths',  y = 'percent_increase',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of shape on percentage change in worth")
    plt.show()
    return

'''
test pos. and neg.

+ : linear up
- : linear down
'''
def test_reproduce_unitworth():
    # testing changes in shape
    results = {'worth': [], 'new_worth' : []}
    depth = 2

    p = make_producer()
    x = p.producerInfo[0]
    x[3] = 10

    while x[3]  < 10000:
        y = Producer.reproduce_unitworth(x, 2)
        results['worth'].append(x[3])
        #results['percent_increase'].append(y / x[3])
        results['new_worth'].append(y)
        x[3]  += 100

    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'worth',  y = 'new_worth',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of current worth on new worth")
    plt.show()
    return

def test_recalibrate_0layer():
    pi0 = np.array([[3, 2, 40, 50],\
            [5, 8, -2, 30],\
            [12, 1, -20, 2]], dtype = "float64")
    print("#-----------------------------------------------------------")
    print("before")
    for p in pi0:
        print("*", p)
    print()

    Producer.recalibrate_0layer(pi0)
    print("after")
    for p in pi0:
        print("*", p)
    print("#-----------------------------------------------------------")
    print()

def test_recalibrate_networth():
    pi = make_producer().producerInfo

    # make [0], [1] bad units
    pi[0] = make_bad_unit_negworth()
    pi[1] = make_bad_unit_negworth()

    print("#-----------------------------------------------------------")
    print("[x] before")
    print(pi)
    print("#-----------------------------------------------------------")
    print("[x] after")
    Producer.recalibrate_networth(pi)
    print(pi)
    print("#-----------------------------------------------------------")



def test_get_cost_clean():

    netWorth = 100
    ui0 = np.array([250, 0, 0, 0], dtype = "float64")
    ui1 = np.array([250, 100, 10, -100], dtype = "float64")
    ui2 = np.array([250, 100, 10, -50], dtype = "float64")

    c0 = Producer.get_cost_clean(ui0, netWorth)
    print("cost given 0 :\t", c0)

    c1 = Producer.get_cost_clean(ui1, netWorth)
    print("cost given 100 :\t", c1)

    c2 = Producer.get_cost_clean(ui2, netWorth)
    print("cost given 50 :\t", c2)


def test_duplicate():
    ui0 = np.array([250, 100, 10, 100], dtype = "float64")
    duplicates = Producer.duplicate_unit(ui0)
    print("duplicates :\n")
    print(duplicates)

'''
tests the cost of taxation on different surface areas
'''
def test_get_cost_taxation():
    p = make_producer()

    results = {'total_surface_area': [], 'taxation' : []}
    for _ in range(15):
        t = Producer.get_cost_taxation(p.producerInfo, p.netWorth) # taxation
        ts = np.sum(p.producerInfo[:, 0]) # total surface area

        results['total_surface_area'].append(ts)
        results['taxation'].append(t / p.netWorth)

        p.producerInfo[:, 0] = p.producerInfo[:, 0] * RF

    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'total_surface_area',  y = 'taxation',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of surface area on taxation")
    plt.show()

'''
description :
- preliminary testing of method `get_cost_rot`
'''
def test_get_cost_rot():
    p = make_producer()

    p.producerInfo[0] = make_bad_unit_negworth(p.producerInfo[0, 4])
    p.producerInfo[-1] = make_bad_unit_negworth(p.producerInfo[-1, 4])

    # TODO : delete

    print("* producer unit")
    print(p.producerInfo)

    nw = Producer.get_networth(p.producerInfo)

    cost = Producer.get_cost_rot(p.producerInfo, nw)

    print()
    print("* cost of rot :\t", cost)

'''
description :
- see method name
'''
def test_get_cost_stunt():

    # for testing single case
    """
    p = make_producer()
    print("* producer unit")
    print(p.producerInfo)

    print("* net worth")
    print(nw)
    print()

    print("* cost of stunt")
    x = Producer.get_cost_stunt(p.producerInfo, nw)
    print(x)
    print()
    """


    """
    print("* normalized cost of stunt")
    x = Producer.get_cost_stunt_measure(p.producerInfo, nw)
    print(x)
    print()
    """

    # for plotting relation of depth to stunt
    p = make_producer()
    results = {'depth': [], 'stunt' : []}
    x = 0

    while x < 32:
        t = Producer.get_cost_stunt(p.producerInfo, p.netWorth)

        td = np.sum(p.producerInfo[:, 1]) # total depth
        results['depth'].append(td)
        results['stunt'].append(t)

        p.producerInfo[:, 1] = p.producerInfo[:, 1] + .1
        x += 0.1

    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'depth',  y = 'stunt',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of depth on stunting effects")
    plt.show()

def test_get_cost_potential_risk():

    # compare producers:
    # sa_1 : 1 (split evenly)
    # sa_2 : 1/2 (split evenly)

    p = make_producer()
    # ---------------------------------------------------------

    results = {'total_surface_area': [], 'risk' : []}
    for _ in range(15):
        r = Producer.get_cost_potential_risk(p.producerInfo) # taxation
        ts = np.sum(p.producerInfo[:, 0]) # total surface area

        results['total_surface_area'].append(ts)
        results['risk'].append(r / p.netWorth)

        p.producerInfo[:, 0] = p.producerInfo[:, 0] * RF

    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'total_surface_area',  y = 'risk',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of surface area on risk")
    plt.show()

#---------------------------------------------#

'''
incomplete
'''
def test_spread_or_enrich_it():

    p = make_producer()

    c = np.array(random.choices(np.arange(p.producerInfo.shape[0]), k = 2))

    # test : increase surface area
    print("indices :\t", c)
    print("before increase surface area :\n")
    print(p.producerInfo)
    p. spread_or_enrich_it(c, mode = 'spread', increase = True)
    print("\nafter increase surface area :\n")
    print(p.producerInfo)
