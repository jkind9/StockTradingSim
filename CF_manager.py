class CF_manager:
    def __init__(self):
        self.cf = None
        #load database

    def update(self):
        # get todays date
        # query data, sql?
        # append to historic data
        pass

    def get_cf(self,T):
        # get cf for previous time period T
        return self.cf

    def stream(self,T):
        # start at T0+T
        # While data iteratively return cf at time t-T
        pass
    def add_bs(self, T):
        # values = [black_scholes(data_packet) for data_packet in stream_T
        # add put cols, add calls