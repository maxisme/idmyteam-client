FROM python:3.8-slim

RUN apt-get -q update && apt-get -y upgrade && apt-get install -y wget unzip cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libdc1394-22-dev

# install opencv
RUN mkdir -p /tmp/opencv
WORKDIR /tmp/opencv/
RUN wget --quiet -O /tmp/opencv/opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip
RUN wget --quiet -O /tmp/opencv/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.4.0.zip
RUN unzip opencv_contrib.zip && unzip opencv.zip
WORKDIR /tmp/opencv/opencv-4.4.0/
RUN mkdir build
WORKDIR /tmp/opencv/opencv-4.4.0/build/
RUN pip install numpy
RUN cmake -D CMAKE_INSTALL_PREFIX=/usr/local \
	-D INSTALL_PYTHON_EXAMPLES=ON \
	-D INSTALL_C_EXAMPLES=OFF \
	-D OPENCV_ENABLE_NONFREE=OFF \
	-D BUILD_NEW_PYTHON_SUPPORT=ON \
	-D BUILD_opencv_python3=ON \
	-D HAVE_opencv_python3=ON \
	-D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv/opencv_contrib-4.4.0/modules \
	-DPYTHON_DEFAULT_EXECUTABLE=$(which python) \
	-D BUILD_EXAMPLES=ON ..

ARG jobs=1
RUN make -j$jobs
RUN make install
RUN ldconfig

# clean up
#RUN rm -rf /tmp/opencv
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
#RUN apt remove --purge $CVPACKAGES
