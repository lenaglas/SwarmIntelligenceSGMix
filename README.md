# SwarmIntelligenceSGMix
SwarmIntelligenceSGMix project on the chair for cybersecurity of the university about providing anonymous communication with an Stop-And-Go-Mix (short SG-Mix) using swarm intelligence.

A SG-Mixes as introduced by [Kesodgan et al.](https://link.springer.com/chapter/10.1007/3-540-49380-8_7) is a server that aims to provide anonymous communication in a network. 
Contrary to a Batch- or Pool-Mix it delays each incoming message individually to prohobit the correlation of incoming and outgoing network. Whenever little messages are sent in the network it results in a lack of anonymity as not many messages are passing through the mix. A way to bypass this problem is to add dummy messages to the network traffic as e.g. proposed by [Diaz et al.](https://link.springer.com/chapter/10.1007/1-4020-8145-6_18). Assuming the flow of non-dummy messages and therefore the capacity of the network varies during the lifetime of the system, having a constant flow rate of dummy messages can lead to an overload of the network's capacity whenever the flow rate of non-dummy messages is high which results again in an unwanted delay of the non-dummy messages. In research this problem has been overcome by introducing a central authority or network manager that mananages the flow rate of dummy messages. However, this makes the system dependend on the central authority and relies on its availability and integrity.

This project aims to overcome this by using swarm intelligence to control the flow rate of dummy messages instead of a central authority. Thereby, every sender is provided information about the current utilization of the network to control the amount of dummy messages he or she sends together with his or her real non-dummy messages. This is realized by introducing Acknoledgement-Messages (short Acks) and a Batch-Mix to the system. Every time a receiver receives a message (forwarded by the SG-Mix) it sends back an Ack to the Batch-Mix. Only the Batch-Mix decrypts the information who the inital message was from and forwards it. When a sender receives an Ack-message it can derive the utilization of the network from the time it took to receive an Ack message for a message he or she has sent. Every sender aims to optimize this duration and therefore the network capacity. 
















The concept was protoypically implemented in python using two different modes of optimization.
