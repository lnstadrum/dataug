cmake_minimum_required(VERSION 3.2.1)
project(FastAugment)

# find CUDA
find_package(CUDA REQUIRED)

# query compilation options from TensorFlow
message(STATUS "Querying TensorFlow for compilation options")
execute_process(COMMAND python3 -c "import tensorflow.sysconfig as c; print(c.get_include(), end='')"
                OUTPUT_VARIABLE TF_INCLUDE_DIRS)
execute_process(COMMAND python3 -c "import tensorflow.sysconfig as c; print(' '.join(c.get_compile_flags()), end='')"
                OUTPUT_VARIABLE TF_COMPILE_FLAGS)
execute_process(COMMAND python3 -c "import tensorflow.sysconfig as c; print(' '.join(c.get_link_flags()), end='')"
                OUTPUT_VARIABLE TF_LINK_FLAGS)

# set flags
set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -std=c++14 -fPIC -O3 -g -Wl,--no-as-needed ${TF_COMPILE_FLAGS} ${TF_LINK_FLAGS}")
set(CUDA_NVCC_FLAGS "${CUDA_NVCC_FLAGS} -std=c++14 -Xptxas -O3 -use_fast_math")
include_directories(${TF_INCLUDE_DIRS})

# add library
CUDA_ADD_LIBRARY(fastaugment
    ${CMAKE_CURRENT_LIST_DIR}/src/augment.cpp
    ${CMAKE_CURRENT_LIST_DIR}/src/augment.cu
    SHARED)

