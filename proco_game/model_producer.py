from .producer import *

class ModelProducer(Producer):

    def __init__(self, producerInfo, loggingDepth = 5):
        super().__init__(producerInfo, loggingDepth)

    '''
    description :
    - decides how producer should choose based on analysis
    - if contradiction : choose the greater in need.

    arguments :
    - analysis : dictionary, see `Producer.analyze`

    return :
    - dictionary : decision
    '''
    def decide_best_0(self, analysis):

        decision = {"spread" : None, 'clean' : None, 'grow' : None}

        # to clean up
        if analysis['rot'] >= self.COST_ROT_THRESHOLD:
            decision['clean'] = 1
        else:
            decision['clean'] = 0

        # surface area spread
            # contradiction
        if analysis['risk'] >= self.COST_RISK_THRESHOLD and\
            analysis['tax'] >= self.COST_TAX_THRESHOLD:

            risk_ = safe_divide(analysis['risk'], self.COST_RISK_THRESHOLD)
            tax_ = safe_divide(analysis['tax'], self.COST_TAX_THRESHOLD)

            if risk_ > tax_:
                decision['spread'] = 1
            else:
                decision['spread'] = -1
        elif analysis['risk'] >= self.COST_RISK_THRESHOLD:
            decision['spread'] = 1
        elif analysis['tax'] >= self.COST_TAX_THRESHOLD:
            decision['spread'] = -1
        else:
            decision['spread'] = 0

        # grow
        if analysis['stunt'] >= self.COST_STUNT_THRESHOLD:
            decision['grow'] = 1
        else:
            decision['grow'] = 0

        return decision

    '''
    description :
    - moves one round;
    - analyses situation, makes decision, reorganize accordingly, then reproduce

    arguments :
    - world : World, the world self lives in
    - logFile : string, file path of verbose logging;

    return :
    - None

    '''
    def move_one(self, world, logFile = LOGFILE_P):
        # clean
        # reorg.
        # reprod.
        # non-consumer costs
        nw0 = self.netWorth

        lf = open(logFile, 'a')

        # reset cache
        self.CLEANED_CACHE = []

        lf.write("\n\t\t--------------PRODUCER MOVING ONE---------------\n")
        lf.write("* total surface area :\t{}\n".format(np.sum(self.producerInfo[:, 0])))
        lf.write("* total depth :\t{}\n".format(np.sum(self.producerInfo[:, 1])))
        lf.write("* total worth :\t{}\n".format(np.sum(self.producerInfo[:, 3])))

        # update net worth
        lf.write("* net worth :\t{}\n".format(self.netWorth))
        self.netWorth = Producer.get_networth(self.producerInfo)

        # analyze and get decision
        analysis = self.analyze()

        lf.write("\n* analysis : \n")
        for k, v in analysis.items():
            lf.write("{}\t{}\n".format(k, v))
        lf.write('\n')

        decision = self.decide_best_0(analysis)
        lf.write("\n* decision : \n")
        for k, v in decision.items():
            lf.write("{}\t{}\n".format(k, v))
        lf.write('\n')

        # reorganize
        self.reorganize(decision)

        self.netWorth = Producer.get_networth(self.producerInfo)

        # sync cleaned units with consumer's possessions
        world.sync_cleaned(self.CLEANED_CACHE)

        # reproduce
        self.reproduce()

        # tax, risk
        nw = self.netWorth
        risks, taxation = self.deduct_expenses()

        # update networth
        lf.write('net worth after deductions :\t{}\n'.format(self.netWorth))
        lf.write("* risk / net worth :\t{}\n".format(safe_divide(risks, nw)))
        lf.write("* taxation /net worth :\t{}\n".format(safe_divide(taxation, nw)))

        x = self.producerInfo[self.producerInfo[:, 3] <= 0].shape[0]
        lf.write("* number of negs :\t{}\n".format(x))
        lf.write("________________________________________________\n")
        lf.close()

        self.round_values()
        self.SELF_LOG_X['delta_networth'].append(self.netWorth / nw0)

    '''
    description :
    - changes depth if consumer buying power reaches above CONSUMER_POWER_THRESHOLD
    '''
    def re_analyze(self, consumerOutput, netChangeInWorth, logFile = LOGFILE_P):

        lf = open(logFile, 'a')

        lf.write("\n\t*reanalysis\n")

        # update net worth
        self.netWorth = Producer.get_networth(self.producerInfo)

        # get reanalysis
        reanalysis = super().re_analyze(consumerOutput, netChangeInWorth)

        for k, v in reanalysis.items():
            lf.write("{}\t{}\n".format(k, v))
        lf.write("\n")

        self.post_log(reanalysis)

        indices = self.choose_units_(criteria = 'number_of_units')

        # increase depth
            # contradiction
        if reanalysis["consumer_power"] >= self.CONSUMER_POWER_THRESHOLD and\
        reanalysis["cost_measure"] >= self.COST_STUNT_THRESHOLD:

            power = safe_divide(reanalysis["consumer_power"], self.CONSUMER_POWER_THRESHOLD)
            stunt = safe_divide(reanalysis["cost_measure"], self.COST_STUNT_THRESHOLD)

            if power > stunt:
                # increase depth
                self.spread_or_enrich_it(indices, mode = 'enrich', increase = True)
                lf.write("increasing depth\n")
                lf.write("* after depth increase :\t{}\n".format(np.sum(self.producerInfo[:, 1])))
            else:
                # duplicate to decrease depth
                self.duplicate(indices)
                lf.write("duplicating\n")
                lf.write("* after duplication :\t{}\n".format(self.netWorth))

        elif reanalysis["consumer_power"] >= self.CONSUMER_POWER_THRESHOLD:
            self.spread_or_enrich_it(indices, mode = 'enrich', increase = True)
            lf.write("increasing depth\n")
            lf.write("* after depth increase :\t{}\n".format(np.sum(self.producerInfo[:, 1])))

        elif reanalysis["cost_measure"] >= self.COST_STUNT_THRESHOLD:
                # duplicate to decrease depth
                self.duplicate(indices)
                lf.write("duplicating\n")
                lf.write("* after duplication :\t{}\n".format(self.netWorth))

        lf.write("---------------------------------------\n")
        lf.close()

    '''
    description :
    - makes duplication of the following units specified by `indices`
    - duplication occurs when >= COST_STUNT_THRESHOLD

    arguments :
    - indices : array, list of indices of producer units
    '''
    def duplicate(self, indices):

        # empty case
        if indices.shape[0] == 0: return

        # order choices based on volatility
        if self.VOLATILITY < 0:
            indices = indices[::-1]

        # get choices
        numUnits = ceil(indices.shape[0] * abs(self.VOLATILITY))
        choices = indices[:numUnits]

        # get targets to duplicate
        toDuplicate = np.copy(self.producerInfo[choices])

        # delete those targets
        self.producerInfo = np.delete(self.producerInfo, choices, axis = 0)

        # duplicate
        duplications = None
        for x in toDuplicate:
            dups = self.duplicate_unit(x)

            if duplications is not None:
                duplications = np.vstack((duplications, dups))
            else:
                duplications = dups

        # add back to producer
        self.producerInfo = np.vstack((self.producerInfo, duplications))

        # update net worth
        self.netWorth = Producer.get_networth(self.producerInfo)


    '''
    simulates moving one;
    possible use for non-ml producer training.
    '''
    @staticmethod
    def simulate_move_one(modelProducer):
        return

    def round_values(self):
        self.producerInfo = np.round(self.producerInfo, ROUNDING_DEPTH)
