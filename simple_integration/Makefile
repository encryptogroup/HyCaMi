XLS_BIN ?= /home/joachim/Downloads/bazel-bin
XLS_SRC ?= /home/joachim/src/xls-spfe-framework

XLSCC ?= $(XLS_BIN)/xls/contrib/xlscc/xlscc
IR_CONVERTER_MAIN ?= $(XLS_BIN)/xls/dslx/ir_converter_main
OPT_MAIN ?= $(XLS_BIN)/xls/tools/opt_main
CODEGEN_MAIN ?= $(XLS_BIN)/xls/tools/codegen_main

STDLIB_PATH ?= $(XLS_SRC)/xls/dslx/stdlib
DSLX_PATH ?= $(XLS_SRC):$(XLS_SRC)/xls

CFLAGS ?= -O3 -m32

ALL += main main-mod

all: $(ALL)

%.noopt.ir %.meta: internal.c clang_args.txt
	$(XLSCC) --top=$(patsubst %.noopt.ir,%,$@) --clang_args_file=clang_args.txt --meta_out=$(patsubst %.noopt.ir,%.meta,$@) internal.c > $@

.PRECIOUS: %.ir
%.ir: %.noopt.ir
	$(OPT_MAIN) $^ > $@

.PRECIOUS: %.v
%.v: %.ir
	$(CODEGEN_MAIN) --generator=combinational --use_system_verilog=false --output_verilog_path $@ $^

.PRECIOUS: %.blif
%.blif: %.v yosys_script.ys.in
	sed "s/@VERILOG_FILE@/$</;s/@TOP_MODULE@/$(patsubst %.v,%,$<)/;s/@BLIF_FILE@/$@/" yosys_script.ys.in > $(patsubst %.v,yosys_script_%.ys,$<)
	yosys -s $(patsubst %.v,yosys_script_%.ys,$<)

.PRECIOUS: %.bench
%.bench: %.blif abc_script.abc.in
	sed "s/@BLIF_FILE@/$</;s/@BENCH_FILE@/$@/" abc_script.abc.in > $(patsubst %.blif,abc_script_%.abc,$<)
	yosys-abc -f $(patsubst %.blif,abc_script_%.abc,$<)

.PRECIOUS: %.shdl
%.shdl: %.bench
	../Bench2SHDL/Bench2SHDL $<
	mv $(patsubst %.bench,%.bench_SHDL,$<) $@
	sed -i 's/ output / /' $@

%_lut8_mo.shdl: %.shdl
	python ../multi-input-output-conversion3.py $< $@ 8 1000000000 1000000000 8

luts.c:
	python ../generate_luts_helper.py . $@

add32.c: add32_lut8_mo.shdl luts.c
	python ../shdl2c.py $< add32.meta $@ $(patsubst %.c,%.h,$@)

main: main.c internal.c
	$(CC) $(CFLAGS) -o $@ $^

main-mod: main.c add32.c luts.c
	$(CC) $(CFLAGS) -o $@ $^

clean:
	rm -f *.ir *.meta *.v *.blif *.bench *.shdl abc_script_*.abc yosys_script_*.ys luts.c luts.h add32.c add32.h main main-mod

.PHONY: all clean
