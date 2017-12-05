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
    for n in graph.nodes():
        if (n not in neighbors) and (n != node):
            neighbors2 = set(graph.neighbors(n))
            nodeScore = 0
            ADegrees = 0
            BDegress = 0
            for i in neighbors:
                ADegrees += len(graph.neighbors(i))
            for j in neighbors2:
                BDegress += len(graph.neighbors(j))            
            for common in neighbors:
                if common  in neighbors2:
                    nodeScore += 1 / len(graph.neighbors(common))
            scores.append(((node, n), nodeScore / ((1 / ADegrees) + (1 / BDegress))))

    scores = sorted(scores, key=lambda x: x[0])
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
#     print(jaccard_wt(g, 'G'))

# if __name__ == '__main__':
#     main()
