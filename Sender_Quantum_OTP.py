from SocketChannel2 import SocketChannel
import Protocols
import pickle

Sender_ADDR = 'localhost'
BOB_ADDR = 'localhost'
Sender_PORT = 5005
Reciever_PORT = 5006

def main():
  mail = "Hello Panel We are Devs of GroveMail :D"

  Protocols.send_a_qmail(mail, Sender_PORT, BOB_ADDR, Reciever_PORT)

  pass

if __name__ == "__main__":
  main()