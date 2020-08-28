from helpers import dijkstra
from location import Location
from package import Package
from hashtable import ChainingHashTable
import csv
from datetime import datetime, date
from collections import namedtuple

class DataLoader:
    LOCATIONS_FILENAME = 'locations.csv'
    PACKAGES_FILENAME = 'packages.csv'
    DISTANCES_FILENAME = 'distances.csv'

    Data = namedtuple('Data', ['package_table', 'location_table', 'distance_table'])

    def __init__(self, simulator, data_dir):
        self.simulator = simulator
        self.data_dir = data_dir
        self.locations = ChainingHashTable()
        self.packages = ChainingHashTable()

    def import_data(self):
        self.distances = self.load_distances()
        self.locations = self.load_locations()
        self.packages = self.load_packages()

        data = DataLoader.Data(
            self.packages,
            self.locations,
            self.distances
        )
        return data

    def load_locations(self):
        """
        A custom hash table implementation is used by the DataLoader class
        for educational purposes.  All relevant magic methods are implemented
        so ChainingHashTable acts as a drop-in replacement for a dictionary.
        The ChainHashTable self-adjusts its size as required, doubling or
        halving in size based on a load factor (item_count/bucket_count)
        to maintain O(1) average complexity for search/insert/delete operations.
        """
        locations_hashtable = ChainingHashTable()
        with open(self.data_dir + DataLoader.LOCATIONS_FILENAME) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                data = dict(row)
                data['LocationID'] = int(data['LocationID'])
                data['Lat'] = float(data['Lat'])
                data['Lon'] = float(data['Lon'])

                loc = Location(
                    int(data['LocationID']),
                    data['Address'],
                    data['City'],
                    data['State'],
                    data['ZIP'],
                    float(data['Lat']),
                    float(data['Lon']),
                    self.distances[int(data['LocationID'])]
                )

                locations_hashtable[data['LocationID']] = loc

        return locations_hashtable

    def load_packages(self):
        packages_hashtable = ChainingHashTable()
        today = date.today()
        with open(self.data_dir + DataLoader.PACKAGES_FILENAME) as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                data = dict(row)
                if data['DeliveryDeadline'] == 'EOD':
                    data['DeliveryDeadline'] = datetime(today.year, today.month, today.day,hour=23,minute=59,second=59)
                else:
                    data['DeliveryDeadline'] = datetime.combine(today, datetime.strptime(data['DeliveryDeadline'], "%I:%M %p").time())
                data['Mass'] = int(data['Mass'])
                data['PackageID'] = int(data['PackageID'])
                data['LocationID'] = int(data['LocationID'])

                package = Package(
                    data['PackageID'],
                    self.locations[data['LocationID']],
                    self.simulator.constants.start_of_day,
                    data['DeliveryDeadline'],
                    data['Mass'],
                    data['SpecialNotes']
                )

                packages_hashtable[data['PackageID']] = package

        return packages_hashtable

    def load_distances(self):
        """
        The direct pairwise distances between locations in the distances.csv
        file are not always the shortest path between locations, which is an
        assumption of the TSP / VRP generalization.  To correct for this,
        the pairwise distances are used to represent a complete graph, which
        is run through a shortest path algorithm (Dijkstra) to minimize the
        distances between locations.
        """
        distances_hashtable = ChainingHashTable()
        with open(self.data_dir + DataLoader.DISTANCES_FILENAME) as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='"')
            locations_x = next(reader, None)
            for i, row in enumerate(reader):
                location_y = int(row[0])
                distances_hashtable[location_y] = ChainingHashTable()
                for j in range(1, len(row)):
                    location_x = int(locations_x[j])
                    distance = float(row[j])
                    distances_hashtable[location_y][location_x] = distance

        mapping = ChainingHashTable()
        mapping_inv = ChainingHashTable()
        for i, location_id in enumerate(distances_hashtable.keys()):
            mapping[location_id] = i
            mapping_inv[i] = location_id

        adj_list = [None] * len(mapping)
        for start, adjs in distances_hashtable.items():
            neighbors = []
            for end, weight in adjs.items():
                neighbors.append((mapping[end], weight))
            adj_list[mapping[start]] = neighbors

        for start, adjs in distances_hashtable.items():
            distances = dijkstra(adj_list, mapping, start)
            for i, dist in enumerate(distances):
                end = mapping_inv[i]
                distances_hashtable[start][end] = dist

        return distances_hashtable