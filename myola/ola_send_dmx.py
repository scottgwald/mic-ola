import array
from ola.ClientWrapper import ClientWrapper

def DmxSent(state):
  wrapper.Stop()

universe = 5
data = array.array('B')
data.append(10)
data.append(50)
data.append(255)

wrapper = ClientWrapper()
client = wrapper.Client()
client.SendDmx(universe, data, DmxSent)
wrapper.Run()
