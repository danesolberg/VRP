from depotstop import DepotStop
from copy import copy
from operator import attrgetter

class Route:
    def __init__(self, truck):
        self.truck = truck
        self.packages = []
        self.depot_stops = [DepotStop(0)]

    def __str__(self):
        steps = list(self.gen_steps())
        return f"truck{self.truck.number}: " + ", ".join(str(e) for e in steps)

    def __len__(self):
        return len(self.packages)

    def opt_copy_packages(self):
        newone = copy(self)
        newone.packages = copy(self.packages)
        return newone

    def opt_copy_depot_stops(self):
        newone = copy(self)
        newone.depot_stops = [copy(stop) for stop in self.depot_stops]
        return newone

    def gen_steps(self):
        ds_idx = 0
        p_idx = 0
        lp = len(self.packages)
        ld = len(self.depot_stops)
        while p_idx < lp and ds_idx < ld:
            if p_idx == self.depot_stops[ds_idx].route_index:
                yield self.depot_stops[ds_idx]
                ds_idx += 1
            else:
                yield self.packages[p_idx]
                p_idx += 1
        while p_idx < lp:
            yield self.packages[p_idx]
            p_idx += 1
        while ds_idx < ld:
            yield self.depot_stops[ds_idx]
            ds_idx += 1
        yield DepotStop(len(self.packages))

    def add_package(self, package, insert_idx=None):
        if insert_idx:
            self.packages.insert(insert_idx, package)
        else:
            self.packages.append(package)
        package.assign_truck(self.truck)

    def remove_package(self, package):
        self.packages.remove(package)
        package.assign_truck(None)

    def get_depot_stop(self, route_idx):
        for stop in self.depot_stops:
            if stop.route_index == route_idx:
                return stop
        return None

    def add_depot_stop(self, insert_idx):
        i = 0
        while i < len(self.depot_stops):
            cur_stop_idx = self.depot_stops[i].route_index
            if insert_idx == cur_stop_idx:
                # depot stop already exists at this route index
                return
            elif insert_idx < cur_stop_idx:
                self.depot_stops.insert(i, DepotStop(insert_idx))
                return
            i += 1
        self.depot_stops.append(DepotStop(insert_idx))

    def remove_depot_stop(self, depot_stop):
        self.depot_stops.remove(depot_stop)

    def move_depot_stop(self, depot_stop, new_idx):
        for stop in self.depot_stops:
            if stop.route_index == new_idx:
                # depot stop already exists at this route index
                return
        depot_stop.route_index = new_idx
        self.depot_stops.sort(key=attrgetter('route_index'))

    def get_depot_stop_indices(self):
        stops = {}
        for stop in self.depot_stops:
            stops[stop.route_index] = stop
        return stops

    def set_minimal_depot_stops(self):
        self.depot_stops.clear()
        for i in range(len(self.packages)):
            if i % self.truck.capacity == 0:
                self.add_depot_stop(i)
