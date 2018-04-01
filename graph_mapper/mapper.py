"""
Tool for assigning nodes of a graph to points on a rectangle, so that heavy edges are short.
"""

import metis


def get_locations(G, width, height):
    """Returns a dictionary mapping every node in G to a Point in a width x height rectangle.

    The mapper attempts to place nodes connected by heavy edges near each other.
    """
    assert (width - 1) * height < len(G) and width * (height - 1) < len(G), \
           '%s by %s rectangle is needlessly big for %s nodes' % (width, height, len(G))

    assert width * height >= len(G), \
           '%s by %s rectangle is too small for %s nodes' % (width, height, len(G))

    if len(G) == width * height:  # easy case where nodes fit perfectly into rectangle
        return _get_locations(G, Point(0, 0), Point(width - 1, height - 1))


    # In general, nodes will fill up all of the first (height-1) rows and only part of the last row
    # We solve this by partitioning into the two corresponding perfectly sized rectangles
    size_tl_nodes = width * (len(G) // width)
    tl_subgraph, br_subgraph = partition(G, size_tl_nodes)
    ret = {}

    ret.update(_get_locations(tl_subgraph, top_left=Point(0, 0),
                              bottom_right=Point(width - 1, len(G) // width - 1)))
    ret.update(_get_locations(br_subgraph, top_left=Point(0, len(G) // width),
                              bottom_right=Point(len(G) % width - 1, len(G) // width)))
    return ret


def _get_locations(G, top_left, bottom_right):
    """Returns dict mapping each node to a Point in rect spanned by top_left and bottom_right.

    Uses recursive graph partitioning to reduce distances between nodes connected by heavy edges.
    At each step, the top_left to bottom_right rectangle is split into two subrectangles, and
    the nodes are assigned to the subrectangles such that the weight of crossing edges is small.
    """
    nodes = list(G.nodes)

    # Base case:
    if len(nodes) == 1:  # for singleton, only choice is to place in the single spot in 1x1 square
        return {nodes[0]: top_left}

    # Recursive case:
    ret = {}

    # if rectangle is wider than tall, split on y axis:
    if bottom_right.x - top_left.x > bottom_right.y - top_left.y:
        half_x = top_left.x + (bottom_right.x - top_left.x - 1) // 2
        size_tl_nodes = (half_x - top_left.x + 1) * (bottom_right.y - top_left.y + 1)
        nodes_tl, nodes_br = partition(G, size_tl_nodes)
        ret.update(_get_locations(
            nodes_tl, top_left=top_left, bottom_right=Point(half_x, bottom_right.y)))
        ret.update(_get_locations(
            nodes_br, top_left=Point(half_x + 1, top_left.y), bottom_right=bottom_right))

    else:  # split on x axis
        half_y = top_left.y + (bottom_right.y - top_left.y - 1) // 2
        size_tl_nodes = (bottom_right.x - top_left.x + 1) * (half_y - top_left.y + 1)
        nodes_tl, nodes_br = partition(G, size_tl_nodes)
        ret.update(_get_locations(
            nodes_tl, top_left=top_left, bottom_right=Point(bottom_right.x, half_y)))
        ret.update(_get_locations(
            nodes_br, top_left=Point(top_left.x, half_y + 1), bottom_right=bottom_right))

    return ret


def partition(G, desired_size):
    """Returns two-tuple of subgraphs that form a partition of the given graph.

    Uses METIS to try to minimize the total weight of edges crossing the cut. The first subgraph in
    the tuple has a size of desired_size.
    """
    desired_fraction = round(float(desired_size) / len(G), 4)
    tpwgts = [(desired_fraction,), (round(1.0 - desired_fraction, 4),)]
    _, labels = metis.part_graph(G, nparts=2, tpwgts=tpwgts, recursive=True, ncuts=10, niter=50)

    subgraph0_nodes = {list(G.nodes)[i] for i in range(len(G)) if labels[i] == 0}
    subgraph1_nodes = set(G.nodes) - subgraph0_nodes

    _force_balance_partition(subgraph0_nodes, subgraph1_nodes, desired_size)

    return G.subgraph(subgraph0_nodes), G.subgraph(subgraph1_nodes)


def _force_balance_partition(subgraph0_nodes, subgraph1_nodes, desired_size):
    # METIS is not perfect and will not always actually yield size_nodes_tl nodes in nodes_tl
    # in this case, just pop enough nodes from one list to the other, until sizes are appropriate
    while len(subgraph0_nodes) > desired_size:
        subgraph1_nodes.add(subgraph0_nodes.pop())
    while len(subgraph0_nodes) < desired_size:
        subgraph0_nodes.add(subgraph1_nodes.pop())


class Point(object):  # pylint: disable=too-few-public-methods
    """Represents a geometric point in 2-D space.

    Direction of coordinate system is as follows (0,0 is top left):
        0,0  1,0  2,0
        0,1  1,1  2,1
        0,2  1,2  2,2
    """
    def __init__(self, x, y):
        assert isinstance(x, int), 'x (%s) needs to be an int' % x
        assert isinstance(y, int), 'y (%s) needs to be an int' % y
        self.x = x
        self.y = y

    def __repr__(self):
        return '(%s, %s)' % (self.x, self.y)

    def __hash__(self):
        return hash((self.x, self.y))

    def __eq__(self, another):
        return self.x == another.x and self.y == another.y
