import array
from ola.ClientWrapper import ClientWrapper

#!/usr/bin/python

# open a microphone in pyAudio and listen for taps

import pyaudio
import struct
import math

import threading

# the_greenlets = []
my_threads = []

wrapper = None
loop_count = 0
TICK_INTERVAL = 34  # in ms
universe = 5
nChannels = 18
mic_intensity = 0

INITIAL_TAP_THRESHOLD = 50
FORMAT = pyaudio.paInt16 
SHORT_NORMALIZE = (1.0/32768.0)
CHANNELS = 2
RATE = 44100  
INPUT_BLOCK_TIME = 0.05
INPUT_FRAMES_PER_BLOCK = int(RATE*INPUT_BLOCK_TIME)
# if we get this many noisy blocks in a row, increase the threshold
OVERSENSITIVE = 3.0/INPUT_BLOCK_TIME                    
# if we get this many quiet blocks in a row, decrease the threshold
UNDERSENSITIVE = 5.0/INPUT_BLOCK_TIME 
# if the noise was longer than this many blocks, it's not a 'tap'
MAX_TAP_BLOCKS = 0.15/INPUT_BLOCK_TIME

def get_rms( block ):
    # RMS amplitude is defined as the square root of the 
    # mean over time of the square of the amplitude.
    # so we need to convert this string of bytes into 
    # a string of 16-bit samples...

    # we will get one short out for each 
    # two chars in the string.
    count = len(block)/2
    format = "%dh"%(count)
    shorts = struct.unpack( format, block )

    # iterate over the block.
    sum_squares = 0.0
    for sample in shorts:
        # sample is a signed short in +/- 32768. 
        # normalize it to 1.0
        n = sample * SHORT_NORMALIZE
        sum_squares += n*n

    return math.sqrt( sum_squares / count )

class TapTester(object):
    def __init__(self):
        self.pa = pyaudio.PyAudio()
        self.stream = self.open_mic_stream()
        self.tap_threshold = INITIAL_TAP_THRESHOLD
        self.noisycount = MAX_TAP_BLOCKS+1 
        self.quietcount = 0 
        self.errorcount = 0

    def stop(self):
        self.stream.close()

    def find_input_device(self):
        device_index = None            
        for i in range( self.pa.get_device_count() ):     
            devinfo = self.pa.get_device_info_by_index(i)   
            print( "Device %d: %s"%(i,devinfo["name"]) )

            for keyword in ["mic","input"]:
                if keyword in devinfo["name"].lower():
                    print( "Found an input: device %d - %s"%(i,devinfo["name"]) )
                    device_index = i
                    return device_index

        if device_index == None:
            print( "No preferred input found; using default input device." )

        return device_index

    def open_mic_stream( self ):
        device_index = self.find_input_device()

        stream = self.pa.open(   format = FORMAT,
                                 channels = CHANNELS,
                                 rate = RATE,
                                 input = True,
                                 input_device_index = device_index,
                                 frames_per_buffer = INPUT_FRAMES_PER_BLOCK)

        return stream

    def tapDetected(self):
        print "Tap!"

    def listen(self):
        try:
            block = self.stream.read(INPUT_FRAMES_PER_BLOCK)
        except IOError, e:
            # dammit. 
            self.errorcount += 1
            print( "(%d) Error recording: %s"%(self.errorcount,e) )
            self.noisycount = 1
            return

        amplitude = get_rms( block )
        amplitude=int(amplitude*100)
        print "threshold:="+ str(self.tap_threshold) + " amplitude:=" + str(amplitude)

        if amplitude > self.tap_threshold:
            s = '*'
            for i in range(amplitude):
                s+='*'
            print s
            # noisy block
            self.quietcount = 0
            self.noisycount += 1
            if self.noisycount > OVERSENSITIVE:
                print "OVERSENSITIVE"
                # turn down the sensitivity
                self.tap_threshold += 1
        else:            
            # quiet block.
            self.noisycount = 0
            self.quietcount += 1
            print "UNDERSENSITIVE"
            if self.quietcount > UNDERSENSITIVE:
                
                # turn up the sensitivity
                self.tap_threshold *= 0.9


def init_array():
  global frame
  frame = array.array('B')
  for i in range(nChannels):
    frame.append(0)

def DmxSent(state):
  if not state.Succeeded():
    wrapper.Stop()

def SendDMXFrame():
  global frame
  global loop_count
  # schdule a function call in 100ms
  # we do this first in case the frame computation takes a long time.
  wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)
  loop_count +=1

  frame[loop_count % nChannels] = ( 10 * loop_count ) % 96

  # # compute frame here
  # data = array.array('B')
  # global loop_count
  # data.append(loop_count % 255)
  # loop_count += 1
  # print loop_count

  # send
  wrapper.Client().SendDmx(universe, frame, DmxSent)

def run_lights():
  global wrapper                                                                                                                        
  init_array()
  wrapper = ClientWrapper()
  wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)
  wrapper.Run()
  # gevent.sleep(0)

def run_mic():
    tt = TapTester()

    while True:
        tt.listen()
        # gevent.sleep(0)

if __name__ == "__main__":
    my_threads.append(threading.Thread(target=run_lights))
    my_threads.append(threading.Thread(target=run_mic))
    for my_thread in my_threads:
      my_thread.start()

    # the_greenlets.append(gevent.spawn(run_lights))
    # the_greenlets.append(gevent.spawn(run_mic))
    # gevent.joinall(the_greenlets)
