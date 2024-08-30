from ortools.sat.python import cp_model
# from typing import Union
import csv
import os
from collections import defaultdict

# directory to loop thru
directory = r"C:\Users\clave\OneDrive\Desktop\Scheduler_app_resources\ra_schedules"

num_ras = 68
num_days = 5  # m-f
num_shifts = 11  # 9-8  == 11 shifts

all_ras = list(range(num_ras))
all_days = list(range(num_days))
all_shifts = list(range(num_shifts))


# # 1 means unavailable:
# # [ [11 bits for M], [11 bits for T], [11 bits for W], [11 bits for R], [11 bits for F] ], <-- this is Amber
# # [ [11 bits for M], [11 bits for T], [11 bits for W], [11 bits for R], [11 bits for F] ], <-- this is Caroline
# # [ [11 bits for M], [11 bits for T], [11 bits for W], [11 bits for R], [11 bits for F] ], <-- this is Dean
# unavailabilityMatrix = []

ra_list = []
# a big array, where each ra has an array and their array has 5 arrays for the days, filled with 11 0s for the shifts (means fully available)
unavailability_matrix = [
    [[0 for _ in range(num_shifts)] for _ in range(num_days)] for _ in range(num_ras)]

# Iterate over files in directory
for name in os.listdir(directory):
    # Open file
    # creates path for every filename by appending it
    with open(os.path.join(directory, name)) as f:
        ra_name = name.split('-')[0]
        ra_list.append(ra_name)  # ra name list, also gives us their index
        ra_spot_in_matrix = ra_list.index(ra_name)
        csvFile = csv.reader(f)
        for line in csvFile:
            for dayNum in range(len(line)):
                # each day only has the shifts that don't work
                for unavail in line[dayNum].split(','):
                    if (unavail):
                        intUnavail = (int(unavail))
                        # change 0 to 1 to show unavailable, subtract 9 to account for starting at 9
                        unavailability_matrix[ra_spot_in_matrix][dayNum][intUnavail-9] = 1

# NOW unavailability matrix is full


model = cp_model.CpModel()

# ADDING METHODS are for ADDING CONSTRAINTS TO THE MODEL!!!

shifts = {}
for r in all_ras:
    for d in all_days:
        for s in all_shifts:
            shifts[(r, d, s)] = model.new_bool_var(f"shift_ra{r}_d{d}_s{s}")
            # shifts[(r, d, s)] equals 1 if shift s is assigned to ra r on day d, and 0 otherwise

# Constraints

# CONSTRAINT 1: for each shift, the sum of the ras assigned to that shift should be between 2 and 4
for d in all_days:
    for s in all_shifts:
        model.Add(sum(shifts[(r, d, s)] for r in all_ras) >= 2)
        model.Add(sum(shifts[(r, d, s)] for r in all_ras) <= 4)


# CONSTRAINT 2: if ra is unavailable that day, do not schedule them
for ra in all_ras:
    for shift in all_shifts:
        for day in all_days:
            if unavailability_matrix[ra][day][shift]:
                model.Add(shifts[ra, day, shift] == 0)


# CONSTRAINT 3: Each RA's total shifts across the week should be between 2 and 3
for ra in all_ras:
    shifts_assigned = sum(shifts[(ra, d, s)]
                          for d in all_days for s in all_shifts)
    # model.Add(shifts_assigned)
    model.Add(shifts_assigned == 3)

# CONSTRAINT 4: At least 2 RAs per shift
for d in all_days:
    for s in all_shifts:
        # Ensure at least 2 RAs are assigned to each shift
        model.Add(sum(shifts[(r, d, s)] for r in all_ras) >= 2)


# Define consecutive shifts variables and objective
consecutive_shifts = {}
for r in all_ras:
    for d in all_days:
        for s in range(num_shifts - 1):
            consecutive_shifts[(r, d, s)] = model.NewBoolVar(
                f'consec_{r}_{d}_{s}')
            model.AddBoolOr([shifts[(r, d, s)].Not(), shifts[(
                r, d, s+1)].Not()]).OnlyEnforceIf(consecutive_shifts[(r, d, s)])
            model.AddBoolAnd([shifts[(r, d, s)], shifts[(r, d, s+1)]]
                             ).OnlyEnforceIf(consecutive_shifts[(r, d, s)])

# Maximize the number of consecutive shifts
model.Maximize(sum(consecutive_shifts[(
    r, d, s)] for r in all_ras for d in all_days for s in range(num_shifts - 1)))


solver = cp_model.CpSolver()
status = solver.Solve(model)

csv_data = [[''] * num_days for _ in all_shifts]
day_headers = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

for d in all_days:
    csv_data.append([day_headers[d]] + [''] * num_shifts)

if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
    for day in all_days:
        for shift in all_shifts:
            ra_assigned = ''
            for ra in all_ras:
                if solver.Value(shifts[(ra, day, shift)]):
                    ra_assigned = f"RA {ra_list[ra]}"  # gets actual name
                    if csv_data[shift][day]:  # If there's already data there
                        csv_data[shift][day] += f", {ra_assigned}"
                    else:  # If it's empty
                        csv_data[shift][day] = ra_assigned
            # csv_data[shift][day] = (ra_assigned)
else:
    print("no solution")

# max number assigned to a shift
max_ras_per_shift = max(len(csv_data[shift][day].split(
    ", ")) for shift in all_shifts for day in all_days)

with open("desk_schedule.csv", 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(["Shift"] + [f"{day}" for day in day_headers])
    # Write the schedule data
    for shift in range(num_shifts):
        writer.writerow(
            [f'Time: {(shift+9) % 12 if (shift+9) % 12 != 0 else 12} '] + csv_data[shift])
