#ifndef UTILITY_H_INCLUDED
#define UTILITY_H_INCLUDED

#include <algorithm>
#include <bitset>
#include <cassert>
#include <cstdlib>
#include <fstream>
#include <iostream>
#include <limits.h>
#include <list>
#include <math.h>
#include <queue>
#include <sstream>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <time.h>
#include <vector>

using namespace std;

void tokenize(const std::string &str, std::vector<string> &tokens);
void eval_SHDL(string filename, vector<bool> &input_list,
               vector<bool> &output_list);
void eval_UC(vector<bool> &input_list, vector<bool> &output_list);
vector<bool> initialize_inputs(string filename);
vector<int> convert_hex_to_binary(int arity, string hex_str);
vector<int> get_binary(int arity, uint64_t num);
template <class T> int find_index(vector<T> &vec, T elem);
template <class T> int find_index(vector<T> &vec, T elem) {
  for (unsigned int i = 0; i < vec.size(); i++) {
    if (vec[i] == elem) {
      return i;
    }
  }
  return -1;
}

#endif // UTILITY_H_INCLUDED
