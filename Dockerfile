FROM python:3.8

RUN mkdir -p /usr/src/idmyteam

RUN apt-get -q update && apt-get -y upgrade && apt-get install -y \
build-essential \
git \
cmake \
wget \
unzip \
yasm \
pkg-config \
libswscale-dev \
libjpeg-dev \
libpng-dev \
libtiff-dev \
libavformat-dev \
libpq-dev \
libffi-dev \
libssl-dev \
libatlas-base-dev \
gfortran \
python-mysqldb \
imagemagick \
shellcheck \
supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*

# install opencv
RUN mkdir -p /tmp/opencv
RUN wget -O /tmp/opencv/opencv.zip https://github.com/opencv/opencv/archive/4.4.0.zip
RUN wget -O /tmp/opencv/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.4.0.zip
WORKDIR /tmp/opencv/
RUN unzip opencv_contrib.zip
RUN unzip opencv.zip
WORKDIR /tmp/opencv/opencv-4.4.0/
RUN mkdir build
WORKDIR /tmp/opencv/opencv-4.4.0/build/
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv/opencv_contrib-4.4.0/modules \
#    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D ENABLE_NEON=OFF \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..

RUN make -j
RUN make install
RUN ldconfig
RUN rm -rf /tmp/opencv
RUN apt-get update && apt-get install -y python-opencv libffi-dev libmariadbclient-dev

#RUN ln -s /usr/local/python/cv2/python-3.7/cv2.cpython-37m-arm-linux-gnueabihf.so /usr/local/lib/python3.7/dist-packages/

# init proj
WORKDIR /usr/src/idmyteam
COPY . .

RUN pip install -r requirements.txt

# background startup scripts
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]