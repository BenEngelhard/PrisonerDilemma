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
        valve_key = self.recipient_key[mouse_id - 1][scenario]
        valve = self.recipients[mouse_id - 1][valve_key]
        open_time = self.rewards[mouse_id - 1][scenario]['opening time']

        if open_time != 0:
            cycle_time = time.time() - self.delivery_times[mouse_id - 1][valve_key]
            open_time = self.correct_opening_time(mouse_id, cycle_time, scenario, open_time)

            valve.OpenValve(open_time / 1000)  # time is converted to seconds
            self.delivery_times[mouse_id - 1][valve_key] = time.time()

    def correct_opening_time(self, mouse_id, cycle_time, scenario, open_time):
        interpolation_index = int(cycle_time/self.correction_bin)
        if interpolation_index >= len(self.correction_values[mouse_id - 1][scenario]):
            interpolation_index = len(self.correction_values[mouse_id - 1][scenario]) -1

        # interpolate opening time
        bin_time = interpolation_index * self.correction_bin
        bin_offset = cycle_time - bin_time
        interpolation_ratio = bin_offset / self.correction_bin

        if interpolation_index > 0:
            prev_bin_correction = self.correction_values[mouse_id - 1][scenario][interpolation_index - 1]
        else:
            prev_bin_correction = 0
        bin_correction = self.correction_values[mouse_id - 1][scenario][interpolation_index] - prev_bin_correction
        correction_factor =  prev_bin_correction + bin_correction * interpolation_ratio
        open_time = int(open_time * (1 + correction_factor / 100)) #correction is given in percent

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
