# Convert the Yosys Bench Format to the Bristol MPC Format by Smart et al.
import sys
import re

filename = str(sys.argv[1])
resultfilename = str(sys.argv[2])
f = open(filename, "r")
g = open(resultfilename, "w")
inputs = []
outputs = []
gates = []
wire_mapping = {}
wire_number = 1

lines = []
num_outputs = 0
num_gates = 0
num_inputs = 0
for l in f:
    if not l.startswith("#"):
        lines.append(l)
    if l.startswith("INPUT"):
        num_inputs = num_inputs + 1
    if l.startswith("OUTPUT"):
        num_outputs = num_outputs + 1
    else:
        gate = l.split()
        if not "LUT" in gate:
            continue
        num_gates = num_gates + 1


output_count = 1
for l in lines:
    if l.startswith("INPUT"):
        input_wire = l[6:-2]
        wire_mapping[input_wire] = wire_number
        inputs.append(input_wire)
        wire_number = wire_number + 1
    elif l.startswith("OUTPUT"):
        wire_mapping[l[7:-2]] = num_gates + num_inputs - num_outputs + output_count
        output_count = output_count + 1
    else:
        gate = l.split()
        if not "LUT" in gate:
            continue
        gatetype = gate[3]
        gatestring = ""

        if not gate[0] in wire_mapping:
            wire_mapping[gate[0]] = wire_number
            wire_number = wire_number + 1
        if len(gate) > 7:
            if gatetype == "0xe":
                gatestring = "OR"
            elif gatetype == "0x6":
                gatestring = "XOR"
            elif gatetype == "0x1":
                gatestring = "NOR"
            elif gatetype == "0x8":
                gatestring = "AND"
            else:
                print("Unknown gatetype: " + str(gatetype))

            a = str(wire_mapping[(gate[5])[:-1]])
            b = str(wire_mapping[gate[6]])
            gates.append(
                "2 1 "
                + a
                + " "
                + b
                + " "
                + str(wire_mapping[gate[0]])
                + " "
                + gatestring
            )
        else:
            if gatetype == "0x1":
                gatestring = "NOT"
            elif gatetype == "0x2":
                gatestring = "BUF"
            else:
                print("Unknown gatetype: " + str(gatetype))

            gates.append(
                "1 1 "
                + str(wire_mapping[gate[5]])
                + " "
                + str(wire_mapping[gate[0]])
                + " "
                + gatestring
            )

        # print(l)
niv = str(len(inputs))
# currently the circuit has no information of the party for each input
g.write(str(len(gates)) + " " + str(len(wire_mapping)) + "\n")
g.write("1 " + niv + "\n")
g.write("1 " + str(num_outputs) + "\n")
g.write("\n")
for gate in gates:
    g.write(gate + "\n")
# print(inputs)
# print(outputs)
print("Adjusted format")
