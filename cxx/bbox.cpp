// Compute the bounding box
#include <stdexcept>
#include <clocale>
#include <algorithm>

#include "reader.hpp"
#include "record.hpp"


int
main(int argc, char *argv[])
{
    const auto fname = "a.bin";

    setlocale(LC_ALL, "");

    const auto h = read_header(fname);
    printf("num_entries = %'d\n", h.num_entries);

    {
        CFile io (fname);
        if (fseek(io.fid, h.offset, SEEK_SET) < 0)
            throw std::runtime_error("ftell 1");

        Record r;
        io.read(&r);

        float
            min_x = r.abs_position[0],
            max_x = r.abs_position[0],
            min_y = r.abs_position[1],
            max_y = r.abs_position[1];

        for (size_t i = 1; i < h.num_entries; i++) {
            io.read(&r);
            min_x = std::min(min_x, r.abs_position[0]);
            max_x = std::max(max_x, r.abs_position[0]);
            min_y = std::min(min_y, r.abs_position[1]);
            max_y = std::max(max_y, r.abs_position[1]);
        }

        printf("[%.3f, %.3f] x [%.3f, %.3f]\n",
               min_x, max_x, min_y, max_y);
    }
}
