from qiskit import *

from channel_class import Channel

n_owner = 2
n_product = 1
owner_offset = 0
product_offset = n_owner

circ = QuantumCircuit(n_owner + n_product)

channel = Channel(product_offset, 5000, remote_port = 5001)


circ.x(0 + channel._offset)
to_tpc = channel.send(circ,[1]) 
circ.draw()


circ_sender = QuantumCircuit(3)

sender_channel = channel
sender_channel._product_offset = 0
circ_sender , offset = sender_channel.receive(circ_sender)#,to_tpc)
circ_sender.draw(output='mpl',filename='outcome1.png')

