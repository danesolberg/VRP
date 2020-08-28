import heapq

def compile_neighbor(solution, swaps):
    """
    <swaps> parameter is in form of [(swap_index, new_route),] sorted ascending
    by swap_index.
    """
    current_swap_idx = 0
    new_solution = []
    swap_len = len(swaps)
    for i in range(len(solution)):
        if current_swap_idx < swap_len and i == swaps[current_swap_idx][0]:
            new_solution.append(swaps[current_swap_idx][1])
            current_swap_idx += 1
        else:
            new_solution.append(solution[i])

    return new_solution

def print_progress_bar(cur_iter, expected_iter, decimals = 1, length = 100, fill = '█', printEnd = "\r"):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (cur_iter / float(expected_iter)))
    filledLength = int(length * cur_iter // expected_iter)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r |{bar}| {percent}%', end = printEnd)
    if cur_iter == expected_iter: 
        print()

def dijkstra(adj_list, mapping, start):
    n = len(adj_list)
    dists = [float("inf")] * n
    parents = [None] * n

    dists[mapping[start]] = 0
    pq = [(0, mapping[start])]

    while pq:
        cur_dist, cur_node = heapq.heappop(pq)
        if cur_dist > dists[cur_node]:
            continue
        neighbors = adj_list[cur_node]
        for i, weight in neighbors:
            distance = weight + cur_dist
            if distance < dists[i]:
                dists[i] = distance
                parents[i] = cur_node
                heapq.heappush(pq, (distance, i))
    return dists