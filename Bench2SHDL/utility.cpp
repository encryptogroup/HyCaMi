#include "utility.h"

void tokenize(const string &str, vector<string> &tokens) {
  tokens.clear();
  char delimiter = ' ';
  string::size_type last_pos = str.find_first_not_of(delimiter, 0);
  string::size_type pos = str.find_first_of(delimiter, last_pos);
  while (string::npos != pos || string::npos != last_pos) {
    tokens.push_back(str.substr(last_pos, pos - last_pos).c_str());
    last_pos = str.find_first_not_of(delimiter, pos);
    pos = str.find_first_of(delimiter, last_pos);
  }
}

vector<int> convert_hex_to_binary(int arity, string hex_str) {
  if (hex_str.rfind("0x", 0) != 0) {
    throw std::runtime_error("Invalid hex format");
  }

  std::vector<int> binary;

  // loop backwards as the LUT is given in a little-endian fashion
  for (size_t i = hex_str.length() - 1; i > 1; i--) {
    const char c = hex_str[i];
    int value;
    if (c >= '0' && c <= '9') {
      value = c - '0';
    } else if (c >= 'a' && c <= 'f') {
      value = c - 'a' + 10;
    } else {
      throw std::runtime_error("Invalid hex digit");
    }

    binary.push_back((value & 0x1) != 0 ? 1 : 0);
    binary.push_back((value & 0x2) != 0 ? 1 : 0);
    binary.push_back((value & 0x4) != 0 ? 1 : 0);
    binary.push_back((value & 0x8) != 0 ? 1 : 0);
  }

  binary.resize(arity, 0);
  return binary;
}

vector<int> get_binary(int arity, uint64_t num) {
  vector<int> binary_rep;
  while (num > 0) {
    if (num % 2 == 0) {
      binary_rep.push_back(0);
    } else {
      binary_rep.push_back(1);
    }
    num >>= 1;
  }
  // Pad to needed size
  int start = binary_rep.size();
  for (int i = start; i < arity; i++) {
    binary_rep.push_back(0);
  }
  reverse(binary_rep.begin(), binary_rep.end());
  return binary_rep;
}

void eval_SHDL(string filename, vector<bool> &input_list,
               vector<bool> &output_list) {
  ifstream file;
  file.open(filename);
  vector<bool> wire_results;
  for (bool bit : input_list) {
    wire_results.push_back(bit);
  }

  string line;
  vector<string> tokens;

  while (getline(file, line)) {
    if (line != "") {
      tokenize(line, tokens);
      int shift = 0;
      if (tokens[1] == "output") {
        shift = 1;
      }
      if (tokens[1 + shift] == "gate") {
        vector<int> function_bits;
        unsigned int arity = stoi(tokens[3 + shift]);
        unsigned int start_index = 6 + shift;
        unsigned int end_index = tokens.size() - 1 - arity - 4;
        for (unsigned int i = start_index; i <= end_index; i++) {
          function_bits.push_back(stoi(tokens[i]));
        }
        vector<int> inputs;
        start_index = tokens.size() - arity - 1;
        end_index = tokens.size() - 2;
        for (unsigned int i = start_index; i <= end_index; i++) {
          inputs.push_back(stoi(tokens[i]));
        }

        assert(inputs.size() == arity);
        uint64_t pol_result = 0;

        for (unsigned int i = 0; i < inputs.size(); i++) {
          pol_result += pow(2, arity - 1 - i) * wire_results[inputs[i]];
        }

        assert((pol_result <= function_bits.size() - 1) && pol_result >= 0);
        int result = function_bits[pol_result];
        assert(result == 0 || result == 1);
        wire_results.push_back(result);
      }
      if (tokens[0] == "outputs") {
        for (unsigned int j = 1; j < tokens.size(); ++j) {
          output_list.push_back(wire_results[stoi(tokens[j])]);
        }
      }
    }
  }
  file.close();
}

void eval_UC(vector<bool> &input_list, vector<bool> &output_list) {
  string circuit = "outputs/circuit";
  string program = "outputs/programming";

  ifstream c_file;
  c_file.open(circuit);
  ifstream p_file;
  p_file.open(program);

  vector<bool> wire_results;

  string c_line;
  string p_line;
  vector<string> c_tokens;
  vector<string> p_tokens;
  unsigned int c_line_counter = 0;
  unsigned int p_line_counter = 0;

  while (getline(c_file, c_line)) {
    c_line_counter++;
    if (c_line == "") {
      continue;
    }
    tokenize(c_line, c_tokens);
    if (c_tokens[0] == "C") { // Parse the input list
      assert(input_list.size() == c_tokens.size() - 1);
      for (unsigned int i = 0; i < input_list.size(); i++) {
        wire_results.push_back(input_list[i]);
      }
      continue;
    } else if (c_tokens[0] == "X" || c_tokens[0] == "Y") {
      bool in1 = wire_results[stoi(c_tokens[1])];
      bool in2 = wire_results[stoi(c_tokens[2])];
      getline(p_file, p_line);
      p_line_counter++;
      tokenize(p_line, p_tokens);
      assert(p_tokens.size() == 1);
      bool control_bit = (bool)stoi(p_tokens[0]);
      if (c_tokens[0] == "X") {
        assert(c_tokens.size() == 5);
        bool out1 = (control_bit) ? in2 : in1;
        bool out2 = (control_bit) ? in1 : in2;
        wire_results.push_back(out1);
        wire_results.push_back(out2);
      } else {
        assert(c_tokens.size() == 4);
        bool out1 = (control_bit) ? in1 : in2;
        wire_results.push_back(out1);
      }
      continue;
    } else if (c_tokens[0] == "U") {
      vector<bool> gate_inputs;
      for (unsigned int i = 1; i < c_tokens.size() - 1; i++) {
        gate_inputs.push_back(wire_results[stoi(c_tokens[i])]);
      }
      getline(p_file, p_line);
      p_line_counter++;
      tokenize(p_line, p_tokens);
      if (p_tokens.empty()) { // If there are no programming bits, i.e. a gate
                              // without inputs whose output wire is never used
                              // in a correct circuit
        wire_results.push_back(0);
        continue;
      }
      assert(p_tokens.size() == pow(2, gate_inputs.size()));
      uint64_t pol_result = 0;

      for (unsigned int i = 0; i < gate_inputs.size(); i++) {
        pol_result += pow(2, gate_inputs.size() - 1 - i) * gate_inputs[i];
      }
      assert((pol_result <= p_tokens.size() - 1) && pol_result >= 0);
      int result = stoi(p_tokens[pol_result]);
      assert(result == 0 || result == 1);
      wire_results.push_back(result);
      continue;
    } else if (c_tokens[0] == "O") {
      for (unsigned int i = 1; i < c_tokens.size(); i++) {
        output_list.push_back(wire_results[stoi(c_tokens[i])]);
      }
      continue;
    } else {
      cout << "Unknown line format" << endl;
    }
  }

  c_file.close();
  p_file.close();
}

vector<bool> initialize_inputs(string filename) {
  const char *filen = filename.c_str();
  ifstream file;
  file.open(filen);

  bool bit;
  string line;
  vector<string> tokens;
  vector<bool> input_list;

  while (getline(file, line)) {
    if (line != "") {
      tokenize(line, tokens);
      if (tokens[1] == "input") {
        bit = (0 == (rand() % 2));
        input_list.push_back(bit);
      }
    }
  }
  file.close();
  return input_list;
}
