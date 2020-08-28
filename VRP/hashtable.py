from functools import wraps
from math import ceil

class ListNode:
    def __init__(self, key, val):
        self.key = key
        self.val = val
        self.next = None

class ChainingHashTable:
    """
        A custom hash table implementation created for educational purposes.
        All relevant magic methods are implemented so that ChainingHashTable
        acts as a drop-in replacement for a dictionary.
        The ChainHashTable self-adjusts its size as required, doubling or
        halving in size based on a load factor (item_count/bucket_count)
        to maintain O(1) average complexity for search/insert/delete operations.
    """
    def __init__(self, init_cap=10):
        self.table = [None] * init_cap
        self.count = 0

    def analyze(func):
        # Decorator function (closure) to wrap the insert(), remove(), and
        # clear() methods, so as to subsequently recalculate the table's load
        # factor and resize the table as necessary to maintain average O(1)
        # complexity.
        @wraps(func)
        def func_wrapper(inst, *args, **kwargs):
            ret = func(inst, *args, **kwargs)
            lf = inst._load_factor()
            if lf > 1:
                inst._resize(2)
            elif lf < 0.25:
                inst._resize(0.5)
            return ret
        return func_wrapper

    def __setitem__(self, key, item):
        self.insert(key, item)

    def __getitem__(self, key):
        return self.search(key)

    def __len__(self):
        return self.count

    def __delitem__(self, key):
        self.remove(key)

    @analyze
    def clear(self):
        self.table.clear()
        self.count = 0

    def has_key(self, key):
        return self.search(key) is not None

    def keys(self):
        return [node.key for node in self._gen_nodes()]

    def values(self):
        return [node.val for node in self._gen_nodes()]

    def items(self):
        return [(node.key, node.val) for node in self._gen_nodes()]

    def __contains__(self, item):
        node = self.search(hash(item))
        return node is not None and node is item

    def _gen_nodes(self):
        for node in self.table:
            cur_node = node
            while cur_node:
                yield cur_node
                cur_node = cur_node.next

    def _load_factor(self):
        return self.count / len(self.table)

    def _resize(self, factor):
        new_table = [None] * max(ceil(len(self.table) * factor), 1)
        for node_to_move in self.table:
            while node_to_move:
                suc_node_to_move = node_to_move.next
                node_to_move.next = None
                bucket_idx = hash(node_to_move.key) % len(new_table)
                cur_node = new_table[bucket_idx]
                
                if cur_node is None:
                    new_table[bucket_idx] = node_to_move
                else:
                    while True:
                        if not cur_node.next:
                            break
                        else:
                            cur_node = cur_node.next
                    cur_node.next = node_to_move
                node_to_move = suc_node_to_move
        self.table = new_table

    @analyze
    def insert(self, key, val):
        bucket_idx = hash(key) % len(self.table)
        cur_node = self.table[bucket_idx]
        
        if cur_node is None:
            self.table[bucket_idx] = ListNode(key, val)
            self.count += 1
            return

        while True:
            if cur_node.key == key:
                cur_node.val = val
                return
            if not cur_node.next:
                break
            else:
                cur_node = cur_node.next
        cur_node.next = ListNode(key, val)
        self.count += 1

    def search(self, key):
        bucket_idx = hash(key) % len(self.table)
        cur_node = self.table[bucket_idx]

        if cur_node is None:
            raise KeyError(key)

        while True:
            if cur_node.key == key:
                return cur_node.val
            if not cur_node.next:
                raise KeyError(key)
            else:
                cur_node = cur_node.next

    @analyze
    def remove(self, key):
        bucket_idx = hash(key) % len(self.table)
        cur_node = self.table[bucket_idx]

        if cur_node is None:
            return

        pred_node = None
        while True:
            if cur_node.key == key:
                if not pred_node:
                    self.table[bucket_idx] = cur_node.next
                else:
                    pred_node.next = cur_node.next
                self.count -= 1

            if not cur_node.next:
                return
            pred_node, cur_node = cur_node, cur_node.next
