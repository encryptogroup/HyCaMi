ALL += a_and_b.shdl a_or_b.shdl not_a_and_not_b.shdl a_and_not_b.shdl not_a_and_b.shdl

all: $(ALL)

.PRECIOUS: %.blif
%.blif: simple.v yosys_script.ys.in
	sed "s/@VERILOG_FILE@/$</;s/@TOP_MODULE@/$(patsubst %.blif,%,$@)/;s/@BLIF_FILE@/$@/" yosys_script.ys.in > $(patsubst %.v,yosys_script_%.ys,$<)
	yosys -s $(patsubst %.v,yosys_script_%.ys,$<)

.PRECIOUS: %.bench
%.bench: %.blif abc_script.abc.in
	sed "s/@BLIF_FILE@/$</;s/@BENCH_FILE@/$@/" abc_script.abc.in > $(patsubst %.blif,abc_script_%.abc,$<)
	yosys-abc -f $(patsubst %.blif,abc_script_%.abc,$<)

%.shdl: %.bench
	../Bench2SHDL/Bench2SHDL $<
	mv $(patsubst %.bench,%.bench_SHDL,$<) $@
	sed -i 's/ output / /' $@

clean:
	rm -f *.blif *.bench *.shdl abc_script_*.abc yosys_script_*.ys

.PHONY: all clean
