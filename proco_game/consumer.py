'''
gratification payoff happens n rounds after purchase :

default is set to 3.
'''

from .constants import *
from .model_producer import *

class Consumer:

    ACTIVITY_LOG = {}

    # ids of owned units : careful!
    OWNED_UNITS = np.array([])
    OWNED_UNITS_INVESTED_WORTH = np.array([]) # this is the amount of worth put in after owned (past 0)
    OWNED_UNITS_SURFACE_AREA = np.array([])

    GRATIFICATION_PAYOFF = {1 : 0, 2 : 0, 3 : 0} # this is the amount to be paid off to consumer next round

    GREED = 0.2 # + for ascending, - for descending, proportion of net worth for current round
    FOCUS = 0.4 # proportion of spendings for this round towards current possessions
    SPEND = 1.5 # value >= 1, scale of worth to put into each new purchase
    INVEST = 1.5 # value >= 1, scale of worth to put into each owned unit.


    '''
    ----- these are some important variables to consider for logging
    - risk : potential risk (calculated in the same way as producer)
    - greed : percentage of worth spent this round
    - grat. payoff
    - investment payoff

    ----- below variables are the y-variables (may also be used as x-variables)
    greed
    focus
    spend
    invest
    '''

    SELF_LOG_X = {'risk' : [], 'delta_risk' : [], 'grat_payoff' : [], \
                'delta_grat_payoff' : [], 'inv_payoff' : [],\
                'delta_inv_payoff' : [], 'new_investments' : [],\
                'surface_area_risk_factor' : [],\
                'delta_surface_area_risk_factor' : [], 'delta_wealth' : []}

    SELF_LOG_Y = {'GREED' : [], 'FOCUS' : [], 'SPEND' : [],\
        'INVEST' : []}

    def __init__(self, wealth):
        self.wealth = wealth
        self.loggingDepth = 5
        self.bankrupt = False
        self.newInvestments = 0 # int, number of new investments

    '''
    description :
    - adds value to payoff at key 1, and shifts other values to the right.
      assumes value at key 3 already added to `wealth`
    '''
    ##
    def add_to_grat_payoff(self, v):
        values = list(self.GRATIFICATION_PAYOFF.values())[:-1]

        self.GRATIFICATION_PAYOFF[1] = v
        for i, v_ in enumerate(values):
            self.GRATIFICATION_PAYOFF[i + 2] = v_

    '''
    description :
    - gets money to spend based on wealth and greed
    '''
    def get_to_spend(self):
        if abs(self.GREED) > 1:
            return self.wealth
        # zero case
        if round(self.wealth, 2) < 0.1:
            return self.wealth

        return abs(self.GREED) * self.wealth

    #-------------------------------------------
    '''
    description :
    - helper to reorder the units of producer
    '''
    # TODO : unused, merge with other cod
    def reorder_producer(producer):
        # reorder units
        indices = producer.producerInfo[:, 3].argsort()

        # descending order
        if GREED < 0:
            indices = indices[::-1]
        producer.producerInfo = producer.producerInfo[indices]
    #-------------------------------------------

    '''
    description :
    - method subtracts consumer's worth from producerUnit's net worth.
      Takes into account the producerUnit's depth.
    - subtraction goes layer by layer of depth : the outermost layer
      has the greatest defense.
    - helper method for method `buy_possession`

    arguments :
    - producerUnit : 5-list, unit from producer
    - worth : float, amount to put into this producerUnit

    return :
    - 5-list, updated producer unit
    '''
    @staticmethod
    def deduct_from_unit(producerUnit, worth):

        # base case : no money to spend
        if worth <= 0 :
            return producerUnit

        # case : purchased, invest and return
        if round(producerUnit[2], ROUNDING_DEPTH) <= 0 and round(producerUnit[3], ROUNDING_DEPTH) <= 0\
            and round(producerUnit[1], ROUNDING_DEPTH) <= 0:
            producerUnit[2] -= worth
            producerUnit[3] -= worth
            return producerUnit

        # get normalized value of producerUnit at layer 0
        normedVal = producerUnit[2] * (1 + (TAX * 3)) ** producerUnit[1]

        # purchase layer and proceed
        if normedVal < worth:

            # case : > 0 depth
            if producerUnit[1] > 0:
                producerUnit[3] -= producerUnit[2] # deduct from net worth
                producerUnit[2] = producerUnit[3] / producerUnit[1] # adjust 0 layer
                producerUnit[1] -= 1 # decrease depth

            # deduct all
            else:
                producerUnit[3] = 0
                producerUnit[2] = 0

            worth -= normedVal
            return Consumer.deduct_from_unit(producerUnit, worth)

        # deduct the normalized worth from normed val
        else:

            # get ratio of cost / normed cost
                ## ??
            scalingFactor = safe_divide(producerUnit[2], normedVal) # s / l
            # this is the value that gets subtracted from producer unit
            toDeduct = worth * scalingFactor
            producerUnit[2] -= toDeduct
            producerUnit[3] -= toDeduct
            return producerUnit

    '''
    description :
    - chooses currently owned units to add to;
    - CAUTION: these units must be synced with producer.

    arguments :
    - worth : float, maximum amount to spend

    return :
    - remainder
    '''
    def invest_possession(self, producer, worth):
        # 0-owned case
        if len(self.OWNED_UNITS) == 0: return worth

        # sort units by invested worth
        sortedInd = self.OWNED_UNITS_INVESTED_WORTH.argsort()
            # descending or ascending order based on greed
        if self.GREED < 0:
            sortedInd = sortedInd[::-1]

        self.OWNED_UNITS = self.OWNED_UNITS[sortedInd]
        self.OWNED_UNITS_INVESTED_WORTH = self.OWNED_UNITS_INVESTED_WORTH[sortedInd]
        self.OWNED_UNITS_SURFACE_AREA = self.OWNED_UNITS_SURFACE_AREA[sortedInd]

        # search for ids
        ## temporary sol'n
        ## TODO : possible bug here.
        '''
        do not throw error for missing values.
        '''
        searchInd = search_list_in_list0(self.OWNED_UNITS, producer.producerInfo[:, 4], False)

        # get owned units
        owned = producer.producerInfo[searchInd]

        # if owned is less than 0:
        if owned.shape[0] == 0:
            ##print("len of owned units is {} but in prod. is {}".format(len(self.OWNED_UNITS), 0))
            return worth

        # iterate through and add worth /
        done = False
        testTotal = 0 # to do : delete
        while not done:
            for i, x in enumerate(owned):
                # get amount to put into this unit
                if worth <= 1:
                    toInvest = worth
                else:
                    toInvest = min(worth, self.OWNED_UNITS_INVESTED_WORTH[i] * self.INVEST)
                    if toInvest == 0:
                        toInvest = worth

                # remember to copy this back!
                owned[i, [2, 3]] = owned[i, [2,3]] - toInvest
                self.OWNED_UNITS_INVESTED_WORTH[i] = self.OWNED_UNITS_INVESTED_WORTH[i] + toInvest

                worth -= toInvest
                worth = round(worth, ROUNDING_DEPTH)

                if worth <= 0:
                    done = True
                    break

        # round owned units info
        self.round_possessions()

        # recalibrate the changed units and update
        Producer.recalibrate_0layer(owned)
        Producer.recalibrate_networth(owned)
        producer.producerInfo[searchInd] = owned

        return 0

    def round_possessions(self):
        self.OWNED_UNITS = np.round(self.OWNED_UNITS, ROUNDING_DEPTH)
        self.OWNED_UNITS_SURFACE_AREA = np.round(\
            self.OWNED_UNITS_SURFACE_AREA, ROUNDING_DEPTH)
        self.OWNED_UNITS_INVESTED_WORTH = np.round(\
            self.OWNED_UNITS_INVESTED_WORTH, ROUNDING_DEPTH)


    def buy_possession(self, producer, worth,logFileC = LOGFILE_C):

        lfc = open(logFileC, 'a')

        lfc.write("----------- CONSUMER MOVES ----------\n")
        lfc.write("\t\t------------buying possession---------\n")

        # get non-owned units
            # order
        producer.producerInfo = producer.producerInfo[producer.producerInfo[:, 3].argsort()]
            # get non-zero
        indices = np.where(producer.producerInfo[:, 3] > 0)[0]

        # reverse order depending on GREED
        if self.GREED < 0:
            indices = indices[::-1]

        if indices.shape[0] == 0:
            lfc.write('* ATTENTION : no available possessions to buy\n')
            lfc.close()
            return

        # iterate through and buy
        indicesOfInterest = np.array([])
        originalWorths = np.copy(producer.producerInfo[:, 3])

        #---------------------------------
        indicesOfInterest = self.buy_targets(producer, indices, worth, indicesOfInterest)
        #---------------------------------

        if indicesOfInterest.shape[0] == 0:
            lfc.write('* ATTENTION : could not buy any\n')
            lfc.close()
            return

        z = np.where(producer.producerInfo[indicesOfInterest, 3] <= 0)[0]
        purchasedIndices = indicesOfInterest[z]

        # get original purchased worths : this is gratification payoff
        ## TODO : maybe gratification payoff should be scheduled for n rounds after
        gratPayOff = np.sum(originalWorths[purchasedIndices])
        self.add_to_grat_payoff(gratPayOff)

        # get ids
        ids = producer.producerInfo[purchasedIndices, 4]

        # get investment values
        inv = np.abs(producer.producerInfo[purchasedIndices, 3])

        # get surface areas
        sa = np.abs(producer.producerInfo[purchasedIndices, 0])

        self.OWNED_UNITS = np.append(self.OWNED_UNITS, ids)
        self.OWNED_UNITS_INVESTED_WORTH = np.append(self.OWNED_UNITS_INVESTED_WORTH, inv)
        self.OWNED_UNITS_SURFACE_AREA = np.append(self.OWNED_UNITS_SURFACE_AREA, sa)

        # round possessions
        self.round_possessions()

        lfc.write("* new ids\n")
        lfc.write("{}\n".format(ids))
        lfc.write("* current investments\n")
        lfc.write("{}\n".format(self.OWNED_UNITS))

        lfc.write("\n* new investments\n")
        lfc.write("{}\n".format(inv))
        lfc.write("* current investments\n")
        lfc.write("{}\n".format(self.OWNED_UNITS_INVESTED_WORTH))

        lfc.write("\n* surface areas of new investments\n")
        lfc.write("{}\n".format(sa))
        lfc.write("* all surface areas of investments\n")
        lfc.write("{}\n".format(self.OWNED_UNITS_SURFACE_AREA))

        lfc.close()

    '''
    description :
    - helper method for `buy_possession`

    return :
    - array, indices of interest (bought or attempted to buy) from target indices
    '''
    def buy_targets(self, producer, targetIndices, worth, indicesOfInterest):
        done = False

        for i in targetIndices:
            # get amount to spend tfor this unit
            toSpend = min(worth,  abs(producer.producerInfo[i, 3] * self.SPEND))

            # if amount to spend is 0 : make it worth / len(indicesOfInterest)
            if toSpend - 0.1 <= 0:
                toSpend = safe_divide(worth, indicesOfInterest.shape[0])

            # spend money on unit
            updatedUnit = Consumer.deduct_from_unit(producer.producerInfo[i], toSpend)
            updatedUnit = updatedUnit.reshape((1, updatedUnit.shape[0]))
            updatedUnit = np.round(updatedUnit, ROUNDING_DEPTH)

            # recalibrate here!
            Producer.recalibrate_0layer(updatedUnit)
            Producer.recalibrate_networth(updatedUnit)

            # log purchase
                # get normalized spendings (w.r.t. depth)
            producer.producerInfo[i] = updatedUnit

            # log index
            indicesOfInterest = np.append(indicesOfInterest, i)

            # update worth
            worth -= toSpend
            worth = round(worth, ROUNDING_DEPTH)

            if worth - 0.1 <= 0.1:
                done = True
                break

        if done:
            return np.array(list(set(indicesOfInterest)), dtype = 'int64')
        else:
            return self.buy_targets(producer, targetIndices, worth, np.array(list(set(indicesOfInterest))))

    '''
    description :
    - chooses units of producer to consume and further invest in

    arguments :
    - producer : Producer

    return :
    - float,consumer expenses
    - float, producer change in net worth
    '''
    def move_one(self, producer, logFileC = LOGFILE_C, logFileP = LOGFILE_P):

        originalNumUnits = self.OWNED_UNITS.shape[0]

        nw0 = producer.netWorth # get original net worth

        lfc = open(logFileC, 'a')

        # get amount to spend
        lfc.write("\n\t\t-------------spendings-----------------\n")

        lfc.write("* total net worth :\t{}\n".format(self.wealth))
        toSpendTotal = self.get_to_spend()

        lfc.write("* amount to spend :\t{}\n".format(toSpendTotal))

        # get potential risk
        potentialRisk = self.get_potential_risk(self.OWNED_UNITS_INVESTED_WORTH, self.OWNED_UNITS_SURFACE_AREA)
        potentialRisk_ = safe_divide(potentialRisk, self.wealth)

            # on units already owned
        ## TODO : warning if FOCUS above 1
        toSpendPossession = toSpendTotal * min(self.FOCUS, 1)
        toSpendNew = toSpendTotal - toSpendPossession

            # invest
        lfc.write("** maximum allocation for investment :\t{}\n".format(toSpendPossession))
        leftover = self.invest_possession(producer,toSpendPossession)

        toSpendNew += leftover

            # buy new
        self.buy_possession(producer, toSpendNew)

            # deduct spendings from consumer wealth
        self.wealth -= toSpendTotal

        ## TODO update producer networth
        producer.netWorth = Producer.get_networth(producer.producerInfo)
        changeNetWorth = abs(producer.netWorth - nw0)

        # producer reanalysis
        producer.re_analyze(toSpendTotal, changeNetWorth, logFile = logFileP)

        # get consumer payoff this round
        lfc.write("\t\t\n-------------payoffs and deductions-----------------\n")

        lfc.write("\n* wealth before payoff :\t{}\n".format(self.wealth))
        gratPayOff, invPayOff = self.payoff()

        gratPayOff_, invPayOff_ = safe_divide(gratPayOff, self.wealth),\
                    safe_divide(invPayOff, self.wealth)

        lfc.write("* wealth after payoff :\t{}\n".format(self.wealth))

        # get surface area risk factor
        sarf = np.sum(self.OWNED_UNITS_SURFACE_AREA)

        # deduct risk
        self.deduct_risk_actual()
        self.round_values()


        lfc.write("* wealth after deduction :\t{}\n".format(self.wealth))
        lfc.write("_________________________________________\n\n")

        # log info
        changeWealth = safe_divide(self.wealth - nw0, nw0)
        self.pre_log(changeWealth, potentialRisk_, gratPayOff_, invPayOff_, sarf, originalNumUnits)
        self.post_log()

        lfc.close()


    # TODO
    '''
    description :
    - payoffs for consumer takes into account both gratification and
      investments

    arguments :
    - actual : boolean, specifies whether payoff is real (adds to wealth)

    return :
    - float : pay off of gratitude
    - float : pay off of investment
    '''
    def payoff(self, actual = True):
        # get value of gratification payoff
        gratPayOff = self.GRATIFICATION_PAYOFF[3]

        # get value of investment payoff
        invPayOff = np.sum(self.OWNED_UNITS_INVESTED_WORTH) * RF

        ##print("----------- consumer payoff -----------")
        ##print("* gratification payoff :\t", gratPayOff)
        ##print("* owned units :\t", len(self.OWNED_UNITS))
        ##print("* investment payoff :\t", invPayOff)
        ##print()
        ##print("------------------------------")

        if actual:
            self.wealth += (gratPayOff + invPayOff)
        return gratPayOff, invPayOff

    '''
    description :
    - checks consumer wealth for bankruptcy
    '''
    def check_bankruptcy(self):
        if self.wealth <= 0: return True
        return False

    def round_values(self):
        self.wealth = round(self.wealth, ROUNDING_DEPTH)

    def get_delta(self, key):

        if len(self.SELF_LOG_X[key]) > 1:
            diff = self.SELF_LOG_X[key][-1] - self.SELF_LOG_X[key][-2]
            return safe_divide(diff, self.SELF_LOG_X[key][-2])
        else:
            return 0

    #---------------------
    '''
    description :
    - logs data
    '''
    def pre_log(self, deltaWealth, potentialRisk, gratPayOff, investmentPayOff, surfaceAreaRiskFactor, originalNumUnits):

        # new investments
        self.SELF_LOG_X['new_investments'].append(self.OWNED_UNITS.shape[0] - originalNumUnits)

        # TODO
        # change in net worth
        self.SELF_LOG_X['delta_wealth'].append(deltaWealth)

        # risk
        self.SELF_LOG_X['risk'].append(potentialRisk) #self.get_potential_risk(self.OWNED_UNITS_INVESTED_WORTH, self.OWNED_UNITS_SURFACE_AREA)
        self.SELF_LOG_X['delta_risk'].append(self.get_delta('risk'))

        # grat. payoff
        self.SELF_LOG_X['grat_payoff'].append(gratPayOff)
        self.SELF_LOG_X['delta_grat_payoff'].append(self.get_delta('grat_payoff'))

        # inv. payoff
        self.SELF_LOG_X['inv_payoff'].append(investmentPayOff)
        self.SELF_LOG_X['delta_inv_payoff'].append(self.get_delta('inv_payoff'))

        # surface area risk factor
        self.SELF_LOG_X['surface_area_risk_factor'].append(surfaceAreaRiskFactor)
        self.SELF_LOG_X['delta_surface_area_risk_factor'].append(self.get_delta('surface_area_risk_factor'))

    def post_log(self):
        self.SELF_LOG_Y['GREED'].append(self.GREED)
        self.SELF_LOG_Y['FOCUS'].append(self.FOCUS)
        self.SELF_LOG_Y['SPEND'].append(self.SPEND)
        self.SELF_LOG_Y['INVEST'].append(self.INVEST)

    #---------------------

    '''
    description :
    - calculation of risk is the same as producer

    return :
    - float, cost of risk
    '''
    def deduct_risk_actual(self):

        indices = []

        # get owned units to incur risk
        for i in range(self.OWNED_UNITS_SURFACE_AREA.shape[0]):
            if random.random() <= RISK:
                indices.append(i)

        # get cost of risk
        risk = self.get_potential_risk(self.OWNED_UNITS_INVESTED_WORTH[indices], self.OWNED_UNITS_SURFACE_AREA[indices])

        # deduct from wealth
        self.wealth -= risk

        return risk# TODO

    '''
    description :
    - calculates the potential risk given some investments and their corresponding surface areas

    arguments :
    - investWorths : array, n-length
    - surfaceAreas : array, n-length

    return :
    - float, potential risk
    '''
    def get_potential_risk(self, investWorths, surfaceAreas):
        risks = RISK_EFFECTS * safe_divide(investWorths, np.log(surfaceAreas))
        totalCost = np.sum(risks)
        return totalCost


    def clear_logs(self):

        for k in self.SELF_LOG_X.keys():
            self.SELF_LOG_X[k] = []

        for k in self.SELF_LOG_Y.keys():
            self.SELF_LOG_Y[k] = []

        self.OWNED_UNITS = np.array([])
        self.OWNED_UNITS_INVESTED_WORTH = np.array([]) # this is the amount of worth put in after owned (past 0)
        self.OWNED_UNITS_SURFACE_AREA = np.array([])
