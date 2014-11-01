import array
from ola.ClientWrapper import ClientWrapper

wrapper = None
loop_count = 0
TICK_INTERVAL = 34  # in ms
universe = 5
nChannels = 18

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
                                                                                                                        
init_array()
wrapper = ClientWrapper()
wrapper.AddEvent(TICK_INTERVAL, SendDMXFrame)
wrapper.Run()
