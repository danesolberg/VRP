from depot import Depot
from depotstop import DepotStop
from optimization import nearest_neighbor
from package import Package
from dataloader import DataLoader
from enum import Enum
from collections import namedtuple
from copy import copy
from datetime import timedelta
from operator import attrgetter

try:
    from matplotlib import pyplot as plt
except:
    plt = None

class Constraint(Enum):
    DELIVERED_BY_DEADLINES = 0
    AVAILABLE_WHEN_LOADED = 1
    PACKAGES_ON_REQUIRED_TRUCKS = 2
    WITHIN_TRUCK_CAPACITY = 3
    SATISFIED_LINKED_DELIVERIES = 4

class DeliverySimulator:
    Constants = namedtuple('Constants', ['number_drivers', 'truck_speed', 'truck_capacity', 'start_of_day'])
    def __init__(
        self,
        depot_location,
        number_drivers,
        truck_speed,
        truck_capacity,
        start_of_day,
        data_dir
    ):
        self.constants = DeliverySimulator.Constants(number_drivers, truck_speed, truck_capacity, start_of_day)
        self.data = DataLoader(self, data_dir).import_data()

        self.depot_location = self.data.location_table[depot_location]
        self.depot = self.create_depot()

        self.change_package_address(9, 1004)
        self.initial_route()

    def current_solution(self):
        return self.depot.get_routes()

    def create_depot(self):
        return Depot(self.constants, self.depot_location, self.data)

    def change_package_address(self, package_id, location_id):
        self.data.package_table[package_id].change_delivery_location(self.data.location_table[location_id])

    def initial_route(self):
        packages = list(self.data.package_table.values())
        packages.sort(key=attrgetter('delivery_deadline', 'earliest_load'))

        linked_packages = self.depot.linked_packages
        for group in linked_packages:
            for package in group:
                self.depot.trucks[0].load_package(package)

        i = 0
        while i < len(packages):
            package = packages[i]
            if package.required_truck_number is not None:
                self.depot.trucks[package.required_truck_number - 1].load_package(package)
                packages.remove(package)
            elif any(package in group for group in self.depot.linked_packages):
                packages.remove(package)
            elif str(package.earliest_load.time()) == '09:05:00':
                self.depot.trucks[1].load_package(package)
                packages.remove(package)
            else:
                i += 1

        i = 0
        while i < len(packages):
            package = packages[i]
            if package.delivery_deadline.hour > 10 or package.earliest_load.hour > 8:
                i += 1
            else:
                self.depot.trucks[0].load_package(package)
                packages.remove(package)

        self.depot.trucks[0].route.packages = nearest_neighbor(self.depot_location, self.depot.trucks[0].route.packages)

        num_loaded = 0
        while packages:
            self.depot.trucks[num_loaded % self.constants.number_drivers].load_package(packages.pop(0))
            num_loaded += 1

        routes = self.depot.get_routes()
        total = 0
        for route in routes:
            route.set_minimal_depot_stops()
            total += len(route)
        assert total == 40

        routes[1].get_depot_stop(0).increase_wait(95)

        for i in range(1, len(routes[0])):
            assert routes[0].packages[i].id != routes[0].packages[i-1].id
        for i in range(1, len(routes[1])):
            assert routes[1].packages[i].id != routes[1].packages[i-1].id

    def insert_optimized_solution(self, solution):
        for i, route in enumerate(solution):
            truck = self.depot.trucks[i]
            truck.route = route

            cur_time = self.constants.start_of_day
            load_time = self.constants.start_of_day
            pred_loc = self.depot_location
            for step in route.gen_steps():
                if type(step) is Package:
                    distance = pred_loc.distances[step.delivery_location.id]
                    cur_time += timedelta(hours=distance/self.constants.truck_speed)

                    step.load_time = load_time
                    step.delivery_time = cur_time

                    pred_loc = step.delivery_location
                    self.data.package_table[step.id] = step
                else:
                    distance = pred_loc.distances[self.depot_location.id]
                    cur_time += timedelta(hours=distance/self.constants.truck_speed, minutes=step.wait_minutes)
                    load_time = cur_time
                    pred_loc = self.depot_location
                truck.miles_driven += distance
                truck.current_location = pred_loc

    def lookup_status(self, cur_time, package_ids):
        def format_table(rows):
            col_lens = [max(list(map(lambda x:len(str(x.get(k))), rows)) + [len(str(k))]) for k in rows[0].keys()]
            col_seps = " | ".join("{:<%s}" % m for m in col_lens) + "\n"
            ret = col_seps.format(*rows[0].keys())
            ret += "-" * (sum(col_lens) + 3*len(col_lens)) + "\n"
            ret += "".join(col_seps.format(*v) for v in [ [str(field) for field in row.values()] for row in rows ])
            return ret

        data = []
        for p_id in package_ids:
            package = self.data.package_table[p_id]
            row = {
                'id': package.id,
                'address': package.delivery_location.address,
                'deadline': package.delivery_deadline.time(),
                'city': package.delivery_location.city,
                'zip': package.delivery_location.zipcode,
                'weight': package.mass,
                'status': package.delivery_status(cur_time)
            }
            data.append(row)
        print(format_table(data))
        
    def eval(self, solution):
        """
        Shortcut function to evaluate the cost of a solution without the
        overhead of also determining constraint satisfaction.
        """
        total_miles = 0
        for route in solution:
            pred_loc = self.depot_location
            for step in route.gen_steps():
                if type(step) is Package:
                    total_miles += pred_loc.distances[step.delivery_location.id]
                    pred_loc = step.delivery_location
                else:
                    total_miles += pred_loc.distances[self.depot_location.id]
                    pred_loc = self.depot_location
            total_miles += pred_loc.distances[self.depot_location.id]
        return total_miles

    def test_eval(self, solution, return_early=False):
        """Calculates the constraint satisfaction and cost of a solution."""
        def update_status(cur_status, incoming_status):
            cur_status = cur_status is None or cur_status is True
            return cur_status and incoming_status

        c0 = Constraint.DELIVERED_BY_DEADLINES
        c1 = Constraint.AVAILABLE_WHEN_LOADED
        c2 = Constraint.PACKAGES_ON_REQUIRED_TRUCKS
        c3 = Constraint.WITHIN_TRUCK_CAPACITY
        c4 = Constraint.SATISFIED_LINKED_DELIVERIES

        constraints = [None] * len(Constraint)

        # O(n)
        constraints[c3.value] = self.validate_constraint(c3, solution=solution, truck_capacity=self.constants.truck_capacity)
        if return_early and False in constraints: return constraints, self.eval(solution)
        # O(n)
        constraints[c4.value] = self.validate_constraint(c4, solution=solution, linked_packages=self.depot.linked_packages)
        if return_early and False in constraints: return constraints, self.eval(solution)

        total_miles = 0
        for route in solution:
            cur_time = self.constants.start_of_day
            load_time = self.constants.start_of_day
            pred_loc = self.depot_location
            for step in route.gen_steps():
                if type(step) is Package:
                    distance = pred_loc.distances[step.delivery_location.id]
                    cur_time += timedelta(hours=distance/self.constants.truck_speed)
                    if step.required_truck_number:
                        # O(1)
                        constraints[c2.value] = update_status(constraints[c2.value], self.validate_constraint(c2, package=step))
                    # O(1)
                    constraints[c0.value] = update_status(constraints[c0.value], self.validate_constraint(c0, package=step, delivery_time=cur_time))
                    # O(1)
                    constraints[c1.value] = update_status(constraints[c1.value], self.validate_constraint(c1, package=step, load_time=load_time))
                    if return_early and False in constraints: return constraints, self.eval(solution)
                    pred_loc = step.delivery_location
                else:
                    distance = pred_loc.distances[self.depot_location.id]
                    cur_time += timedelta(hours=distance/self.constants.truck_speed, minutes=step.wait_minutes)
                    load_time = cur_time
                    pred_loc = self.depot_location
                total_miles += distance
            total_miles += pred_loc.distances[self.depot_location.id]

        return constraints, total_miles

    @staticmethod
    def validate_constraint(constraint, **kwargs):
        if constraint == Constraint.DELIVERED_BY_DEADLINES:
            # O(1)
            package, delivery_time = kwargs['package'], kwargs['delivery_time']
            if delivery_time > package.delivery_deadline:
                return False
            return True
        elif constraint == Constraint.AVAILABLE_WHEN_LOADED:
            # O(1)
            package, load_time = kwargs['package'], kwargs['load_time']
            if load_time < package.earliest_load:
                return False
            return True
        elif constraint == Constraint.PACKAGES_ON_REQUIRED_TRUCKS:
            # O(1)
            package = kwargs['package']
            if package.required_truck_number:
                if package.required_truck_number != package.assigned_truck.number:
                    return False
            return True
        elif constraint == Constraint.WITHIN_TRUCK_CAPACITY:
            # The number of depot stops is roughly equal to n // truck_capacity,
            # but theoretically goes up to n - 1 if every other package deliver
            # is following by a return trip to the depot (truck_capacity = 1).
            # O(n)
            solution, truck_capacity = kwargs['solution'], kwargs['truck_capacity']
            ret = [None] * len(solution)
            for i, route in enumerate(solution):
                if len(route.packages) <= truck_capacity:
                    ret[i] = True
                else:
                    cur_idx = 0
                    for stop in route.depot_stops:
                        if stop.route_index - cur_idx > truck_capacity:
                            ret[i] = False
                        cur_idx = stop.route_index
                    if len(route.packages) - cur_idx > truck_capacity:
                        ret[i] = False
                    if ret[i] is None:
                        ret[i] = True
            return all(ret)
        elif constraint == Constraint.SATISFIED_LINKED_DELIVERIES:
            # O(n)
            solution, linked_packages = kwargs['solution'], kwargs['linked_packages']
            linked_packages = [copy(group) for group in linked_packages]
            for route in solution:
                gen = route.gen_steps()
                packages_loaded_together = []
                # Each package in each route is iterated through, but can
                # return early if all linked deliveries are satisfied before the
                # route finishes.  A number of depot stops roughly equal to
                # n // truck_capacity, but theoretically up to n - 1 possible
                # depot spots, are also included.
                # O(n + n - 1) = O(n)
                for step in gen:
                    if not linked_packages:
                        return True
                    if type(step) is Package:
                        if step.linked_package_group is not None:
                            packages_loaded_together.append(step)
                    else:
                        # While packages_loaded_together will never exceed a
                        # realistically constant truck capacity, this whole
                        # block executes (in worst case) for every depot stop.
                        # This means an iteration for every package in the
                        # route is possible if every package is a member of a
                        # linked delivery constraint (unlikely).
                        # Ω(# of linked packages) / O(n)
                        for package in packages_loaded_together:
                            group = package.linked_package_group
                            if group is not None:
                                # A.issubset(B) has a time complexity of O(len(A))
                                # Since the gap between depot stops is equal to
                                # truck capacity, the complexity of this
                                # operation is O(1) as long as truck capacity
                                # is constant or does not grow in proportion
                                # to the number of packages being delivered.
                                if group <= set(packages_loaded_together):
                                    l = len(linked_packages)
                                    # Testing if a group of linked deliveries
                                    # is satisfied by the current solution
                                    # only occurs once for a group.
                                    # O(1) since a linked delivery can not
                                    # include more packages than truck
                                    # capacity or else the constraint logically
                                    # fails immediately.
                                    linked_packages.remove(group)
                                    assert l == len(linked_packages) + 1
                                else:
                                    return False
                            # Exit test early if no more linked delivery
                            # constraints remain to be tested.
                            if not linked_packages:
                                return True
                        # Technically list.clear() is O(n) because reference
                        # counts for all the objects in the list need to be
                        # decremented for garbage collection.  Instead, a new
                        # empty list could be allocated with constant time, but
                        # the same O(n) garbage collection would still occur,
                        # and the overhead from the large constant factor
                        # would exceed the cost of clearing. From an algorithmic
                        # standpoint this is constant time.
                        # O(1)
                        packages_loaded_together.clear
            return True

    def minimize_wait_times(self, solution):
        for route in solution:
            for stop in route.depot_stops:
                while stop.wait_minutes > 0 and all(self.test_eval(solution)[0]):
                    stop.decrease_wait(1)
                if not all(self.test_eval(solution)[0]):
                    stop.increase_wait(1)
        assert all(self.test_eval(solution)[0]) == True

    def print_routes(self, solution):
        for route in solution:
            pred_loc = self.depot_location
            for step in route.gen_steps():
                if type(step) is DepotStop:
                    cur_loc = self.depot_location
                else:
                    cur_package = step
                    cur_loc = cur_package.delivery_location
                distance = pred_loc.distances[cur_loc.id]
                print(f"{pred_loc} --- {distance} --- {cur_loc}")
                pred_loc = cur_loc
    
    def plot_routes(self, solution):
        if plt is None:
            raise ImportError('Must install matplotlib to plot route.')

        fig, ax = plt.subplots(2, sharex=True, sharey=True)
        locations = []

        for route in solution:
            for package in route.packages:
                loc = package.delivery_location
                coords = loc.coords
                locations.append(coords)

        for route_num, route in enumerate(solution):
            ax[route_num].scatter(s=28, x=[c[0] for c in locations], y=[c[1] for c in locations], c='black')
            ax[route_num].scatter(x=[self.depot_location.coords[0]], y=[self.depot_location.coords[1]], c='green')

            start_pos = self.depot_location.coords
            for step in route.gen_steps():
                if type(step) is DepotStop:
                    cur_loc = self.depot_location
                else:
                    cur_package = step
                    cur_loc = cur_package.delivery_location

                end_pos = cur_loc.coords
                ax[route_num].annotate("", xycoords='data', xy=end_pos, textcoords='data')
                ax[route_num].annotate("", xy=end_pos, xycoords='data', xytext=start_pos, textcoords='data', arrowprops=dict(arrowstyle="->", connectionstyle="arc3", relpos=(0,0)))
                plt.pause(0.5)
                start_pos = end_pos
            ax[route_num].annotate("", xy=self.depot_location.coords, xycoords='data', xytext=start_pos, textcoords='data', arrowprops=dict(arrowstyle="->", connectionstyle="arc3"))
            plt.pause(2)
        plt.show()
