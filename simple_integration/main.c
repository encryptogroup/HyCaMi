#include <stdint.h>
#include <stdio.h>

uint32_t add32(uint32_t a, uint32_t b);

void main() {
  const uint32_t a = 0xdeadbeef;
  const uint32_t b = 0xcafebabe;

  printf("%x + %x = %x\n", a, b, a + b);
  printf("add32(%x, %x) = %x\n", a, b, add32(a, b));
}
