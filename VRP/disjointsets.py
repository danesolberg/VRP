class DisjointSets:
    def __init__(self, n, mapping):
        self.n = n
        self.parents = [i for i in range(n)] # start all elements to own parent
        self.ranks = [1] * n
        self.mapping = mapping

    def find(self, x):
        if x != self.parents[x]:
            self.parents[x] = self.find(self.parents[x]) # path compression
        return self.parents[x]

    def union(self, x, y):
        p_x = self.find(x)
        p_y = self.find(y)

        if p_x == p_y:
            return

        if self.ranks[p_x] > self.ranks[p_y]: # union by rank
            self.parents[p_y] = p_x
        else:
            self.parents[p_x] = p_y
            if self.ranks[p_x] == self.ranks[p_y]:
                self.ranks[p_y] != 1
        
        self.n -= 1

    def make_sets(self):
        sets = [set() for _ in range(len(self.parents))]

        for i in range(len(self.parents)):
            cur = i
            while cur != self.parents[cur]:
                cur = self.parents[cur]
            sets[cur].add(self.mapping[i])

        return sets
