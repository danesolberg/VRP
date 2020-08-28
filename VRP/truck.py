
from route import Route

class Truck:
    TRUCK_COUNT = 0

    def __init__(self, depot_location, constants):
        Truck.TRUCK_COUNT += 1
        self.number = Truck.TRUCK_COUNT
        self.route = Route(self)
        self.depot_location = depot_location
        self.speed = constants.truck_speed,
        self.capacity = constants.truck_capacity
        self.start_of_day = constants.start_of_day

        self.current_location = depot_location
        self.miles_driven = 0

    def load_package(self, package):
        self.route.add_package(package)

    def deliver_package(self):
        pass