

class DisjointSet:
    size = 0

    def __init__(self):
        self.__items = {}

    """def union(self, root1, root2):
            if self.__items[root2] < self.__items[root1]:
                    self.__items[root1] = root2
            else:
                    if self.__items[root1] == self.__items[root2]:
                            self.__items[root1] -= 1

                    self.__items[root2] = root1
    """
    def union(self, root1, root2):
        self.__items[root2] = self.find(root1)
    
    """
    def find(self, x):
            try:
                    while self.__items[x] > 0:
                            x = self.__items[x]
            
            except KeyError:
                    self.__items[x] = -1

            return x
    """

    def find(self, x):
        try:
            while self.__items[x] != x:
                x = self.__items[x]
        except KeyError:
            self.__items[x] = x
        return x
    '''
    def split_sets(self):
            sets = {}
            j = 0

            for j in self.__items.keys():
                    root = self.find(j)
                    
                    if root > 0:
                            if sets.has_key(root):
                                    _list = sets[root]
                                    _list.append(j)

                                    sets[root] = _list
                            else:
                                    sets[root] = [j]

            return sets
    '''

    def split_sets(self):
        sets = {}
        for item in self.__items.keys():
            root = self.find(item)
            if root in sets:
                _list = sets[root]
                _list.append(item)
                sets[root] = _list
            else:
                sets[root] = [item]
        return sets

    def dump(self):
        print(self.__items)

