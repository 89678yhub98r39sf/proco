from .consumer import *

class SmartConsumer(Consumer):

    def __init__(self, wealth, model):
        super().__init__(wealth)
        self.model = model

    '''
    first determines values of controller variables, then moves.

    consumer has access to to the following variables :
    `risk`, `grat_payoff`, `inv_payoff`, and `surface_area_risk_factor`.

    consumer must choose values for :
    * GREED
    * FOCUS
    * SPEND
    * INVEST
    '''
    def move_one(self, producer, logFileC = LOGFILE_C, logFileP = LOGFILE_P):

        originalNumUnits = self.OWNED_UNITS.shape[0]
        nw0 = producer.netWorth # get original net worth

        # make prediction
        new_values = self.model.predict([self.get_info()])

        self.GREED, self.FOCUS, self.SPEND, self.INVEST =\
            new_values[0, 0], new_values[0, 1], new_values[0, 2], new_values[0, 3]

        super().move_one(producer, logFileC, logFileP)

    def get_info(self):

        # calculate potential risk
        potentialRisk = self.get_potential_risk(self.OWNED_UNITS_INVESTED_WORTH, self.OWNED_UNITS_SURFACE_AREA)
        potentialRisk_ = safe_divide(potentialRisk, self.wealth)

        # calculate expected payoffs
        gratPayOff, invPayOff = self.payoff(actual = False)

            # scale them
        gratPayOff_, invPayOff_ = safe_divide(gratPayOff, self.wealth),\
                    safe_divide(invPayOff, self.wealth)

        # get surface area risk factor
        sarf = np.sum(self.OWNED_UNITS_SURFACE_AREA)

        # get deltas
        if len(self.SELF_LOG_X['risk']) > 0:
            deltaPotentialRisk = safe_divide(potentialRisk_, self.SELF_LOG_X['delta_risk'][-1])
            deltaGratPayoff = safe_divide(gratPayOff_, self.SELF_LOG_X['delta_grat_payoff'][-1])
            deltaInvPayoff = safe_divide(invPayOff_, self.SELF_LOG_X['delta_inv_payoff'][-1])
            deltaSARF = safe_divide(sarf, self.SELF_LOG_X['delta_surface_area_risk_factor'][-1])
        else:
            deltaPotentialRisk = 0
            deltaGratPayoff = 0
            deltaInvPayoff = 0
            deltaSARF = 0

        return [potentialRisk_, deltaPotentialRisk, gratPayOff_, deltaGratPayoff,\
            invPayOff_, deltaInvPayoff, sarf, deltaSARF]
