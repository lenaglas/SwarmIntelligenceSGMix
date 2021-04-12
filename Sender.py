# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020

import System, Messages
import threading
from datetime import datetime, timedelta, date
import csv


class Sender:
    def __init__(self, id):

        # GENEARATING SENDER INFORMATION:
        # dictionary with all messages intiated by the sender
        self.messages = {}
        # dictionary with all received ack-messages
        self.ack_messages = {}
        self.id = id
        # lambda for non dummy messages, globally set in System.py
        self.lambda_interarrival = System.INTERARRIVAL_LAMBDAS[id]
        # lambda for dummy-messages
        self.lambda_dummy = self.lambda_interarrival
        # counter how many ack-messages are received, necessary to terminate the warm-up phase
        self.ack_counter = 0
        # current best duration, reference value for optimisation
        self.dur_opt = 0
        # variable, if system is currently in warm up phase
        self.warmup_phase = 1
        # counter how many acks for non-dummy-messages were received, for sender to know, when all non-dummy messages
        # got back as ack-messages
        self.ack_messages_real = 0
        # variable to tell the sender when to stop sending dummy messages
        self.dummy_stop = 0

        # add sender to list of all senders
        System.senders.append(self)

        # INITIATION OF MESSAGE STREAMS:
        if System.OPTIMIZATION_MODE == 3:
            # if the system is ran without dummy messages (opt mode 3) the warm up phase is skipped
            # and only one stream for non-dummy messages is initiated
            self.create_message(0)
        else:
            # if dummy messages are used, a dummy stream is initiated to begin the warm up phase
            self.create_dummy_message(0)

    # stream for non-dummy-messages
    def create_message(self, i):
        # creating object of type Message
        msg = Messages.Message(self, i, 0)
        # sending message after pre-calculated interarrival time has passed
        t = threading.Timer(msg.interarrival_time, self.send_message, args=(msg, i,))
        t.start()

    # stream for dummy-messages
    def create_dummy_message(self, i):
        # same logic as above
        msg = Messages.Message(self, i, 1)

        # sending of a message after the precaculated (exp. distributed) arrival time has passed
        t = threading.Timer(msg.interarrival_time, self.send_message, args=(msg, i,))
        t.start()

    # sending each message
    def send_message(self, msg, i):
        if System.stopp == 0:  # to prevent dummy messages to be sent after System has stopped
            System.sg_mix.receive_message(msg)

        # after a messages is sent a new non-dummy or dummy message gets initiated depending on what kind the sent
        # message was
        if msg.dummy == 1 and self.dummy_stop == 0:
            i = i + 1
            self.create_dummy_message(i)

        if i < System.NUMBER_OF_MESSAGES - 1 and msg.dummy == 0:
            i = i + 1
            self.create_message(i)

    def receive_ack_message(self, ack_message):
        arrival_time = datetime.now().time()

        # combining information from the original message and its ack-message using the id of both
        id = ack_message.id
        message = self.messages[id]
        post_time = message.post_time

        # calculation of sender how long the message took to sender
        duration = datetime.combine(date.today(), arrival_time) - datetime.combine(date.today(), post_time.time())
        duration = duration.total_seconds()

        # completing the message object with information , so all information is stored there
        message.duration = duration
        message.arrival_time = arrival_time
        message.waited_for_batch = ack_message.waited_for_batch

        # increasing of the ack-counter
        self.ack_counter = self.ack_counter + 1

        # increasing counter of all acknowledged non-dummy-messages
        if ack_message.id[0] == "M":
            self.ack_messages_real = self.ack_messages_real + 1

        # printing information about processed message for user
        print("WAITED: ", ack_message.waited_for_batch, ack_message.id)
        print(duration)
        print("with lambda: ", self.messages[id].lambda_interarrival)

        # check if warm up phase is over
        if self.ack_counter == System.SCOPE_WARMUP_PHASE:
            self.terminate_warm_up_phase()

        # optimisation of lambda_dummy
        if self.warmup_phase == 0:
            self.perform_optimisation(self.messages[id])

        # check if sender has sent all non-dummy messages, terminate sending dummy messages if so
        if self.ack_messages_real == System.NUMBER_OF_MESSAGES and self.dummy_stop == 0:
            print("Sender ", self.id, " is done ", datetime.now().time())
            self.dummy_stop = 1
            System.done = System.done + 1

            # check if all senders are done sending messages and create csv file for simualtion round
            if System.done == System.NUMBER_OF_SENDERS and System.stopp == 0:
                self.create_csv()

    def terminate_warm_up_phase(self):
        duration_sum = 0.0

        for i in self.messages:
            # calculation of first first reference value dur_opt:
            if self.messages[i].duration != 0:  # to exclude messages for which the duration haven't been caculated
                duration_sum = duration_sum + self.messages[i].duration

        self.dur_opt = round(duration_sum / System.SCOPE_WARMUP_PHASE, 6)

        # terminating warm-up-phase
        self.warmup_phase = 0

        # if an optimisation mode is chosen that uses dummy messages:
        if System.OPTIMIZATION_MODE != 3:
            # second message stream for non-dummy-messages is intiated
            self.create_message(0)

    def perform_optimisation(self, message):
        # optimisation is only performed if system is running in opt.mode 1 or 2
        if System.OPTIMIZATION_MODE != 0:
            # check if duration is better than current dur_opt
            if (message.duration < self.dur_opt):
                # if so, update dur_opt
                self.dur_opt = message.duration
            else:
                # if batch-mix is not working at full capacity yet, lambda_dummy needs to be increased
                if message.waited_for_batch == 0:
                    # OPTIMIZATION MODE 1:
                    if System.OPTIMIZATION_MODE == 1:
                        new_lambda = self.lambda_dummy * (1 + System.OPTIMIZATION_FACTOR)
                        # lambda_dummy is only increased, if lambda of the current message is higher than lambda_dummy
                        if new_lambda <= message.lambda_interarrival * (1 + System.OPTIMIZATION_FACTOR):
                            self.lambda_dummy = new_lambda

                    # OPTMIZATION MODE 2:
                    else:
                        # continuous optimisation
                        self.lambda_dummy = self.lambda_dummy * (1 + (System.OPTIMIZATION_FACTOR) / (self.lambda_dummy))


                # same logic as above for decreasing lambda_dummy
                else:
                    if System.OPTIMIZATION_MODE == 1:
                        new_lambda = self.lambda_dummy * (1 - System.OPTIMIZATION_FACTOR)
                        if new_lambda >= message.lambda_interarrival * (1 - System.OPTIMIZATION_FACTOR):
                            self.lambda_dummy = new_lambda
                    else:
                        new_lambda = self.lambda_dummy * (1 - (System.OPTIMIZATION_FACTOR) / (self.lambda_dummy))
                        if new_lambda > 0:
                            self.lambda_dummy = new_lambda

    # after all senders have sent their messages, a csv with all dummy and non-dummy messages sent is created
    def create_csv(self):
        # result file as declared in System.py
        with open(System.outputfile, mode='w', newline='') as result_file:
            # columns of the csv
            fieldnames = ["DURATION", "ID", "LAMBDA", "DUMMY", "WAITED_FOR_BATCH", "SENDER_ID", "POST_TIME",
                          "ARRIVAL_TIME", "OPT_MODE", "OPT_FACTOR", "BATCH_SIZE", "NUMBER_SENDERS", "NUMBER_MESSAGES",
                          "WARM UP SCOPE"]
            result_writer = csv.DictWriter(result_file, fieldnames=fieldnames, delimiter=';')
            result_writer.writeheader()

            # filling the csv with all non-dummy messages sent
            for i in System.receivers:
                for j in System.receivers[i].messages:
                    result_writer.writerow(
                        {"DURATION": j.duration, "ID": j.id, "LAMBDA": j.lambda_interarrival, "DUMMY": j.dummy,
                         "WAITED_FOR_BATCH": j.waited_for_batch, "SENDER_ID": j.sender.id,
                         "POST_TIME": j.post_time, "ARRIVAL_TIME": j.arrival_time, "OPT_MODE": System.OPTIMIZATION_MODE,
                         "OPT_FACTOR": System.OPTIMIZATION_FACTOR,
                         "BATCH_SIZE": System.BATCH_SIZE, "NUMBER_SENDERS": System.NUMBER_OF_SENDERS,
                         "NUMBER_MESSAGES": System.NUMBER_OF_MESSAGES, "WARM UP SCOPE": System.SCOPE_WARMUP_PHASE})

            # adding all dummy-messages sent to the csv
            for k in System.dummy_receiver.messages:
                result_writer.writerow(
                    {"DURATION": k.duration, "ID": k.id, "LAMBDA": k.lambda_interarrival, "DUMMY": k.dummy,
                     "WAITED_FOR_BATCH": k.waited_for_batch,
                     "SENDER_ID": k.sender.id, "POST_TIME": k.post_time, "ARRIVAL_TIME": k.arrival_time,
                     "OPT_MODE": System.OPTIMIZATION_MODE, "OPT_FACTOR": System.OPTIMIZATION_FACTOR,
                     "BATCH_SIZE": System.BATCH_SIZE, "NUMBER_SENDERS": System.NUMBER_OF_SENDERS,
                     "NUMBER_MESSAGES": System.NUMBER_OF_MESSAGES,
                     "WARM UP SCOPE": System.SCOPE_WARMUP_PHASE})

                # terminating the system
                System.stopp = 1
