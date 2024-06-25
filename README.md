# HyCaMi

### HyCaMi: High-Level Synthesis for Cache Side-Channel Mitigation

By *Heiko Mantel¹, Joachim Schmidt², Thomas Schneider², Maximilian Stillger², Tim Weißmantel¹, Hossein Yalame²*
(¹[ENCRYPTO, TU Darmstadt](https://www.encrypto.de/) ²[MAIS, TU Darmstadt](https://www.mais.informatik.tu-darmstadt.de/))
in [Design Automation Conference (DAC'24)](https://61dac.conference-program.com/presentation/?id=RESEARCH1936&sess=sess156).
[Paper available here.](https://encrypto.de/papers/MSSSWY24.pdf)

## Structure

This repository contains code and artifacts for reproducing our
results.

- GitHub releases
  - XLS High-Level Synthesis toolchain
  - CacheAudit v0.3
  - Unhardened and hardened block cipher source and binaries
  - Intermediate circuit files and C source artifacts
  - Analysis data spreadsheets
- Repository
  - Hardening workflow
  - LUT merging
  - LUT2C

## Instructions

1. Setup
2. Executing hardening workflow
3. Postprocessing and optimization of hardened C source
4. Compilation of resulting C source
5. Static side-channel analysis

### Setup

Download and extract the artifacts from the [release
page](https://github.com/encryptogroup/HyCaMi/releases).

```bash
sudo apt install build-essential yosys python3
make -C Bench2SHDL
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Executing hardening workflow

This part of the workflow prepares circuits by compiling C code to a hardened C code.

```bash
# Evaluation/Comparison-RiCaSi-1.0 can be the path of the extracted release archive
cd Evaluation/Comparison-RiCaSi-1.0/cross_library_aes/2-Compilation/openssl
make -C src -f Makefile.Te
```

### Postprocessing

```bash
python ../../inline.py src/Te0_f_lut6a_mo.c
make openssl-aes-wrapper-enc-Te
```

### Analysis

Now we can perform two independent analysis.

#### Side-Channel Analysis

```bash
cd ../4-Side-Channel-Analysis-Of-Protected-Code/openssl/
make analysis
```

#### Correctness Check

```bash
cd ../3-Functional-Correctness/openssl/
python test.py
```

## Disclaimer

This code is experimental and should not be used in production. We do
not provide security guarantees.
