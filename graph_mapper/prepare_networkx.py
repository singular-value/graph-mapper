# Helper file: get_networkx turns the specified qasm into a NetworkX graph of CNOTs
import networkx as nx
G = nx.Graph()

def get_networkx(qasm_filepath):
    with open('qasm_filepath', 'r') as fp:
        G.graph['edge_weight_attr'] = 'weight'
        for i, line in enumerate(fp):
            if i % 1000 == 0:
                print(i)
            if 'cx' not in line:
                continue

            split = line[3:-2].strip().split(',')
            src = split[0]
            dst = split[1]
            if G.has_edge(src, dst):
                G[src][dst]['weight'] += 1
            else:
                G.add_edge(src, dst, weight=1)
    return G
