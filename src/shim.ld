OUTPUT_FORMAT("elf32-powerpc", "elf32-powerpc", "elf32-powerpc")
OUTPUT_ARCH(powerpc:common)

ENTRY(Shim_ConvertPathToEntrynum)

SECTIONS
{
    . = 0x805B0000;

    .text : ALIGN(32) {
        *(.text .text.*)
        *(.rodata .rodata.*)
        *(.data .data.*)
        *(.sdata .sdata.*)
        *(.sbss .sbss.*)
        *(.bss .bss.*)
        *(COMMON)
    }

    /DISCARD/ : {
        *(.comment)
        *(.note*)
        *(.eh_frame)
    }
}
