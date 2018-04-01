import unittest
from unittest.mock import patch, ANY

import networkx as nx

import mapper

class TestIntegration(unittest.TestCase):
    def test_linear(self):
        # 1D-test with 8 nodes. Make 4 edges heavy -> those 4 pairs should be mapped together
        G = nx.complete_graph(8)
        G.graph['edge_weight_attr'] = 'weight'
        for i in range(8):
            for j in range(i + 1, 8):
                G[i][j].update({'weight': 1})

        heavy_edges = [{0, 5}, {1, 2}, {3, 7}, {4, 6}]
        for heavy_edge in map(tuple, heavy_edges):
            G[heavy_edge[0]][heavy_edge[1]].update({'weight': 99})

        # 1x8
        node_to_location = mapper.get_locations(G, 1, 8)
        location_to_node = {value: key for key, value in node_to_location.items()}
        adjacent_pairs = [{location_to_node[mapper.Point(0, i)],
                           location_to_node[mapper.Point(0, i+1)]} for i in range(0, 8, 2)]
        self.assertCountEqual(adjacent_pairs, heavy_edges)

        # 8x1
        node_to_location = mapper.get_locations(G, 8, 1)
        location_to_node = {value: key for key, value in node_to_location.items()}
        adjacent_pairs = [{location_to_node[mapper.Point(i, 0)],
                           location_to_node[mapper.Point(i+1, 0)]} for i in range(0, 8, 2)]
        self.assertCountEqual(adjacent_pairs, heavy_edges)


class TestGetLocations(unittest.TestCase):
    def test_enforce_rectangle_size(self):
        with self.assertRaises(AssertionError):
            mapper.get_locations(nx.empty_graph(16), 4, 5)

        with self.assertRaises(AssertionError):
            mapper.get_locations(nx.empty_graph(16), 5, 4)

        with self.assertRaises(AssertionError):
            mapper.get_locations(nx.empty_graph(10), 3, 3)

    @patch('mapper._get_locations')
    def test_perfect_size(self, mock__get_locations):
        G = nx.empty_graph(16)
        mapper.get_locations(G, 4, 4)
        mock__get_locations.assert_called_once_with(G, mapper.Point(0, 0), mapper.Point(3, 3))

    @patch('mapper._get_locations')
    @patch('mapper.partition')
    def test_imperfect_size(self, mock_partition, mock__get_locations):
        G, G0, G1 = nx.empty_graph(97), nx.empty_graph(90), nx.empty_graph(7)
        mock_partition.return_value = G0, G1
        mapper.get_locations(G, 10, 10)

        # For mapping 97 nodes to a 10x10 square, we should subdivide into
        # 90 nodes mapped to a 10x9 rectangle and 7 nodes mapped to a 7x1 rectangle
        mock_partition.assert_called_once_with(G, 90)

        mock__get_locations.assert_any_call(G0, top_left=mapper.Point(0, 0),
                                            bottom_right=mapper.Point(9, 8))
        mock__get_locations.assert_any_call(G1, top_left=mapper.Point(0, 9),
                                            bottom_right=mapper.Point(6, 9))
        self.assertEqual(mock__get_locations.call_count, 2)

    def test__get_locations_base_case(self):
        G = nx.empty_graph(1)
        self.assertEqual(mapper._get_locations(G, mapper.Point(18, 12), mapper.Point(18, 12)),
                         {list(G.nodes)[0]: mapper.Point(18, 12)})

    def test__get_locations_wide_rectangle(self):
        _get_locations_copy = mapper._get_locations

        # 5x4 rectangle should be split into 2x4 and 3x4
        G = nx.empty_graph(20)
        with patch('mapper._get_locations') as mock__get_locations:
            _get_locations_copy(G, mapper.Point(0, 0), mapper.Point(4, 3))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 0),
                                                bottom_right=mapper.Point(1, 3))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(2, 0),
                                                bottom_right=mapper.Point(4, 3))
            self.assertEqual(mock__get_locations.call_count, 2)

        mock__get_locations.reset_mock()

        # 6x4 rectangle should be split into 3x4 and 3x4
        G = nx.empty_graph(24)
        with patch('mapper._get_locations') as mock__get_locations:
            _get_locations_copy(G, mapper.Point(0, 0), mapper.Point(5, 3))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 0),
                                                bottom_right=mapper.Point(2, 3))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(3, 0),
                                                bottom_right=mapper.Point(5, 3))
            self.assertEqual(mock__get_locations.call_count, 2)

    def test__get_locations_tall_rectangle(self):
        _get_locations_copy = mapper._get_locations

        # 4x5 rectangle should be split into 4x2 and 4x3
        G = nx.empty_graph(20)
        with patch('mapper._get_locations') as mock__get_locations:
            _get_locations_copy(G, mapper.Point(0, 0), mapper.Point(3, 4))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 0),
                                                bottom_right=mapper.Point(3, 1))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 2),
                                                bottom_right=mapper.Point(3, 4))
            self.assertEqual(mock__get_locations.call_count, 2)

        mock__get_locations.reset_mock()

        # 4x6 rectangle should be split into 4x3 and 4x3
        G = nx.empty_graph(24)
        with patch('mapper._get_locations') as mock__get_locations:
            _get_locations_copy(G, mapper.Point(0, 0), mapper.Point(3, 5))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 0),
                                                bottom_right=mapper.Point(3, 2))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 3),
                                                bottom_right=mapper.Point(3, 5))
            self.assertEqual(mock__get_locations.call_count, 2)

        mock__get_locations.reset_mock()

        # a square (4x4 here) should also be split on x axis (so 4x2 and 4x2)
        G = nx.empty_graph(16)
        with patch('mapper._get_locations') as mock__get_locations:
            _get_locations_copy(G, mapper.Point(0, 0), mapper.Point(3, 3))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 0),
                                                bottom_right=mapper.Point(3, 1))
            mock__get_locations.assert_any_call(ANY, top_left=mapper.Point(0, 2),
                                                bottom_right=mapper.Point(3, 3))
            self.assertEqual(mock__get_locations.call_count, 2)



class TestPartition(unittest.TestCase):
    # NB(pranav): this is technically not a unit test, since it invokes METIS.
    def test_basic(self):
        # construct complete graph with heavy edges between nodes of same parity
        G = nx.complete_graph(20)
        G.graph['edge_weight_attr'] = 'weight'
        for i in range(20):
            for j in range(i + 1, 20):
                if i % 2 == j % 2:
                    G[i][j].update({'weight': 99})
                else:
                    G[i][j].update({'weight': 1})

        subgraph0, subgraph1 = mapper.partition(G, 10)

        # one subgraph should have even nodes, one subgraph should have odd nodes
        self.assertEqual(len(subgraph0), 10)
        self.assertEqual(len(subgraph1), 10)
        self.assertEqual({tuple(subgraph0), tuple(subgraph1)},
                         {(0, 2, 4, 6, 8, 10, 12, 14, 16, 18), (1, 3, 5, 7, 9, 11, 13, 15, 17, 19)})

    def test_empty_graph(self):
        # METIS should not break if graph has no edges
        G = nx.empty_graph(20)

        subgraph0, subgraph1 = mapper.partition(G, 10)
        self.assertEqual(len(subgraph0), 10)
        self.assertEqual(len(subgraph1), 10)
        self.assertEqual(set(subgraph0).union(set(subgraph1)), set(range(20)))

        subgraph0, subgraph1 = mapper.partition(G, 17)
        self.assertEqual(len(subgraph0), 17)
        self.assertEqual(len(subgraph1), 3)
        self.assertEqual(set(subgraph0).union(set(subgraph1)), set(range(20)))

    def test__force_balance_partition(self):
        subgraph0_nodes, subgraph1_nodes = set(range(0, 10)), set(range(10, 20))
        mapper._force_balance_partition(subgraph0_nodes, subgraph1_nodes, 5)
        self.assertEqual(len(subgraph0_nodes), 5)
        self.assertEqual(len(subgraph1_nodes), 15)
        self.assertEqual(len(subgraph0_nodes.union(subgraph1_nodes)), 20)

        subgraph0_nodes, subgraph1_nodes = set(range(0, 10)), set(range(10, 20))
        mapper._force_balance_partition(subgraph0_nodes, subgraph1_nodes, 15)
        self.assertEqual(len(subgraph0_nodes), 15)
        self.assertEqual(len(subgraph1_nodes), 5)
        self.assertEqual(len(subgraph0_nodes.union(subgraph1_nodes)), 20)


if __name__ == '__main__':
    unittest.main()
