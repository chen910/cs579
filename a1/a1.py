# coding: utf-8

# # CS579: Assignment 1
#
# In this assignment, we'll implement community detection and link prediction algorithms using Facebook "like" data.
#
"""
	The file `edges.txt.gz` indicates like relationships between facebook users. This was collected using snowball sampling: 
	beginning with the user "Bill Gates", I crawled all the people he "likes", then, for each newly discovered user,
	I crawled all the people they liked.
"""
#
# We'll cluster the resulting graph into communities, as well as recommend friends for Bill Gates.
#
# Complete the **15** methods below that are indicated by `TODO`. I've provided some sample output to help guide your implementation.


# You should not use any imports not listed here:
from collections import Counter, defaultdict, deque
import copy
import math
import networkx as nx
import urllib.request


## Community Detection

def example_graph():
    """
    Create the example graph from class. Used for testing.
    Do not modify.
    """
    g = nx.Graph()
    g.add_edges_from([('A', 'B'), ('A', 'C'), ('B', 'C'), ('B', 'D'), ('D', 'E'), ('D', 'F'), ('D', 'G'), ('E', 'F'), ('G', 'F')])
    return g

def bfs(graph, root, max_depth):
    """
    Perform breadth-first search to compute the shortest paths from a root node to all
    other nodes in the graph. To reduce running time, the max_depth parameter ends
    the search after the specified depth.
    E.g., if max_depth=2, only paths of length 2 or less will be considered.
    This means that nodes greather than max_depth distance from the root will not
    appear in the result.

    You may use these two classes to help with this implementation:
      https://docs.python.org/3.5/library/collections.html#collections.defaultdict
      https://docs.python.org/3.5/library/collections.html#collections.deque

    Params:
      graph.......A networkx Graph
      root........The root node in the search graph (a string). We are computing
                  shortest paths from this node to all others.
      max_depth...An integer representing the maximum depth to search.

    Returns:
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree

    In the doctests below, we first try with max_depth=5, then max_depth=2.

    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    >>> sorted(node2distances.items())
    [('A', 3), ('B', 2), ('C', 3), ('D', 1), ('E', 0), ('F', 1), ('G', 2)]
    >>> sorted(node2num_paths.items())
    [('A', 1), ('B', 1), ('C', 1), ('D', 1), ('E', 1), ('F', 1), ('G', 2)]
    >>> sorted((node, sorted(parents)) for node, parents in node2parents.items())
    [('A', ['B']), ('B', ['D']), ('C', ['B']), ('D', ['E']), ('F', ['E']), ('G', ['D', 'F'])]
    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 2)
    >>> sorted(node2distances.items())
    [('B', 2), ('D', 1), ('E', 0), ('F', 1), ('G', 2)]
    >>> sorted(node2num_paths.items())
    [('B', 1), ('D', 1), ('E', 1), ('F', 1), ('G', 2)]
    >>> sorted((node, sorted(parents)) for node, parents in node2parents.items())
    [('B', ['D']), ('D', ['E']), ('F', ['E']), ('G', ['D', 'F'])]
    """
    q = deque()
    q.append(root)
    seen = set()
    seen.add(root)
    node2distances = defaultdict(int)
    node2num_paths = defaultdict(int)
    node2num_paths[root] = 1
    node2parents = defaultdict(list)
    #recursive BFS
    while q:
    	n = q.popleft()
    	#jump out when one search reach the max_depth
    	if node2distances[n] == max_depth:
    		continue
    	for nn in graph.neighbors(n):
    		if nn not in seen:
    			q.append(nn)
    			node2distances[nn] = node2distances[n] + 1
    			node2num_paths[nn] = node2num_paths[n]
    			node2parents[nn].append(n)
    			seen.add(nn)
    		elif node2distances[nn] == node2distances[n] + 1:
    			node2parents[nn].append(n)
    			node2num_paths[nn] += node2num_paths[n]
    return node2distances, node2num_paths, node2parents


def complexity_of_bfs(V, E, K):
    """
    If V is the number of vertices in a graph, E is the number of
    edges, and K is the max_depth of our approximate breadth-first
    search algorithm, then what is the *worst-case* run-time of
    this algorithm? As usual in complexity analysis, you can ignore
    any constant factors. E.g., if you think the answer is 2V * E + 3log(K),
    you would return V * E + math.log(K)
    >>> v = complexity_of_bfs(13, 23, 7)
    >>> type(v) == int or type(v) == float
    True
    """
    return V + E


def bottom_up(root, node2distances, node2num_paths, node2parents):
    """
    Compute the final step of the Girvan-Newman algorithm.
    See p 352 From your text:
    https://github.com/iit-cs579/main/blob/master/read/lru-10.pdf
        The third and final step is to calculate for each edge e the sum
        over all nodes Y of the fraction of shortest paths from the root
        X to Y that go through e. This calculation involves computing this
        sum for both nodes and edges, from the bottom. Each node other
        than the root is given a credit of 1, representing the shortest
        path to that node. This credit may be divided among nodes and
        edges above, since there could be several different shortest paths
        to the node. The rules for the calculation are as follows: ...

    Params:
      root.............The root node in the search graph (a string). We are computing
                       shortest paths from this node to all others.
      node2distances...dict from each node to the length of the shortest path from
                       the root node
      node2num_paths...dict from each node to the number of shortest paths from the
                       root node that pass through this node.
      node2parents.....dict from each node to the list of its parents in the search
                       tree
    Returns:
      A dict mapping edges to credit value. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

      Any edges excluded from the results in bfs should also be exluded here.

    >>> node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    >>> result = bottom_up('E', node2distances, node2num_paths, node2parents)
    >>> sorted(result.items())
    [(('A', 'B'), 1.0), (('B', 'C'), 1.0), (('B', 'D'), 3.0), (('D', 'E'), 4.5), (('D', 'G'), 0.5), (('E', 'F'), 1.5), (('F', 'G'), 0.5)]
    """
    node2credit_value = defaultdict(int)
    edge2credit_value = defaultdict(int)
    sorted_nodes = sorted(node2distances.items(), key = lambda x:x[1], reverse = True)
    
    #Each node otherthan the root is given credict 1
    node2credit_value[root] = 0
    for n,d in sorted_nodes:
    	if n != root:
    		node2credit_value[n] = 1
    #bottom up
    for n,d in sorted_nodes:
    	#sum the path to node
    	path2node = 0
    	for p in node2parents[n]:
    		path2node += node2num_paths[p]
    	#bottom up the node credit to edge credit
    	for p in node2parents[n]:
    		edge = tuple(sorted((n, p)))
    		edge2credit_value[edge] = node2credit_value[n] * node2num_paths[p] / path2node
    		node2credit_value[p] += edge2credit_value[edge]
    return edge2credit_value


def approximate_betweenness(graph, max_depth):
    """
    Compute the approximate betweenness of each edge, using max_depth to reduce
    computation time in breadth-first search.

    You should call the bfs and bottom_up functions defined above for each node
    in the graph, and sum together the results. Be sure to divide by 2 at the
    end to get the final betweenness.

    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A dict mapping edges to betweenness. Each key is a tuple of two strings
      representing an edge (e.g., ('A', 'B')). Make sure each of these tuples
      are sorted alphabetically (so, it's ('A', 'B'), not ('B', 'A')).

    >>> sorted(approximate_betweenness(example_graph(), 2).items())
    [(('A', 'B'), 2.0), (('A', 'C'), 1.0), (('B', 'C'), 2.0), (('B', 'D'), 6.0), (('D', 'E'), 2.5), (('D', 'F'), 2.0), (('D', 'G'), 2.5), (('E', 'F'), 1.5), (('F', 'G'), 1.5)]
    """
    edge2betweenness = defaultdict(int)
    for n in graph.nodes():
    	node2distances, node2num_paths, node2parents = bfs(graph, n, max_depth)
    	edge2credit_value = bottom_up(n, node2distances, node2num_paths, node2parents)
    	for e,c in edge2credit_value.items():
    		edge2betweenness[tuple(sorted(e))] += c
    # divide by 2
    for e,c in edge2credit_value.items():
    	edge2betweenness[e] = c / 2
    return edge2betweenness


def is_approximation_always_right():
    """
    Look at the doctests for approximate betweenness. In this example, the
    edge with the highest betweenness was ('B', 'D') for both cases (when
    max_depth=5 and max_depth=2).

    Consider an arbitrary graph G. For all max_depth > 1, will it always be
    the case that the edge with the highest betweenness will be the same
    using either approximate_betweenness verses the exact computation?
    Answer this question below.

    In this function, you just need to return either the string 'yes' or 'no'
    (no need to do any actual computations here).
    >>> s = is_approximation_always_right()
    >>> type(s)
    <class 'str'>
    """
    return 'yes'


def partition_girvan_newman(graph, max_depth):
    """
    Use your approximate_betweenness implementation to partition a graph.
    Unlike in class, here you will not implement this recursively. Instead,
    just remove edges until more than one component is created, then return
    those components.
    That is, compute the approximate betweenness of all edges, and remove
    them until multiple comonents are created.

    You only need to compute the betweenness once.
    If there are ties in edge betweenness, break by edge name (e.g.,
    (('A', 'B'), 1.0) comes before (('B', 'C'), 1.0)).

    Note: the original graph variable should not be modified. Instead,
    make a copy of the original graph prior to removing edges.
    See the Graph.copy method https://networkx.github.io/documentation/development/reference/generated/networkx.Graph.copy.html
    Params:
      graph.......A networkx Graph
      max_depth...An integer representing the maximum depth to search.

    Returns:
      A list of networkx Graph objects, one per partition.

    >>> components = partition_girvan_newman(example_graph(), 5)
    >>> components = sorted(components, key=lambda x: sorted(x.nodes())[0])
    >>> sorted(components[0].nodes())
    ['A', 'B', 'C']
    >>> sorted(components[1].nodes())
    ['D', 'E', 'F', 'G']
    """
    copy = graph.copy()
    betweenness = sorted(approximate_betweenness(copy, max_depth).items(), key= lambda x: (-x[1],x[0][0],x[0][1]))
    for edge,val in betweenness:
    	copy.remove_edge(*edge)
    	if nx.number_connected_components(copy) > 1:
    		break
    partition_graph = sorted(list(nx.connected_component_subgraphs(copy)), key = lambda x: -len(x))
    return partition_graph


def get_subgraph(graph, min_degree):
    """Return a subgraph containing nodes whose degree is
    greater than or equal to min_degree.
    We'll use this in the main method to prune the original graph.

    Params:
      graph........a networkx graph
      min_degree...degree threshold
    Returns:
      a networkx graph, filtered as defined above.

    >>> subgraph = get_subgraph(example_graph(), 3)
    >>> sorted(subgraph.nodes())
    ['B', 'D', 'F']
    >>> len(subgraph.edges())
    2
    """
    subgraph = graph.copy()
    degrees = nx.degree(subgraph)
    for n, d in degrees.items():
    	if d < min_degree:
    		subgraph.remove_node(n)
    return subgraph


""""
Compute the normalized cut for each discovered cluster.
I've broken this down into the three next methods.
"""

def volume(nodes, graph):
    """
    Compute the volume for a list of nodes, which
    is the number of edges in `graph` with at least one end in
    nodes.
    Params:
      nodes...a list of strings for the nodes to compute the volume of.
      graph...a networkx graph

    >>> volume(['A', 'B', 'C'], example_graph())
    4
    """
    #volume = nx.volume(graph, nodes, weight=None)
    copy = graph.copy()
    edgeV = 0
    for n in nodes:
    	for e in copy.edges():
    		if n == e[0] or n == e[1]:
    			edgeV += 1
    			copy.remove_edge(*e)
    return edgeV


def cut(S, T, graph):
    """
    Compute the cut-set of the cut (S,T), which is
    the set of edges that have one endpoint in S and
    the other in T.
    Params:
      S.......set of nodes in first subset
      T.......set of nodes in second subset
      graph...networkx graph
    Returns:
      An int representing the cut-set.

    >>> cut(['A', 'B', 'C'], ['D', 'E', 'F', 'G'], example_graph())
    1
    """
    cut = 0
    for i in S:
    	for j in T:
    		if graph.has_edge(i,j):
    			cut += 1
    return cut


def norm_cut(S, T, graph):
    """
    The normalized cut value for the cut S/T. (See lec06.)
    Params:
      S.......set of nodes in first subset
      T.......set of nodes in second subset
      graph...networkx graph
    Returns:
      An float representing the normalized cut value

    """
    cutSet, vs, vt = cut(S, T, graph), volume(S, graph), volume(T, graph) 
    return cutSet / vs + cutSet / vt


def score_max_depths(graph, max_depths):
    """
    In order to assess the quality of the approximate partitioning method
    we've developed, we will run it with different values for max_depth
    and see how it affects the norm_cut score of the resulting partitions.
    Recall that smaller norm_cut scores correspond to better partitions.

    Params:
      graph........a networkx Graph
      max_depths...a list of ints for the max_depth values to be passed
                   to calls to partition_girvan_newman

    Returns:
      A list of (int, float) tuples representing the max_depth and the
      norm_cut value obtained by the partitions returned by
      partition_girvan_newman. See Log.txt for an example.
    """
    score = []
    for val in max_depths:
    	partition_graph = partition_girvan_newman(graph, val)
    	score.append((int(val),float(norm_cut(partition_graph[0].nodes(), partition_graph[1].nodes(), graph))))
    return score


## Link prediction

# Next, we'll consider the link prediction problem. In particular,
# we will remove 5 of the accounts that Bill Gates likes and
# compute our accuracy at recovering those links.

def make_training_graph(graph, test_node, n):
    """
    To make a training graph, we need to remove n edges from the graph.
    As in lecture, we'll assume there is a test_node for which we will
    remove some edges. Remove the edges to the first n neighbors of
    test_node, where the neighbors are sorted alphabetically.
    E.g., if 'A' has neighbors 'B' and 'C', and n=1, then the edge
    ('A', 'B') will be removed.

    Be sure to *copy* the input graph prior to removing edges.

    Params:
      graph.......a networkx Graph
      test_node...a string representing one node in the graph whose
                  edges will be removed.
      n...........the number of edges to remove.

    Returns:
      A *new* networkx Graph with n edges removed.

    In this doctest, we remove edges for two friends of D:
    >>> g = example_graph()
    >>> sorted(g.neighbors('D'))
    ['B', 'E', 'F', 'G']
    >>> train_graph = make_training_graph(g, 'D', 2)
    >>> sorted(train_graph.neighbors('D'))
    ['F', 'G']
    """
    ###TODO
    training_graph = graph.copy()
    remove_num = 0
    for node in sorted(graph.neighbors(test_node)):
    	training_graph.remove_edge(test_node, node)
    	remove_num += 1
    	if remove_num == n:
    		break
    return training_graph



def jaccard(graph, node, k):
    """
    Compute the k highest scoring edges to add to this node based on
    the Jaccard similarity measure.
    Note that we don't return scores for edges that already appear in the graph.

    Params:
      graph....a networkx graph
      node.....a node in the graph (a string) to recommend links for.
      k........the number of links to recommend.

    Returns:
      A list of tuples in descending order of score representing the
      recommended new edges. Ties are broken by
      alphabetical order of the terminal node in the edge.

    In this example below, we remove edges (D, B) and (D, E) from the
    example graph. The top two edges to add according to Jaccard are
    (D, E), with score 0.5, and (D, A), with score 0. (Note that all the
    other remaining edges have score 0, but 'A' is first alphabetically.)

    >>> g = example_graph()
    >>> train_graph = make_training_graph(g, 'D', 2)
    >>> jaccard(train_graph, 'D', 2)
    [(('D', 'E'), 0.5), (('D', 'A'), 0.0)]
    """
    neighbors = set(graph.neighbors(node))
    print(neighbors)
    count = 0
    scores = []
    for n in graph.nodes():
    	if((n not in graph.neighbors(node)) & (n != node)):
    		neighbors2 = set(graph.neighbors(n))
    		scores.append(((node, n), len(neighbors & neighbors2) / len(neighbors | neighbors2)))

    scores = sorted(scores, key=lambda x: (-x[1], x[0][1]))
    return scores[:k]


# One limitation of Jaccard is that it only has non-zero values for nodes two hops away.
#
# Implement a new link prediction function that computes the similarity between two nodes $x$ and $y$  as follows:
#
# $$
# s(x,y) = \beta^i n_{x,y,i}
# 
# S = beta^i * n_
#
# where
# - $\beta \in [0,1]$ is a user-provided parameter
# - $i$ is the length of the shortest path from $x$ to $y$
# - $n_{x,y,i}$ is the number of shortest paths between $x$ and $y$ with length $i$


def path_score(graph, root, k, beta):
    """
    Compute a new link prediction scoring function based on the shortest
    paths between two nodes, as defined above.

    Note that we don't return scores for edges that already appear in the graph.

    This algorithm should have the same time complexity as bfs above.

    Params:
      graph....a networkx graph
      root.....a node in the graph (a string) to recommend links for.
      k........the number of links to recommend.
      beta.....the beta parameter in the equation above.

    Returns:
      A list of tuples in descending order of score. Ties are broken by
      alphabetical order of the terminal node in the edge.

    In this example below, we remove edge (D, F) from the
    example graph. The top two edges to add according to path_score are
    (D, F), with score 0.5, and (D, A), with score .25. (Note that (D, C)
    is tied with a score of .25, but (D, A) is first alphabetically.)

    >>> g = example_graph()
    >>> train_graph = g.copy()
    >>> train_graph.remove_edge(*('D', 'F'))
    >>> path_score(train_graph, 'D', k=4, beta=.5)
    [(('D', 'F'), 0.5), (('D', 'A'), 0.25), (('D', 'C'), 0.25)]
    """
    ###TODO
    node2distances, node2num_paths, node2parents = bfs(graph, root, len(graph.edges()))
    pscore = []
    for n in graph.nodes():
    	if((n not in graph.neighbors(root)) & (n != root)):
    		i = node2distances[n]
    		np = node2num_paths[n]
    		pscore.append(((root, n), (beta ** i) * np))
    pscore = sorted(pscore, key=lambda x: (-x[1], x[0][1]))
    return pscore[:k]

def evaluate(predicted_edges, graph):
    """
    Return the fraction of the predicted edges that exist in the graph.

    Args:
      predicted_edges...a list of edges (tuples) that are predicted to
                        exist in this graph
      graph.............a networkx Graph

    Returns:
      The fraction of edges in predicted_edges that exist in the graph.

    In this doctest, the edge ('D', 'E') appears in the example_graph,
    but ('D', 'A') does not, so 1/2 = 0.5

    >>> evaluate([('D', 'E'), ('D', 'A')], example_graph())
    0.5
    """
    ###TODO
    predict_val = 0
    for e in predicted_edges:
    	if graph.has_edge(*e) == True:
    		predict_val += 1
    evaluate_val = predict_val / len(predicted_edges)
    return evaluate_val


"""
Next, we'll download a real dataset to see how our algorithm performs.
"""
def download_data():
    """
    Download the data. Done for you.
    """
    urllib.request.urlretrieve('http://cs.iit.edu/~culotta/cs579/a1/edges.txt.gz', 'edges.txt.gz')


def read_graph():
    """ Read 'edges.txt.gz' into a networkx **undirected** graph.
    Done for you.
    Returns:
      A networkx undirected graph.
    """
    return nx.read_edgelist('edges.txt.gz', delimiter='\t')


def main():
    """
    FYI: This takes ~10-15 seconds to run on my laptop.
    """
    # node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    # print("bfs with %d max_depth" %(5))
    # print(sorted(node2distances.items()), "\n", sorted(node2num_paths.items()), "\n", sorted((node, sorted(parents)) for node, parents in node2parents.items()))
    # node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 2)
    # print("bfs with %d max_depth" %(2))
    # print(sorted(node2distances.items()), "\n", sorted(node2num_paths.items()), "\n", sorted((node, sorted(parents)) for node, parents in node2parents.items()))
    # node2distances, node2num_paths, node2parents = bfs(example_graph(), 'E', 5)
    # result = bottom_up('E', node2distances, node2num_paths, node2parents)
    # print("bottom up: ", result.items())
    # print("betweenness: ", sorted(approximate_betweenness(example_graph(), 2).items()))
    # components = partition_girvan_newman(example_graph(), 5)
    # components = sorted(components, key=lambda x: sorted(x.nodes())[0])
    # print("partition 1: ", sorted(components[0].nodes()))
    # print("partition 2: ", sorted(components[1].nodes()))
    # subgraph = get_subgraph(example_graph(), 3)
    # print("subgraph: ", sorted(subgraph.nodes()))
    # print("volume: ", volume(['A', 'B', 'C'], example_graph()))
    # print("cut: ", cut(['A', 'B', 'C'], ['D', 'E', 'F', 'G'], example_graph()))
    # print("norm_cut: ", norm_cut(['A', 'B', 'C'], ['D', 'E', 'F', 'G'], example_graph()))
    # train_graph = make_training_graph(example_graph(), 'D', 2)
    # print("train_graph: ", sorted(train_graph.neighbors('D')))
    # print("jaccard: ", jaccard(train_graph, 'D', 2))
    # g = example_graph()
    # train_graph = g.copy()
    # train_graph.remove_edge(*('D', 'F'))
    # print("path_score: ", path_score(train_graph, 'D', k=4, beta=.5))
    # print("evalute: ", evaluate([('D', 'E'), ('D', 'A')], example_graph()) )
    download_data()
    graph = read_graph()
    print('graph has %d nodes and %d edges' %
          (graph.order(), graph.number_of_edges()))
    subgraph = get_subgraph(graph, 2)
    print('subgraph has %d nodes and %d edges' %
          (subgraph.order(), subgraph.number_of_edges()))
    print('norm_cut scores by max_depth:')
    print(score_max_depths(subgraph, range(1,5)))
    clusters = partition_girvan_newman(subgraph, 3)
    print('first partition: cluster 1 has %d nodes and cluster 2 has %d nodes' %
          (clusters[0].order(), clusters[1].order()))
    print('cluster 2 nodes:')
    print(clusters[1].nodes())
    test_node = 'Bill Gates'
    train_graph = make_training_graph(subgraph, test_node, 5)
    print('train_graph has %d nodes and %d edges' %
          (train_graph.order(), train_graph.number_of_edges()))


    jaccard_scores = jaccard(train_graph, test_node, 5)
    print('\ntop jaccard scores for Bill Gates:')
    print(jaccard_scores)
    print('jaccard accuracy=%g' %
          evaluate([x[0] for x in jaccard_scores], subgraph))

    path_scores = path_score(train_graph, test_node, k=5, beta=.1)
    print('\ntop path scores for Bill Gates for beta=.1:')
    print(path_scores)
    print('path accuracy for beta .1=%g' %
          evaluate([x[0] for x in path_scores], subgraph))



if __name__ == '__main__':
    main()
