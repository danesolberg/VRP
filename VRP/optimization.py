from neighborhoodoperators import NeighborhoodOperators
from perturbations import Perturbations
from simulatedannealing import SimulatedAnnealing
import logging

def nearest_neighbor(start_loc, packages):
    cur_loc = start_loc
    i = 0
    new_packages = packages[:]
    while i < len(new_packages):
        nearest_idx = i
        nearest_dist = float('inf')
        for j in range(i, len(new_packages)):
            loc = new_packages[j].delivery_location
            dist = cur_loc.distances[loc.id]
            if dist < nearest_dist:
                nearest_dist = dist
                nearest_idx = j
        new_packages[i], new_packages[nearest_idx] = new_packages[nearest_idx], new_packages[i] 

        cur_loc = new_packages[i].delivery_location
        i += 1
    return new_packages

def two_opt(solution, test_eval):
    ret = []
    for route_idx, route in enumerate(solution):
        best = route.opt_copy_packages()
        best_cost = test_eval([best if i == route_idx else r for i, r in enumerate(solution)])[1]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route.packages)-2):
                for j in range(i+1, len(route.packages)+1):
                    if j-i == 1: continue # changes nothing
                    new_route = route.opt_copy_packages()
                    new_route.packages[i:j] = route.packages[j-1:i-1:-1] # this is the 2optSwap
                    new_feas, new_cost = test_eval([new_route if i == route_idx else r for i, r in enumerate(solution)])
                    if all(new_feas) and new_cost < best_cost:
                        best = new_route
                        best_cost = new_cost
                        improved = True
            route = best
        ret.append(best)
    assert sum(len(r.packages) for r in solution) == sum(len(r.packages) for r in ret)
    return ret

def three_opt(solution, test_eval):
    ret = []
    for route_idx, route in enumerate(solution):
        best = route.opt_copy_packages()
        best_cost = test_eval([best if i == route_idx else r for i, r in enumerate(solution)])[1]
        improved = True
        while improved:
            improved = False
            for i in range(1, len(route.packages)-3):
                for j in range(i+1, len(route.packages)-2):
                    for k in range(i+2, len(route.packages)-1):
                        a, c, e = i, j, k
                        b, d, f = a+1, c+1, e+1

                        p = route.packages
                        three_opts = [
                            p[:a+1] + p[b:c+1]    + p[e:d-1:-1] + p[f:], # 2-opt
                            p[:a+1] + p[c:b-1:-1] + p[d:e+1]    + p[f:], # 2-opt
                            p[:a+1] + p[c:b-1:-1] + p[e:d-1:-1] + p[f:], # 3-opt
                            p[:a+1] + p[d:e+1]    + p[b:c+1]    + p[f:], # 3-opt
                            p[:a+1] + p[d:e+1]    + p[c:b-1:-1] + p[f:], # 3-opt
                            p[:a+1] + p[e:d-1:-1] + p[b:c+1]    + p[f:], # 3-opt
                            p[:a+1] + p[e:d-1:-1] + p[c:b-1:-1] + p[f:]  # 2-opt
                        ]
                        for new_packages in three_opts:
                            new_route = route.opt_copy_packages()
                            new_route.packages = new_packages
                            new_feas, new_cost = test_eval([new_route if i == route_idx else r for i, r in enumerate(solution)])
                            if all(new_feas) and new_cost < best_cost:
                                best = new_route
                                best_cost = new_cost
                                improved = True
            route = best
        ret.append(best)
    assert sum(len(r.packages) for r in solution) == sum(len(r.packages) for r in ret)
    return ret

def local_search(solution, test_eval):
    i = 0
    STUCK_THRESHOLD = 100
    ITERATION_THRESHOLD = 50000
    cur_feas, cur_cost = test_eval(solution)
    best = solution
    if all(cur_feas):
        best_feasible = solution
    else:
        best_feasible = None
    feas_weights = [1] * len(cur_feas)
    weighted_feas = lambda l: sum([feas_weights[i] * int(not l[i]) for i in range(len(feas_weights))])
    cur_weighted_feas = weighted_feas(cur_feas)
    inc_weights = lambda l: list(map(lambda x: feas_weights[x[0]] + 1 if x[1] == False else feas_weights[x[0]], enumerate(l)))
    stuck = 0
    improved = True
    while improved:
        if stuck > STUCK_THRESHOLD:
            logging.warning('Stuck local search. Stopping...')
            return best_feasible
        improved = False
        neighbors = NeighborhoodOperators.generate_neighbors(solution)

        for neighbor in neighbors:
            i += 1
            if i > ITERATION_THRESHOLD:
                logging.warning('Reached iteration limit. Stopping...')
                return best_feasible
            new_feas, new_cost = test_eval(neighbor)
            if weighted_feas(new_feas) < cur_weighted_feas-50 or new_cost < cur_cost:
                stuck = 0
                best = neighbor
                cur_cost = new_cost
                cur_feas = new_feas
                cur_weighted_feas = weighted_feas(cur_feas)
                if cur_weighted_feas == 0:
                    best_feasible = best
                feas_weights = [1] * len(cur_feas)
                improved = True
                break
            
        if not improved and cur_weighted_feas > 0:
            stuck += 1
            feas_weights = inc_weights(cur_feas)
            cur_weighted_feas = weighted_feas(cur_feas)
            improved = True
    return best_feasible

def iterative_local_search(initial_solution, test_eval, iterations):
    best = initial_solution
    assert all(test_eval(best)[0]) == True
    best_cost = test_eval(initial_solution)[1]
    for i in range(iterations):
        print(f"Round {i+1}/{iterations}...")
        initial_solution = two_opt(initial_solution, test_eval)
        ls_solution = local_search(initial_solution, test_eval)
        if test_eval(ls_solution)[1] < test_eval(initial_solution)[1]:
            initial_solution = ls_solution
        
        new_cost = test_eval(initial_solution)[1]
        if new_cost < best_cost:
            best = initial_solution
            best_cost = new_cost
        print('Best solution cost: %s' % best_cost)
        k = 0
        while True:
            k += 1
            if k > 10000:
                logging.warning("Unable to find feasible perturbation.")
                break
            # p_solution = NeighborhoodOperators.local_three_opt(best)
            p_solution = Perturbations.double_bridge(best)
            if all(test_eval(p_solution)[0]):
                initial_solution = p_solution
                break
        print('New neighborhood cost: %s' % test_eval(initial_solution)[1])
        print()
    assert all(test_eval(best)[0]) == True
    return best

def iterative_stochastic_optimization(solution, test_eval, iterations, iter_per_temp):
    best_sol = solution
    prev_sol = solution
    cur_sol = solution
    for i in range(iterations):
        print(f"Round {i+1}/{iterations}...")
        sim = SimulatedAnnealing(test_eval, cur_sol, 1000, 0.01, iter_per_temp, 0.9995)
        sim.run()
        cur_feas, cur_cost = sim.test_eval(sim.solution)
        if all(cur_feas) and cur_cost < test_eval(cur_sol)[1]:
            cur_sol = sim.solution

        local_opt = two_opt(cur_sol, sim.test_eval)
        if sim.test_eval(local_opt)[1] < sim.test_eval(cur_sol)[1]:
            cur_sol = local_opt

        if sim.test_eval(cur_sol)[1] < sim.test_eval(best_sol)[1]:
            best_sol = cur_sol
        print('Current best solution cost: %s' % sim.test_eval(best_sol)[1])
        
        if prev_sol is cur_sol:
            k = 0
            while True:
                k += 1
                if k > 5000:
                    logging.warning("Unable to find feasible perturbation.")
                    break
                p_sol = Perturbations.double_bridge(best_sol)
                if all(sim.test_eval(p_sol)[0]):
                    cur_sol = p_sol
                    break
            print('New neighborhood cost: %s' % test_eval(p_sol)[1])
            print()

        prev_sol = cur_sol
    assert all(sim.test_eval(best_sol)[0]) == True
    return best_sol