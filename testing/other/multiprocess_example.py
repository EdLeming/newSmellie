from multiprocessing.pool import ThreadPool
from smellie import power_meter, ni_trigger_generator

def measure_power(nsamples,sample_rate):
    print "Power measurement begin."
    power_mean, power_sd, power_range = pm.get_mean_power(nsamples,sample_rate)
    print "Power measurement finished."
    return power_mean, power_sd, power_range

if __name__ == "__main__":
    pm = power_meter.PowerMeter()
    ni = ni_trigger_generator.TriggerGenerator()
    pm.port_open()
    pool = ThreadPool(processes=1)

    measure_power_args = (10,10) #(nsamples,rate)
    trig_pulses = 30000
    trig_rate = 10000 #Hz

    for i in range(3):
        async_measure_power = pool.apply_async(measure_power, measure_power_args)
        print "Triggers begin."
        ni.generate_triggers(trig_pulses, trig_rate, 'SUPERK')
        print "Triggers finished."
        power_mean, power_sd, power_range = async_measure_power.get()
        print i,power_mean, power_sd, power_range
 
    pm.port_close() 