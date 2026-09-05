/*
 * Worms Battle Islands - Full Asset Redirection Shim
 * Safe Aligned NAND On-Demand Loading Shim
 */

typedef signed int s32;
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
typedef unsigned long long u64;
typedef signed long long s64;
typedef unsigned long uintptr_t;
#define NULL ((void*)0)

#ifndef ENABLE_LOGGING
#define ENABLE_LOGGING 0
#endif

#if ENABLE_LOGGING
typedef void (*OSReport_t)(const char* fmt, ...);
#define fn_OSReport ((OSReport_t)0x80276100)
#define SHIM_LOG(...) fn_OSReport(__VA_ARGS__)
#else
#define fn_OSReport(...) ((void)0)
#define SHIM_LOG(...) ((void)0)
#endif

typedef struct DVDCommandBlock DVDCommandBlock;
typedef struct DVDFileInfo DVDFileInfo;
typedef void (*DVDCallback)(s32 result, DVDFileInfo* fileInfo);

struct DVDCommandBlock {
    DVDCommandBlock* next;
    DVDCommandBlock* prev;
    u32 command;
    s32 state;
    u32 offset;
    u32 length;
    void* addr;
    u32 currTransferNum;
    u32 transferredSize;
    void* cb;
    DVDCallback callback;
    void* userData;
};

struct DVDFileInfo {
    DVDCommandBlock cb;
    u32 startAddr;
    u32 length;
    DVDCallback callback;
};

#if ENABLE_SENSOR_FLASH
extern void Blink_Milestone(int n);
extern void Blink_Error(void);
#else
#define Blink_Milestone(n) ((void)0)
#define Blink_Error()      ((void)0)
#endif

/* Assembly Trampolines to Original Functions in main.dol */
extern s32 Orig_DVDConvertPathToEntrynum(const char* path);
extern s32 Orig_DVDFastOpen(s32 entrynum, DVDFileInfo* fileInfo);
extern s32 Orig_DVDOpen(const char* fileName, DVDFileInfo* fileInfo);
extern s32 Orig_DVDReadAsyncPrio(DVDFileInfo* fileInfo, void* addr, s32 length, s32 offset, DVDCallback callback, s32 prio);
extern s32 Orig_DVDClose(DVDFileInfo* fileInfo);

static inline int shim_strcmp(const char* s1, const char* s2) {
    while (*s1 && (*s1 == *s2)) {
        s1++;
        s2++;
    }
    return *(const unsigned char*)s1 - *(const unsigned char*)s2;
}

static inline void shim_memcpy(void* dst, const void* src, u32 n) {
    u8* d = (u8*)dst;
    const u8* s = (const u8*)src;
    while (n--) {
        *d++ = *s++;
    }
}

static inline int IsDVDDiscLoaded(void) {
    return 0;
}

#define VIRTUAL_ENTRY_BASE 100000
#define IS_VIRTUAL_ENTRY(e) ((e) >= VIRTUAL_ENTRY_BASE)
#define VIRTUAL_ADDR_FLAG 0x7F000000

typedef struct VirtualFileEntry {
    const char* path;
    u32 length;
    u32 offset;
    s32 origEntrynum;
    u32 origStartAddr;
} VirtualFileEntry;

static VirtualFileEntry s_FileTable[] = {
    { "DataWii/Audio/Atrac/Generic.spd", 10222796, 0x00000000, -1, 0 },
    { "DataWii/Audio/Atrac/Generic.spt", 152, 0x009BFD00, -1, 0 },
    { "DataWii/Audio/Banks/sfx/FE_Ambient.spd", 2640527, 0x009BFDC0, -1, 0 },
    { "DataWii/Audio/Banks/sfx/FE_Ambient.spt", 2076, 0x00C44880, -1, 0 },
    { "DataWii/Audio/Banks/sfx/FrontEnd.spd", 39887, 0x00C450C0, -1, 0 },
    { "DataWii/Audio/Banks/sfx/FrontEnd.spt", 522, 0x00C4ECC0, -1, 0 },
    { "DataWii/Audio/Banks/sfx/Game.spd", 1685760, 0x00C4EF00, -1, 0 },
    { "DataWii/Audio/Banks/sfx/Game.spt", 3778, 0x00DEA800, -1, 0 },
    { "DataWii/Audio/Banks/landscapeeditor.spd", 122848, 0x00DEB700, -1, 0 },
    { "DataWii/Audio/Banks/landscapeeditor.spt", 818, 0x00E09700, -1, 0 },
    { "DataWii/Audio/Banks/sfx/Misc.spd", 844772, 0x00E09A40, -1, 0 },
    { "DataWii/Audio/Banks/sfx/Misc.spt", 3038, 0x00ED7E40, -1, 0 },
    { "DataWii/Audio/Banks/speech/Area51.spd", 363822, 0x00ED8A40, -1, 0 },
    { "DataWii/Audio/Banks/speech/Area51.spt", 1854, 0x00F31780, -1, 0 },
    { "DataWii/Audio/Banks/speech/CrazedWarVet.spd", 360676, 0x00F31EC0, -1, 0 },
    { "DataWii/Audio/Banks/speech/CrazedWarVet.spt", 1854, 0x00F89FC0, -1, 0 },
    { "DataWii/Audio/Banks/speech/English.spd", 224683, 0x00F8A700, -1, 0 },
    { "DataWii/Audio/Banks/speech/English.spt", 1854, 0x00FC14C0, -1, 0 },
    { "DataWii/Audio/Banks/speech/French.spd", 201535, 0x00FC1C00, -1, 0 },
    { "DataWii/Audio/Banks/speech/French.spt", 1854, 0x00FF2F40, -1, 0 },
    { "DataWii/Audio/Banks/speech/German.spd", 201738, 0x00FF3680, -1, 0 },
    { "DataWii/Audio/Banks/speech/German.spt", 1854, 0x01024AC0, -1, 0 },
    { "DataWii/Audio/Banks/speech/GuerillaWarfare.spd", 331626, 0x01025200, -1, 0 },
    { "DataWii/Audio/Banks/speech/GuerillaWarfare.spt", 1854, 0x01076180, -1, 0 },
    { "DataWii/Audio/Banks/speech/Italian.spd", 234358, 0x010768C0, -1, 0 },
    { "DataWii/Audio/Banks/speech/Italian.spt", 1854, 0x010AFC40, -1, 0 },
    { "DataWii/Audio/Banks/speech/Jarhead.spd", 402743, 0x010B0380, -1, 0 },
    { "DataWii/Audio/Banks/speech/Jarhead.spt", 1854, 0x011128C0, -1, 0 },
    { "DataWii/Audio/Banks/speech/PresidentBush.spd", 555516, 0x01113000, -1, 0 },
    { "DataWii/Audio/Banks/speech/PresidentBush.spt", 1854, 0x0119AA00, -1, 0 },
    { "DataWii/Audio/Banks/speech/PreviewWii.spd", 155794, 0x0119B140, -1, 0 },
    { "DataWii/Audio/Banks/speech/PreviewWii.spt", 1040, 0x011C1200, -1, 0 },
    { "DataWii/Audio/Banks/speech/ReligiousSold.spd", 467310, 0x011C1640, -1, 0 },
    { "DataWii/Audio/Banks/speech/ReligiousSold.spt", 1854, 0x012337C0, -1, 0 },
    { "DataWii/Audio/Banks/speech/SecretAgent.spd", 423911, 0x01233F00, -1, 0 },
    { "DataWii/Audio/Banks/speech/SecretAgent.spt", 1854, 0x0129B700, -1, 0 },
    { "DataWii/Audio/Banks/speech/SecretMilitary.spd", 323506, 0x0129BE40, -1, 0 },
    { "DataWii/Audio/Banks/speech/SecretMilitary.spt", 1854, 0x012EAE00, -1, 0 },
    { "DataWii/Audio/Banks/speech/Spanish.spd", 233597, 0x012EB540, -1, 0 },
    { "DataWii/Audio/Banks/speech/Spanish.spt", 1854, 0x013245C0, -1, 0 },
    { "DataWii/Audio/Banks/speech/SpecialOps.spd", 295915, 0x01324D00, -1, 0 },
    { "DataWii/Audio/Banks/speech/SpecialOps.spt", 1854, 0x0136D100, -1, 0 },
    { "DataWii/BuildInfo.txt", 52, 0x0136D840, -1, 0 },
    { "DataWii/Default.cfg", 20, 0x0136D880, -1, 0 },
    { "DataWii/Modules.rso", 2478912, 0x0136D8C0, -1, 0 },
    { "DataWii/Video/T17.thp", 1906912, 0x015CAC00, -1, 0 },
    { "DataWii/Video/THQ.thp", 3766656, 0x0179C500, -1, 0 },
    { "DataWii/Video/ThpPlayerFiles/2nd_time.mid", 12103, 0x01B33E80, -1, 0 },
    { "DataWii/Video/ThpPlayerFiles/gm16adpcm.pcm", 881485, 0x01B36E00, -1, 0 },
    { "DataWii/Video/ThpPlayerFiles/gm16adpcm.wt", 193082, 0x01C0E180, -1, 0 },
    { "DataWii/Wow3.sel", 44736, 0x01C3D3C0, -1, 0 },
    { "DataWii/first.zip", 733221, 0x01C48280, -1, 0 },
    { "DataWii/frontend.zip", 4594145, 0x01CFB2C0, -1, 0 },
    { "DataWii/game.zip", 8604285, 0x0215CCC0, -1, 0 },
};
#define NUM_VIRTUAL_FILES 54

typedef struct ioctlv {
    void* data;
    u32 len;
} ioctlv;

typedef struct IPCCmd {
    u32 cmd;        /* 1 = Open, 2 = Close, 3 = Read, 4 = Write, 5 = Seek, 6 = Ioctl, 7 = Ioctlv */
    s32 result;     /* Return code from IOS */
    s32 fd;         /* File descriptor */
    union {
        struct { const char* path; u32 mode; } open;
        struct { void* data; u32 len; } read;
        struct { s32 where; s32 whence; } seek;
        struct { u32 ioctl; void* in; u32 in_len; void* out; u32 out_len; } ioctl;
        struct { u32 ioctl; u32 cnt_in; u32 cnt_out; ioctlv* vec; } ioctlv;
    };
} IPCCmd;

typedef s32 (*IOS_Open_t)(const char* path, u32 mode);
typedef s32 (*IOS_Close_t)(s32 fd);

#define fn_IOS_Open     ((IOS_Open_t)0x802B9D90)
#define fn_IOS_Close    ((IOS_Close_t)0x802AF110)

#define IOCTL_ES_OPENCONTENT  0x09
#define IOCTL_ES_READCONTENT  0x0A
#define IOCTL_ES_CLOSECONTENT 0x0B
#define IOCTL_ES_SEEKCONTENT  0x23

#define CONTENT2_TOTAL_SIZE   0x02992380U

/* Statically allocated 32-byte aligned ES structures to prevent stack corruption */
static u8 s_StaticEsBuf[64 * 1024] __attribute__((aligned(32)));
static char s_EsDevicePath[] __attribute__((aligned(32))) = "/dev/es";

/*
 * Cache management for PowerPC (Broadway):
 * dcbf (Data Cache Block Flush) flushes dirty cache lines to physical RAM AND invalidates
 * the cache line in L1/L2 cache. Unprivileged and safe for user-space execution.
 */
static inline void shim_DCFlushRange(void* addr, u32 len) {
    if (!addr || !len) return;
    u32 start = (u32)addr & ~31;
    u32 end = ((u32)addr + len + 31) & ~31;
    for (u32 p = start; p < end; p += 32) {
        asm volatile("dcbf 0, %0" : : "r"(p) : "memory");
    }
    asm volatile("sync; isync" : : : "memory");
}

static s32 (*s_fn_IOS_Ipc)(IPCCmd* cmd) = NULL;

static s32 Init_IOS_Ipc(void) {
    if (s_fn_IOS_Ipc) return 0;
    u32* pc = (u32*)0x802B9D90;
    for (int i = 0; i < 16; i++) {
        u32 insn = pc[i];
        if ((insn & 0xFC000003) == 0x48000001) { // 'bl' instruction
            s32 offset = (s32)(insn & 0x03FFFFFC);
            if (offset & 0x02000000) offset |= (s32)0xFC000000; // Sign-extend
            s_fn_IOS_Ipc = (s32 (*)(IPCCmd*))((uintptr_t)&pc[i] + offset);
            fn_OSReport("[SHIM] Found __IOS_Ipc at 0x%08X\n", (u32)s_fn_IOS_Ipc);
            return 0;
        }
    }
    fn_OSReport("[SHIM ERROR] Could not find __IOS_Ipc inside IOS_Open\n");
    return -1;
}

static s32 shim_IOS_Ioctlv(s32 fd, s32 ioctl, u32 cnt_in, u32 cnt_out, ioctlv* vec) {
    if (Init_IOS_Ipc() < 0 || !s_fn_IOS_Ipc) return -1;

    static IPCCmd cmd __attribute__((aligned(32)));
    cmd.cmd = 7; // IOS_IOCTLV
    cmd.result = 0;
    cmd.fd = fd;
    cmd.ioctlv.ioctl = ioctl;
    cmd.ioctlv.cnt_in = cnt_in;
    cmd.ioctlv.cnt_out = cnt_out;
    cmd.ioctlv.vec = vec;

    shim_DCFlushRange(&cmd, sizeof(cmd));
    s32 res = s_fn_IOS_Ipc(&cmd);
    shim_DCFlushRange(&cmd, sizeof(cmd));

    return res < 0 ? res : cmd.result;
}

static inline void* GetR13(void) {
    void* r13;
    __asm__ volatile("mr %0, 13" : "=r"(r13));
    return r13;
}

static s32 s_EsFd = -1;
static s32 s_ContentCfd = -1;

/* ES API Helpers using IOS_Ioctlv */
static s32 ES_Init(void) {
    if (s_EsFd >= 0) return 0;
    shim_DCFlushRange(s_EsDevicePath, sizeof(s_EsDevicePath));
    s_EsFd = fn_IOS_Open(s_EsDevicePath, 0);
    fn_OSReport("[SHIM] IOS_Open('/dev/es') = %d\n", s_EsFd);
    if (s_EsFd < 0) {
        fn_OSReport("[SHIM ERROR] IOS_Open('/dev/es') failed: %d\n", s_EsFd);
        Blink_Error();
        return s_EsFd;
    }
    return 0;
}

static s32 ES_OpenContent(u16 index) {
    if (ES_Init() < 0) return -1;

    static ioctlv vec[1] __attribute__((aligned(32)));
    static u32 idx_arg __attribute__((aligned(32)));

    idx_arg = (u32)index;
    vec[0].data = &idx_arg;
    vec[0].len = sizeof(u32);

    shim_DCFlushRange(&idx_arg, sizeof(idx_arg));
    shim_DCFlushRange(vec, sizeof(vec));

    s32 cfd = shim_IOS_Ioctlv(s_EsFd, IOCTL_ES_OPENCONTENT, 1, 0, vec);
    fn_OSReport("[SHIM] ES_OpenContent(index=%u) = %d\n", (u32)index, cfd);
    return cfd;
}

static s32 ES_ReadContent(s32 cfd, void* data, u32 data_size) {
    if (s_EsFd < 0 || cfd < 0 || !data || !data_size) return -1;

    static ioctlv vec[2] __attribute__((aligned(32)));
    static s32 cfd_arg __attribute__((aligned(32)));

    cfd_arg = cfd;
    vec[0].data = &cfd_arg;
    vec[0].len = sizeof(s32);
    vec[1].data = data;
    vec[1].len = data_size;

    shim_DCFlushRange(&cfd_arg, sizeof(cfd_arg));
    shim_DCFlushRange(data, data_size);
    shim_DCFlushRange(vec, sizeof(vec));

    s32 res = shim_IOS_Ioctlv(s_EsFd, IOCTL_ES_READCONTENT, 1, 1, vec);
    shim_DCFlushRange(data, data_size);
    return res;
}

static s32 ES_SeekContent(s32 cfd, s32 where, s32 whence) {
    if (s_EsFd < 0 || cfd < 0) return -1;

    static ioctlv vec[3] __attribute__((aligned(32)));
    static s32 cfd_arg __attribute__((aligned(32)));
    static s32 where_arg __attribute__((aligned(32)));
    static s32 whence_arg __attribute__((aligned(32)));

    cfd_arg = cfd;
    where_arg = where;
    whence_arg = whence;

    vec[0].data = &cfd_arg;
    vec[0].len = sizeof(s32);
    vec[1].data = &where_arg;
    vec[1].len = sizeof(s32);
    vec[2].data = &whence_arg;
    vec[2].len = sizeof(s32);

    shim_DCFlushRange(&cfd_arg, sizeof(cfd_arg));
    shim_DCFlushRange(&where_arg, sizeof(where_arg));
    shim_DCFlushRange(&whence_arg, sizeof(whence_arg));
    shim_DCFlushRange(vec, sizeof(vec));

    return shim_IOS_Ioctlv(s_EsFd, IOCTL_ES_SEEKCONTENT, 3, 0, vec);
}

static s32 __attribute__((unused)) ES_CloseContent(s32 cfd) {
    if (s_EsFd < 0 || cfd < 0) return -1;

    static ioctlv vec[1] __attribute__((aligned(32)));
    static s32 cfd_arg __attribute__((aligned(32)));

    cfd_arg = cfd;
    vec[0].data = &cfd_arg;
    vec[0].len = sizeof(s32);

    shim_DCFlushRange(&cfd_arg, sizeof(cfd_arg));
    shim_DCFlushRange(vec, sizeof(vec));

    return shim_IOS_Ioctlv(s_EsFd, IOCTL_ES_CLOSECONTENT, 1, 0, vec);
}

static s32 EnsureContent2Open(void) {
    if (s_ContentCfd >= 0) return 0;

    /* Open content index 2 via ES */
    s_ContentCfd = ES_OpenContent(2);
    if (s_ContentCfd < 0) {
        fn_OSReport("[SHIM ERROR] ES_OpenContent(2) failed: %d\n", s_ContentCfd);
        Blink_Error();
        return s_ContentCfd;
    }

    /* Test read: read 32 bytes from offset 0 */
    s32 r = ES_ReadContent(s_ContentCfd, s_StaticEsBuf, 32);
    (void)r;
    fn_OSReport("[SHIM] ES_ReadContent test: res=%d, hdr=%02X%02X%02X%02X\n",
        r, (u32)s_StaticEsBuf[0], (u32)s_StaticEsBuf[1],
        (u32)s_StaticEsBuf[2], (u32)s_StaticEsBuf[3]);
    /* Seek back to 0 */
    ES_SeekContent(s_ContentCfd, 0, 0);

    Blink_Milestone(6); // 6 distinct flashes: ES content 2 archive opened successfully
    return 0;
}

static s32 ReadFromContent2(void* dst, u32 offset, u32 length) {
    if (EnsureContent2Open() != 0) {
        fn_OSReport("[SHIM ERROR] Content2 not open\n");
        return -1;
    }

    static int s_first_read_signaled = 0;
    if (!s_first_read_signaled) {
        s_first_read_signaled = 1;
        Blink_Milestone(7); // 7 distinct flashes: Asset stream started
    }

    uintptr_t addr = (uintptr_t)dst;
    /* Fast-path: If destination is 32-byte aligned, length is a 32-byte multiple,
     * and destination is within MEM1 (0x80000000..0x817FFFFF), DMA directly into dst. */
    if ((addr & 31) == 0 && (length & 31) == 0 && addr >= 0x80000000 && (addr + length) <= 0x81800000) {
        s32 s = ES_SeekContent(s_ContentCfd, (s32)offset, 0);
        if (s >= 0) {
            s32 r = ES_ReadContent(s_ContentCfd, dst, length);
            if (r == 0) {
                return (s32)length;
            }
        }
    }

    /* Safe bounce-buffer fallback for unaligned destinations or MEM2 buffers */
    u8* out = (u8*)dst;
    u32 remaining = length;
    u32 cur_off = offset;
    while (remaining > 0) {
        u32 chunk = remaining;
        if (chunk > sizeof(s_StaticEsBuf)) chunk = sizeof(s_StaticEsBuf);

        u32 read_size = chunk;
        u32 aligned_size = (chunk + 31) & ~31;
        if (aligned_size <= sizeof(s_StaticEsBuf) && (cur_off + aligned_size) <= CONTENT2_TOTAL_SIZE) {
            read_size = aligned_size;
        }

        s32 s = ES_SeekContent(s_ContentCfd, (s32)cur_off, 0);
        if (s < 0) {
            fn_OSReport("[SHIM ERROR] ES_SeekContent(off=%u) = %d\n", cur_off, s);
            return -1;
        }

        s32 r = ES_ReadContent(s_ContentCfd, s_StaticEsBuf, read_size);
        if (r < 0) {
            fn_OSReport("[SHIM ERROR] ES_ReadContent(len=%u) = %d\n", read_size, r);
            return -1;
        }

        shim_memcpy(out, s_StaticEsBuf, chunk);
        shim_DCFlushRange(out, chunk);

        out += chunk;
        cur_off += chunk;
        remaining -= chunk;
    }

    return (s32)length;
}

static inline const char* normalize_asset_path(const char* s);

static inline const char* normalize_asset_path(const char* s) {
    if (!s) return "";
    while (s[0] == '/' || (s[0] == '.' && s[1] == '/')) {
        if (s[0] == '/') s++;
        else s += 2;
    }
    /* If there is any prefix ending in ':', skip past it (e.g. "zips:", "data:", "dvd:") */
    const char* col = s;
    while (*col && *col != '/' && *col != '\\') {
        if (*col == ':') {
            s = col + 1;
            break;
        }
        col++;
    }
    while (s[0] == '/' || (s[0] == '.' && s[1] == '/')) {
        if (s[0] == '/') s++;
        else s += 2;
    }
    if ((s[0] == 'd' || s[0] == 'D') &&
        (s[1] == 'a' || s[1] == 'A') &&
        (s[2] == 't' || s[2] == 'T') &&
        (s[3] == 'a' || s[3] == 'A') &&
        (s[4] == 'w' || s[4] == 'W') &&
        (s[5] == 'i' || s[5] == 'I') &&
        (s[6] == 'i' || s[6] == 'I') &&
        (s[7] == '/' || s[7] == '\\')) {
        s += 8;
    }
    while (s[0] == '/' || (s[0] == '.' && s[1] == '/')) {
        if (s[0] == '/') s++;
        else s += 2;
    }
    return s;
}

static inline int shim_strcasecmp_path(const char* s1, const char* s2) {
    if (!s1 || !s2) return -1;
    s1 = normalize_asset_path(s1);
    s2 = normalize_asset_path(s2);

    while (*s1 && *s2) {
        char c1 = *s1;
        char c2 = *s2;
        if (c1 == '\\') c1 = '/';
        if (c2 == '\\') c2 = '/';
        if (c1 >= 'A' && c1 <= 'Z') c1 += ('a' - 'A');
        if (c2 >= 'A' && c2 <= 'Z') c2 += ('a' - 'A');
        if (c1 != c2) return (int)((unsigned char)c1 - (unsigned char)c2);
        s1++;
        s2++;
    }
    char c1 = *s1;
    char c2 = *s2;
    if (c1 == '\\') c1 = '/';
    if (c2 == '\\') c2 = '/';
    return (int)((unsigned char)c1 - (unsigned char)c2);
}

static s32 FindVirtualFile(const char* path) {
    if (!path) return -1;
    for (u32 i = 0; i < NUM_VIRTUAL_FILES; i++) {
        if (shim_strcasecmp_path(path, s_FileTable[i].path) == 0) {
            return (s32)i;
        }
    }
    return -1;
}

static void EnsureRealDVDAddress(u32 idx) {
    if (!IsDVDDiscLoaded()) {
        return;
    }
    if (idx < NUM_VIRTUAL_FILES && s_FileTable[idx].origStartAddr == 0) {
        s32 real_entry = Orig_DVDConvertPathToEntrynum(s_FileTable[idx].path);
        if (real_entry >= 0) {
            s_FileTable[idx].origEntrynum = real_entry;
            DVDFileInfo origInfo;
            if (Orig_DVDFastOpen(real_entry, &origInfo)) {
                s_FileTable[idx].origStartAddr = origInfo.startAddr;
                Orig_DVDClose(&origInfo);
            }
        }
    }
}

void Debug_Step(s32 n) {
    fn_OSReport("[CHECKPOINT %d]\n", n);
}


void Hook_Checkpoint_1(void) {
    fn_OSReport("[CHECKPOINT 1] Subsystems registered, entering Audio init\n");
}

void Hook_Checkpoint_2(void) {
    fn_OSReport("[CHECKPOINT 2] Audio initialized, creating Engine\n");
}

void Hook_Checkpoint_3(void) {
    fn_OSReport("[CHECKPOINT 3] Engine created, entering 0x80124650\n");
}

void Hook_Trace_4674(void) {
    fn_OSReport("[TRACE] 0x80124674: calling 0x80124710\n");
}

s32 Dummy_Blr(void) {
    return 0;
}

static char* s_fake_argv[] = {
    "main.dol",
    "zips:/first.zip",
    "zips:/frontend.zip",
    "zips:/game.zip"
};

void Hook_Ctor_Trace(u32 ctor_addr, u32 idx) {
    if (idx < 5 || (idx % 50) == 0 || idx >= 290) {
        fn_OSReport("[CTOR %u/294] calling 0x%08X\n", idx, ctor_addr);
    }
}

void Hook_Trace_OSInit_Done(void) {
    fn_OSReport("[TRACE] OSInit returned to __start (0x80004170)!\n");
}

void Hook_Trace_Start_InitUser(void) {
    fn_OSReport("[TRACE] __start (0x800041A4): Calling __init_user (global ctors)\n");
}

void Hook_Trace_Start_Main(void) {
    fn_OSReport("[TRACE] __start (0x800041B0): Calling main(0x8018DC88)\n");
}

void Hook_MainTrace(int* argc, char*** argv) {
    static int s_m4_done = 0;
    if (!s_m4_done) {
        s_m4_done = 1;
        Blink_Milestone(4);
    }
    
    fn_OSReport("[SHIM] === main(0x8018DC88) entered successfully! ===\n");
    fn_OSReport("[SHIM] Original argc: %d\n", *argc);
    
    // Forge argc and argv
    *argc = 4;
    *argv = s_fake_argv;
    fn_OSReport("[SHIM] Forged argc: %d, argv[1]: %s\n", *argc, (*argv)[1]);

    // Force the DVD-ready flag to 1. In WAD mode the DVD disc check fails
    // and this flag is left at 0, which prevents DVDOpen from ever being called.
    void* r13 = GetR13();
    *(u32*)((u8*)r13 - 11144) = 1;
    fn_OSReport("[SHIM] Forced DVD-ready flag at -11144(r13) to 1\n");
}

void Hook_Trace_DCA4(void) {
    fn_OSReport("[TRACE] 0x8018DCA4: Registering subsystems (0x80126D2C)\n");
}

void Hook_Trace_DCAC(void) {
    fn_OSReport("[TRACE] 0x8018DCAC: Audio subsystem (0x8016923C)\n");
}

void Hook_Trace_DCD8(void) {
    fn_OSReport("[TRACE] 0x8018DCD8: Calling Engine_Run (0x80124650)\n");
}

int Hook_EarlyMain(int argc, char **argv) {
    fn_OSReport("[SHIM] main() entered successfully! argc=%d\n", argc);
    
    // Force the DVD-ready flag to 1. In WAD mode the DVD disc check fails
    // and this flag is left at 0, which prevents DVDOpen from ever being called.
    void* r13 = GetR13();
    *(u32*)((u8*)r13 - 11144) = 1;
    fn_OSReport("[SHIM] Forced DVD-ready flag at -11144(r13) to 1\n");
    
    return ((int (*)(int, char**))0x8018DC88)(argc, argv);
}

void Hook_Trace_4694(void) {
    fn_OSReport("[TRACE] 0x8018F378: window/renderer init entered\n");
}

void Hook_Trace_DVDInit(void) {
    fn_OSReport("[TRACE] 0x80118E5C: DVD Init sequence called!\n");
}

void Hook_Trace_E1F4(void) {
    fn_OSReport("[TRACE] 0x8018E1F4: File loading init called!\n");
}

void Hook_Trace_1954(void) {
    fn_OSReport("[TRACE] 0x80151954: Early file opener called!\n");
}

void Hook_Trace_ZipMount(void) {
    fn_OSReport("[TRACE] 0x801581F8: ZipMount called!\n");
}

void Hook_Trace_FileDevice_Ctor(void) {
    fn_OSReport("[TRACE] 0x80157828: FileDevice Constructor called!\n");
}

void Hook_Step_A(void) {
    fn_OSReport("[STEP A] 0x8018F3A4: get manager\n");
}

void Hook_Step_B(void) {
    fn_OSReport("[STEP B] 0x8018F3F4: get graphics\n");
}

/* Step C is hooked at 0x8018F434 which is: bl GetFileContext (0x8016AC5C)
   Make it call-through so we can log what GetFileContext returns */
void* Hook_Step_C(void) {
    fn_OSReport("[STEP C] 0x8018F434: calling GetFileContext...\n");
    void* ctx = ((void* (*)(void))0x8016AC5C)();
#if ENABLE_LOGGING
    void* r13 = GetR13();
    void* fileDevice = *(void**)((u8*)r13 - 9152);
    void* fileCtxGlobal = *(void**)((u8*)r13 - 9036);
    fn_OSReport("[STEP C] GetFileContext returned ctx=0x%08X, FileDevice=-9152(r13)=0x%08X, -9036(r13)=0x%08X\n",
                (u32)ctx, (u32)fileDevice, (u32)fileCtxGlobal);
#endif
    return ctx;
}

void Hook_Step_D(void) {
    fn_OSReport("[STEP D] 0x8018F478: renderer setup\n");
}

void Hook_Step_E(void) {
    fn_OSReport("[STEP E] 0x8018F480: set active context\n");
}

void Hook_Step_F(void) {
    fn_OSReport("[STEP F] 0x8018F500: engine method 60\n");
}

void Hook_Trace_469C(void) {
    fn_OSReport("[TRACE] 0x8012469C: calling 0x8012497C (main loop)\n");
}

/* --- call-through trace hooks --- */
/* Each hook prints a log line then tail-calls the original function so r3 is correctly returned */

void Hook_DoFrame_Trace1(void) {
    fn_OSReport("[DF 1] 0x80124A48 -> bl 0x80126750 (Tick/Zips-pre)\n");
    ((void (*)(void))0x80126750)();
}

void Hook_DoFrame_Trace2(void) {
    fn_OSReport("[DF 2] 0x80124A54 -> bl 0x80165EDC\n");
    ((void (*)(void))0x80165EDC)();
}

void Hook_DoFrame_Trace3(void) {
    fn_OSReport("[DF 3] 0x80124A60 -> bl 0x8027EA80\n");
    ((void (*)(void))0x8027EA80)();
}

void Hook_DoFrame_Trace4(void) {
    fn_OSReport("[DF 4] 0x80124A6C -> bl 0x8027E990\n");
    ((void (*)(void))0x8027E990)();
}

/* UpdateSubsystems - returns subsystem ptr in r3; our null check at 0x80124A90 relies on it */
void* Hook_DoFrame_Trace5(void) {
    fn_OSReport("[DF 5] 0x80124A84 -> bl 0x802273D8 (UpdateSubsystems)\n");
    void* result = ((void* (*)(void))0x802273D8)();
    fn_OSReport("[DF 5 ret] subsystem=0x%08X\n", (u32)result);
    return result;
}

/* GetFileContext - returns file context in r3 */
void* Hook_DoFrame_Trace5A(void) {
    fn_OSReport("[DF 5A] 0x80124AA0 -> bl 0x8016AC5C (GetFileContext)\n");
    void* result = ((void* (*)(void))0x8016AC5C)();
    fn_OSReport("[DF 5A ret] fileCtx=0x%08X\n", (u32)result);
    return result;
}

void Hook_DoFrame_Trace5B(void) { fn_OSReport("[DF TRACE 5B] 0x80124C60 before BundleStrings\n"); }
void Hook_DoFrame_Trace5C(void) { fn_OSReport("[DF TRACE 5C] 0x80124C70 before WiiStrap str\n"); }
void Hook_DoFrame_Trace5D(void) { fn_OSReport("[DF TRACE 5D] 0x80124CA4 before WiiStrap model\n"); }
void Hook_DoFrame_Trace5E(void) { fn_OSReport("[DF TRACE 5E] 0x80124CB8 before Engine_Update\n"); }
void Hook_DoFrame_Trace6(void) { fn_OSReport("[DF TRACE 6] 0x80124CC0 before Engine_Render\n"); }

static void DummyMethod(void) {}
static void* s_DummyVTable[128];
static struct {
    void* vtable;
} s_DummyProfiler;
static s32 s_ProfilerInitialized = 0;

static u8 s_GfxDeviceBuf[1024] __attribute__((aligned(32)));
static int s_GfxDeviceInitialized = 0;

void EnsureGfxDevice(void) {
    if (!s_GfxDeviceInitialized) {
        void* r13 = GetR13();
        void* gfx = *(void**)((u8*)r13 - 7448);
        if (!gfx) {
            fn_OSReport("[SHIM] Constructing Graphics Device at 0x%08X...\n", (u32)s_GfxDeviceBuf);
            ((void* (*)(void*))0x80224938)(s_GfxDeviceBuf);
            ((void (*)(void*))0x8022515C)(s_GfxDeviceBuf);
            ((void (*)(void*))0x80225050)(s_GfxDeviceBuf);
            ((void (*)(void*))0x80224E88)(s_GfxDeviceBuf);
            *(void**)((u8*)r13 - 7448) = s_GfxDeviceBuf;
            fn_OSReport("[SHIM] Graphics Device created! (r13-7448=0x%08X)\n", *(u32*)((u8*)r13 - 7448));
        }
        s_GfxDeviceInitialized = 1;
    }
}

void Shim_DoFrame(void* engine, u32 dt) {
    fn_OSReport("[SHIM] Shim_DoFrame entered\n");
    fn_OSReport("[DF] calling 0x80124A48 (Tick/ZipMount-check)\n");
#if ENABLE_LOGGING
    {
        void* r13 = GetR13();
        void* eng = *(void**)((u8*)r13 - 8800);
        fn_OSReport("[DF] engine from -8800(r13)=0x%08X, arg engine=0x%08X\n", (u32)eng, (u32)engine);
    }
#endif
    ((void (*)(void*, u32))0x80124A24)(engine, dt);
    fn_OSReport("[SHIM] Shim_DoFrame 0x80124A24 finished\n");
    EnsureGfxDevice();
    void* r13 = GetR13();
    void* gfxDevice = *(void**)((u8*)r13 - 7448);
    if (gfxDevice) {
        ((void (*)(void*))0x80224F10)(gfxDevice);
        fn_OSReport("[SHIM] Shim_DoFrame SwapBuffers finished\n");
    }
}

void Shim_Engine_Render(void* engine) {
    EnsureGfxDevice();
    void* r13 = GetR13();
    void* gfxDevice = *(void**)((u8*)r13 - 7448);
    if (gfxDevice) {
        ((void (*)(void*))0x80224F10)(gfxDevice);
    }
}

u32 Shim_Loop_Tick(void) {
    static u32 s_TickCount = 0;
    s_TickCount++;
    if ((s_TickCount % 300) == 1) {
        fn_OSReport("[HEARTBEAT] Frame #%u running smoothly!\n", s_TickCount);
    }
    return ((u32 (*)(void))0x801583E8)();
}

void Shim_Engine_Update(void* engine) {
    EnsureGfxDevice();
#if ENABLE_LOGGING
    static s32 s_UpdateTrace = 0;
    if (s_UpdateTrace < 3) {
        s_UpdateTrace++;
        fn_OSReport("[SHIM] Engine_Update pass #%d\n", s_UpdateTrace);
    }
#endif
    if (!s_ProfilerInitialized) {
        for (int i = 0; i < 128; i++) {
            s_DummyVTable[i] = (void*)DummyMethod;
        }
        s_DummyProfiler.vtable = s_DummyVTable;
        
        void* r13 = GetR13();
#if ENABLE_LOGGING
        void* gfxDevice = *(void**)((u8*)r13 - 7448);
        fn_OSReport("[SHIM] gfxDevice at -7448(r13) = 0x%08X\n", (u32)gfxDevice);
#endif
        
        if (engine) {
            void** sub_array = (void**)engine;
            for (int i = 0; i < 48; i++) {
                if (sub_array[i] == NULL) {
                    sub_array[i] = &s_DummyProfiler;
                }
            }
        }
        
        void* global_engine = *(void**)((u8*)r13 - 8800);
        if (global_engine) {
            void** sub_array2 = (void**)global_engine;
            for (int i = 0; i < 48; i++) {
                if (sub_array2[i] == NULL) {
                    sub_array2[i] = &s_DummyProfiler;
                }
            }
        }
        s_ProfilerInitialized = 1;
    }
    ((void (*)(void*, u32))0x801900E0)(engine, 30);
}

#if ENABLE_LOGGING
static u64 s_FileOpenedMask = 0;
#endif

s32 Hook_DVDConvertPathToEntrynum(const char* path) {
    static int s_m5_done = 0;
    if (!s_m5_done) {
        s_m5_done = 1;
        Blink_Milestone(5);
    }
    
    fn_OSReport("[DVD] ConvertPathToEntrynum('%s')\n", path ? path : "NULL");
    s32 idx = FindVirtualFile(path);
    if (idx >= 0) {
        EnsureRealDVDAddress((u32)idx);
#if ENABLE_LOGGING
        if (!(s_FileOpenedMask & (1ULL << (u32)idx))) {
            s_FileOpenedMask |= (1ULL << (u32)idx);
            fn_OSReport("[ASSET] Opened '%s' (%u bytes) (caller=0x%08X)\n", s_FileTable[idx].path, s_FileTable[idx].length, (u32)__builtin_return_address(0));
        }
#endif
        return VIRTUAL_ENTRY_BASE + idx;
    }

    if (IsDVDDiscLoaded()) {
        return Orig_DVDConvertPathToEntrynum(path);
    }
    fn_OSReport("[ERROR] DVD file not found: '%s' (caller=0x%08X)\n", path ? path : "NULL", (u32)__builtin_return_address(0));
    return -1;
}

s32 Hook_DVDFastOpen(s32 entrynum, DVDFileInfo* fileInfo) {
    u32 idx = 0;
    if (IS_VIRTUAL_ENTRY(entrynum)) {
        idx = (u32)(entrynum - VIRTUAL_ENTRY_BASE);
    } else if (entrynum == 0) {
        idx = 51; /* first.zip */
    } else {
        if (IsDVDDiscLoaded()) {
            return Orig_DVDFastOpen(entrynum, fileInfo);
        }
        fn_OSReport("[FASTOPEN FAIL] entrynum=%d (caller=0x%08X)\n", entrynum, (u32)__builtin_return_address(0));
        return 0;
    }

    if (idx < NUM_VIRTUAL_FILES) {
        EnsureRealDVDAddress(idx);
        if (fileInfo) {
            fileInfo->startAddr = (s_FileTable[idx].origStartAddr != 0 && IsDVDDiscLoaded()) ? s_FileTable[idx].origStartAddr : (VIRTUAL_ADDR_FLAG | idx);
            fileInfo->length = s_FileTable[idx].length;
            fileInfo->callback = NULL;
            fileInfo->cb.state = 0;
            fileInfo->cb.command = 0;
            fileInfo->cb.transferredSize = 0;
            fileInfo->cb.offset = 0;
            fileInfo->cb.length = s_FileTable[idx].length;
        }
        return 1;
    }
    return 0;
}

s32 Hook_DVDOpen(const char* fileName, DVDFileInfo* fileInfo) {
    fn_OSReport("[DVD] DVDOpen('%s')\n", fileName ? fileName : "NULL");
    s32 idx = FindVirtualFile(fileName);
    if (idx >= 0) {
        return Hook_DVDFastOpen(VIRTUAL_ENTRY_BASE + idx, fileInfo);
    }
    if (IsDVDDiscLoaded()) {
        return Orig_DVDOpen(fileName, fileInfo);
    }
    fn_OSReport("[ERROR] DVDOpen file not found: '%s'\n", fileName ? fileName : "NULL");
    return 0;
}

s32 Hook_DVDReadAsyncPrio(DVDFileInfo* fileInfo, void* addr, s32 length, s32 offset, DVDCallback callback, s32 prio) {
    if (fileInfo && ((fileInfo->startAddr & 0xFF000000) == VIRTUAL_ADDR_FLAG)) {
        u32 idx = fileInfo->startAddr & 0x00FFFFFF;
        if (idx < NUM_VIRTUAL_FILES) {
#if ENABLE_LOGGING
            static u32 s_ReadCount = 0;
            s_ReadCount++;
            if (s_ReadCount <= 15) {
                fn_OSReport("[ASSET READ #%u] '%s': %d bytes at offset %d\n", s_ReadCount, s_FileTable[idx].path, length, offset);
            }
#endif
            EnsureRealDVDAddress(idx);
            if (s_FileTable[idx].origStartAddr != 0 && IsDVDDiscLoaded()) {
                fileInfo->startAddr = s_FileTable[idx].origStartAddr;
                return Orig_DVDReadAsyncPrio(fileInfo, addr, length, offset, callback, prio);
            }
            
            void* dst = addr;
            if ((uintptr_t)dst < 0x80000000) {
                dst = (void*)((uintptr_t)dst | 0x80000000);
            }
            
            u32 file_raw_off = s_FileTable[idx].offset + (u32)offset;
            s32 bytes_read = ReadFromContent2(dst, file_raw_off, (u32)length);
            
            fileInfo->cb.state = 0; /* DVD_STATE_END */
            fileInfo->cb.transferredSize = (bytes_read > 0 ? bytes_read : length);
            fileInfo->cb.addr = dst;
            fileInfo->cb.length = length;
            fileInfo->cb.offset = offset;
            if (callback) {
                callback(bytes_read > 0 ? bytes_read : length, fileInfo);
            }
            return 1;
        }
    }

    if (IsDVDDiscLoaded()) {
        return Orig_DVDReadAsyncPrio(fileInfo, addr, length, offset, callback, prio);
    }
    if (fileInfo) {
        fileInfo->cb.state = 0;
        fileInfo->cb.transferredSize = length;
    }
    if (callback) {
        callback(length, fileInfo);
    }
    return 1;
}

s32 Hook_DVDClose(DVDFileInfo* fileInfo) {
    if (IsDVDDiscLoaded()) {
        return Orig_DVDClose(fileInfo);
    }
    return 1;
}
