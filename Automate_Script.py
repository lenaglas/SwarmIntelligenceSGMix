# Projektseminar "Optimierung eines SG-Mix-Netzwerkes mithilfe von Schwarmintelligenz"
# Master Wirtschaftsinformatik, Uni Regensburgs
# written by Magdalena Glas and Verena Mainz, July 2020
import subprocess
from datetime import datetime, timedelta, date
import os
import System, Sender
import csv, statistics

# variable to set how many simulation runs should be made with one set of parameters
NUMBER_SIMULATIONS = 5

# creating global variables for set of simulation runs
time = datetime.now().strftime("%d%m_%H_%M_%S")
name = f'OPT_{System.OPTIMIZATION_MODE}_BatchSize_{System.BATCH_SIZE}_L8-16'

# values used for evaluation-csv, shows min and max value for each run plus how often
# a non-dummy-message reached the batch-mix while it was busy
min_values = []
max_values = []
batch_capacities = []

# creating a directory to store the csv for each run plus the evaluation csv in
path = "./Auswertung/" + name + "/"
os.mkdir(path)

# calling the simulations runs using a batch command
for i in range(NUMBER_SIMULATIONS):
    print("GO NR ", i)
    filename = path + name + "_" + "simulation_" + str(i + 1) + ".csv"
    System.outputfile = filename
    # start the program with batch command
    cmd = "py Main.py --outputfile " + System.outputfile
    os.system(cmd)

# after all simulation runs are performed an evaluation csv is being created
medians = []
directory = os.path.join(path)
for root, dirs, files in os.walk(directory):
    for file in files:
        if file.endswith(".csv"):
            with open(path + "\\" + file) as csvfile:
                durations = []
                lambdas = []
                capacities = 0
                f = csv.DictReader(csvfile, delimiter=';')
                # reading every line (message) of each created csv
                for row in f:
                    # columns CSV:
                    # DURATION, ID, LAMBDA, DUMMY, WAITED_FOR_BATCH, SENDER_ID, POST_TIME, ARRIVAL_TIME, BATCH_SIZE, NUMBER_SENDERS, NUMBER_MESSAGES, OPT_MODE
                    dummy = int(row["DUMMY"])
                    # reading the duration of each non-dummy message
                    # this is the value that is used for evaluating a simulation run
                    if dummy == 0:
                        duration = float(row["DURATION"])
                        durations.append(duration)
                        capacities = capacities + int(row["WAITED_FOR_BATCH"])
                    else:
                        # reading all vales for lambda_dummy
                        lambda_interarrival = float(row["LAMBDA"])
                        lambdas.append(lambda_interarrival)

                if len(durations) != 0:
                    # calculating the median of all durations
                    medians.append(statistics.median(durations))

            # if dummy messages are in use, calculating min and max value for lambda_dummy for each run
            if System.OPTIMIZATION_MODE != 3:
                min_values.append(min(lambdas))
                max_values.append(max(lambdas))
            else:
                min_values.append(0)
                max_values.append(0)
            batch_capacities.append(capacities)

print("Min values: ", min_values)
print("Max values: ", max_values)
print("ALL MEDIANS:")
print(medians)

# creating the evaluation file
evaluation_file = path + name + "_evaluation.csv"
with open(evaluation_file, 'a') as csvevaluation:
    # columns of the evaluation csv:
    # OPTIMIZATION FACTOR, MEDIAN, BATCH_SIZE, WAITED, MAX_LAMBDA, MIN_LAMBDA, OPT_MODE
    headers = "optimization_factor" + ";" + "Median" + ";" + "Batch Size" + ";" + "Waited for Batch" + ";" + "Max Lambda" + ";" + "Min Lambda" + ";" + "OPT Mode"
    csvevaluation.write(headers)
    csvevaluation.write("\n")
    # creating one entry in csv per simulation run
    for i in range(NUMBER_SIMULATIONS):
        row = str(System.OPTIMIZATION_FACTOR) + ";" + str(medians[i]) + ";" + str(System.BATCH_SIZE) + ";" + str(
            batch_capacities[i]) + ";" + str(max_values[i]) + ";" + str(min_values[i]) + ";" + str(
            System.OPTIMIZATION_MODE)
        row = row.replace(".", ",")  # as excel is used in german
        csvevaluation.write(row)
        csvevaluation.write("\n")
