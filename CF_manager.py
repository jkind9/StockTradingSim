import dolthub
import os 
import json 

class CF_manager:
    def __init__(self):
        if "CF.json" in os.listdir("sim_data"):
            with open("sim_data/CF.json", "r+") as file:

                self.cf = json.loads(file.read())
        else:
            self.update()
        #load database

    def update(self):
        print("<<<<UPDATING>>>>")
        new_data_bool = dolthub.get_ticker_data()
        if new_data_bool:
            dolthub.data_csv_to_json()

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
        pass
    
CF_instance = CF_manager()