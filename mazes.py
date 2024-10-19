import sys
from collections import namedtuple
from enum import IntEnum
from functools import partial
from heapq import heappop, heappush
from math import inf
from operator import itemgetter, sub
from typing import Optional

rows, cols, alarm_count = [int(i) for i in input().split()]
ROWS = rows + 2
COLS = cols + 2
CLEAR = {".", "C", "T", "o", "x"}
WALLS = {"#", "?"}
DIRECTION = {
    (-1, 0): "UP",
    (1, 0): "DOWN",
    (0, -1): "LEFT",
    (0, 1): "RIGHT",
}


def sign(x):
    if x < 0:
        return -1
    elif x > 0:
        return 1
    else:
        return 0


def square_dist(left, right):
    r1, c1 = left
    r2, c2 = right
    return (r2 - r1) ** 2 + (c2 - c1) ** 2


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
        if 0 <= ri < ROWS and 0 <= ci < COLS and maze[ri][ci] == "?"
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
    above_nodes: list[Optional[Node]] = [None] * COLS
    foggy = set()
    for i, row in enumerate(maze):
        if i in {0, len(maze) - 1}:
            continue
        # print("- working row", i, row, file=sys.stderr)
        left_node = None
        for j, cell in enumerate(row):
            if j in {0, len(row) - 1}:
                continue
            # print("- position", (i, j), file=sys.stderr)

            left = maze[i][j - 1]
            right = maze[i][j + 1]

            above = maze[i - 1][j]
            below = maze[i + 1][j]

            if cell in CLEAR:
                this = Node(i, j)

                ## Collect nodes near fog
                if potential_neighbors(maze, this.pos):
                    foggy.add(this.pos)

                # horizontal coridor
                if (
                    this.pos != pos
                    and above in WALLS
                    and below in WALLS
                    and left in CLEAR
                    and right in CLEAR
                ):
                    # print("horizontal coridor", this.pos, file=sys.stderr)
                    pass
                elif (
                    this.pos != pos
                    and left in WALLS
                    and right in WALLS
                    and above in CLEAR
                    and below in CLEAR
                ):
                    # print("vertical coridor", this.pos, file=sys.stderr)
                    pass
                else:
                    # if this.pos == pos:
                    #     print("create node on current position", pos, file=sys.stderr)
                    nodes.append(this)
                    if left_node:
                        left_node.link(this)
                    left_node = None if right in WALLS else this

                    if above_nodes[j]:
                        above_nodes[j].link(this)
                    above_nodes[j] = None if below in WALLS else this

    return nodes, list(foggy)


Edge = namedtuple("Edge", ["vertex", "weight"])


class UnidirectedWeightedGraph:
    """Every node is just an index"""

    def __init__(self, nodes, goal):
        self.adjacency = [list() for _ in range(len(nodes))]
        self.node_index = {node.pos: i for i, node in enumerate(nodes)}

        if isinstance(goal, list):
            for gi in goal:
                if gi not in self.node_index:
                    nearby_goal = [
                        (edi, n) for n in nodes if (edi := n.edge_distance(gi)) != inf
                    ]
                    nearby_goal.sort(key=itemgetter(0))
                    _, chosen = nearby_goal[0]
                    self.node_index[gi] = self.node_index[chosen.pos]
        elif goal not in self.node_index:
            nearby_goal = [
                (edi, n) for n in nodes if (edi := n.edge_distance(goal)) != inf
            ]
            nearby_goal.sort(key=itemgetter(0))
            _, chosen = nearby_goal[0]
            self.node_index[goal] = self.node_index[chosen.pos]

        for i, node in enumerate(nodes):
            for link in node.links:
                distance = max(tuple(map(abs, map(sub, node.pos, link.pos))))
                self.adjacency[i].append(Edge(self.node_index[link.pos], distance))


def dijkstra(graph, start, dest, nodes):
    size = len(graph.node_index)
    trail = [None] * size
    distance = [inf] * size
    distance[start] = 0
    q = [(0, start)]

    pos = start
    while q:
        _, pos = heappop(q)
        print(">", nodes[pos].pos, "->", graph.adjacency[pos], file=sys.stderr)
        if pos == dest:
            print("found", pos, dest, file=sys.stderr)
            break
        dist = distance[pos]
        for edge in graph.adjacency[pos]:
            alt = dist + edge.weight
            if alt < distance[edge.vertex]:
                distance[edge.vertex] = alt
                trail[edge.vertex] = pos
                heappush(q, (alt, edge.vertex))

    if pos == dest:
        path = [dest]
        while (pos := trail[pos]) is not None:
            path.append(pos)
    else:
        path = []

    return path


def find_path(pos, goal, nodes, graph):
    start = graph.node_index[pos]
    if isinstance(goal, list):
        ipath = []
        for gi in goal:
            dest = graph.node_index[gi]
            print("trying from", pos, "to", gi, file=sys.stderr)
            ipath = dijkstra(graph, start, dest, nodes)
            if ipath:
                break
    else:
        dest = graph.node_index[goal]
        ipath = dijkstra(graph, start, dest, nodes)

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
        if 0 <= ri < ROWS and 0 <= ci < COLS and maze[ri][ci] in CLEAR
    ]


class State(IntEnum):
    EXPAND = 0
    TO_CC = 1
    TO_HOME = 2


cc = None
home = None
status = State.EXPAND

while True:
    row, col = (int(i) for i in input().split())
    pos = (row + 1, col + 1)

    maze = list()

    for i in range(ROWS):
        if i in {0, ROWS - 1}:
            maze.append("#" * COLS)
            continue
        line = input()
        if (tcol := line.find("T")) >= 0:
            home = i, tcol + 1
        if (tcol := line.find("C")) >= 0:
            cc = i, tcol + 1
        if i == pos[0]:
            line = replace_index(line, col, "o")
        maze.append("#" + line + "#")

    nodes, foggy = parse(maze, pos)

    # looking for closest foggy node
    _dist = partial(square_dist, pos)
    foggy.sort(key=_dist)
    foggy_dist = [(square_dist(pos, fi), fi) for fi in foggy]
    print("foggy", foggy[:5], file=sys.stderr)

    if status == State.EXPAND:
        if not foggy:
            status = State.TO_CC
        if pos == cc:
            status = State.TO_HOME
    elif status == State.TO_CC:
        if pos == cc:
            status = State.TO_HOME

    if status == State.EXPAND:
        goal = foggy[:5]
    elif status == State.TO_CC:
        goal = cc
    else:
        goal = home

    # maze[goal[0]] = replace_index(maze[goal[0]], goal[1], "x")
    print(*maze, sep="\n", file=sys.stderr)
    print("ss:", status, goal, file=sys.stderr)

    # print("nodes", nodes, file=sys.stderr)

    graph = UnidirectedWeightedGraph(nodes, goal)
    # print(graph.adjacency, file=sys.stderr)
    trail = find_path(pos, goal, nodes, graph)

    print("trail:", trail, file=sys.stderr)
    if len(trail) > 1:
        towards = trail[-2]  # last position should be the current one
        diff = tuple(map(sign, map(sub, towards, trail[-1])))
    elif len(trail) == 1:
        towards = goal[0] if isinstance(goal, list) else goal
        diff = tuple(map(sign, map(sub, towards, pos)))
    else:
        trail = find_path(pos, cc, nodes, graph)
        if len(trail) > 1:
            diff = tuple(map(sign, map(sub, trail[-2], trail[-1])))
        elif len(trail) == 1:
            diff = tuple(map(sign, map(sub, cc, pos)))
        else:
            raise RuntimeError

    print(DIRECTION[diff])
