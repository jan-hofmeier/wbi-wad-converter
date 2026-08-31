/*
 * Nintendo LZ77 Type 0x11 (LZ11) Compressor
 * Standalone, portable C implementation for Wii DOL compression.
 */

#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>

#define MAX_OFFSET 0x1000      /* 4096 bytes max backward displacement */
#define MAX_MATCH_LEN 0x10110  /* 65808 bytes max match length */
#define MIN_MATCH_LEN 3
#define HASH_SIZE 65536

static inline uint16_t hash3(const uint8_t* p) {
    return (uint16_t)(((p[0] << 8) ^ (p[1] << 4) ^ p[2]) & (HASH_SIZE - 1));
}

int lz11_compress(const uint8_t* in_data, size_t in_size, uint8_t** out_data, size_t* out_size) {
    if (!in_data || in_size == 0) return -1;

    size_t max_out = in_size + (in_size / 8) + 256;
    uint8_t* out = (uint8_t*)malloc(max_out);
    if (!out) return -1;

    size_t out_pos = 0;
    out[out_pos++] = 0x11;

    if (in_size <= 0xFFFFFF) {
        out[out_pos++] = (uint8_t)(in_size & 0xFF);
        out[out_pos++] = (uint8_t)((in_size >> 8) & 0xFF);
        out[out_pos++] = (uint8_t)((in_size >> 16) & 0xFF);
    } else {
        out[out_pos++] = 0;
        out[out_pos++] = 0;
        out[out_pos++] = 0;
        out[out_pos++] = (uint8_t)(in_size & 0xFF);
        out[out_pos++] = (uint8_t)((in_size >> 8) & 0xFF);
        out[out_pos++] = (uint8_t)((in_size >> 16) & 0xFF);
        out[out_pos++] = (uint8_t)((in_size >> 24) & 0xFF);
    }

    int32_t* head = (int32_t*)malloc(HASH_SIZE * sizeof(int32_t));
    int32_t* prev = (int32_t*)malloc(in_size * sizeof(int32_t));
    if (!head || !prev) {
        free(head);
        free(prev);
        free(out);
        return -1;
    }
    for (int i = 0; i < HASH_SIZE; i++) head[i] = -1;

    size_t in_pos = 0;
    while (in_pos < in_size) {
        size_t flag_pos = out_pos++;
        uint8_t flag_byte = 0;

        for (int bit = 7; bit >= 0; bit--) {
            if (in_pos >= in_size) break;

            size_t best_len = 0;
            size_t best_disp = 0;

            if (in_pos + MIN_MATCH_LEN <= in_size) {
                uint16_t h = hash3(&in_data[in_pos]);
                int32_t match_pos = head[h];
                int chain_len = 128;

                while (match_pos >= 0 && chain_len-- > 0) {
                    size_t disp = in_pos - (size_t)match_pos;
                    if (disp > MAX_OFFSET || disp == 0) break;

                    size_t max_len = in_size - in_pos;
                    if (max_len > MAX_MATCH_LEN) max_len = MAX_MATCH_LEN;

                    size_t match_len = 0;
                    while (match_len < max_len && in_data[in_pos + match_len] == in_data[match_pos + match_len]) {
                        match_len++;
                    }

                    if (match_len >= MIN_MATCH_LEN && match_len > best_len) {
                        best_len = match_len;
                        best_disp = disp;
                        if (best_len >= MAX_MATCH_LEN) break;
                    }

                    match_pos = prev[match_pos];
                }
            }

            if (best_len >= MIN_MATCH_LEN) {
                flag_byte |= (1 << bit);
                size_t d = best_disp - 1;

                if (best_len <= 16) {
                    out[out_pos++] = (uint8_t)(((best_len - 1) << 4) | ((d >> 8) & 0x0F));
                    out[out_pos++] = (uint8_t)(d & 0xFF);
                } else if (best_len <= 0x110) {
                    size_t l = best_len - 0x11;
                    out[out_pos++] = (uint8_t)((l >> 4) & 0x0F);
                    out[out_pos++] = (uint8_t)(((l & 0x0F) << 4) | ((d >> 8) & 0x0F));
                    out[out_pos++] = (uint8_t)(d & 0xFF);
                } else {
                    size_t l = best_len - 0x111;
                    out[out_pos++] = (uint8_t)(0x10 | ((l >> 12) & 0x0F));
                    out[out_pos++] = (uint8_t)((l >> 4) & 0xFF);
                    out[out_pos++] = (uint8_t)(((l & 0x0F) << 4) | ((d >> 8) & 0x0F));
                    out[out_pos++] = (uint8_t)(d & 0xFF);
                }

                for (size_t i = 0; i < best_len && in_pos + i + MIN_MATCH_LEN <= in_size; i++) {
                    uint16_t h = hash3(&in_data[in_pos + i]);
                    prev[in_pos + i] = head[h];
                    head[h] = (int32_t)(in_pos + i);
                }
                in_pos += best_len;
            } else {
                out[out_pos++] = in_data[in_pos];
                if (in_pos + MIN_MATCH_LEN <= in_size) {
                    uint16_t h = hash3(&in_data[in_pos]);
                    prev[in_pos] = head[h];
                    head[h] = (int32_t)in_pos;
                }
                in_pos++;
            }
        }
        out[flag_pos] = flag_byte;
    }

    free(head);
    free(prev);

    *out_data = out;
    *out_size = out_pos;
    return 0;
}

int main(int argc, char** argv) {
    if (argc < 3) {
        fprintf(stderr, "Usage: %s <input_file> <output_lz11>\n", argv[0]);
        return 1;
    }

    FILE* fin = fopen(argv[1], "rb");
    if (!fin) {
        perror("Failed to open input file");
        return 1;
    }

    fseek(fin, 0, SEEK_END);
    size_t in_size = ftell(fin);
    fseek(fin, 0, SEEK_SET);

    uint8_t* in_data = (uint8_t*)malloc(in_size);
    if (!in_data || fread(in_data, 1, in_size, fin) != in_size) {
        fclose(fin);
        fprintf(stderr, "Failed to read input file\n");
        return 1;
    }
    fclose(fin);

    uint8_t* out_data = NULL;
    size_t out_size = 0;

    if (lz11_compress(in_data, in_size, &out_data, &out_size) != 0) {
        free(in_data);
        fprintf(stderr, "LZ11 compression failed\n");
        return 1;
    }

    FILE* fout = fopen(argv[2], "wb");
    if (!fout) {
        perror("Failed to open output file");
        free(in_data);
        free(out_data);
        return 1;
    }

    if (fwrite(out_data, 1, out_size, fout) != out_size) {
        fprintf(stderr, "Failed to write output file\n");
        fclose(fout);
        free(in_data);
        free(out_data);
        return 1;
    }

    fclose(fout);
    printf("Compressed: %zu bytes -> %zu bytes (%.1f%%)\n", in_size, out_size, (double)out_size / in_size * 100.0);

    free(in_data);
    free(out_data);
    return 0;
}
