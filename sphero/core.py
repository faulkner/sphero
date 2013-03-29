# coding: utf-8
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
        tries=retry
        logging.info('connecting to %s' % self.path)
        while True:
            try:
                self.sp = serial.Serial(self.path, 115200)
                return
            except serial.serialutil.SerialException:
                logging.info('retrying')
                if not retry:
                    raise SpheroError('failed to connect after %d tries' % (tries-retry))
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


    def prep_str(self, s):
        """ Helper method to take a string and give a array of "bytes" """
        return [ord(c) for c in s]    

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
        # GET_DEVICE_NAME is not really part of the api, 
        # it has changed to GET_BLUETOOTH_INFO.
        # Which returns both name and Bluetooth mac address.
        return self.get_bluetooth_info().name

    def set_device_name(self, newname):
        """ Sets internal device name. (not announced bluetooth name).
        requires utf-8 encoded string. """
        return self.write(request.SetDeviceName(self.seq, *self.prep_str(newname)))

    def get_bluetooth_info(self):
        return self.write(request.GetBluetoothInfo(self.seq))

    def set_auto_reconnect(self):
        raise NotImplementedError

    def get_auto_reconnect(self):
        raise NotImplementedError

    def get_power_state(self):
        raise NotImplementedError

    def set_power_notification(self):
        raise NotImplementedError

    def sleep(self, wakeup=0, macro=0, orbbasic=0):
        return self.write(request.Sleep(self.seq, wakeup, macro, orbbasic))

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

    def set_heading(self, value):
        """value can be between 0 and 359"""
        return self.write(request.SetHeading(self.seq, value))

    def set_stabilization(self, state):
        return self.write(request.SetStabilization(self.seq, state))

    def set_rotation_rate(self, val):
        """value ca be between 0x00 and 0xFF:
            value is a multiplied with 0.784 degrees/s except for:
            0   --> 1 degrees/s
            255 --> jumps to 400 degrees/s
        """
        return self.write(request.SetRotationRate(self.seq, val))

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

    def set_back_led_output(self, value):
        """value can be between 0x00 and 0xFF"""
        return self.write(request.SetBackLEDOutput(self.seq, value))

    def roll(self, speed, heading, state=1):
        """
        speed can have value between 0x00 and 0xFF 
        heading can have value between 0 and 359 
        
        """
        return self.write(request.Roll(self.seq, speed, heading, state ))

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

    # Additional "higher-level" commands
    
    def stop(self):
        return self.roll(0,0)

if __name__ == '__main__':
    import time
    logging.getLogger().setLevel(logging.DEBUG)
    s = Sphero()
    s.connect()

    #print ( s.set_device_name("Sphero-Salmon") )

    print( """Bluetooth info: 
        name: %s
        bta: %s
        """ 
        % ( s.get_bluetooth_info().name, 
            s.get_bluetooth_info().bta
          ) 
    )

    s.set_rotation_rate(0x00)
    s.set_heading(0)
    time.sleep(1)
    s.roll(0x80, 270)
    time.sleep(2)
    s.set_heading(45)
    time.sleep(3)
    s.stop()


    

    # handy for debugging calls
    def raw(did, cid, *data, **kwargs):
        req = request.Request(s.seq, *data)
        req.did = did
        req.cid = cid
        if 'fmt' in kwargs:
            req.fmt = kwargs['fmt']
        res = s.write(req)
        logging.debug('request: %s', repr(req.bytes))
        logging.debug('response: %s', repr(res.data))
        return res
