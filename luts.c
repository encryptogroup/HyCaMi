#include <stdint.h>

struct out8_t {
  int8_t o0;
  int8_t o1;
  int8_t o2;
  int8_t o3;
  int8_t o4;
  int8_t o5;
  int8_t o6;
  int8_t o7;
};

// roughly 66 instructions
struct out8_t lut_8_to_8(uint32_t i0, uint32_t i1, uint32_t i2, uint32_t i3,
                         uint32_t i4, uint32_t i5, uint32_t i6, uint32_t i7) {

  // 8 to 8 LUT = 256 bytes =  4 * 64 byte
  // 32 KiB / 8-way associative cache / 64 byte line size / 64 cache sets (e.g.
  // Intel Coffee lake L1D Cache)
  uint8_t lut[32768];

  struct out8_t ret;

  // 21 instructions
  uint32_t addr =
      i0 | i1 << 1 | i2 << 2 | i3 << 3 | i4 << 4 | i5 << 5 | i6 << 6 | i7 << 7;

  // 4 instructions
  addr = ((addr >> 6) * 4096) + (addr % 64);

  // 1 instruction
  uint8_t out = lut[addr];

  // 4 instructions each = 32 instructions
  ret.o0 = out & 0b1;
  ret.o1 = (out & 0b10) > 1;
  ret.o2 = (out & 0b100) > 2;
  ret.o3 = (out & 0b1000) > 3;
  ret.o4 = (out & 0b10000) > 4;
  ret.o5 = (out & 0b100000) > 5;
  ret.o6 = (out & 0b1000000) > 6;
  ret.o7 = (out & 0b10000000) > 7;

  return ret;
}

// 57 instructions
struct out8_t lut_8_to_8_leaky(uint32_t i0, uint32_t i1, uint32_t i2,
                               uint32_t i3, uint32_t i4, uint32_t i5,
                               uint32_t i6, uint32_t i7) {
  // 256 bytes = 4 * 64 byte
  uint8_t lut[256];

  struct out8_t ret;

  // 21 instructions
  uint32_t addr =
      i0 | i1 << 1 | i2 << 2 | i3 << 3 | i4 << 4 | i5 << 5 | i6 << 6 | i7 << 7;

  // 1 instruction
  // ATTENTION: this leaks
  uint8_t out = lut[addr];

  // 4 instructions each = 32 instructions
  ret.o0 = out & 0b1;
  ret.o1 = (out & 0b10) > 1;
  ret.o2 = (out & 0b100) > 2;
  ret.o3 = (out & 0b1000) > 3;
  ret.o4 = (out & 0b10000) > 4;
  ret.o5 = (out & 0b100000) > 5;
  ret.o6 = (out & 0b1000000) > 6;
  ret.o7 = (out & 0b10000000) > 7;

  return ret;
}

// 28 instructions
uint32_t lut_8_to_1(uint32_t i0, uint32_t i1, uint32_t i2, uint32_t i3,
                    uint32_t i4, uint32_t i5, uint32_t i6, uint32_t i7) {

  // 2^8 bits = 256 bits = 32 byte
  uint8_t lut[32];

  // 21 instructions
  uint32_t addr =
      i0 | i1 << 1 | i2 << 2 | i3 << 3 | i4 << 4 | i5 << 5 | i6 << 6 | i7 << 7;

  // 1 instruction
  addr = addr / 8;

  // 1 instruction
  uint32_t out = lut[addr];

  return out >> (addr % 8);
}
