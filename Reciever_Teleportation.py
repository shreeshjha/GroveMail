from qiskit import *
import matplotlib.pyplot as plt

from channel_class import Channel

circ_reciever = QuantumCircuit(3)


reciever_channel = Channel(myport = 5001, remote_port = 5000)
circ_reciever, offset = reciever_channel.receive(circ_reciever)#,to_tpc)

circ_reciever.cx(-1+offset,0+offset)
circ_reciever.cz(-2+offset,0+offset)

circ_reciever.rx(-0.1,0 + offset)
circ_reciever.ry(-0.94,0 + offset)
circ_reciever.rz(-0.54,0 + offset)
circ_reciever.rx(-0.234,0 + offset)

circ_reciever.draw(output='mpl',filename='teleport_bob.png')


from qiskit import Aer
backend = Aer.get_backend('statevector_simulator')
job = execute(circ_reciever,backend)
result = job.result()
outputstate = result.get_statevector(circ_reciever,decimals=3)
print(outputstate)


meas = QuantumCircuit(3,1)
meas.barrier(range(3))
meas.measure([2],range(1))
qc = circ_reciever + meas


backend_sim = Aer.get_backend('qasm_simulator')
job_sim = execute(qc,backend_sim,shots=1024)
result_sim = job_sim.result()
counts = result_sim.get_counts(qc)
print(counts)

