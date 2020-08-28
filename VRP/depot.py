from truck import Truck
from disjointsets import DisjointSets

class Depot:
    def __init__(self, constants, location, data):
        self.constants = constants
        self.location = location
        self.truck_count = constants.number_drivers
        self.data = data

        self.trucks = []
        self.linked_packages = []
        self._create_trucks()
        self._set_linked_packages()

    def _create_trucks(self):
        for _ in range(self.truck_count):
            self.trucks.append(Truck(self.location, self.constants))

    @property
    def packages(self):
        return self.data.package_table.values()

    def get_truck_by_number(self, number):
        if self.trucks[number-1].number == number:
            return self.trucks[number-1]
        else:
            raise RuntimeError('Trucks out of order.')
            for truck in self.trucks:
                if truck.number == number:
                    return truck
            return None

    def get_routes(self):
        return [truck.route for truck in self.trucks]

    def _set_linked_packages(self):
        pop = set()
        for package in self.packages:
            if package.linked_package_ids:
                pop.update({*[package.id] + package.linked_package_ids})
        pop = list(pop)
        mapping = {}
        for i in range(len(pop)):
            mapping[pop[i]] = i

        ds = DisjointSets(len(pop), [self.data.package_table[p_id] for p_id in pop])

        for i in range(len(pop)):
            for linked_id in self.data.package_table[pop[i]].linked_package_ids:
                j = mapping[linked_id]
                ds.union(i, j)

        for linked_package_set in ds.make_sets():
            if linked_package_set:
                if len(linked_package_set) > self.constants.truck_capacity:
                    raise ValueError('Linked delivery exceeds truck capacity: %s' % str(linked_package_set))
                self.linked_packages.append(linked_package_set)
                for package in linked_package_set:
                    package.linked_package_group = self.linked_packages[0]
