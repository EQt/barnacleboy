test: bbox a.bin
	./bbox

bbox: bbox.cpp reader.hpp record.hpp
	$(CXX) -Wall -o $@ $<
