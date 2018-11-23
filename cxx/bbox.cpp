// Compute the bounding box
#include "reader.hpp"
#include <clocale>


int
main(int argc, char *argv[])
{
    setlocale(LC_ALL, "");
    const auto h = read_header("a.bin");
    printf("num_entries = %'d\n", h.num_entries);
}
