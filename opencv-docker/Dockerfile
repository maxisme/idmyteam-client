FROM python:3.8
RUN uname -a

ARG jobs=1
ARG CVPACKAGES="wget unzip cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev python-numpy libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev"

RUN apt-get -q update && apt-get -y upgrade && apt-get install -y $CVPACKAGES

# install opencv
RUN mkdir -p /tmp/opencv
WORKDIR /tmp/opencv/
RUN wget --quiet -O /tmp/opencv/opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip
RUN wget --quiet -O /tmp/opencv/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.4.0.zip
RUN unzip opencv_contrib.zip && unzip opencv.zip
WORKDIR /tmp/opencv/opencv-4.4.0/
RUN mkdir build
WORKDIR /tmp/opencv/opencv-4.4.0/build/
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv/opencv_contrib-4.4.0/modules \
#    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
#    -D ENABLE_NEON=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..

RUN make -j$jobs
RUN make install
RUN ldconfig

# clean up
RUN rm -rf /tmp/opencv
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
#RUN apt remove --purge $CVPACKAGES
