# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020
import System, Sender
import argparse


# messages to be send within the startup phase (before sender begins to send dummy messages)

def main():
    # System is started with the name of the csv outputfile
    # this is called by Automate_Script.py
    parser = argparse.ArgumentParser()
    parser.add_argument('-o', '--outputfile', type=str, required=True)
    args = parser.parse_args()
    System.outputfile = args.outputfile

    # when system is started, s senders who start their message streams are created
    for i in range(System.NUMBER_OF_SENDERS):
        sender = Sender.Sender(i)


if __name__ == '__main__':
    main()
