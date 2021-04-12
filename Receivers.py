# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020

import System, Messages
from datetime import datetime


class Receiver:
    def __init__(self, id):
        # list of all messages received
        self.messages = []
        # id of the receiver
        self.id = id

    # method to receive messages from sg-mix
    def receive_message(self, msg):
        self.messages.append(msg)
        # creating ack-message to confirm the receipt of the message
        ack_msg = Messages.AckMessage(msg)

        # check if System is still running
        if System.stopp == 0:
            # forwarding ack-message to batch-mix
            System.batch_mix.receive_message(ack_msg)
