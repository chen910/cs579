import networkx as nx


def jaccard_wt(graph, node):
    """
    The weighted jaccard score, defined above.
    Args:
    graph....a networkx graph
    node.....a node to score potential new edges for.
    Returns:
    A list of ((node, ni), score) tuples, representing the 
              score assigned to edge (node, ni)
              (note the edge order)
    """
    neighbors = set(graph.neighbors(node))
    scores = []
    nodeScore = 0
    ADegrees = 0
    BDegress = 0
    for i in neighbors:
        ADegrees += len(graph.neighbors(i))
    for n in graph.nodes():
        if n not in neighbors and n != node:
            neighbors2 = set(graph.neighbors(n))
    for j in neighbors2:
        BDegress += len(graph.neighbors(j))
    for n in neighbors:
        if n not in neighbors2:
            nodeScore += 1 / len(graph.neighbors(n))
    scores.append(((node, i), nodeScore / ((1 / ADegrees) + (1 / BDegress))))

    scores = sorted(scores, key=lambda x: (-x[1], x[0][1]))
    return scores

# def example_graph():
#     """
#     Create the example graph from class. Used for testing.
#     Do not modify.
#     """
#     g = nx.Graph()
#     g.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('G', 'F')])
#     return g

# def main():
#     g = example_graph()
#     print(jaccard_wt(g, 'D'))

# if __name__ == '__main__':
#     main()
