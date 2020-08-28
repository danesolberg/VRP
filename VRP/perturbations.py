from helpers import compile_neighbor
import random
from operator import attrgetter

class Perturbations:
    @staticmethod
    def double_bridge(solution):
        """ Random double-bridge move """
        route_idx = random.randint(0, len(solution) - 1)
        
        new_route = solution[route_idx].opt_copy_packages()
        n = len(new_route)
        
        if n < 4:
            return None

        while True:
            cut   = random.sample(range(n - 1), 4)
            cut   = [e+1 for e in cut]
            cut   = sorted(cut)
            if n < 8 or (cut[1] > cut[0]+1 and cut[2] > cut[1]+1 and cut[3] > cut[2]+1):
                break
        
        zero  = new_route.packages[:cut[0]]
        one   = new_route.packages[cut[0]:cut[1]]
        two   = new_route.packages[cut[1]:cut[2]]
        three = new_route.packages[cut[2]:cut[3]]
        four  = new_route.packages[cut[3]:]
        
        new_route.packages = zero + three + two + one + four
        assert len(solution[route_idx]) == len(new_route)
        assert sorted(solution[route_idx].packages, key=attrgetter('id')) == sorted(new_route.packages, key=attrgetter('id'))
        return compile_neighbor(solution, [(route_idx, new_route)])
