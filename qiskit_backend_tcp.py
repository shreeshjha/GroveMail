from qiskit import *
from qiskit.quantum_info import Statevector
from parser import QSerializer
import socket
from SocketChannel import SocketChannel

class Channel:    
    def __init__(self,product_offset=0):
        self._state_vector = None
        self._arr_qubits = None
        self._basis_gates = ['u1', 'u2', 'u3', 'cx','x','y','H','z']
        self._owner = True
        self._offset = 0
        self._product_offset = product_offset
        
    def send(self,circuit,arr_qubits):
        self._state_vector = Statevector.from_instruction(circuit)  
        self._arr_qubits = arr_qubits
       
        ser = parser.QSerializer()
        ser.add_element('channel_class', self)
        str_to_send = ser.encode()

        message = str_to_send
        TCP_IP = '127.0.0.1'

        channel = SocketChannel()
        channel.connect(TCP_IP, 5005)

        channel.send(message)
    
        return self
        
    def receive(self,circuit)#,recieve_channel):  
        channel = SocketChannel(port=5005, listen=True)
        data = channel.receive()
        print("received data:", data)
        
        ser2 = parser.QSerializer()
        ser2.decode(data)
        recieve_channel = ser2.get_element('channel_class')
        
        self._product_offset = recieve_channel._product_offset
        if(recieve_channel._owner):
            self._owner = False
            self._offset = self._product_offset
        
        new_circuit = QuantumCircuit(len(recieve_channel._state_vector.dims()))
        new_circuit.initialize(recieve_channel._state_vector.data, range(len(recieve_channel._state_vector.dims())))
        new_circuit = transpile(new_circuit, basis_gates=self._basis_gates)
        return new_circuit, self._offset   


# In[34]:



n_owner = 2
n_product = 1
owner_offset = 0
product_offset = n_owner



circ = QuantumCircuit(n_owner + n_product)
channel = Channel(product_offset)
circ.h(0 + channel._offset)


to_tpc = channel.send(circ,[1])  ## TODO: remove
circ.draw()

circ_reciever = QuantumCircuit(3)

reciever_channel = Channel()
circ_reciever, offset = reciever_channel.receive(circ_reciever)#,to_tpc)
circ_reciever.draw()

circ_reciever.h(0+offset)

to_tpc = reciever_channel.send(circ_reciever,[1])
circ_reciever.draw()


circ_sender = QuantumCircuit(3)

sender_channel = Channel()
circ_sender , offset = sender_channel.receive(circ_sender,to_tpc)
circ_sender.draw()



