#!/usr/bin/env python

import sys
import os

max_lut_in = 8
max_lut_out = 8

indent = "  "
lut_input_type = "uint32_t"
lut_output_type = "uint8_t"

if len(sys.argv) != 3:
    print(f"Usage: {sys.argv[0]} [include directory] [output source]")
    exit(1)

output_h_path = os.path.join(sys.argv[1], "luts.h")
output_c_path = sys.argv[2]

with open(output_h_path, 'w') as f:
    f.write(f"/** Generated by {sys.argv[0]} **/\n\n")

    # struct defs
    for lut_out_size in range(1, max_lut_out + 1):
        f.write(f"struct out{lut_out_size}_t {{\n")

        for i in range(lut_out_size):
            f.write(f"{indent}{lut_output_type} o{i};\n")

        f.write("};\n\n")

    for lut_in_size in range(1, max_lut_in + 1):
        for lut_out_size in range(1, max_lut_out + 1):
            # return type
            f.write(f"struct out{lut_out_size}_t ")

            # fn name
            f.write(f"lut_{lut_in_size}_to_{lut_out_size}(")

            # parameters
            params = [None] * lut_in_size
            for i in range(lut_in_size):
                params[i] = f"{lut_input_type} i{i}"
            f.write(", ".join(["uint8_t* truth_table"] + params))

            f.write(f");\n\n")

        f.write("\n");

with open(output_c_path, 'w') as f:
    f.write(f"/** Generated by {sys.argv[0]} **/\n\n")
    f.write(f"#include <stdint.h>\n")
    f.write(f"#include \"luts.h\"\n\n")

    for lut_in_size in range(1, max_lut_in + 1):
        for lut_out_size in range(1, max_lut_out + 1):
            # return type
            f.write(f"struct out{lut_out_size}_t ")

            # fn name
            f.write(f"lut_{lut_in_size}_to_{lut_out_size}(")

            # parameters
            params = [None] * lut_in_size
            for i in range(lut_in_size):
                params[i] = f"{lut_input_type} i{i}"
            f.write(", ".join(["uint8_t* truth_table"] + params))

            # function body
            f.write(f") {{\n")

            f.write(f"{indent}struct out{lut_out_size}_t ret;\n")

            addr = " | ".join(["i0"] + [f"i{x} << {x}" for x in range(1, lut_in_size)])
            f.write(f"{indent}uint32_t addr = {addr};\n")

            f.write(f"{indent}addr = ((addr >> 6) * 4096) + (addr % 64);\n")

            f.write(f"{indent}uint8_t out = truth_table[addr];\n")

            f.write(f"{indent}ret.o0 = out & 0b1;\n")
            for i in range(1, lut_out_size):
                zeros = "0" * i
                f.write(f"{indent}ret.o{i} = (out & 0b1{zeros}) > 0;\n")

            f.write(f"{indent}return ret;\n")

            f.write("}\n\n")

        f.write("\n");