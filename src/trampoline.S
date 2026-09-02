.global Call_IOS_Open
.type Call_IOS_Open, @function
Call_IOS_Open:
    stwu 1, -32(1)
    mflr 0
    stw 0, 24(1)
    lis 12, 0x802B
    ori 12, 12, 0x9D90
    mtctr 12
    bctrl
    lwz 0, 24(1)
    mtlr 0
    addi 1, 1, 32
    blr

.global Call_IOS_Close
.type Call_IOS_Close, @function
Call_IOS_Close:
    stwu 1, -32(1)
    mflr 0
    stw 0, 24(1)
    lis 12, 0x802B
    ori 12, 12, 0x9E60
    mtctr 12
    bctrl
    lwz 0, 24(1)
    mtlr 0
    addi 1, 1, 32
    blr

.global Call_IOS_Ioctlv
.type Call_IOS_Ioctlv, @function
Call_IOS_Ioctlv:
    stwu 1, -32(1)
    mflr 0
    stw 0, 24(1)
    lis 12, 0x802B
    ori 12, 12, 0xA200
    mtctr 12
    bctrl
    lwz 0, 24(1)
    mtlr 0
    addi 1, 1, 32
    blr

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

.global M1_Wrapper
.type M1_Wrapper, @function
M1_Wrapper:
#if ENABLE_SENSOR_FLASH
    stwu 1, -64(1)
    mflr 0
    stw 0, 68(1)
    stw 3, 16(1)
    stw 4, 20(1)
    stw 5, 24(1)

    lis 4, flag_m1@h
    ori 4, 4, flag_m1@l
    lwz 5, 0(4)
    cmpwi 5, 0
    bne m1_skip
    li 5, 1
    stw 5, 0(4)

    li 3, 1
    bl Blink_Milestone

m1_skip:
    lwz 0, 68(1)
    mtlr 0
    lwz 3, 16(1)
    lwz 4, 20(1)
    lwz 5, 24(1)
    addi 1, 1, 64
#endif
    # Call original target 0x8027EB70 and return
    lis 12, 0x8027
    ori 12, 12, 0xEB70
    mtctr 12
    bctr

.global M2_Wrapper
.type M2_Wrapper, @function
M2_Wrapper:
#if ENABLE_SENSOR_FLASH
    stwu 1, -64(1)
    mflr 0
    stw 0, 68(1)
    stw 3, 16(1)
    stw 4, 20(1)
    stw 5, 24(1)

    lis 4, flag_m2@h
    ori 4, 4, flag_m2@l
    lwz 5, 0(4)
    cmpwi 5, 0
    bne m2_skip
    li 5, 1
    stw 5, 0(4)

    li 3, 2
    bl Blink_Milestone

m2_skip:
    lwz 0, 68(1)
    mtlr 0
    lwz 3, 16(1)
    lwz 4, 20(1)
    lwz 5, 24(1)
    addi 1, 1, 64
#endif
    # Execute original instruction at 0x80004170 (lis r4, 0x8000)
    lis 4, 0x8000
    # Branch to 0x80004174
    lis 12, 0x8000
    ori 12, 12, 0x4174
    mtctr 12
    bctr

.global M3_Wrapper
.type M3_Wrapper, @function
M3_Wrapper:
#if ENABLE_SENSOR_FLASH
    stwu 1, -64(1)
    mflr 0
    stw 0, 68(1)
    stw 3, 16(1)
    stw 4, 20(1)
    stw 5, 24(1)

    lis 4, flag_m3@h
    ori 4, 4, flag_m3@l
    lwz 5, 0(4)
    cmpwi 5, 0
    bne m3_skip
    li 5, 1
    stw 5, 0(4)

    li 3, 3
    bl Blink_Milestone

m3_skip:
    lwz 0, 68(1)
    mtlr 0
    lwz 3, 16(1)
    lwz 4, 20(1)
    lwz 5, 24(1)
    addi 1, 1, 64
#endif
    # Branch to Hook_MainTrace_Trampoline
    lis 12, Hook_MainTrace_Trampoline@h
    ori 12, 12, Hook_MainTrace_Trampoline@l
    mtctr 12
    bctr

.global Blink_Milestone
.type Blink_Milestone, @function
Blink_Milestone:
#if ENABLE_SENSOR_FLASH
    stwu 1, -64(1)
    mflr 0
    stw 0, 68(1)
    stw 3, 16(1)
    stw 4, 20(1)
    stw 5, 24(1)
    stw 6, 28(1)
    stw 7, 32(1)
    stw 8, 36(1)
    
    mr 8, 3
    cmpwi 8, 0
    ble bm_end
    
    bl TurnOff_Sensor
    bl Delay3_0s
    
bm_loop:
    bl TurnOn_Sensor
    bl Delay0_6s
    bl TurnOff_Sensor
    bl Delay0_6s
    
    subi 8, 8, 1
    cmpwi 8, 0
    bgt bm_loop
    
    bl Delay3_0s
    
bm_end:
    lwz 3, 16(1)
    lwz 4, 20(1)
    lwz 5, 24(1)
    lwz 6, 28(1)
    lwz 7, 32(1)
    lwz 8, 36(1)
    lwz 0, 68(1)
    mtlr 0
    addi 1, 1, 64
#endif
    blr

.global Blink_Error
.type Blink_Error, @function
Blink_Error:
#if ENABLE_SENSOR_FLASH
    stwu 1, -64(1)
    mflr 0
    stw 0, 68(1)
    stw 3, 16(1)
    stw 4, 20(1)
    stw 5, 24(1)
    stw 6, 28(1)
    stw 7, 32(1)
    stw 8, 36(1)
    
    li 8, 20
be_loop:
    bl TurnOn_Sensor
    bl Delay0_1s
    bl TurnOff_Sensor
    bl Delay0_1s
    subi 8, 8, 1
    cmpwi 8, 0
    bgt be_loop
    
    lwz 3, 16(1)
    lwz 4, 20(1)
    lwz 5, 24(1)
    lwz 6, 28(1)
    lwz 7, 32(1)
    lwz 8, 36(1)
    lwz 0, 68(1)
    mtlr 0
    addi 1, 1, 64
#endif
    blr

#if ENABLE_SENSOR_FLASH
TurnOff_Sensor:
    lis 4, 0xCD80
    ori 4, 4, 0x00C0
    lwz 5, 0(4)
    lis 6, 0xFFFF
    ori 6, 6, 0xFEFF
    and 5, 5, 6
    stw 5, 0(4)
    blr
    
TurnOn_Sensor:
    lis 4, 0xCD80
    ori 4, 4, 0x00C0
    lwz 5, 0(4)
    ori 5, 5, 0x0100
    stw 5, 0(4)
    blr
    
Delay0_1s:
    lis 6, 0x0200
    ori 6, 6, 0x0000
    li 7, 0
d01s:
    addi 7, 7, 1
    cmpw 7, 6
    blt d01s
    blr

Delay0_6s:
    lis 6, 0x0900
    ori 6, 6, 0x0000
    li 7, 0
d06s:
    addi 7, 7, 1
    cmpw 7, 6
    blt d06s
    blr
    
Delay3_0s:
    lis 6, 0x2C00
    ori 6, 6, 0x0000
    li 7, 0
d30s:
    addi 7, 7, 1
    cmpw 7, 6
    blt d30s
    blr

.section .bss
.align 4
flag_m1: .long 0
flag_m2: .long 0
flag_m3: .long 0
flag_m4: .long 0
flag_m5: .long 0
#endif

