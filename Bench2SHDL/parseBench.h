#include <algorithm>
#include <chrono>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <list>
#include <queue>
#include <random>
#include <sstream>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <time.h>
#include <unordered_map>
#include <unordered_set>
#include <vector>

#include "utility.h"
using namespace std;

class Graph {
public:
  class Node {
  public:
    Node(int number, string name, string type);
    int number;
    string name;
    string type;
    vector<int> function_bits;
    vector<Node *> inputs;
    vector<Node *> outputs;
    vector<Graph::Node *> copy_gates;
  };

  vector<Node *> nodes;
  vector<int> output_nodes;
};

void parse_bench(string str_filename);
void make_copy_gate_tree(Graph::Node *v);
void write_shdl_line(ofstream &os, Graph::Node *v);
void write_node_with_copy_gates(ofstream &os, Graph::Node *u, int &number);
void parse_bench(string str_filename, int copies);
Graph *create_random_graph(unsigned int num_inputs, unsigned int num_gates,
                           unsigned int num_outputs, unsigned int max_outdegree,
                           unsigned int max_indegree, string filename);
Graph *convert_into_fanout2(Graph *g);
void shdl_to_bench(string filename);
