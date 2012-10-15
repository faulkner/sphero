import serial
import struct
import logging
import glob

import request


class SpheroError(Exception):
    pass


class Sphero(object):
    def __init__(self, path=None):
        self.sp = None
        self.dev = 0x00
        self.seq = 0x00
        self.set_sphero(path)

    def set_sphero(self, path=None):
        if not path:
            spheros = self.paired_spheros()
            if not spheros:
                raise SpheroError('you need to pair with a Sphero first')
            path = spheros[-1]

        self.path = path

    def paired_spheros(self):
        return glob.glob('/dev/tty.Sphero*')

    def connect(self, retry=100):
        logging.info('connecting to %s' % self.path)
        while True:
            try:
                self.sp = serial.Serial(self.path, 115200)
                return
            except serial.serialutil.SerialException:
                logging.info('retrying')
                if not retry:
                    raise SpheroError('failed to connect after %d tries' % retry)
                retry -= 1

    def write(self, packet):
        self.sp.write(str(packet))
        self.seq += 1
        if self.seq == 0xFF:
            self.seq = 0x00

        header = struct.unpack('5B', self.sp.read(5))
        body = self.sp.read(header[-1])

        response = packet.response(header, body)

        if response.success:
            return response
        else:
            raise SpheroError('request failed (request: %s:%s, response: %s:%s)' % (header, repr(body), response.header, repr(response.body)))

    # CORE COMMANDS

    def ping(self):
        return self.write(request.Ping(self.seq))

    def set_rgb(self, r, g, b, persistant=False):
        return self.write(request.SetRGB(self.seq, r, g, b, 0x01 if persistant else 0x00))

    def get_rgb(self):
        return self.write(request.GetRGB(self.seq))

    def get_version(self):
        raise NotImplementedError

    def get_device_name(self):
        raise NotImplementedError

    def get_bluetooth_info(self):
        raise NotImplementedError

    def set_auto_reconnect(self):
        raise NotImplementedError

    def get_auto_reconnect(self):
        raise NotImplementedError

    def get_power_state(self):
        raise NotImplementedError

    def set_power_notification(self):
        raise NotImplementedError

    def sleep(self):
        raise NotImplementedError

    def get_voltage_trip_points(self):
        raise NotImplementedError

    def set_voltage_trip_points(self):
        raise NotImplementedError

    def set_inactivity_timeout(self):
        raise NotImplementedError

    def jump_to_bootloader(self):
        raise NotImplementedError

    def perform_level_1_diagnostics(self):
        raise NotImplementedError

    def perform_level_2_diagnostics(self):
        raise NotImplementedError

    def clear_counters(self):
        raise NotImplementedError

    def set_time_value(self):
        raise NotImplementedError

    def poll_packet_times(self):
        raise NotImplementedError

    # SPHERO COMMANDS

    def set_heading(self):
        raise NotImplementedError

    def set_stabilization(self):
        raise NotImplementedError

    def set_rotation_rate(self):
        raise NotImplementedError

    def set_application_configuration_block(self):
        raise NotImplementedError

    def get_application_configuration_block(self):
        raise NotImplementedError

    def reenable_demo_mode(self):
        raise NotImplementedError

    def get_chassis_id(self):
        raise NotImplementedError

    def set_chassis_id(self):
        raise NotImplementedError

    def self_level(self):
        raise NotImplementedError

    def set_data_streaming(self):
        raise NotImplementedError

    def configure_collision_detection(self):
        raise NotImplementedError

    def set_back_led_output(self):
        raise NotImplementedError

    def roll(self):
        raise NotImplementedError

    def set_boost_with_time(self):
        raise NotImplementedError

    def set_raw_motor_values(self):
        raise NotImplementedError

    def set_motion_timeout(self):
        raise NotImplementedError

    def set_option_flags(self):
        raise NotImplementedError

    def get_option_flags(self):
        raise NotImplementedError

    def get_configuration_block(self):
        raise NotImplementedError

    def set_device_mode(self):
        raise NotImplementedError

    def run_macro(self):
        raise NotImplementedError

    def save_temporary_macro(self):
        raise NotImplementedError

    def reinit_macro(self):
        raise NotImplementedError

    def abort_macro(self):
        raise NotImplementedError

    def get_macro_status(self):
        raise NotImplementedError

    def set_macro_parameter(self):
        raise NotImplementedError

    def append_macro_chunk(self):
        raise NotImplementedError

    def erase_orbbasic_storage(self):
        raise NotImplementedError

    def append_orbbasic_fragment(self):
        raise NotImplementedError

    def run_orbbasic_program(self):
        raise NotImplementedError

    def abort_orbbasic_program(self):
        raise NotImplementedError

    # BOOTLOADER COMMANDS (still looking for actual docs on these)

    def begin_bootloader_reflash(self):
        raise NotImplementedError

    def set_bootloader_page(self):
        raise NotImplementedError

    def leave_bootloader(self):
        raise NotImplementedError

    def is_bootloader_page_blank(self):
        raise NotImplementedError

    def erase_user_config(self):
        raise NotImplementedError


if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)
    s = Sphero()
    s.connect()

    # connected?  throw a rave!
    import random
    for x in range(100):
        s.set_rgb(random.randrange(0, 255),
                  random.randrange(0, 255),
                  random.randrange(0, 255))
