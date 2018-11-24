#pragma once
#include <cstdio>
#include <string>
#include <stdexcept>


struct CFile
{
    std::FILE *fid = nullptr;

    template<typename T>
    T read();

    template<typename T>
    void read(T*);

    CFile(const char *fname, const char *mode = "r");
    ~CFile();
};


CFile::CFile(const char *fname, const char *mode)
{
    fid = fopen(fname, mode);
    if (!fid)
        throw std::runtime_error(std::string("Could not open ") +
                                 fname + " in mode " + mode);
}


CFile::~CFile()
{
    if (fid)
        fclose(fid);
}


template<typename T>
T
CFile::read()
{
    T val;
    size_t nbytes = fread(&val, sizeof(T), 1, fid);
    if (nbytes != 1)
        throw std::runtime_error(std::string("could not read ") +
                                 std::to_string(sizeof(T)) + " bytes");
    return val;
}


template<typename T>
void
CFile::read(T*)
{


}


struct Header
{
    uint8_t version = -1;
    uint32_t num_entries = uint32_t(-1);
    size_t offset = 0;
};


static const auto HEADER_LEN = 429;



Header
read_header(const char *fname)
{
    CFile io (fname, "rb");
    const auto version = io.read<uint8_t>();
    if (version != 1)
        throw std::runtime_error(std::string("version not 1 but ") +
                                 std::to_string(version));
    const auto is_corrupt = io.read<uint8_t>();
    if (is_corrupt) {
        printf("%d\n", is_corrupt);
        throw std::runtime_error("is corrupt");
    }
    Header h;
    h.num_entries = io.read<decltype(h.num_entries)>();
    const auto header_len = io.read<uint32_t>();
    if (header_len != HEADER_LEN)
        throw std::runtime_error("Unexpected HEADER_LEN");
    fseek(io.fid, header_len, SEEK_CUR);

    h.offset = ftell(io.fid);
    return h;
}
