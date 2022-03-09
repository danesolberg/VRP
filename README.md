# Vehicle Route Optimization Simulator
Optimization project for the Vehicle Routing Problem (VRP) with capacity and time window constraints (CVRPTW).

## Traveling Salesman Problem
A TSP is an important problem in theoretical computer science and operations research, and a popular example of an NP-hard problem in combinatorial optimization.  The task is to find the most efficient route that brings a salesman through a defined set of cities, in any order, but where the salesman returns back to the city in which they started.  More concisely, find the lowest cost Hamiltonian cycle for a set of points on a graph based on some loss function.

### Vehicle Routing Problem
The VRP is a generalization of the TSP, allowing for a number of complications such as time windows to be in each city, fuel expenditure while traveling, carrying capacity of packages in the vehicles, etc.

## Optimizations
Since this problem is intractable to solve analytically, as there is no polynomial time solution to NP-hard problems (vis-a-vis exponential complexity algorithms), the computational approach taken is usually to find a "good enough" solution via optimization heuristics.  The approach taken based on a review of current literature in this domain was **Simulated Annealing**
