import threading,time,logging,numpy
from smellie import power_meter, ni_trigger_generator

def measure_power(power_n, time_delay):
    power_entries = numpy.array([])
    power_ranges = numpy.array([])
    logging.debug('Power: measuring')
    for x in range(power_n+1):
        power = pm.get_power()
        power_entries = numpy.append(power_entries, power )
        power_ranges = numpy.append(power_ranges, pm.get_power_range() )
        time.sleep(time_delay)
    logging.debug('Power: finished')
    global power_mean
    global power_sd
    global power_range
    power_mean = numpy.mean(power_entries)
    power_sd = numpy.std(power_entries)
    power_range = numpy.amax(power_ranges) 

def generate_triggers(n_pulses, repetition_rate):
    logging.debug('Triggers: generating')
    ni.generate_triggers(n_pulses, repetition_rate, 'PQ')
    logging.debug('Triggers: finished')

pm = power_meter.PowerMeter()
ni = ni_trigger_generator.TriggerGenerator()
power_mean = None
power_sd = None
power_range = None

logging.basicConfig(level=logging.DEBUG,format='(%(threadName)-10s) %(message)s',)

pm.port_open() 

thread_power = threading.Thread(name='measure_power', target=measure_power, kwargs={'power_n':100,'time_delay':0.01})
thread_power.setDaemon(True)
thread_trigger = threading.Thread(name='generate_triggers', target=generate_triggers, kwargs={'n_pulses':50000, 'repetition_rate':10000})

thread_trigger.start()
time.sleep(.5)
thread_power.start()

thread_trigger.join()
thread_power.join()

print 'Power: {}, SD: {}, Range: {}'.format(power_mean,power_sd,power_range)

pm.port_close()