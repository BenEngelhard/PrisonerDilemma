import time
from infrastructure.ModuleConfiguration import __USE_ARDUINO_SIM

if __USE_ARDUINO_SIM:
    import infrastructure.Arduino_related_code.ArduinoDigitalSim as Arduino
else:
    import infrastructure.Arduino_related_code.ArduinoDigital as Arduino

from infrastructure.Arduino_related_code.ValveControl import ValveControl

class RewardManager:
    def __init__(self, comport, channels, rewards, corr_bin, corr_values):
        Arduino.openComPort(comport)
        self.rewards = rewards
        self.correction_bin = int(corr_bin)
        self.correction_values = corr_values
        self.recipient_key = [{'CC': 'Coo',
                               'CD': 'Coo',
                               'DC': 'Def',
                               'DD': 'Def',
                               'CN': 'Cen'},
                              {'CC': 'Coo',
                               'CD': 'Def',
                               'DC': 'Coo',
                               'DD': 'Def',
                               'CN': 'Cen'}]
        self.recipients = [{} for _ in range(len(channels))]
        self.delivery_times = [{} for _ in range(len(channels))]
        for i in range(len(channels)):
            for key in channels[i]:
                self.recipients[i][key] = ValveControl(int(channels[i][key]))
                self.delivery_times[i][key] = time.time()

    def deliver_reward(self, mouse_id, scenario):
        key = self.recipient_key[mouse_id - 1][scenario]
        valve = self.recipients[mouse_id - 1][key]
        open_time = int(self.rewards[mouse_id - 1][scenario]['opening time'])
        open_time = self.correct_opening_time(mouse_id, scenario, open_time)

        valve.OpenValve(open_time / 1000)  # time is converted to seconds
        self.delivery_times[mouse_id - 1][key] = time.time()

    def correct_opening_time(self, mouse_id, scenario, open_time):
        key = self.recipient_key[mouse_id - 1][scenario]
        cycle_time = time.time() - self.delivery_times[mouse_id - 1][key]
        interpolation_index = int(cycle_time/self.correction_bin)

        # interpolate opening time
        if interpolation_index == 0:
            low_value = 0
            high_value = int(self.correction_values[mouse_id - 1][scenario][interpolation_index])
            base_time = 0
        elif interpolation_index < len(self.delivery_times[mouse_id - 1][scenario] - 1):
            low_value = self.correction_values[mouse_id - 1][scenario][interpolation_index]
            high_value = self.correction_values[mouse_id - 1][scenario][interpolation_index + 1]
            base_time = interpolation_index * self.correction_bin
        else:
            low_value = self.correction_values[mouse_id - 1][scenario][-2]
            high_value = self.correction_values[mouse_id - 1][scenario][-1]
            base_time = (len(self.correction_values[mouse_id - 1][scenario]) - 2) * self.correction_bin

        correction_factor = (high_value-low_value)/100*(cycle_time - base_time)/self.correction_bin
        open_time = open_time * (1 + correction_factor )

        return open_time

    def is_reward_delivered(self):
        reward_delivered = True
        for i in range(len(self.recipients)):
            for key in self.recipients[i]:
                if self.recipients[i][key].IsValveOpen():
                    reward_delivered = False
                    pass
        return reward_delivered

    def get_reward(self, mouse_id, scenario):
        return self.rewards[mouse_id -1][scenario]['water volume']
