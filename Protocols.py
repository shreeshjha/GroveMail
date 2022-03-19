#!/usr/bin/env python3
from qiskit import *
from qiskit.quantum_info import Statevector
from textwrap import wrap
from random import randrange
from SocketChannel2 import SocketChannel
import pickle
from channel_class import Channel
import time
import numpy as np

def str_to_lbin(mail, bin_size=4):
    clist = [ord(x) for x in mail]
    bins = ''.join([format(x,'08b') for x in clist])
    return wrap(bins,bin_size)


def bins_to_str(lbin):
    sbin = ''.join(lbin) 
    lbin8 = wrap(sbin, 8)
    mail = chr(int(lbin8[0],2))
    for c in lbin8[1:]:
        mail+=chr(int(c,2))

    return mail
 

def encode_cinfo_to_qstate(cinfo_bin):
    nreg = len(cinfo_bin)
    qcirc = QuantumCircuit(nreg, nreg)
    for i,bit_i in enumerate(cinfo_bin[::-1]):
        if int(bit_i):
            qcirc.x(i)
    return qcirc


def generate_otp_key(key_length):
    x_key=bin(randrange(2**key_length))[2:] 
    z_key=bin(randrange(2**key_length))[2:] 

    return {'x': x_key, 'z': z_key}


def otp_enc_dec(qcirc, otpkey):
    r_x , r_z = otpkey['x'], otpkey['z']
    for i,k in enumerate(zip(r_x,r_z)):
        if k[0]:
            qcirc.x(i)
        if k[1]:
            qcirc.z(i)



def qotp_send(qcirc, otpkey, qChannel=None):
    otp_enc_dec(qcirc, otpkey)
    qChannel.send(qcirc, [0,1,2,3])
    time.sleep(1)


def send_a_qmail(mail, port, destAddr, destPort, batch_size=4):
    nqubit = batch_size

    print('Sender wants to send the panel a sweet mail Actually a Quantum State as Mailing System is In Works %s'%mail)
    classicC = SocketChannel(port+10, False)
    classicC.connect(destAddr, destPort+10)

    Lbins = str_to_lbin(mail, batch_size)

    print('Encryption is in process .........')
    otpkey = generate_otp_key(len(Lbins)*batch_size)
    print('X state vector -key %s'%otpkey['x'], 'Z state vector -key %s'%otpkey['z'])

    classicC.send(pickle.dumps(otpkey))
    print("We are Grove we have sent the panel:", otpkey)
    classicC.close()
    time.sleep(2)

    key_per_batch = [{'x':x,'z':z} for x,z in zip(wrap(otpkey['x'],batch_size),wrap(otpkey['z'],batch_size))]

    n_owner = batch_size
    n_product = batch_size
    product_offset = 0
    channel = Channel(product_offset, port, remote_port=destPort)

    for bin_batch,k in zip(Lbins, key_per_batch):  
        print('Performing QOTP for string', bin_batch)
        qcirc = encode_cinfo_to_qstate(bin_batch)
        qotp_send(qcirc, k, channel)
    print("Transmission complete.")

def receive_a_qmail(port, srcAddr, srcPort, batch_size=4, adversary=False):
    classicC = SocketChannel(port+10, True)
    classicC.connect(srcAddr, srcPort+10)
    otpkey = classicC.receive()
    otpkey = pickle.loads(otpkey)
    print("We are the Panel and we confirm we have received: ", otpkey)
    classicC.close()
    time.sleep(1)

    key_per_batch = [{'x':x,'z':z} for x,z in zip(wrap(otpkey['x'],batch_size),wrap(otpkey['z'],batch_size))]

    n_owner = batch_size
    n_product = batch_size
    product_offset = 0
    channel = Channel(product_offset, port, remote_port=srcPort)

    qcirc = None
  
    recv = "Sender" if adversary else "Reciever"
    bob_meas_results = []
    for k in key_per_batch:
        circ_reciever = QuantumCircuit(batch_size, batch_size)
        circ_reciever, offset = channel.receive(circ_reciever)
        if not adversary:
            otp_enc_dec(circ_reciever, k)

        simulator = Aer.get_backend('qasm_simulator')
        nqubit = len(otpkey['x'])
        
        circ_reciever.measure(np.arange(batch_size)+offset, range(batch_size))
        counts = execute(circ_reciever, backend=simulator, shots = 1).result()

        output = list(counts.get_counts().keys())[0]
        bob_meas_results.append(output)
        print('%s measures'%recv, bob_meas_results[-1])
    print('%ss mail %s'%(recv, bins_to_str(bob_meas_results)))

    return bins_to_str(bob_meas_results)


def apply_grover_oracle2(qcirc, dquery):
    qcirc.cz(1,0)
    if dquery == '11':
        qcirc.z(0)
        qcirc.z(1)
    elif dquery == '01':
        qcirc.z(1)
    elif dquery == '10':
        qcirc.z(0)
    else : pass


def multiparty_2grover_local(port, destPort):

    print("GroveMail Developer sends quantum state |00>")
    qcirc = QuantumCircuit(2,2) 
    qcirc.h(0)    
    qcirc.h(1)  

    n_owner = 2
    n_product = 2
    product_offset = 0
    channel = Channel(product_offset, port, remote_port=destPort)

    print("Sender send qubits to Database, we are processing the database :D")
    channel.send(qcirc, [0,1])


    print("Sender received qubits")
    qcirc, offset = channel.receive(qcirc)

    qcirc.h(0)
    qcirc.h(1)
    qcirc.cz(0,1)
    qcirc.h(0)
    qcirc.h(1)
    qcirc.measure([0,1],[0,1])
    simulator = Aer.get_backend('qasm_simulator')
    counts = execute(qcirc, backend=simulator, shots = 1).result()

    print("GroveMail Delievery", list(counts.get_counts().keys())[0])


def oscar_sends(dquery, port, srcPort):
    qcirc = QuantumCircuit(2,2) 
    n_owner = 2
    n_product = 2
    product_offset = 0
    channel = Channel(product_offset, port, remote_port=srcPort)

    print("Database received qubits")
    qcirc, offset = channel.receive(qcirc)
    apply_grover_oracle2(qcirc, dquery)

    print("Database sending qubits to Sender")
    channel.send(qcirc, [0,1])
