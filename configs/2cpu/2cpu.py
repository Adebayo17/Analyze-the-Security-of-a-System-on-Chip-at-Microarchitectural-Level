from collections import namedtuple
import m5
import sys
from m5.objects import *
from caches import *

option = namedtuple('option', ('l1i_size', 'l1d_size', 'l2_size'))('128MB', '128MB', '512MB')

def createCPU(l2bus, membus):
    # create the CPU
    #cpu = DerivO3CPU()
    cpu = X86TimingSimpleCPU()

    # create L1 cache
    cpu.icache = L1ICache(option)
    cpu.dcache = L1DCache(option)

    cpu.icache.connectCPU(cpu)
    cpu.dcache.connectCPU(cpu)

    # connect to shared cache level 2 bus
    cpu.icache.connectBus(l2bus)
    cpu.dcache.connectBus(l2bus)

    # create and connect interrupt port
    cpu.createInterruptController()
    cpu.interrupts[0].pio = membus.mem_side_ports
    cpu.interrupts[0].int_requestor = membus.cpu_side_ports
    cpu.interrupts[0].int_responder = membus.mem_side_ports

    return cpu

# The System object, root of all other component
system = System()

# set up the clock and the voltage
# It seems like the frequency is the same for all cpu
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# setup memory simulation
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# create L2 bus
system.l2bus = L2XBar()

# create the system wide bus
system.membus = SystemXBar()

# create 2 cpus
system.cpu = [createCPU(system.l2bus, system.membus), createCPU(system.l2bus, system.membus)]

# create L2 Cache
system.l2cache = L2Cache(option)
system.l2cache.connectCPUSideBus(system.l2bus)
system.l2cache.connectMemSideBus(system.membus)

system.system_port = system.membus.cpu_side_ports

# create memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

# create the process workload for the cpu 1
process1 = Process(pid = 100)
process1.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
# the fact that workload accepting an array indicate that a cpu can handle multiple command
system.cpu[0].workload = [process1]
system.cpu[0].createThreads()

# create the process workload for the cpu 2
process2 = Process(pid = 200)
process2.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
# the fact that workload accepting an array indicate that a cpu can handle multiple command
system.cpu[1].workload = [process2]
system.cpu[1].createThreads()

# create the root and start the system
root = Root(full_system = False, system = system)
print("Looking Error")
m5.instantiate()
print("Looked Error")

print("Beginning simulation")
print("Looked Error")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'.format(m5.curTick(), exit_event.getCause()))
