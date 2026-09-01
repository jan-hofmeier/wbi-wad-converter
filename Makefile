DEVKITPRO ?= /opt/devkitpro
DEVKITPPC ?= $(DEVKITPRO)/devkitPPC

PPC_CC     = $(DEVKITPPC)/bin/powerpc-eabi-gcc
PPC_OBJCOPY= $(DEVKITPPC)/bin/powerpc-eabi-objcopy
HOST_CC   ?= gcc

ENABLE_SENSOR_FLASH ?= 0
CFLAGS = -O2 -Wall -m32 -mhard-float -meabi -mno-sdata -nostartfiles -nodefaultlibs -fno-builtin -fno-tree-loop-distribute-patterns -DENABLE_SENSOR_FLASH=$(ENABLE_SENSOR_FLASH)

.PHONY: all shim tools release wad clean

all: shim tools

shim: precompiled/dvd_nand_shim.bin

precompiled/dvd_nand_shim.bin: src/dvd_nand_shim.c src/trampoline.S src/shim.ld
	@mkdir -p precompiled
	$(PPC_CC) $(CFLAGS) -T src/shim.ld -Wl,-Map=precompiled/dvd_nand_shim.elf.map -o precompiled/dvd_nand_shim.elf src/dvd_nand_shim.c src/trampoline.S
	$(PPC_OBJCOPY) -O binary precompiled/dvd_nand_shim.elf $@
	@rm -f precompiled/dvd_nand_shim.elf
	@echo "[+] Generated precompiled/dvd_nand_shim.bin"

tools: tools/lz11_compress

tools/lz11_compress: src/lz11_compress.c
	@mkdir -p tools
	$(HOST_CC) -O3 src/lz11_compress.c -o $@
	@echo "[+] Generated tools/lz11_compress"

release:
	python3 build_release.py

wad: all
	@if [ -z "$(INPUT)" ] || [ -z "$(LOADER)" ]; then \
		echo "Usage: make wad INPUT=<path_to_wbfs_or_iso> LOADER=<path_to_nand_loader>"; \
		exit 1; \
	fi
	python3 convert.py -i "$(INPUT)" -l "$(LOADER)" -o "$(or $(OUTPUT),worms_bi.wad)"

clean:
	rm -rf build/ dist/ tools/ work_temp/ *.lz11 test_extract/
