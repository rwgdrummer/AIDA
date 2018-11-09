# Dockerfile
# Created on: Oct 26, 2018
#     Author: scott

FROM ubuntu:18.04

ENV TZ 'US/Eastern'
RUN echo $TZ > /etc/timezone && \
   apt-get update && apt-get install -y tzdata && \
   rm /etc/localtime && \
   ln -snf /usr/share/zoneinfo/America/New_York /etc/localtime && \
   dpkg-reconfigure -f noninteractive tzdata && \
   apt-get clean

RUN apt-get update && apt-get install -y \
    g++ \
    cmake \
    wget \
    git \
    pkg-config \
    qt5-default

RUN apt-get install -y \
    libavcodec-dev libavformat-dev libswscale-dev \
    libjpeg-dev libpng-dev libtiff-dev libwebp-dev libtbb-dev

RUN git clone https://github.com/opencv/opencv.git && \
    git clone https://github.com/opencv/opencv_contrib.git && \
    cd opencv_contrib && git checkout 3.4.3 && \
    cd ../opencv && git checkout 3.4.3

RUN cd opencv && mkdir build && cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release \
        -DOPENCV_EXTRA_MODULES_PATH=../../opencv_contrib/modules \
        -DWITH_1394=OFF \
        -DWITH_CARBON=OFF \
        -DWITH_VTK=OFF \
        -DWITH_CUDA=OFF \
        -DWITH_CUFFT=OFF \
        -DWITH_CUBLAS=OFF \
        -DWITH_EIGEN=OFF \
        -DWITH_FFMPEG=ON \
        -DWITH_GSTREAMER=OFF \
        -DWITH_GTK=OFF \
        -DWITH_IPP=OFF \
        -DWITH_JASPER=OFF \
        -DWITH_JPEG=ON \
        -DWITH_WEBP=ON \
        -DWITH_OPENEXR=OFF \
        -DWITH_OPENGL=ON \
        -DWITH_OPENNI=OFF \
        -DWITH_OPENNI2=OFF \
        -DWITH_PNG=ON \
        -DWITH_PVAPI=OFF \
        -DWITH_GIGEAPI=OFF \
        -DWITH_QT=OFF \
        -DWITH_QUICKTIME=OFF \
        -DWITH_TBB=ON \
        -DWITH_OPENMP=OFF \
        -DWITH_CSTRIPES=OFF \
        -DWITH_PTHREADS_PF=OFF \
        -DWITH_TIFF=ON \
        -DWITH_UNICAP=OFF \
        -DWITH_V4L=OFF \
        -DWITH_LIBV4L=OFF \
        -DWITH_XIMEA=OFF \
        -DWITH_XINE=OFF \
        -DWITH_CLP=OFF \
        -DWITH_OPENCL=OFF \
        -DWITH_OPENCL_SVM=OFF \
        -DWITH_OPENCLAMDFFT=OFF \
        -DWITH_OPENCLAMDBLAS=OFF \
        -DWITH_INTELPERC=OFF \
        -DWITH_MATLAB=OFF \
        -DWITH_IPP_A=OFF \
        -DWITH_VA=OFF \
        -DWITH_VA_INTEL=OFF \
        -DWITH_GDAL=OFF \
        -DWITH_GPHOTO2=OFF \
        \
        -DBUILD_SHARED_LIBS=ON \
        -DBUILD_opencv_apps=OFF \
        -DBUILD_DOCS=OFF \
        -DBUILD_EXAMPLES=OFF \
        -DBUILD_PACKAGE=OFF \
        -DBUILD_PERF_TESTS=OFF \
        -DBUILD_TESTS=OFF \
        -DBUILD_WITH_DYNAMIC_IPP=OFF \
        \
        -DBUILD_ZLIB=OFF \
        -DBUILD_TIFF=OFF \
        -DBUILD_JASPER=OFF \
        -DBUILD_JPEG=OFF \
        -DBUILD_WEBP=OFF \
        -DBUILD_PNG=OFF \
        -DBUILD_OPENEXR=OFF \
        -DBUILD_TBB=OFF \
        \
        -DBUILD_opencv_java=OFF \
        \
        -DPYTHON_EXECUTABLE=OFF \
        -DBUILD_opencv_python2=OFF \
        -DBUILD_opencv_python3=OFF \
        -DINSTALL_C_EXAMPLES=OFF \
        -DINSTALL_PYTHON_EXAMPLES=OFF \
        -DENABLE_PRECOMPILED_HEADERS=ON \
        -DENABLE_CXX11=ON \
        .. && \
    make install
    
ADD openbr-OpenCV-3.4-compatibility-and-cluster-exposure.patch .
RUN git clone https://github.com/biometrics/openbr.git && \
    cd openbr && \
    git submodule init && \
    git submodule update && \
    git apply ../openbr-OpenCV-3.4-compatibility-and-cluster-exposure.patch && \
    mkdir build && \
    cd build && \
    cmake -DCMAKE_BUILD_TYPE=Release .. && \
    make install

ADD FaceIndex.tgz .
ADD TestImages.tgz .
RUN cd FaceIndex && \
    THIRD_PARTY_CPPFLAGS=`pkg-config --cflags Qt5Core` DEST=/usr/local make install

RUN OPENBR_ROOT=/usr/local /usr/local/bin/IndexFaces ./TestImages/TestImages.txt 1