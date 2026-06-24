import infrastructure.Data_analysis.FileUtilities as fUtile
from infrastructure.Data_analysis.LoggerABC import BaseLogger


class EventLogger(BaseLogger):
    def __init__(self, oppid):
        super().__init__(5)
        self.event_number = 0  # Initialize event number
        self.csv_file_path = fUtile.get_file_path(oppid) + '_eventlog.csv'
        self.temp_data = []  # Temporary storage for events to calculate Time in State later

    def start_logging(self):
        header = ["Trigger", "Trial Number", "State", "Location", "Time"]
        self._create_file(header)

    def log_data(self, trigger, trial_number, state, location, time):
        data = [trigger, trial_number, state, location, time]
        self._log_data(data)

