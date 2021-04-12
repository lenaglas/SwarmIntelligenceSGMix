#Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
#Master Wirtschaftsinformatik, Uni Regensburgs
#written by Magdalena Glas and Verena Mainz, July 2020

import Receivers, Mixes

#VALUES TO CONFIGURE:

#0: no opt, 1: batch opt, 2: continouus opt, 3:no dummy messages
OPTIMIZATION_MODE = 2
#batch size b
BATCH_SIZE = 20
#optimisation factor f
OPTIMIZATION_FACTOR = 0.01
#messages in warm_up_phase
SCOPE_WARMUP_PHASE = 50
#number of non-dummy-messages per sender
NUMBER_OF_MESSAGES = 500
#processing time of one batch
BATCH_DURATION=0.05
NUMBER_OF_SENDERS = 2
#parameter for sg-mix delay t_i
MU_DELAY = 1000
#lambda for non-dummy messages for each sender
INTERARRIVAL_LAMBDAS=[8,16]
NUMBER_OF_RECEIVERS = 50
D_MIN = 0
D_MAX = 1
CONTENTS = ["A", "B", "C"]  # just a random selection to give each message a content
# clock deviation assumed to be 0
SYN = 0


#information used globally within the system
outputfile="" #set in main.py
done=0
stopp=0
batches = []
receivers = []
receivers = {}
senders = []


#intitaion of receivers, sg-mix and batch-mix
for i in range(NUMBER_OF_RECEIVERS):
    receiver = Receivers.Receiver(i)
    # for the users/senders to select a receiver to send the message to
    receivers[i]=receiver

dummy_receiver = Receivers.Receiver(999)

batch_mix = Mixes.BatchMix()
sg_mix = Mixes.SG_Mix()

