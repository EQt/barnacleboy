// Compute the bounding box
#include "reader.hpp"
#include "record.hpp"
#include <stdexcept>
#include <clocale>


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

        printf("sizeof(Record) = %d\n", int(sizeof(Record)));

        // float
        //     min_x, max_x, min_y, max_y;
        // Record r;
    }
}
