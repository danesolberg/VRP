class DepotStop:
    def __init__(self, route_index, wait_minutes=0):
        self.route_index = route_index
        self.wait_minutes = wait_minutes

    def __repr__(self):
        return f"<DepotStop: wait {self.wait_minutes}>"

    def __str__(self):
        return f"D({self.wait_minutes})"

    def increase_wait(self, minutes):
        self.wait_minutes += minutes

    def decrease_wait(self, minutes):
        self.wait_minutes = max(self.wait_minutes - minutes, 0)