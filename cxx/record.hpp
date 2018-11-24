#pragma once
#include <cstdint>

#pragma pack(push, 1)
struct Record
{
    uint64_t barcode;
    uint16_t barcode_id;
    uint16_t fov_id;
    float    total_magnitude;
    uint16_t pixel_centroid[2];
    float    weighted_pixel_centroid[2];
    float    abs_position[2];
    uint16_t area;
    float    pixel_trace_mean[16];
    float    pixel_trace_std[16];
    uint8_t  is_exact;
    uint8_t  error_bit;
    uint8_t  error_dir;
    float    av_distance;
    uint32_t cellID;
    uint8_t  inNucleus;
    double   distNucleus;
    double   distPeriphery;
};
#pragma pack(pop)

static_assert(sizeof(Record) == 194, "Record wrongly aligned");
