import numpy as np
import argparse
import sys
import re
import random
from queue import PriorityQueue
import heapq
import time
import copy

class heap():
    def __init__(self):
        self.h = []

    def add(self, a):
        heapq.heappush(self.h, a)

    def pop(self):
        return heapq.heappop(self.h)

    def adjust(self, prev, now):
        self.h.remove(prev)
        self.h.append(now)
        heapq.heapify(self.h)

    def empty(self):
        return len(self.h) == 0

def read(file):
    file_obj = open(file, 'r')
    name = file_obj.readline().split(' ')[-1]
    vertices = file_obj.readline().split(' ')[-1]
    depot = file_obj.readline().split(' ')[-1]
    required_edges = file_obj.readline().split(' ')[-1]
    non_required_edges = file_obj.readline().split(' ')[-1]
    vehicles = file_obj.readline().split(' ')[-1]
    capacity = file_obj.readline().split(' ')[-1]
    total_cost_of_required_edges = file_obj.readline().split(' ')[-1]
    file_obj.readline().split(' ')[-1]
    edges = []
    for line in file_obj:
        if line == 'END':
            break
        edge = re.split(' |\n', line)
        while '' in edge:
            edge.remove('')
        edges.append([(int(edge[0])-1, int(edge[1])-1),
                     int(edge[2]), int(edge[3])])
    return {'name': name,
            'vertices': vertices,
            'depot': depot,
            'required_edges': required_edges,
            'non_required_edges': non_required_edges,
            'vehicles': vehicles,
            'capacity': capacity,
            'total_cost_of_required_edges': total_cost_of_required_edges,
            'edges': edges}

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', required=True)
    parser.add_argument('-s', default=114514)
    return parser

def print_res(route, cost, depot):
    print('s', end=' ')
    for i in range(len(route)):
        print(depot, end=',')
        for j in route[i]:
            print('(', end='')
            print(j[0]+1, end=',')
            print(j[1]+1, end='),')
        if i != len(route)-1:
            print(depot, end=',')
    print(depot)
    print('q', cost)

def dij(st, map):
    h = heap()
    isvisited = [st]
    h.add((0, st))
    dist = [np.Inf for _ in range(len(map))]
    dist[st] = 0
    while not h.empty():
        cur = h.pop()[1]
        for i in range(len(map)):
            if i == st:
                continue
            if map[cur][i] == [-1]:
                continue
            dis = dist[cur] + map[cur][i][0]
            if i not in isvisited:
                isvisited.append(i)
                dist[i] = dis
                h.add((dis, i))
            else:
                if dis < dist[i]:
                    h.adjust((dist[i], i), (dis, i))
                    dist[i] = dis
    return dist


def path_scanning(map, distances, depot, demand_edge, capacity):
    vehic_route = []
    demands = copy.deepcopy(demand_edge)
    for e in demand_edge:
        demands.append((e[1], e[0]))
    while len(demands):
        route = []
        cap = capacity
        cur = depot
        while cap >= 0:
            candidate_edge = []
            min_dis = np.Inf
            for edge in demands:
                dis = distances[cur][edge[0]]
                if dis < min_dis:
                    candidate_edge.clear()
                    candidate_edge.append(edge)
                    min_dis = dis
                elif dis == min_dis:
                    candidate_edge.append(edge)
            if not len(candidate_edge):
                break
            if len(candidate_edge) == 1:
                next = candidate_edge[0]
            else:
                index = random.randint(0, len(candidate_edge)-1)
                next = candidate_edge[index]
            if cap < map[next[0]][next[1]][1]:
                break
            demands.remove(next)
            demands.remove((next[1], next[0]))
            cur = next[1]
            route.append(next)
            cap -= map[next[0]][next[1]][1]
        if len(route) != 0: vehic_route.append(route)
    return vehic_route

def path_scanning_random(map, distances, depot, demand_edge, capacity, alpha):
    vehic_route = []
    demands = copy.deepcopy(demand_edge)
    for e in demand_edge:
        demands.append((e[1], e[0]))
    while len(demands):
        route = []
        cap = capacity
        cur = depot
        while cap >= 0:
            candidate_edge = []
            for edge in demands:
                dis = distances[cur][edge[0]]
                candidate_edge.append((dis, edge))
            candidate_edge.sort()
            if len(candidate_edge) == 0: break
            if len(candidate_edge) <= alpha: next = candidate_edge[random.randint(0, len(candidate_edge)-1)][1]
            else: next = candidate_edge[random.randint(0,alpha)][1]
            if cap < map[next[0]][next[1]][1]:
                break
            demands.remove(next)
            demands.remove((next[1], next[0]))
            cur = next[1]
            route.append(next)
            cap -= map[next[0]][next[1]][1]
        if len(route) != 0: vehic_route.append(route)
    return vehic_route


def get_cost(routes, map, distances, depot):
    cost = 0
    for route in routes:
        cur = depot
        for node in route:
            cost += map[node[0]][node[1]][0] + distances[cur][node[0]]
            cur = node[1]
        cost += distances[cur][depot]
    return cost

def get_cost_each(route, map, distances, depot):
    cost = 0
    cur = depot
    for node in route:
        cost += map[node[0]][node[1]][0] + distances[cur][node[0]]
        cur = node[1]
    cost += distances[cur][depot]
    return cost



def ga(parameters, tot_time):
    start_time = time.time()
    edges = parameters['edges']
    depot = int(parameters['depot'])-1
    required = parameters['required_edges']
    non_required = parameters['non_required_edges']
    num_vehicles = int(parameters['vehicles'])
    vehicles_capacity = int(parameters['capacity'])
    tot_cost = parameters['total_cost_of_required_edges']
    vertices = int(parameters['vertices'])

    map = [[[-1] for i in range(vertices)] for i in range(vertices)]
    all_demand_edges = []

    for e in edges:
        edge = e[0]
        cost = e[1]
        demand = e[2]
        if demand != 0:
            all_demand_edges.append(edge)
        map[edge[0]][edge[1]] = (cost, demand)
        map[edge[1]][edge[0]] = (cost, demand)

    distances = []
    for i in range(vertices):
        distances.append(dij(i, map))

    population_size = 5000
    parents_size = 50
    offspring_size = 100
    generation = 100

    init_population = []
    for _ in range(population_size):
        route = path_scanning(map, distances, depot, all_demand_edges, vehicles_capacity)
        cost = get_cost(route, map, distances, depot)
        init_population.append((cost, route))

    init_population.sort()
    # parents = init_population[:parents_size]
    parents = []
    parents.extend(init_population[:int(parents_size*0.1)])
    parents.extend(random.sample(init_population[int(parents_size*0.1):int(len(init_population)*0.3)], k=int(parents_size*0.5)))
    parents.extend(random.sample(init_population[int(len(init_population)*0.3):], k=int(parents_size*0.4)))
    parents.sort()
    # print(parents[0][0])

    tot_time -= time.time() - start_time
    curtime = 0
    # cnt = 0
    # best = 0
    local_optimum_cnt = 0
    alpha = 1
    while tot_time > curtime*1.3:  # generation > 0:
        st_time = time.time()
        offsprings = []
        
        # this is origin mutation method
        for parent in parents:
            for _ in range(offspring_size):
                parent_dna = copy.deepcopy(parent[1])
                index = random.sample([i for i in range(len(parent_dna))], random.randint(0, len(parent_dna)-1))
                variation_genes = []
                for i in index:
                    variation_genes.extend(parent[1][i])
                    parent_dna.remove(parent[1][i])
                new_dna = path_scanning_random(map, distances, depot, variation_genes, vehicles_capacity, alpha=alpha)
                new_dna.extend(parent_dna)
                new_dna2 = path_scanning(map, distances, depot, variation_genes, vehicles_capacity)
                new_dna2.extend(parent_dna)

                cost = get_cost(new_dna, map, distances, depot)
                cost2 = get_cost(new_dna2, map, distances, depot)
                offsprings.append((cost, new_dna))
                offsprings.append((cost2, new_dna2))

        # offsprings.extend(parents)
        offsprings.sort()
        if parents[0][0] == offsprings[0][0]:
            local_optimum_cnt += 1
        else: local_optimum_cnt == 0
        if local_optimum_cnt < 20:
            alpha = 1
        elif local_optimum_cnt < 40:
            alpha = 2
        else:
            alpha = 3

        parents = []
        parents.extend(offsprings[:int(parents_size*0.1)])
        parents.extend(random.sample(offsprings[int(parents_size*0.1):int(len(offsprings)*0.3)], k=int(parents_size*0.5)))
        parents.extend(random.sample(offsprings[int(len(offsprings)*0.3):], k=int(parents_size*0.4)))
        parents.sort()
        # print(parents[0][0])
        curtime = time.time() - st_time
        tot_time -= curtime
    return parents[0], depot

if __name__ == '__main__':
    argv = sys.argv
    file_path = argv[1]
    tot_time = int(argv[3])
    if len(argv) == 6:
        seed = argv[5]
    else:
        seed = 114514
    st_time = time.time()
    parameters = read(file_path)

    res, depot = ga(parameters, tot_time)
    q, s = res
    print_res(s, q, depot)
    ed_time = time.time()
    print('tot time:',tot_time)
    print('run time:',ed_time-st_time)
    print('random seed:', seed)