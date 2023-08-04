# This file is from the Gem5 tutorial
# url = https://www.gem5.org/documentation/learning_gem5/part1/simple_config/

import m5
from m5.objects import *

# create the system
system = System()

# setting up the clock on the system
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '1GHz'
system.clk_domain.voltage_domain = VoltageDomain()

# setting up the memory
system.mem_mode = 'timing'
system.mem_ranges = [AddrRange('512MB')]

# creating the cpu
system.cpu = X86TimingSimpleCPU()

# system-wide memory bus
system.membus = SystemXBar()

system.cpu.icache_port = system.membus.cpu_side_ports
system.cpu.dcache_port = system.membus.cpu_side_ports

# setting up an IO controller on the CPU
system.cpu.createInterruptController()
system.cpu.interrupts[0].pio = system.membus.mem_side_ports
system.cpu.interrupts[0].int_requestor = system.membus.cpu_side_ports
system.cpu.interrupts[0].int_responder = system.membus.mem_side_ports

system.system_port = system.membus.cpu_side_ports

# setting up the memory controller
system.mem_ctrl = MemCtrl()
system.mem_ctrl.dram = DDR3_1600_8x8()
system.mem_ctrl.dram.range = system.mem_ranges[0]
system.mem_ctrl.port = system.membus.mem_side_ports

binary = 'tests/test-progs/hello/bin/x86/linux/hello'

# for gem5 V21 and beyond
system.workload = SEWorkload.init_compatible(binary)

# creating the process
process = Process()
process.cmd = [binary]
system.cpu.workload = process
system.cpu.createThreads()

# instantiate the system and the simulation
root = Root(full_system = False, system = system)
m5.instantiate()

print("Beginning simulation!")
exit_event = m5.simulate()

print('Exiting @ tick {} because {}'
      .format(m5.curTick(), exit_event.getCause()))