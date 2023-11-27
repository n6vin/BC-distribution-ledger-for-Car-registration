#!/usr/bin/python3.6

from miner import Miner

import ast
from multiprocessing import Process, Manager
import socket

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)
DIFFICULTY = 1      # Number of zeroes at the beginning of a new hash
GENESIS_BLOCK = {
    "hash": "0",
    "car": {
        "id": "GENESIS BLOCK"
    }
}


def main():
    blockchain = [
        GENESIS_BLOCK
    ]

    print_blockchain(blockchain)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        while True:
            conn, addr = s.accept()
            with conn:
                print('Connected by', addr)
                data = conn.recv(2048)
                print("A new block received: ", data.decode())
                # in python3 the string must be encoded
                conn.sendall("hello from server side".encode())

                msg = ast.literal_eval(data.decode())
                try:
                    if msg['request']:
                        answer(msg, blockchain)
                except KeyError:

                    miners(msg, blockchain)


def miners(block, blockchain):
    new_block = Manager().dict()
    new_block["block"] = None
    new_block["validated"] = None
    miners_lst = []
    for i in range(3):
        miners_lst.append(Miner(i, block, blockchain, DIFFICULTY, new_block))

    jobs = []
    for miner in miners_lst:
        p = Process(target=miner.mine)
        jobs.append(p)
        p.start()

    for p in jobs:
        p.join()

    if new_block["validated"]:
        blockchain.append(new_block["block"].get_block_obj(True))
        print_blockchain(blockchain)
    else:
        print("The block has been rejected!")


def print_blockchain(blockchain):
    print("\n")
    print("BLOCKCHAIN CONTENT")
    for block in blockchain:
        print("\n")
        print(block)


def answer(msg, blockchain):
    print("\n")
    if msg["request"] == "history":
        for block in blockchain:
            try:
                block_car = ast.literal_eval(block['car'])
                if block_car['id'] == msg['car_id']:
                    print("\n")
                    print(block)
            except ValueError:
                pass


if __name__ == '__main__':
    main()
