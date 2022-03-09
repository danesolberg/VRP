# Vehicle Route Optimization Simulator
Optimization project for the Vehicle Routing Problem (VRP) with capacity and time window constraints (CVRPTW).

## Traveling Salesman Problem
A TSP is an important problem in theoretical computer science and operations research, and a popular example of an NP-hard problem in combinatorial optimization.  The task is to find the most efficient route that brings a salesman through a defined set of cities, in any order, but where the salesman returns back to the city in which they started.  More concisely, find the lowest cost Hamiltonian cycle for a set of points on a graph based on some loss function.

### Vehicle Routing Problem
The VRP is a generalization of the TSP, allowing for a number of complications such as time windows to be in each city, fuel expenditure while traveling, carrying capacity of packages in the vehicles, etc.

## Optimizations
Since this problem is intractable to solve analytically, as there is no polynomial time solution to NP-hard problems (vis-a-vis exponential complexity algorithms), the computational approach taken is usually to find a "good enough" solution via optimization heuristics.  The approach taken based on a review of current literature in this domain was **Simulated Annealing**.

### Simulated Annealing
- Simulated Annealing is a metaheuristic technique that has been extensively studied in regard to its performance when applied to the Vehicle Routing Problem. The technique derives its name from the metallurgical process of annealing, whereby a piece of metal (or in fact any material of crystalline atomic structure) is heated to a critical point where the atoms inside the material can reform into a new crystalline structure and is then allowed to slowly cool as new crystals develop.
- The algorithm is analogous to the physical process.  The algorithm starts at a high "temperature" and each iteration of the process "cools" the temperature down until a specified temperature is reached. During each iteration, a set of solutions are generated that are altered slightly from the current solution.  These related solutions are referred to as "neighbors."  The steps to generate neighboring solutions are independent of the Simulated Annealing metaheuristic, but it is important that each neighbor is a single, reversible step change away from the current working solution.
- Each iteration, once a neighborhood of solutions is generated, the cost difference between the current solution and a neighbor solution is calculated.  If the neighbor solution has a lower cost, it is automatically accepted.  If the neighbor solution cost is greater than the current solution, it can still be accepted according to the probability e^(-delta_cost/temp).
- Thus, there are two stages that the algorithm moves through as the temperature decreases.  At hotter temperatures, the algorithm is in an "exploratory" stage where it readily accepts worse solutions in an attempt to escape local minima costs.  At colder temperatures the "exploitative" stage begins, and the algorithm attempts to optimize within the bounds of the local minima that it currents finds itself in. As with other heuristics, there is no guarantee that the global optima will be found.
