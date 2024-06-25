#!/usr/bin/env python

import io
import re
import sys

import metadata_output_pb2

indent = "  "
wire_type = "uint32_t"

if len(sys.argv) < 5 or len(sys.argv) > 6:
    print(f"Usage: {sys.argv[0]} [shdl circuit] [metadata protobuf] [output c source] [output header] [original c source]")
    exit(1)

shdl_path = sys.argv[1]
metadata_path = sys.argv[2]
output_c_path = sys.argv[3]
output_h_path = sys.argv[4]
original_c_path = None if len(sys.argv) < 6 else sys.argv[5]

out_fn = io.StringIO()
out_tts = io.StringIO()
signature = io.StringIO()
prologue = io.StringIO()
epilogue = io.StringIO()
additional_headers = io.StringIO()

metadata = metadata_output_pb2.MetadataOutput()
with open(metadata_path, 'rb') as f:
    metadata.ParseFromString(f.read())

top_fn_proto = metadata.top_func_proto
return_type = top_fn_proto.return_type
params = top_fn_proto.params


# --- parse additional headers ---

if original_c_path:
    with open(original_c_path) as f:
        for line in f.readlines():
            if line.startswith("#include"):
                additional_headers.write(line)


# --- signature generation ---

def proto_type_to_c_type(proto_type):
    if proto_type.HasField("as_int"):
        return ("" if proto_type.as_int.is_signed else "u") + f"int{proto_type.as_int.width}_t"
    if proto_type.HasField("as_inst"):
        return f"struct {proto_type.as_inst.name.name}";
    if proto_type.HasField("as_array"):
        element_type = proto_type_to_c_type(proto_type.as_array.element_type)
        return f"{element_type}"
    else:
        raise RuntimeError(f"proto_type_to_c_type: add support for {proto_type}")

# return type
signature.write(proto_type_to_c_type(return_type))
signature.write(" ")

# fn name
signature.write(top_fn_proto.name.fully_qualified_name)

# parameters
params_c_list = [None] * len(params)
for i, p in enumerate(params):
    if p.type.HasField("as_array"):
        params_c_list[i] = "const " + proto_type_to_c_type(p.type) + " " + p.name + f"[{p.type.as_array.size}]"
    else:
        params_c_list[i] = "const " + proto_type_to_c_type(p.type) + " " + p.name
params_c = ", ".join(params_c_list)
signature.write(f"({params_c})")


# --- glue code generation ---

def struct_fields(struct_id):
    for struct in metadata.structs:
        if struct.as_struct.name.as_inst.name.id == struct_id:
            return struct.as_struct.fields
    raise RuntimeError(f"struct with id {struct_id} not found")

def unpack_type(first_wire_number, proto_type, name, out):
    if proto_type.HasField("as_int"):
        for i in range(proto_type.as_int.width):
            wire_number = first_wire_number + i
            mask = "0b1" + "0" * i
            out.write(f"{indent}{wire_type} wire_{wire_number} = ({name} & {mask}) != 0;\n")
        return proto_type.as_int.width
    if proto_type.HasField("as_inst"):
        wire_number = first_wire_number
        struct_id = proto_type.as_inst.name.id
        for field in reversed(struct_fields(struct_id)):
            wire_number += unpack_type(wire_number, field.type, f"{name}.{field.name}", out)
        return wire_number - first_wire_number
    if proto_type.HasField("as_array"):
        element_type = proto_type.as_array.element_type
        size = proto_type.as_array.size
        wire_number = first_wire_number
        for i in range(size):
            wire_number += unpack_type(wire_number, element_type, f"{name}[{i}]", out)
        return wire_number - first_wire_number
    else:
        raise RuntimeError(f"unpack_type: add support for {proto_type}")

def pack_type(wire_numbers, first_index_into_wire_numbers, proto_type, name, out, depth=0):
    type_name = proto_type_to_c_type(proto_type)
    if proto_type.HasField("as_int"):
        if depth == 0:
            out.write(f"{indent}{type_name} {name} = 0;\n")

        for i in range(proto_type.as_int.width):
            wire_number = wire_numbers[first_index_into_wire_numbers + i]
            out.write(f"{indent}{name} |= (wire_{wire_number} << {i});\n")
        return proto_type.as_int.width
    if proto_type.HasField("as_inst"):
        if depth == 0:
            out.write(f"{indent}{type_name} {name} = {{0}};\n")

        index_into_wire_numbers = first_index_into_wire_numbers
        struct_id = proto_type.as_inst.name.id
        for field in reversed(struct_fields(struct_id)):
            index_into_wire_numbers += pack_type(wire_numbers, index_into_wire_numbers, field.type, f"{name}.{field.name}", out, depth + 1)
        return index_into_wire_numbers - first_index_into_wire_numbers
    if proto_type.HasField("as_array"):
        if depth == 0:
            out.write(f"{indent}{type_name} {name}[{proto_type.as_array.size}] = {{0}};\n");

        element_type = proto_type.as_array.element_type
        size = proto_type.as_array.size
        index_into_wire_numbers = first_index_into_wire_numbers
        for i in range(size):
            index_into_wire_numbers += pack_type(wire_numbers, index_into_wire_numbers, element_type, f"{name}[{i}]", out, depth + 1)
        return index_into_wire_numbers - first_index_into_wire_numbers
    else:
        raise RuntimeError(f"pack_type: add support for {proto_type}")

# prologue
wire_number = 0
for p in params:
    wire_number += unpack_type(wire_number, p.type, p.name, prologue)

with open(shdl_path) as shdl_circuit:
    count = 0
    for line in shdl_circuit:
        elements = re.split(r"\s*[=,()\n\s\[\]]\s*", line)
        elements = list(filter(lambda x: x != "", elements))

        if "outputs" in elements:
            # epilogue
            pack_type(list(map(int, elements[1:])), 0, return_type, "result", epilogue)
            epilogue.write(f"{indent}return result;\n")

        if "gate" in elements:
            num_inputs = int(elements[elements.index("arity") + 1])
            num_outputs = int(elements.index("gate"))

            out_fn.write(f"{indent}struct out{num_outputs}_t out_{count} = ")
            out_fn.write(f"lut_{num_inputs}_to_{num_outputs}(")

            # parameters
            out_fn.write(f"truth_table_{count}, ")

            # insert input bits
            args = ", ".join([f"wire_{i}" for i in elements[-num_inputs:]])
            out_fn.write(args)

            out_fn.write(");\n")

            # unpack output bits
            for i in range(num_outputs):
                output_wire_number = int(elements[i])
                out_fn.write(f"{indent}{wire_type} wire_{output_wire_number} = out_{count}.o{i};\n")

            out_fn.write("\n")

            # write truth table

            out_tts.write(f"static uint8_t truth_table_{count}[] = {{")

            begin_tt_index = elements.index("table") + 1
            num_tt_entries = 2 ** num_inputs
            tt = [None] * num_outputs
            for i in range(num_outputs):
                tt[i] = [0] * num_tt_entries
                for j in range(num_tt_entries):
                    tt[i][j] = elements[begin_tt_index + i * num_tt_entries + j]

            # https://datagy.io/python-transpose-list-of-lists/
            tt = reversed(tt)
            transposed_tuples = list(zip(*tt))
            transposed_tt = [list(sublist) for sublist in transposed_tuples]

            byte_literals = []
            for i, tt in enumerate(transposed_tt):
                if i % 64 == 0 and i > 0:
                    byte_literals += ["0"] * (4096 - 64)

                joined = "".join(tt).zfill(8)
                byte_literal = "0b" + joined
                byte_literals.append(byte_literal)

            out_tts.write(", ".join(byte_literals))
            out_tts.write("};\n")

        count += 1

with open(output_c_path, 'w') as f:
    f.write(f"#include \"{output_h_path}\"\n");
    f.write(f"#include \"luts.h\"\n");

    f.write(out_tts.getvalue())

    f.write(signature.getvalue())
    f.write(" {\n")
    f.write(prologue.getvalue())
    f.write(out_fn.getvalue())
    f.write(epilogue.getvalue())
    f.write("}\n")

with open(output_h_path, 'w') as f:
    f.write("#include <stdint.h>\n");
    f.write(additional_headers.getvalue())
    f.write(signature.getvalue())
    f.write(";\n")
