from neighborhoodoperators import NeighborhoodOperators
from helpers import print_progress_bar
import random
import math

try:
    from matplotlib import pyplot as plt
except:
    plt = None

class SimulatedAnnealing:
    """
        Simulated Annealing is a metaheuristic technique that has been
        extensively studied in regard to its performance when applied to the
        Vehicle Routing Problem.
        The technique derives its name from the metallurgical process
        of annealing, whereby a piece of metal (or in fact any material of
        crystalline atomic structure) is heated to a critical point where the
        atoms inside the material can reform into a new crystalline structure
        and is then allowed to slowly cool as new crystals develop.
        The algorithm is analogous to the physical process.  The algorithm
        starts at a high "temperature" and each iteration of the process
        "cools" the temperature down until a specified temperature is reached.
        During each iteration, a set of solutions are generated that are
        altered slightly from the current solution.  These related solutions 
        are referred to as "neighbors."  The steps to generate neighboring
        solutions are independent of the Simulated Annealing metaheuristic, but
        it is important that each neighbor is a single, reversible step change
        away from the current working solution.
        Each iteration, once a neighborhood of solutions is generated,
        the cost difference between the current solution and a neighbor
        solution is calculated.  If the neighbor solution has a lower cost,
        it is automatically accepted.  If the neighbor solution cost is greater
        than the current solution, it can still be accepted according to the
        probability e^(-delta_cost/temp).
        Thus, there are two stages that the algorithm moves through as the
        temperature decreases.  At hotter temperatures, the algorithm is in an
        "exploratory" stage where it readily accepts worse solutions in an
        attempt to escape local minima costs.  At colder temperatures the
        "exploitative" stage begins, and the algorithm attempts to optimize
        within the bounds of the local minima that it currents finds itself in.
        As with other heuristics, there is no guarantee that the global
        optima will be found.
    """
    def __init__(self, test_eval_func, init_solution, init_temp, final_temp, iter_per_temp=100, alpha=10):
        self.test_eval = test_eval_func
        self.solution = init_solution
        self.cur_feas, self.cur_cost = test_eval_func(init_solution)
        self.init_temp = init_temp
        self.cur_temp = init_temp
        self.final_temp = final_temp
        self.iter_per_temp = iter_per_temp
        self.alpha = alpha
        self.cur_iter = 0
        self.exp_iter = self.calc_iterations()
        self.feasible = all(self.cur_feas)

        self.plot_costs = []

    def decrement_temp(self):
        """Decrement the current temperature according to a geometric reduction."""
        self.cur_temp *= self.alpha

    def calc_iterations(self):
        """
        Calculate the number of iterations required to reduce the initial
        temperature down to the specific final temperature as set during
        SimulatedAnnealing object instantiation.
        """
        i = 0
        cur_temp = self.cur_temp
        while cur_temp > self.final_temp:
            i += 1
            cur_temp *= self.alpha
        return i

    def isTerminationCriteriaMet(self):
        """Return True when the current temperature is less than or equal to
        the specified final temperature."""
        return self.cur_temp <= self.final_temp

    def plot_cost_graph(self):
        if plt is None:
            raise ImportError('Must install matplotlib to plot route.')

        plt.plot(list(range(len(self.plot_costs))), self.plot_costs)
        plt.xlabel('Iteration')
        plt.ylabel('Cost')
        plt.show()

    def run(self):
        cur_prog = 0.0
        # Continue looping until the initial temperature reduces down below the
        # final temperature as set by the SimulatedAnnealing object instantiation
        # parameters.  This naively appears to be a constant factor within the
        # runtime complexity analysis; however, studies on the simulated
        # annealing algorithm suggest that a suitably optimal solution can only
        # be found through a number of iterations proportional to n, which
        # indicates a proper asymptotic complexity of O(n)
        # O(n)
        while not self.isTerminationCriteriaMet():
            # Calculate current percentage of completion, as measured by
            # iteration count, and output this percentage to the terminal
            # in the form of a progress bar.
            # O(1)
            self.cur_iter += 1
            new_prog = round(self.cur_iter/self.exp_iter, 2)
            if new_prog > cur_prog or self.cur_iter == self.exp_iter:
                print_progress_bar(self.cur_iter, self.exp_iter, decimals=0)
                cur_prog = new_prog
            # For each discrete temperature, run the neighborhood generation
            # and solution comparison steps for a specified number of iterations
            # as set by the SimulatedAnnealing object instantiation parameters.
            # O(1)
            for _ in range(self.iter_per_temp):
                # Generate a list of neighboring local solution states based on
                # probabilistic operators that create these neighbor states
                # by applying singular, random changes to the current solution.
                # Runtime complexity is determined by the specific operators
                # used to generate the neighborhood, but this implementation is
                # sadly Θ(n) due to copying of list-based routes.
                neighbors = NeighborhoodOperators.generate_neighbors(self.solution)
                # Choose the first neighbor solution from the neighborhood
                # generator function.  The generator randomly chooses the type
                # of solution-modulating operator that is applied to create
                # each neighbor.
                # O(1)
                try:
                    new_solution = next(neighbors)
                except:
                    continue
                # Calculate the cost (miles driven) between the current
                # solution and the chosen neighbor solution.  A large cost
                # padding is applied to solutions that are not 'feasible,'
                # meaning solutions that do not satisfy all problem constraints.
                # O(n)
                cur_cost = self.cur_cost
                new_feas, new_cost = self.test_eval(new_solution, return_early=True)
                cur_cost_adj, new_cost_adj = cur_cost, new_cost
                feasible = all(new_feas)
                if not feasible:
                    new_cost_adj += self.init_temp*1000
                if not self.feasible:
                    cur_cost_adj += self.init_temp*1000
                delta_cost = new_cost_adj - cur_cost_adj

                # Per the simulated annealing algorithm, neighbor solutions
                # with a lower cost than the current solution are automatically
                # accepted.
                # O(1)
                if delta_cost <= 0:
                    self.solution = new_solution
                    self.feasible = feasible
                    self.cur_cost = new_cost
                # Per the simulated annealing algorithm, if the new solution
                # is not better, accept it with a probability of e^(-delta_cost/temp).
                # To do this we generate a random value [0,1] and compare it to
                # e^(-delta_cost/temp), as e^x is bounded (0,1) for all x < 0.
                # O(1)
                else:
                    if random.uniform(0, 1) < math.exp(-delta_cost / self.cur_temp):
                        self.solution = new_solution
                        self.feasible = feasible
                        self.cur_cost = new_cost
            # Decrement the temperature according to the geometric function
            # temp = temp*alpha where alpha is a value less than 1 set during
            # the SimulatedAnnealing object instantiation.
            # O(1)
            self.plot_costs.append(self.cur_cost)
            self.decrement_temp()
        return self.solution
