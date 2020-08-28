from deliverysimulator import DeliverySimulator, Constraint
from optimization import two_opt, iterative_stochastic_optimization
from datetime import datetime, date
import logging

def show_package_statuses(cur_time, simulator):
    today = date.today()
    exit_input = 0
    while exit_input == 0:
        print(f'View package statuses at {cur_time} (y) or choose custom time (c)? y/n/c')
        ans = input()
        if ans == 'y':
            cur_time = datetime.strptime(cur_time, "%I:%M %p").time()
            simulator.lookup_status(datetime.combine(today, cur_time), range(1,41))
            exit_input = 1
        elif ans == 'c':
            while True:
                print('Enter custom time (hh:mm AM/PM) or go (b)ack:')
                ans = input()
                if ans == 'b':
                    break
                try:
                    custom_time = datetime.strptime(ans, "%I:%M %p").time()
                except:
                    continue
                simulator.lookup_status(datetime.combine(today, custom_time), range(1,41))
                exit_input = 1
                break
        elif ans == 'n':
            exit_input = 1

def main():
    today = date.today()
    # Construct main delivery simulator object, from which all function and
    # optimization occurs.
    simulator = DeliverySimulator(999, 2, 18, 16, datetime(today.year, today.month, today.day, hour=8), '../data/')
    
    # Evaluate cost of initial, naive solution.
    sol = simulator.current_solution()
    feas, cost = simulator.test_eval(sol)
    print(f"Initial routing solution requires {round(cost,1)} total miles.\n")

    # Perform local optimization of the initial solution using a 2-opt
    # greedy strategy.
    print("Performing greedy local optimization...")
    sol = two_opt(sol, simulator.test_eval)
    feas, cost = simulator.test_eval(sol)
    print('Done!')
    print(f"Locally optimal routing solution requires {round(cost,1)} total miles.\n")

    # Tests embedded in code for now.
    assert all(simulator.test_eval(sol)[0]) == True

    # Perform further optimization through probabilistic simulated annealing
    # technique.
    print("Performing stochastic optimization through simulated annealing...")
    best_sol = iterative_stochastic_optimization(sol, simulator.test_eval, 1, 20)

    # As outlined in the SimulatedAnnealing and NeighborhoodOperator classes,
    # heuristic techniques are applied via random step changes to the current
    # solution to find a suitable solution.  One such step change is adding 
    # and removing truck wait times, to satisfied earliest package load time
    # constraints.  This can result in excessive wait times between package 
    # deliveries, as the goal is not to optimize for delivery time outside of
    # time window constraints.  Due to this fact, the program minimizes wait
    # times in the optimized solution to align with realistic usage.
    simulator.minimize_wait_times(best_sol)

    feas, cost = simulator.test_eval(best_sol)
    print('Done!')
    print(f"Optimized heuristic routing solution requires {round(cost,1)} total miles.\n")

    # Tests embedded in code for now.
    assert all(feas) == True
    for constraint in Constraint:
        print('Final solution satisfies %s constraint: %s' % (constraint.name, feas[constraint.value]))
    print('Final solution satisfies all problem constraints.')
    print()

    # Once a suitable solution is found, the route and package objects are
    # inserted back into the functional delivery system classes for further
    # operation by the end user.
    simulator.insert_optimized_solution(best_sol)
    for truck in simulator.depot.trucks:
        print(truck.route)
    print()

    # Creates the terminal-based interface for the end user to lookup
    # package status at arbitrary times.
    print('Performing package lookup...')
    show_package_statuses('8:55 AM', simulator)
    show_package_statuses('10:00 AM', simulator)
    show_package_statuses('12:04 PM', simulator)

    print('Simulation finished!')

# Main program. Entry point to code execution.
if __name__ == "__main__":
    main()
