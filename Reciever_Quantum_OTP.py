from SocketChannel2 import SocketChannel
import Protocols
import pickle

Sender_ADDR = 'localhost'
Reciever_ADDR = 'localhost'
Sender_PORT = 5005
Reciever_PORT = 5006

def main():

  Protocols.receive_a_qmail(Receiver_PORT, Sender_ADDR, Sender_PORT, adversary=True)

  pass

if __name__ == "__main__":
  main()