.global Hook_MainEntry
.type Hook_MainEntry, @function
Hook_MainEntry:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    bl Hook_EarlyMain
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    blr

.global Hook_CP1
Hook_CP1:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    bl Hook_Checkpoint_1
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    li 3, 0
    blr

.global Hook_MainTrace_Trampoline
.type Hook_MainTrace_Trampoline, @function
Hook_MainTrace_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    addi 3, 1, 112
    addi 4, 1, 116
    bl Hook_MainTrace
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    stwu 1, -32(1)
    lis 12, 0x8018
    ori 12, 12, 0xDC8C
    mtctr 12
    bctr

.global Hook_Trace_DCA4_Trampoline
.type Hook_Trace_DCA4_Trampoline, @function
Hook_Trace_DCA4_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    bl Hook_Trace_DCA4
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    lis 12, 0x8012
    ori 12, 12, 0x6D2C
    mtctr 12
    bctr

.global Hook_Trace_DCAC_Trampoline
.type Hook_Trace_DCAC_Trampoline, @function
Hook_Trace_DCAC_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    bl Hook_Trace_DCAC
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    lis 12, 0x8016
    ori 12, 12, 0x923C
    mtctr 12
    bctr

.global Hook_Trace_DCD8_Trampoline
.type Hook_Trace_DCD8_Trampoline, @function
Hook_Trace_DCD8_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    bl Hook_Trace_DCD8
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    lis 12, 0x8012
    ori 12, 12, 0x4650
    mtctr 12
    bctr

.global Hook_Trace_E1F4_Trampoline
.type Hook_Trace_E1F4_Trampoline, @function
Hook_Trace_E1F4_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    stw 5, 120(1)
    bl Hook_Trace_E1F4
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 5, 120(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    stwu 1, -48(1)
    lis 12, 0x8018
    ori 12, 12, 0xE1F8
    mtctr 12
    bctr

.global Hook_Trace_1954_Trampoline
.type Hook_Trace_1954_Trampoline, @function
Hook_Trace_1954_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    bl Hook_Trace_1954
    lwz 3, 112(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    stwu 1, -32(1)
    lis 12, 0x8015
    ori 12, 12, 0x1958
    mtctr 12
    bctr

.global Hook_Trace_ZipMount_Trampoline
.type Hook_Trace_ZipMount_Trampoline, @function
Hook_Trace_ZipMount_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    stw 5, 120(1)
    bl Hook_Trace_ZipMount
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 5, 120(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    stwu 1, -32(1)
    lis 12, 0x8015
    ori 12, 12, 0x81FC
    mtctr 12
    bctr

.global Hook_Trace_FileDevice_Ctor_Trampoline
.type Hook_Trace_FileDevice_Ctor_Trampoline, @function
Hook_Trace_FileDevice_Ctor_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    bl Hook_Trace_FileDevice_Ctor
    lwz 3, 112(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    stwu 1, -16(1)
    lis 12, 0x8015
    ori 12, 12, 0x782C
    mtctr 12
    bctr

.global Orig_DVDConvertPathToEntrynum
.type Orig_DVDConvertPathToEntrynum, @function
Orig_DVDConvertPathToEntrynum:
    stwu 1, -48(1)
    lis 12, 0x8028
    ori 12, 12, 0xB3B4
    mtctr 12
    bctr

.global Orig_DVDFastOpen
.type Orig_DVDFastOpen, @function
Orig_DVDFastOpen:
    cmpwi 3, 0
    lis 12, 0x8028
    ori 12, 12, 0xB6C4
    mtctr 12
    bctr

.global Orig_DVDOpen
.type Orig_DVDOpen, @function
Orig_DVDOpen:
    stwu 1, -144(1)
    lis 12, 0x8028
    ori 12, 12, 0xB734
    mtctr 12
    bctr

.global Orig_DVDReadAsyncPrio
.type Orig_DVDReadAsyncPrio, @function
Orig_DVDReadAsyncPrio:
    stwu 1, -32(1)
    lis 12, 0x8028
    ori 12, 12, 0xB9A4
    mtctr 12
    bctr

.global Orig_DVDClose
.type Orig_DVDClose, @function
Orig_DVDClose:
    stwu 1, -16(1)
    lis 12, 0x8028
    ori 12, 12, 0xB854
    mtctr 12
    bctr

.global Hook_Trace_Start_InitUser_Trampoline
.type Hook_Trace_Start_InitUser_Trampoline, @function
Hook_Trace_Start_InitUser_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    bl Hook_Trace_Start_InitUser
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    lis 12, 0x8028
    ori 12, 12, 0x1430
    mtctr 12
    bctr

.global Hook_Trace_Start_Main_Trampoline
.type Hook_Trace_Start_Main_Trampoline, @function
Hook_Trace_Start_Main_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 3, 112(1)
    stw 4, 116(1)
    bl Hook_Trace_Start_Main
    lwz 3, 112(1)
    lwz 4, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    lis 12, 0x8018
    ori 12, 12, 0xDC88
    mtctr 12
    bctr

.global Hook_Ctor_Trampoline
.type Hook_Ctor_Trampoline, @function
Hook_Ctor_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    stw 12, 112(1)
    stw 31, 116(1)
    
    mr 3, 12
    lis 4, 0x8040
    ori 4, 4, 0x5820
    subf 4, 4, 31
    srawi 4, 4, 2
    
    bl Hook_Ctor_Trace
    
    lwz 12, 112(1)
    lwz 31, 116(1)
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    
    mtctr 12
    bctr

.global Hook_Trace_OSInit_Done_Trampoline
.type Hook_Trace_OSInit_Done_Trampoline, @function
Hook_Trace_OSInit_Done_Trampoline:
    stwu 1, -128(1)
    mflr 0
    stw 0, 132(1)
    bl Hook_Trace_OSInit_Done
    lwz 0, 132(1)
    mtlr 0
    addi 1, 1, 128
    addis 4, 0, -32768
    blr

.global Hook_Safe_Memcpy
.type Hook_Safe_Memcpy, @function
Hook_Safe_Memcpy:
    lis 12, 0x8000
    cmplw 3, 12
    bge 1f
    lis 12, 0x0C00
    cmplw 3, 12
    blt 11f
    lis 12, 0x0E00
    cmplw 3, 12
    bge 11f
    oris 3, 3, 0xC000
    b 1f
11:
    oris 3, 3, 0x8000
1:
    lis 12, 0x8000
    cmplw 4, 12
    bge 2f
    lis 12, 0x0C00
    cmplw 4, 12
    blt 21f
    lis 12, 0x0E00
    cmplw 4, 12
    bge 21f
    oris 4, 4, 0xC000
    b 2f
21:
    oris 4, 4, 0x8000
2:
    cmplwi 1, 5, 0
    lis 12, 0x8000
    ori 12, 12, 0x43C8
    mtctr 12
    bctr

.global Hook_Safe_Memset
.type Hook_Safe_Memset, @function
Hook_Safe_Memset:
    lis 12, 0x8000
    cmplw 3, 12
    bge 1f
    lis 12, 0x0C00
    cmplw 3, 12
    blt 11f
    lis 12, 0x0E00
    cmplw 3, 12
    bge 11f
    oris 3, 3, 0xC000
    b 1f
11:
    oris 3, 3, 0x8000
1:
    cmplwi 5, 32
    lis 12, 0x8000
    ori 12, 12, 0x4664
    mtctr 12
    bctr
