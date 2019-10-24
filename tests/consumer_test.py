"""
from ..src.smart_consumer import *
from .producer_test import *
"""

from .context.proco.smart_consumer import *
from .producer_test import *

def make_consumer(w = 10 ** 6):

    c = Consumer(w)
    return c

'''
description :
- to ensure consumer spends the proper amount per round.
'''
def test_get_to_spend():
    c = make_consumer()

    # case 1 : greed < 1
    assert c.get_to_spend() == c.GREED * c.wealth, "incorrect wealth!"

    # case 2 : greed >= 1
    c.GREED = 2.6
    assert c.get_to_spend() == c.wealth, "incorrect wealth!"

# TODO : account for rounding error
def test_invest_possession():

    p = make_producer()
    c = make_consumer()

    # assign some ids for consumer to own
        # random units
    o =  random.choices(p.producerInfo[:, 4], k=2)
        # consumer owns them
    c.OWNED_UNITS = np.append(c.OWNED_UNITS, o)

    # make these ids negative
    indices = search_list_in_list0(c.OWNED_UNITS, p.producerInfo[:, 4])

    for i in indices:
        p.producerInfo[i] = make_bad_unit0(p.producerInfo[i, 4])
    p.netWorth = Producer.get_networth(p.producerInfo)

        # assign some random investments into these choices
    i = [random.uniform(5, 300) for j in range(2)]
    c.OWNED_UNITS_INVESTED_WORTH = np.append(c.OWNED_UNITS_INVESTED_WORTH, i)

        # add in surface area info
    c.OWNED_UNITS_SURFACE_AREA = np.append(c.OWNED_UNITS_SURFACE_AREA, p.producerInfo[indices, 0])

    # before investment
    print("\t\t* BEFORE PRODUCER")
    print(p.producerInfo, '\n')
    print("* net worth")
    nw0 = Producer.get_networth(p.producerInfo)
    print(Producer.get_networth(p.producerInfo), "\n")

    print("\n\t\tBEFORE CONSUMER")
    print("* owned")
    print(c.OWNED_UNITS)
    print("* invested worth")
    print(c.OWNED_UNITS_INVESTED_WORTH)
    print("* total investments")
    inv0 = np.sum(c.OWNED_UNITS_INVESTED_WORTH)
    print(inv0)

    # invest here
    c.invest_possession(p, 500)

    # after investment
    print("----------------------------------------------------")
    print("\t\t* AFTER PRODUCER")
    print("* producer")
    print(p.producerInfo, '\n')
    print("* net worth")
    print(Producer.get_networth(p.producerInfo), "\n")

    print("\n\t\tAFTER CONSUMER")
    print("* owned")
    print(c.OWNED_UNITS)
    print("* invested worth")
    print(c.OWNED_UNITS_INVESTED_WORTH)
    print("* total investments")
    inv1 = np.sum(c.OWNED_UNITS_INVESTED_WORTH)
    print(inv1)

    # TODO : remember to update networth!
    assert Producer.get_networth(p.producerInfo) == nw0 - 500, "net worth {} is supposed to be {}".format(\
        Producer.get_networth(p.producerInfo), nw0 - 500)
    assert inv1 == round(inv0 + 500, ROUNDING_DEPTH), "incorrect investment worth {} should be {}".format(inv1, inv0 + 500)


'''
description :
- this test is to display the effects of depth on consumer buying power.
- NO assertions

* NOTE : not bad.
'''
def test_deduct_from_unit():

    # this is to test single unit
    """
    p = make_unit()

    '''
    p[1] = 0
    p[2] = 5000
    p[3] = 5000
    '''

    p_ = np.copy(p)

    print("original unit :\t", p, '\n')
    Consumer.deduct_from_unit(p, worth = 500)
    print("new unit :\t", p, '\n')
    return
    """

    # this is to plot effect of different depths on consumer
    # buying power.
    p = make_unit()
    results = {'depths': [], 'delta_worth' : []}

    print("original worth :\t", p[3])
    for d in range(20):

        p_ = np.copy(p)

        ##print("*", p)

        p_[1] = d

        if d == 0:
            p_[2] = p_[3]

        p_ = Consumer.deduct_from_unit(p_, worth = 500)

        diff = p[3] - p_[3]
        percentDiff = diff / p[3]

        print("depth :\t", d, "\tbefore :\t", p[3], "\tafter :\t", p_[3])
        #print("percent diff :\t", percentDiff, "\tdepth :\t", d)

        results['depths'].append(d)
        results['delta_worth'].append(percentDiff)


    res = pd.DataFrame(results)
    fig = sns.catplot(x = 'depths',  y = 'delta_worth',\
        data = res)

    fig.set_xticklabels(rotation = 90)
    plt.title("Effect of depth on consumer power")
    plt.show()

#-----------------------------------------------------
'''
description :
- checks if `buy_possession` method is feasible

NOTE : okay.
'''
def test_buy_possession():

    p = make_producer()
    c = make_consumer()
    w = 500

    print()
    print("\t\t* BEFORE PRODUCER")
    print("\n* producer :\n", p.producerInfo)
    print("\n* producer net worth :\t", p.netWorth)

    print("\n\n\t\t* BEFORE CONSUMER")
    print("\n* consumer owned :\t", c.OWNED_UNITS)
    print("\n* consumer investments :\t", c.OWNED_UNITS_INVESTED_WORTH)
    inv0 = np.sum(c.OWNED_UNITS_INVESTED_WORTH)

    c.buy_possession(p, w)

    print("----------------------------------------------------")
    print("\t\t* AFTER PRODUCER")
    print("\n* producer :\n", p.producerInfo)
    print("\n* producer net worth :\t", Producer.get_networth(p.producerInfo))

    print("\n\n\t\t* AFTER CONSUMER")
    print("\n* consumer owned :\t", c.OWNED_UNITS)
    print("\n* consumer investments :\t", c.OWNED_UNITS_INVESTED_WORTH)
    inv1 = np.sum(c.OWNED_UNITS_INVESTED_WORTH)

    print("\n\n** investments :\t", inv1 - inv0)
    print()

#---------------------------------------------

def test_add_to_grat_payoff():

    c = make_consumer()
        # make default grat. payoff
    c.GRATIFICATION_PAYOFF[1] = 100
    c.GRATIFICATION_PAYOFF[2] = 200
    c.GRATIFICATION_PAYOFF[3] = 300

    print("gratification before\n")
    print(c.GRATIFICATION_PAYOFF)
    print()

        # add new value
    c.add_to_grat_payoff(1001)

    print("gratification after\n")
    print(c.GRATIFICATION_PAYOFF)
    print()


######
'''
tests to add :

- payoff()
'''
