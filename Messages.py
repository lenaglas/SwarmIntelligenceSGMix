# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020

from datetime import datetime, timedelta
import System
import random
import math


class Message:
    def __init__(self, sender, i, dummy):
        # calculating lambdas for optimisation here
        mu_delay = System.MU_DELAY

        # information if the message is a dummy-message or not
        self.dummy = dummy

        # id of the sender that initiates the message
        self.sender = sender

        # see method get_id() below for creating the id of a message
        self.id = self.get_id(i)

        # lambda for the exponential distribution which models the arrival rate
        if self.dummy == 1:
            self.lambda_interarrival = sender.lambda_dummy
        else:
            self.lambda_interarrival = sender.lambda_interarrival

        # time difference to current time at what the message is sent, following an exponential distribution with
        # parameter lambda_interrival
        self.interarrival_time = get_poisson_time_slot(self.lambda_interarrival)

        # information that is added using the variable from the ack-message
        self.waited_for_batch = 0

        # time at what the message is actually sent
        time_now = datetime.now()
        self.post_time = time_now + timedelta(seconds=self.interarrival_time)

        # receiver and content of the message both chosen randomly
        self.receiver = self.get_receiver()
        self.content = self.get_content()

        # parameter of the exponential distribution modeling the delay time at the sg-mix
        self.mu_delay = mu_delay

        # time the message gets delayed at sg-mix
        self.t_i = get_poisson_time_slot(mu_delay)

        # time slot at which the message can arrive at the sg-mix i if more sg-mixes were added, the sum of delays at
        # each sg-mix that is passed before i needs to be added to Tmin, Tmax
        self.TS_min = self.get_ts_min()
        self.TS_max = self.get_ts_max()

        # the following to be set as soon the sender gets an ack-message for the message
        self.duration = 0
        self.arrival_time = 0
        self.ack = 0
        sender.messages[self.id] = self

    # id is generated as the combination of letter M for non-dummy Messages and D for Dummy messages
    # and the number of the message in the current stream: D004 is the fourth dummy-message of a sender
    def get_id(self, i):
        i = str(i)
        j = i.zfill(3)
        if self.dummy == 0:
            id = "M" + j
            return id
        else:
            id = "D" + j
            return id

    def get_receiver(self):
        # if the message is a dummy message, it always gets sent to the dummy receiver
        if self.dummy == 1:
            return System.dummy_receiver
        # otherwise a receiver is randomly chosen from the list of senders
        return random.choice(System.receivers)

    # calculation of TS_min, TS_max with the global Parameters D_MIN, D_MAX and syn, set in System.py
    def get_ts_min(self):
        return self.post_time + timedelta(seconds=System.D_MIN) - timedelta(seconds=System.SYN)

    def get_ts_max(self):
        return self.post_time + timedelta(seconds=System.D_MAX) + timedelta(seconds=System.SYN)

    # choosing a random content M for a message
    def get_content(self):
        return random.choice(System.CONTENTS)


# object AckMessage consisting of ID and sender of the original message the waited-variable is set by the batch-mix,
# in case the Ack-Message reaches it while a other batch mix is currently processed
class AckMessage:
    def __init__(self, msg):
        self.id = msg.id
        self.sender = msg.sender
        self.waited_for_batch = 0

# calculation of a exponential distributed time slot. This is used both for calculating interarrival times with lambda
# and the delay times with mu
def get_poisson_time_slot(exp_parameter):
    p = random.random()
    delay_time = round((-math.log(1.0 - p) / exp_parameter), 6)
    return delay_time
