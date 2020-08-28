from datetime import datetime, date
import re

class Package:
    def __init__(self, id, delivery_location, earliest_load, delivery_deadline, mass, notes):
        self.id = id
        self.delivery_location = delivery_location
        self.earliest_load = earliest_load
        self.delivery_deadline = delivery_deadline
        self.mass = mass
        self.notes = notes
        self.assigned_truck = None

        self.required_truck_number = None
        self.linked_package_ids = []
        self.linked_package_group = None
        self._parse_notes()

        self.load_time = None
        self.delivery_time = None

    def __repr__(self):
        # return f"<Package {self.id}: truck {self.assigned_truck.number}>"
        return f"P.{self.id}"

    def __hash__(self):
        return self.id

    def _parse_notes(self):
        if self.notes == "Delayed on flight---will not arrive to depot until 9:05 am":
            today = date.today()
            self.earliest_load = datetime(today.year, today.month, today.day, hour=9, minute=5)
        elif self.notes == "Wrong address listed":
            today = date.today()
            self.earliest_load = datetime(today.year, today.month, today.day, hour=10, minute=20)
        elif self.notes == "Can only be on truck 2":
            self.required_truck_number = 2
        elif "Must be delivered with" in self.notes:
            self.linked_package_ids = [int(p) for p in re.findall("([\d]+)", self.notes)]

    def assign_truck(self, truck):
        self.assigned_truck = truck

    def change_delivery_location(self, location):
        self.delivery_location = location

    def delivery_status(self, cur_time):
        if cur_time < self.earliest_load:
            return 'NOT READY'
        elif cur_time < self.load_time:
            return 'AT HUB'
        elif cur_time < self.delivery_time:
            return 'EN ROUTE'
        else:
            return 'DELIVERED'
