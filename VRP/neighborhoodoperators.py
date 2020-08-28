from perturbations import Perturbations
from helpers import compile_neighbor
import random
from copy import copy

class NeighborhoodOperators:
    """
    This class holds the operators that are used to generate neighboring
    solutions to the Vehicle Routing Problem (VRP).  The metaheuristic
    Simulated Annealing technique requires a neighborhood of solutions,
    created by taking the current working solution and modifying it with
    singular, reversible changes, that are compared to the current solution
    to move towards an optimized solution.  Here, in practice, random shifts
    are made to a solution to generate neighboring solutions, where the
    Simulated Annealing algorithm always accepts better (lower cost)
    solutions and probabilistically accepts worse solutions based on the
    magnitude of the worse-ness and current parameters within the algorithm. 
    """
    @staticmethod
    def local_three_opt(solution):
        """
        Delete three random edges of a randomly selected VRP route, and then
        recreate a valid tour by reversing a random segment.  Note that this
        is a "strict" 3-opt, as the 3 configurations that equate to 2-opt
        swaps (of the 7 total 3-opt configurations) are removed.  The 2-opt
        operator is implemented below in local_flip().
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        route = solution[route_idx]
        n = len(route)

        if n < 3:
            return None

        a, c, e = random.sample(range(n+1), 3)
        a, c, e = sorted([a, c, e])
        b, d, f = a+1, c+1, e+1

        new_route = route.opt_copy_packages()
        p = route.packages

        which = random.randint(0,3)
        if which == 0:
            new_route.packages = p[:a+1] + p[c:b-1:-1] + p[e:d-1:-1] + p[f:]
        elif which == 1:
            new_route.packages = p[:a+1] + p[d:e+1]    + p[b:c+1]    + p[f:]
        elif which == 2:
            new_route.packages = p[:a+1] + p[d:e+1]    + p[c:b-1:-1] + p[f:]
        elif which == 3:
            new_route.packages = p[:a+1] + p[e:d-1:-1] + p[b:c+1]    + p[f:]

        assert len(new_route) == len(route)
        return compile_neighbor(solution, [(route_idx, new_route)])

    @staticmethod
    def local_flip(solution):
        """
        Also called the 2-opt swap.  Select two nodes of a route and reverse
        their order.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_packages()

        if len(new_route) < 2:
            return None

        idx1, idx2 = random.sample(range(1, len(new_route)+1), 2)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1

        
        new_route.packages[idx1:idx2] = solution[route_idx].packages[idx2-1:idx1-1:-1]

        assert len(new_route) == len(solution[route_idx])
        return compile_neighbor(solution, [(route_idx, new_route)])

    @staticmethod
    def local_swap(solution):
        """
        Swap the position of two nodes a randomly selected route.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_packages()

        if len(new_route) < 2:
            return None

        idx1, idx2 = random.sample(range(len(new_route)), 2)
        new_route.packages[idx1], new_route.packages[idx2] = new_route.packages[idx2], new_route.packages[idx1]
        assert len(solution[route_idx]) == len(new_route)
        return compile_neighbor(solution, [(route_idx, new_route)])

    @staticmethod
    def local_insertion(solution):
        """
        Move a randomly selected node to a new position in the same route.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        route = solution[route_idx]

        if len(route) < 2:
            return None

        idx1, idx2 = random.sample(range(len(route)), 2)
        while abs(idx1 - idx2) == 1 and len(route) > 2:
            idx1, idx2 = random.sample(range(len(route)), 2)
        if idx1 > idx2:
            idx1, idx2 = idx2, idx1
        new_route = copy(route)
        new_route.packages = route.packages[:idx1] + route.packages[idx1+1:idx2] + [route.packages[idx1]] + route.packages[idx2:]
        assert len(route) == len(new_route)
        return compile_neighbor(solution, [(route_idx, new_route)])

    @staticmethod
    def local_add_hub(solution):
        """
        Add a hub / depot stop into a random position in a route, allowing a
        truck to load back up to capacity.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_depot_stops()

        if len(new_route) < 1:
            return None

        hub_indices = new_route.get_depot_stop_indices()
        hub_idx = random.randint(1, len(new_route) - 1)
        tries = 0
        while hub_idx in hub_indices and tries < 10:
            tries += 1
            hub_idx = random.randint(1, len(new_route) - 1)

        new_route.add_depot_stop(hub_idx)

        assert abs(len(solution[route_idx].depot_stops) - len(new_route.depot_stops)) <= 1
        return compile_neighbor(solution, [(route_idx, new_route)])

    @staticmethod
    def local_remove_hub(solution):
        """
        Remove a hub / depot stop at random.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_depot_stops()
        
        hub_indices = new_route.get_depot_stop_indices()
        if hub_indices:
            stop = random.choice(list(hub_indices.values()))  
            new_route.remove_depot_stop(stop)
            assert len(new_route.depot_stops) == len(solution[route_idx].depot_stops) - 1
            return compile_neighbor(solution, [(route_idx, new_route)])
        else:
            return None

    @staticmethod
    def local_move_hub(solution):
        """
        Move a hub / depot stop at random.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_depot_stops()
        
        hub_indices = new_route.get_depot_stop_indices()
        if hub_indices:
            stop = random.choice(list(hub_indices.values()))
            while True:
                new_idx = random.randint(1, len(new_route) - 2)
                if new_idx != stop.route_index:
                    break
            new_route.move_depot_stop(stop, new_idx)
            assert len(new_route.depot_stops) == len(solution[route_idx].depot_stops)
            return compile_neighbor(solution, [(route_idx, new_route)])
        else:
            return None

    @staticmethod
    def local_add_pause(solution):
        """
        Add a pause (wait time), of a random duration between 1 and 30 minutes,
        to a randomly selected hub / depot stop.  As this version of the
        CVRPTW (constrained vehicle routing problem with time windows)
        includes earliest-load-times but not earliest-delivery-times, truck
        pauses can be generalized as only occuring while at the depot without
        losing optimization ability.  Therefore, pauses are maintained as a
        property of the DepotStop class.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_depot_stops()
        
        hub_indices = new_route.get_depot_stop_indices()

        if hub_indices:
            stop = random.choice(list(hub_indices.values()))
            minutes = random.randint(1, 30)
            stop.increase_wait(minutes)
            assert sum(d.wait_minutes for d in solution[route_idx].depot_stops) == sum(d.wait_minutes for d in new_route.depot_stops) - minutes
            return compile_neighbor(solution, [(route_idx, new_route)])
        else:
            return None

    @staticmethod
    def local_remove_pause(solution):
        """
        Remove pause / wait time, of a random duration between 1 and 30 minutes,
        to a randomly selected hub / depot stop.  As this version of the
        CVRPTW (constrained vehicle routing problem with time windows)
        includes earliest-load-times but not earliest-delivery-times, truck
        pauses can be generalized as only occuring while at the depot without
        losing optimization ability.  Therefore, pauses are maintained as a
        property of the DepotStop class.
        Θ(n)
        """
        route_idx = random.randint(0, len(solution) - 1)
        new_route = solution[route_idx].opt_copy_depot_stops()
        
        hub_indices = new_route.get_depot_stop_indices()

        if hub_indices:
            stop = random.choice(list(hub_indices.values()))
            minutes = random.randint(1, 30)
            stop.decrease_wait(minutes)

            assert sum(max(d.wait_minutes - minutes, 0) if stop.route_index == d.route_index else d.wait_minutes for d in solution[route_idx].depot_stops) == sum(d.wait_minutes for d in new_route.depot_stops)
            return compile_neighbor(solution, [(route_idx, new_route)])
        else:
            return None

    @staticmethod
    def nonlocal_insertion(solution):
        """
        Delete a random node from one route and insert it into a random
        position in a different route.
        Θ(n)
        """
        if len(solution) < 2:
            raise ValueError('Can not generate neighbor from non-local operator without multiple routes.')

        route_idx1, route_idx2 = random.sample(range(len(solution)), 2)
        if not solution[route_idx1] or not solution[route_idx2]:
            return None

        new_route1 = solution[route_idx1].opt_copy_packages()
        new_route2 = solution[route_idx2].opt_copy_packages()

        idx1 = random.randint(0, len(new_route1) - 1)
        idx2 = random.randint(0, len(new_route2) - 1)

        package_copy = copy(new_route1.packages[idx1])
        new_route1.packages.pop(idx1)
        new_route2.add_package(package_copy, idx2)

        assert len(solution[route_idx1]) + len(solution[route_idx2]) == len(new_route1) + len(new_route2)

        swaps = [(route_idx1, new_route1), (route_idx2, new_route2)]
        swaps.sort()

        return compile_neighbor(solution, swaps)

    @staticmethod
    def nonlocal_swap(solution):
        """
        Exchange the positions of two nodes from different routes.
        Θ(n)
        """
        if len(solution) < 2:
            raise ValueError('Can not generate neighbor from non-local operator without multiple routes.')

        route_idx1, route_idx2 = random.sample(range(len(solution)), 2)
        if not solution[route_idx1] or not solution[route_idx2]:
            return None
        
        new_route1 = solution[route_idx1].opt_copy_packages()
        new_route2 = solution[route_idx2].opt_copy_packages()

        idx1 = random.randint(0, len(new_route1) - 1)
        idx2 = random.randint(0, len(new_route2) - 1)

        package_copy1 = copy(new_route1.packages[idx1])
        package_copy2 = copy(new_route2.packages[idx2])

        new_route1.packages[idx1] = package_copy2
        new_route2.packages[idx2] = package_copy1
        new_route1.packages[idx1].assign_truck(new_route1.truck)
        new_route2.packages[idx2].assign_truck(new_route2.truck)

        assert len(solution[route_idx1]) + len(solution[route_idx2]) == len(new_route1) + len(new_route2)
        assert solution[route_idx1].packages[idx1].id == package_copy1.id and solution[route_idx2].packages[idx2].id == package_copy2.id
        for i in range(1, len(new_route1)):
            assert new_route1.packages[i].id != new_route1.packages[i-1].id
        for i in range(1, len(new_route2)):
            assert new_route2.packages[i].id != new_route2.packages[i-1].id

        swaps = [(route_idx1, new_route1), (route_idx2, new_route2)]
        swaps.sort()
        return compile_neighbor(solution, swaps)

    @staticmethod
    def generate_neighbors(solution):
        """
        A generator function to yield neighbors to a given solution in
        random order.
        Θ(n)
        """
        ops = [
            NeighborhoodOperators.local_swap,
            NeighborhoodOperators.local_flip,
            NeighborhoodOperators.local_insertion,
            NeighborhoodOperators.nonlocal_insertion,
            NeighborhoodOperators.nonlocal_swap,
            NeighborhoodOperators.local_add_hub,
            NeighborhoodOperators.local_remove_hub,
            NeighborhoodOperators.local_move_hub,
            NeighborhoodOperators.local_add_pause,
            NeighborhoodOperators.local_remove_pause,
            NeighborhoodOperators.local_three_opt,
            Perturbations.double_bridge
        ]
        random.shuffle(ops)
        for gen in ops:
            neighbor = gen(solution)
            if neighbor:
                yield neighbor
