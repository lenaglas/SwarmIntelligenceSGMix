# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020

from datetime import datetime, timedelta, date
import threading
import random
import System
import time


class SG_Mix:
    def __init__(self):
        # usage of ids in case the system gets extended to a sg-mix-cascade
        self.id = id

    def receive_message(self, msg):

        # check if message arrives in the correct time slot. Otherwise reject the message with a error message
        time_now = datetime.now()
        if time_now < msg.TS_min or time_now > msg.TS_max:
            # error message:
            print("rejected as the message hasn't arrived in the correct time slot")

        # stop forwarding the messages if System was stopped
        elif System.stopp == 0:
            # if system is still running, forward the message using threading delay with the sg-delay T_i of the message
            t = threading.Timer(msg.t_i, self.send_message, args=(msg,))
            t.start()

    def send_message(self, msg):
        # forwarding of the message to the receiver after t_i seconds have passed
        receiver = msg.receiver
        receiver.receive_message(msg)


class BatchMix:
    def __init__(self):
        self.all_messages = []
        self.list = []  # all messages in the mix
        self.batch = []  # currently processed batch

    def receive_message(self, ack_msg):
        # with arrival of the message it gets added to the batch-list
        self.list.append(ack_msg)

        # if message arrives at the batch-mix while another batch is in process, the waited-variable is set

        if (self.list.index(ack_msg) > System.BATCH_SIZE):
            ack_msg.waited_for_batch = 1

        # Batch_Size = b
        # as soon as there are at least b messages in the list, and the last batch is processed, the next batch gets processed
        if len(self.list) >= System.BATCH_SIZE and len(self.batch) == 0 and System.stopp == 0:

            # seperating the batch to send from the list, to make sure other messages can reach the batch
            self.batch = self.list[:System.BATCH_SIZE]
            self.list = self.list[System.BATCH_SIZE:]

            # duplicates from the batch are removed
            self.batch = self.remove_duplicates()

            # randomly change of order of the batch
            random.shuffle(self.batch)
            time.sleep(System.BATCH_DURATION)

            # messages in the batch are sent
            for ack_msg in self.batch:
                self.send_message(ack_msg)
            self.batch=[]

    # method to send a message object to its original sender
    def send_message(self, ack_msg):
        # stop forwarding the messages in case the System was stopped
        if (System.stopp == 0):
            sender = ack_msg.sender
            # sending the message to sender
            sender.receive_ack_message(ack_msg)

    # comparing messages to all messages that have arrived until that point at the batch mix
    def remove_duplicates(self):
        global rejected_messages_batch
        for i in self.batch:
            for j in self.all_messages:
                if i != j and i.id == j.id and i.sender == j.sender and i.arrival_time == j.arrival_time:
                    print("DUPLICATE: ", j.id, j.sender.id, "and ", i.id, i.sender.id)
                    # removing message from batch if duplicate
                    self.batch.remove(j)
                    System.rejected_messages_batch = System.rejected_messages_batch + 1

        return self.batch
