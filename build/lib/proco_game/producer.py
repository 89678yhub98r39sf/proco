from .constants import *

class Producer:

    SELF_LOG_X = {'risk' : [], 'delta_risk' : [],\
        'tax' : [], 'delta_tax' : [],\
        'growth' : [], 'delta_growth' : [],\
        'consumer_power' : [], 'delta_consumer_power' : [],\
        'cost_measure' : [], 'delta_cost_measure' : [],\
        'rot' : [], 'delta_rot' : [],\
        'stunt' : [], 'delta_stunt' : [],\
        'delta_networth' :[]}

    SELF_LOG_Y = {'COST_ROT_THRESHOLD' : [], 'COST_TAX_THRESHOLD' : [],\
        'COST_RISK_THRESHOLD' : [], 'COST_STUNT_THRESHOLD' : [],\
        'CONSUMER_POWER_THRESHOLD' : [], 'VOLATILITY' : []}


    # the controller variables 
    COST_ROT_THRESHOLD = 0.2 # clean up
    COST_TAX_THRESHOLD = TAX * 2 # surface area down
    COST_RISK_THRESHOLD = RISK * 2 # surface area up

    COST_STUNT_THRESHOLD = 0.6 # depth down
    CONSUMER_POWER_THRESHOLD = 0.8  # depth up

        # in the event of some standard being violated, the degree to which to act
    VOLATILITY = 1.0 # value between -1 and 1 inclusive
    CURRENT_ID = None

    CLEANED_CACHE = []

    def __init__(self, producerInfo, loggingDepth = 5):
        self.producerInfo = producerInfo
        self.loggingDepth = loggingDepth # number of past rounds to keep in log

        self.netWorth = Producer.get_networth(self.producerInfo)
        self.averageUnitWorth = Producer.get_average_unitworth(self.producerInfo)

        self.CURRENT_ID = np.max(self.producerInfo[:, 4]) + 1
        self.dead = False

    '''
    description :
    - calculates the average unit worth

    arguments :
    - producerInfo : see class variable

    return :
    - float, mean unit worth
    '''
    @staticmethod
    def get_average_unitworth(producerInfo):
        return np.mean(producerInfo[:, 3])

    @staticmethod
    def get_networth(producerInfo):
        return round(np.sum(producerInfo[:, 3]), ROUNDING_DEPTH)

    #------ MAINTENANCE METHODS
    '''
    description :
    - method is to be used after modification to `producerInfo`;
      checks for any negative or 0 values in units and removes them.
    - ex. : after consumer moves;
    '''
    ##
    @staticmethod
    def recalibrate_0layer(producerInfo):
        for x in producerInfo:
            # if layer 0 <= 0 and depth is greater than 0
            if x[2] <= 0 and x[1] > 0:
                x[1] = x[1] - 1 # decrease depth
                x[3] += x[2] # decrease net worth
                x[2] = x[3] / (x[1] +1) # set new depth-0 worth

    '''
    description :
    - method is to be used after changes to unit[3], checks to see
      if worth is >= 0-layer, modifies if isn't.
    - changes depth to 0, layer-0 equal to unit worth.
    - ex. use : after costs due to tax, risk, maintenance.
    '''
    ##
    @staticmethod
    def recalibrate_networth(producerInfo):
        for x in producerInfo:
            if x[3] < x[2]:
                x[2] = x[3]
                x[1] = 0

            # depth is 0, layer 0 must equal net worth
            elif x[3] > x[2] and x[1] == 0:
                x[2] = x[3]

    '''
    description :
    - gets the cost to remove the unit; less negative units are
      more expensive to remove

    - UPDATE : cost of cleaning is scaled by reproductive factor.
    '''
    ## TODO : work on cost of cleaning
    @staticmethod
    def get_cost_clean(unitInfo, netWorth):

        assert unitInfo[3] <= 0, "cannot clean out positive unit!"
        return - unitInfo[3] * RF

    # END MAINTENANCE METHODS ----------#


    ##
    '''
    description :
    - given unit, reproduces it w.r.t. depth (higher the depth, higher the cost of tax)

    arguments :
    - unitInfo : 5-list, unit in `producerInfo`
    - rf : int, reproductive factor

    return :
    - float, updated unit worth
    '''
    @staticmethod
    def reproduce_unitworth(unitInfo, rf):
        # factors to consider :
        '''
        tax occurs on depth : higher the depth higher the tax
        '''
        uw = None
        if unitInfo[3] >= 0:
            uw = unitInfo[3] * rf
            uw = uw * (1 - TAX)** unitInfo[1]
            return uw
        else:
            uw = unitInfo[3] * rf
            uw = - (-uw) * (1 + TAX) ** unitInfo[1]
        return uw

    '''
    description :
    - duplication produces RF units with total worth equal to 1/RF * originalWorth
    - each unit will have 0-depth, 1/RF * originalSutest_spread_or_enrich_itrfaceArea
    - one of the duplicates will have the same id as the original
      and the other ones will not.

    return :
    - RF x 4 matrix, duplicate offspring
    '''
    ##
    def duplicate_unit(self, unitInfo):
        newNetWorth = unitInfo[3] / RF
        worthPerUnit = newNetWorth / RF
        saPerUnit = unitInfo[0] / RF
        newUnit = np.array([[saPerUnit, 0, worthPerUnit, worthPerUnit]],\
            dtype="float64")

        repeats = np.repeat(newUnit, repeats = [RF], axis=0)
        idCol = np.zeros((repeats.shape[0], 1))
        repeats = np.hstack((repeats, idCol))
            # add back original id
        repeats[0, 4] = unitInfo[4]

        for i in range(1, repeats.shape[0]):
            repeats[i, 4] = self.CURRENT_ID
            self.CURRENT_ID += 1

        return repeats


    '''
    description :
    - increases surface area of unit by factor of RF
    '''
    ##
    @staticmethod
    def spread_unit(unitInfo, increase = True):
        if increase :
            return unitInfo[0] * RF
        else:
            return unitInfo[0] / RF

    '''
    description :
    - increases depth of unit by factor of RF
    '''
    ## TODO : find a good scaling factor (denum) for enrichment
    @staticmethod
    def enrich_unit(unitInfo, increase = True):
        if increase :
            # if zero : just make RF
            if unitInfo[1] == 0:
                unitInfo[1] = RF
            else:
                unitInfo[1] = unitInfo[1] * (1 + RF / 10)
        else:
            unitInfo[1] = unitInfo[1] / (1 - RF / 10)

        return unitInfo[1]

    #----- methods to calculate current measures to compare
    #      with controller variables

    ## this is tentative
    '''
    description :
    - gets the cost of taxation given current surface areas of units
    - units with greater surface area result in higher tax costs

    - arbitrary rule
    -- z = total surface area
    -- set scaling factor F to 10 ** 10
    -- taxation = net_worth * (TAX * (1 + z / F))
    '''
    @staticmethod
    def get_cost_taxation(producerInfo, netWorth, array = True):
        # this is arbitrary scaling factor
        scalingFactor = 10 ** 4

        # get total surface area
        '''
        tsa = np.sum(producerInfo[:, 0])
        taxation = netWorth * (TAX * (1 + tsa / scalingFactor))
        '''
        # get taxation
        taxation = producerInfo[:, 3] * (TAX * (1 + producerInfo[:, 0] / scalingFactor))

        if array:
            return taxation

        return np.sum(taxation)

    '''
    description :
    - this method is to be called immediately after consumer moves

    return :
    - float, between 0 and 1 inclusive
    '''
    #?
    @staticmethod
    def get_consumer_power(consumerOutput, netChangeInWorth):
        return abs(safe_divide(netChangeInWorth, consumerOutput))

    '''
    description :
    - applies function `get_cost_clean` over all info

    return :
    - float
    '''
    #?
    @staticmethod
    def get_cost_rot(producerInfo, netWorth):
        # get non-positive units
        pi = producerInfo[producerInfo[:, 3] <= 0]
        if pi.shape[0] == 0: return 0

        # apply funcstochastically
        s = np.apply_along_axis(Producer.get_cost_clean, 1, pi, netWorth)

        return np.sum(s)

    ##
    '''
    description :
    - given producerInfo and and its net worth, gets adjust growth (w.r.t. depth),
      returns ratio of adjusted growth / potential growth
    - WARNING : adjusted growth may be smaller than the original value.

    arguments :
    - producerInfo : n x 5 array, representation of producer's assets
    - netWorth : float, total worth of `producerInfo`

    return :
    - float, <= 1, adjusted growth / potential growth
    '''
    @staticmethod
    def get_cost_stunt(producerInfo, netWorth):
        potential = netWorth * RF
        actual = np.apply_along_axis(Producer.reproduce_unitworth, 1, producerInfo, RF)

        return 1 - safe_divide(np.sum(actual), potential)

    @staticmethod
    def get_cost_potential_risk_(unitInfo):
        costRisk = safe_divide((RISK_EFFECTS * unitInfo[3]), log(unitInfo[0]))
        return abs(costRisk)

    ##
    @staticmethod
    def get_cost_potential_risk(producerInfo, array = True):
        if producerInfo.shape[0] == 0: return 0

        potentialCosts = np.apply_along_axis(Producer.get_cost_potential_risk_, 1, producerInfo)
        if array:
            return potentialCosts * RISK

        return np.sum(potentialCosts) * RISK

    #--------------------------------------------------------------------
    '''
    re-analyze measures the ratios for the below variables;
    excludes CONSUMER_POWER_THRESHOLD
    '''
    def analyze(self):
        # update net worth
        self.netWorth = Producer.get_networth(self.producerInfo)

        # get measures

            # cost of rot needs to be divided by next round's potential worth
        rotRatio = safe_divide(Producer.get_cost_rot(self.producerInfo, self.netWorth),  (self.netWorth * RF))
            # set arbitrary scaling factor
        taxationRatio = safe_divide(Producer.get_cost_taxation(self.producerInfo, self.netWorth, array = False), self.netWorth)
            # RISK_EFFECTS is arbitrary
        riskRatio = safe_divide(Producer.get_cost_potential_risk(self.producerInfo, array = False), self.netWorth)
        stuntRatio = Producer.get_cost_stunt(self.producerInfo, self.netWorth)

        analysis = {'rot' : rotRatio, 'tax' : taxationRatio,\
            'risk' : riskRatio, 'stunt' : stuntRatio}

        self.pre_log(analysis)
        return analysis

    """
    description :
    - calculates measures for possibly changing the depth of producer units.
    - measures are : consumer power, cost measure.
    - consumer power : consumer_input / producer_networth_change
    - cost measure : producer_actual_growth / producer_potential_growth
    """
    def re_analyze(self, consumerOutput, netChangeInWorth):

        # check if duplication is necessary
        costMeasure = Producer.get_cost_stunt(self.producerInfo, self.netWorth)

        return {"consumer_power" : Producer.get_consumer_power(consumerOutput, netChangeInWorth),\
            "cost_measure" : costMeasure}

    #--------------------------------------------------------------------

    ###### BELOW NEEDS TO BE TESTED!
    #------ METHODS USED FOR REORGANIZATION.

    # TODO : update networth?
    '''
    description :
    - if producerInfo has negative net worth or is empty, then dead
    '''
    def check_dead(self):
        if self.producerInfo.shape[0] == 0: return True

        # CAUTION
        if self.netWorth <= 0: return True
        return False

    '''
    description :
    - chooses units based on criteria

    arguments :
    - criteria : `surface_area`, `clean`, `number_of_units`

    return :
    - array, indices of choices
    '''
    def choose_units_(self, criteria = 'surface_area'):
        #
        results = None
        if criteria == 'surface_area':
            results = self.producerInfo[:, 0].argsort()
        elif criteria == 'clean':
                # sort ascending order (worth)
            self.producerInfo = self.producerInfo[self.producerInfo[:, 3].argsort()]
            results = np.where(self.producerInfo[:, 3] <= 0)[0]
        else:
            results = self.producerInfo[:, 1].argsort()
        return results

    '''
    cleans out x proportion of negative units based on volatility
    '''
    def clean_it(self, indices):

        indices = np.where(self.producerInfo[:, 3] <= 0)[0]

        # empty case
        if indices.shape[0] == 0: return

        # get choices based on volatility
        if self.VOLATILITY < 0:
            indices = indices[::-1]
        numUnits = ceil(indices.shape[0] * abs(self.VOLATILITY))
        choices = indices[:numUnits]

        # get choices and their cost
        target = self.producerInfo[choices]
        cost = Producer.get_cost_rot(target, self.netWorth)

        # clean and charge cost
        self.producerInfo = np.delete(self.producerInfo, choices, axis = 0)

        # TODO : 0-case

        # minus cost
        if self.producerInfo.shape[0] != 0:
            costPerUnit = cost / self.producerInfo.shape[0]
            self.producerInfo[:, 3] -= costPerUnit

        # recalibrate
        Producer.recalibrate_networth(self.producerInfo)

        # TODO
        # add cleaned units to cache
        # this is to be synchronized with consumer.

        self.CLEANED_CACHE = target[:, 4]

        # update networth
        self.netWorth = Producer.get_networth(self.producerInfo)

    '''
    description :
    - increases the surface area/depth of x number of units based on VOLATILITY
    '''
    def spread_or_enrich_it(self, indices, mode = 'spread', increase = True):
        # 0-case
        if indices.shape[0] == 0 : return

        # get choices based on volatility
        if self.VOLATILITY < 0:
            indices = indices[::-1]

        # get choices
        numUnits = ceil(indices.shape[0] * abs(self.VOLATILITY))
        choices = indices[:numUnits]

        if mode == 'spread':
            change = np.apply_along_axis(Producer.spread_unit, 1, self.producerInfo[choices], increase)
            change = change.reshape((1, change.shape[0]))
            self.producerInfo[choices, 0] = change
        else:
            change  = np.apply_along_axis(Producer.enrich_unit, 1, self.producerInfo[choices], increase)
            change = change.reshape((1, change.shape[0]))
            self.producerInfo[choices, 1] = change

    def reorganize(self, decision, logFile = LOGFILE_P):

        # spread (surface area)
        #      no change in networth
        if decision['spread'] == 1 or decision['spread'] == -1:
            indices = self.choose_units_(criteria = 'surface_area')

            if decision['spread'] == 1:
                self.spread_or_enrich_it(indices, mode = 'spread', increase = True)
            else:
                self.spread_or_enrich_it(indices, mode = 'spread', increase = False)

        self.netWorth = Producer.get_networth(self.producerInfo)

        # shrink depth if need be
        #   no change in networth
        if decision['grow'] == 1:
            indices = self.choose_units_(criteria = 'number_of_units')
            self.spread_or_enrich_it(indices, mode = 'enrich', increase = False)
        self.netWorth = Producer.get_networth(self.producerInfo)

        # remove negatives
        # TODO : should  be at top?
        if decision['clean'] == 1:
            indices = self.choose_units_(criteria = 'clean')
            self.clean_it(indices)

        # update net worth
        self.netWorth = Producer.get_networth(self.producerInfo)


    # reproduction
    def reproduce(self):
        newWorths = np.apply_along_axis(Producer.reproduce_unitworth, 1, self.producerInfo, RF)
        prevWorth = copy.deepcopy(self.netWorth) # is the copy necessary?

        # update new net worth
        self.producerInfo[:, 3] = newWorths
        Producer.recalibrate_networth(self.producerInfo)

        self.netWorth = Producer.get_networth(self.producerInfo)

        self.SELF_LOG_X['growth'].append(self.netWorth / prevWorth - 1)

        if len(self.SELF_LOG_X['risk']) >= 2:
            self.SELF_LOG_X['delta_growth'].append(safe_divide(self.SELF_LOG_X['growth'][-1], self.SELF_LOG_X['growth'][-2]))
        else:
            self.SELF_LOG_X['delta_growth'].append(0)


    '''
    description :
    - this is for calculating actual risk this round
    '''
    def get_actual_risk(self):
        # choose units to incur risk
        indices = []
        for i in range(self.producerInfo.shape[0]):
            if random.random() <= RISK:
                indices.append(i)

        risk = Producer.get_cost_potential_risk(self.producerInfo[indices])
        return indices, risk

    '''
    description :
    - deducts expenses from actual risk and taxation.
    '''
    def deduct_expenses(self):
        # get expenses
        indices, risks = self.get_actual_risk()
        taxation = Producer.get_cost_taxation(self.producerInfo, self.netWorth)

        # deduct
        self.producerInfo[indices, 3] -= risks
        self.producerInfo[:, 3] -= taxation

        self.netWorth = Producer.get_networth(self.producerInfo)

        # recalibrate
        Producer.recalibrate_networth(self.producerInfo)

        # update net worth
        self.netWorth = Producer.get_networth(self.producerInfo)
        return np.sum(risks), np.sum(taxation)


    '''
    description :
    - logs y-values for training data

    arguments :
    - dictionary, see return of method `re_analyze`
    '''
    def pre_log(self, analysis):

        # risk
        self.SELF_LOG_X['risk'].append(analysis['risk'])
        # rot
        self.SELF_LOG_X['rot'].append(analysis['rot'])
        # tax
        self.SELF_LOG_X['tax'].append(analysis['tax'])
        # stunt
        self.SELF_LOG_X['stunt'].append(analysis['stunt'])

        if len(self.SELF_LOG_X['risk']) >= 2:
            self.SELF_LOG_X['delta_risk'].append(safe_divide(self.SELF_LOG_X['risk'][-1], self.SELF_LOG_X['risk'][-2]))
            self.SELF_LOG_X['delta_rot'].append(safe_divide(self.SELF_LOG_X['rot'][-1], self.SELF_LOG_X['rot'][-2]))
            self.SELF_LOG_X['delta_tax'].append(safe_divide(self.SELF_LOG_X['tax'][-1], self.SELF_LOG_X['tax'][-2]))
            self.SELF_LOG_X['delta_stunt'].append(safe_divide(self.SELF_LOG_X['stunt'][-1], self.SELF_LOG_X['stunt'][-2]))
        else:
            self.SELF_LOG_X['delta_risk'].append(0)
            self.SELF_LOG_X['delta_rot'].append(0)
            self.SELF_LOG_X['delta_tax'].append(0)
            self.SELF_LOG_X['delta_stunt'].append(0)

    '''
    description :
    - logs y-values for training data

    arguments :
    - dictionary, see return of method `re_analyze`
    '''
    def post_log(self, reanalysis):
        self.SELF_LOG_X['consumer_power'].append(reanalysis['consumer_power'])
        self.SELF_LOG_X['cost_measure'].append(reanalysis['cost_measure'])

        if len(self.SELF_LOG_X['risk']) >= 2:
            self.SELF_LOG_X['delta_consumer_power'].append(safe_divide(self.SELF_LOG_X['consumer_power'][-1], self.SELF_LOG_X['consumer_power'][-2]))
            self.SELF_LOG_X['delta_cost_measure'].append(safe_divide(self.SELF_LOG_X['cost_measure'][-1], self.SELF_LOG_X['cost_measure'][-2]))
        else:
            self.SELF_LOG_X['delta_consumer_power'].append(0)
            self.SELF_LOG_X['delta_cost_measure'].append(0)

        self.SELF_LOG_Y['COST_ROT_THRESHOLD'].append(self.COST_ROT_THRESHOLD)
        self.SELF_LOG_Y['COST_TAX_THRESHOLD'].append(self.COST_TAX_THRESHOLD)
        self.SELF_LOG_Y['COST_RISK_THRESHOLD'].append(self.COST_RISK_THRESHOLD)
        self.SELF_LOG_Y['COST_STUNT_THRESHOLD'].append(self.COST_STUNT_THRESHOLD)
        self.SELF_LOG_Y['CONSUMER_POWER_THRESHOLD'].append(self.CONSUMER_POWER_THRESHOLD)
        self.SELF_LOG_Y['VOLATILITY'].append(self.VOLATILITY)

    '''
    description :
    - clear logs; to be used after each run of world.
    '''
    def clear_logs(self):

        for k in self.SELF_LOG_X.keys():
            self.SELF_LOG_X[k] = []

        for k in self.SELF_LOG_Y.keys():
            self.SELF_LOG_Y[k] = []

        self.CLEANED_CACHE = []
