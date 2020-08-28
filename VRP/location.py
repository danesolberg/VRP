class Location:
    def __init__(self, id, address, city, state, zipcode, lat, lon, distances):
        self.id = id
        self.address = address
        self.city = city
        self.state = state
        self.zipcode = zipcode
        self.coords = (lat, lon)
        self.distances = distances

    def __repr__(self):
        return f"L.{self.id}"

    def distance_to(location_id):
        return self.distances[location_id]