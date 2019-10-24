from .smart_consumer import *

class World:

    def __init__(self, p, c, first = 'p'):
        self.pro = p
        self.co = c

        self.first = 'p'
        self.round = 0
        self.winner = None
        self.end = False

    def move_one(self):

        ##print("consumer wealth :\t{}\tproducer shape :\t{}".format(self.co.wealth, self.pro.producerInfo.shape))
        if self.end: return

        if self.pro.producerInfo.size >= 10 ** 6 / 2:
            self.end = True
            return

        if self.first == 'p':
            self.pro.move_one(self)
            self.co.move_one(self.pro)
        else:
            self.co.move_one(self.pro)
            self.pro.move_one(self)

        # check bankruptcy
        self.co.bankrupt = self.co.check_bankruptcy()
        # check dead
        self.pro.dead = self.pro.check_dead()

        if self.co.bankrupt:
            self.winner = "PRODUCER"
            self.end = True

        if self.pro.dead:
            self.winner = 'CONSUMER'
            self.end = True

        self.round += 1

    '''
    description :
    - updates consumer's OWNED_UNITS after producer has cleaned itself.
    '''
    def sync_cleaned(self, cleanedIds):
        # no clean
        if cleanedIds == [] : return

        # search for cleaned ids in consumer possessions
        d = search_list_in_list(cleanedIds, self.co.OWNED_UNITS)
        indices = np.array(list(d.values()))

        # delete cleaned units from consumer's possessions
        np.delete(self.co.OWNED_UNITS, indices, axis = 0)
        np.delete(self.co.OWNED_UNITS_INVESTED_WORTH, indices, axis = 0)
        np.delete(self.co.OWNED_UNITS_SURFACE_AREA, indices, axis = 0)

    def move_n(self, n = None, limitRounds = 600, conPath = CON, proPath = PROD):

        # clear log files
        open(LOGFILE_C, 'w').close()
        open(LOGFILE_P, 'w').close()

        if n is None:
            while not self.end and self.round < limitRounds:
                self.move_one()

        else:
            while n > 0:
                self.move_one()
                n -= 1

        print("-------------------------------")
        print("WINNER :\t", self.winner)
        print("number of rounds :\t", self.round)
        print("consumer wealth :\t", self.co.wealth)
        print("producer net worth :\t", self.pro.netWorth)
        print("--------------------------------")
        #-----
        """
        print("consumer :\t", self.co.wealth)
        print("producer :\t", self.pro.netWorth)
        print()
        """
        #-----

        self.save_data(conPath, proPath)

    def save_data(self, conPath, proPath):
        # merge x's and y's
        self.co.SELF_LOG_X.update(self.co.SELF_LOG_Y)
        self.pro.SELF_LOG_X.update(self.pro.SELF_LOG_Y)

        # con save
        if not os.path.isfile(conPath):
            with open(conPath, 'w') as f:
                pd.DataFrame(self.co.SELF_LOG_X).to_csv(f)
        else:
            with open(conPath, 'a') as f:
                pd.DataFrame(self.co.SELF_LOG_X).to_csv(f, header = False)

        # prod save
        if not os.path.isfile(proPath):
            with open(proPath, 'w') as f:
                pd.DataFrame(self.pro.SELF_LOG_X).to_csv(f)
        else:
            with open(proPath, 'a') as f:
                pd.DataFrame(self.pro.SELF_LOG_X).to_csv(f, header = False)
