import sys
from collections import namedtuple
from heapq import heappop, heappush
from math import inf
from operator import itemgetter, sub
from typing import Optional

rows, cols, alarm_count = [int(i) for i in input().split()]
CLEAR = {".", "C", "T", "o"}


def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def potential_neighbors(maze, pos) -> list[tuple[int, int]]:
    r, c = pos
    directions = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]
    return [
        (ri, ci)
        for ri, ci in directions
        if 0 <= ri < rows and 0 <= ci < cols and maze[ri][ci] == "?"
    ]


class Node:
    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.pos = row, col
        self.links = list()

    def __repr__(self):
        fmt_edges = ",".join(str(edi.pos) for edi in self.links)
        return f"{self.pos}[{fmt_edges}]"

    def link(self, other):
        self.links.append(other)
        other.links.append(self)

    def edge_distance(self, pos):
        row, col = pos
        if row == self.row and col == self.col:
            return 0
        elif row == self.row:
            if col < self.col and any(e.col <= col for e in self.links):
                return self.col - col
            elif col > self.col and any(col <= e.col for e in self.links):
                return col - self.col
        elif col == self.col:
            if row < self.row and any(e.row <= row for e in self.links):
                return self.row - row
            elif row > self.row and any(row <= e.row for e in self.links):
                return row - self.row
        return inf


def parse(maze, pos):
    nodes = list()
    top_nodes: list[Optional[Node]] = [None] * len(maze)
    foggy = set()
    for i, row in enumerate(maze):
        left = None
        for j, col in enumerate(row):
            if col in CLEAR:
                this = Node(i, j)
                if potential_neighbors(maze, this.pos):
                    foggy.add(this.pos)

                look_right = maze[i][j + 1]
                if left is None:
                    nodes.append(this)
                    left = this
                elif look_right not in CLEAR:
                    nodes.append(this)
                    left.link(this)
                    left = None
                elif this.pos == pos:
                    nodes.append(this)
                    left.link(this)
                    left = this

                look_above = maze[i - 1][j]
                look_below = maze[i + 1][j]
                if look_above in CLEAR:
                    above = top_nodes[i]
                    assert above
                    above.link(this)

                if look_below in CLEAR:
                    top_nodes[i] = this
                else:
                    top_nodes[i] = None

    return nodes, foggy


Edge = namedtuple("Edge", ["vertex", "weight"])


class UnidirectedWeightedGraph:
    """Every node is just an index"""

    def __init__(self, nodes):
        self.node_index = {node.pos: i for i, node in enumerate(nodes)}
        self.adjacency = [list() for _ in range(len(nodes))]

        for i, node in enumerate(nodes):
            for link in node.links:
                distance = max(tuple(map(abs, map(sub, node.pos, link.pos))))
                self.adjacency[i].append(Edge(self.node_index[link.pos], distance))


def dijkstra(graph, start, dest):
    print("dij", start, dest, file=sys.stderr)
    size = len(graph.node_index)
    trail = [None] * size
    distance = [inf] * size
    distance[start] = 0
    q = [(0, start)]

    pos = start
    while q:
        _, pos = heappop(q)
        print("> picked", pos, file=sys.stderr)

        dist = distance[pos]
        for edge in graph.adjacency[pos]:
            alt = dist + edge.weight
            if alt < distance[edge.vertex]:
                distance[edge.vertex] = alt
                trail[edge.vertex] = pos
                heappush(q, (alt, edge.vertex))

    print("stopped at", pos, " and trail is", trail, file=sys.stderr)
    path = [dest]
    while (pos := trail[pos]) is not None:
        path.append(pos)

    return path


def find_path(pos, goal, nodes, graph):
    start_nodes = [
        (edi, ni)
        for ni in nodes
        if (edi := ni.edge_distance(pos)) is not inf and ni.pos != goal
    ]
    if not start_nodes:
        raise RuntimeError(f"Position {pos} is not on the grid")
    start_nodes.sort(key=itemgetter(0))
    print("start from", start_nodes, file=sys.stderr)
    start = graph.node_index[start_nodes[0][1].pos]
    dest = graph.node_index[goal]
    ipath = dijkstra(graph, start, dest)

    print("index path", ipath, file=sys.stderr)
    path = [nodes[i].pos for i in ipath]
    return path


def replace_index(text, index, replacement):
    return f"{text[:index]}{replacement}{text[index+1:]}"


def neighbors(maze, pos) -> list[tuple[int, int]]:
    r, c = pos
    directions = [
        (r - 1, c),
        (r + 1, c),
        (r, c - 1),
        (r, c + 1),
    ]
    return [
        (ri, ci)
        for ri, ci in directions
        if 0 <= ri < rows and 0 <= ci < cols and maze[ri][ci] in CLEAR
    ]


DIRECTION = {
    (-1, 0): "UP",
    (1, 0): "DOWN",
    (0, -1): "LEFT",
    (0, 1): "RIGHT",
}


target = None
cc = None
start = None

while True:
    row, col = (int(i) for i in input().split())
    pos = (row, col)
    maze = list()
    for i in range(rows):
        line = input()
        maze.append(line)
        if (tcol := line.find("T")) >= 0:
            start = i, tcol
        if (tcol := line.find("C")) >= 0:
            cc = i, tcol

    maze[row] = replace_index(maze[row], col, "o")
    print(*maze, sep="\n", file=sys.stderr)

    nodes, foggy = parse(maze, pos)
    print("foggy", foggy, file=sys.stderr)
    print("nodes", nodes, file=sys.stderr)

    graph = UnidirectedWeightedGraph(nodes)
    # print(graph.adjacency, file=sys.stderr)

    if target is None:
        if foggy:
            goal = next(iter(foggy))
        else:
            target = cc
            goal = target
    elif pos == cc:
        target = start
        goal = target
    else:
        goal = target

    something = find_path(pos, goal, nodes, graph)
    print("goal", goal, "path:", something, file=sys.stderr)

    towards = something[-2]  # last position should be the current one
    diff = tuple(map(sign, map(sub, something[-2], something[-1])))
    print(diff, file=sys.stderr)

    print(DIRECTION[diff])
