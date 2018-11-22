# Memory Mapped IO

Quite
[controversial](https://eklausmeier.wordpress.com/2016/02/03/performance-comparison-mmap-versus-read-versus-fread/) 
whether `fread`, `mmap` or the system call `read` performance best.

Eventually, we should benchmark on several systems using the `perf` Kernel tool.


## Programming Languages

Calling `mmap` on Unix systems in `C` is not [that difficult](https://www.poftut.com/mmap-tutorial-with-examples-in-c-and-cpp-programming-languages/).

In Rust, there is **TODO**.

In Numpy (Python) there is `numpy.memmap`.
