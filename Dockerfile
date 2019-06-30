FROM resin/raspberry-pi2-debian:latest

EXPOSE 8080

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
libraspberrypi-bin \
python3-dev \
supervisor && apt-get clean && rm -rf /var/lib/apt/lists/*

# install python 3.6
#RUN mkdir -p /tmp/python3
#WORKDIR /tmp/python3/
#RUN wget -O python.tar.xz https://www.python.org/ftp/python/3.6.3/Python-3.6.3.tar.xz
#RUN tar xJf python.tar.xz
#WORKDIR Python-3.6.3/
#RUN ./configure
#RUN make
#RUN make install

# install pip
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py
RUN rm get-pip.py
RUN pip3 install --upgrade pip
RUN pip3 install numpy

#RUN dd if=/dev/zero of=/swapfile1GB bs=1M count=1024
#RUN mkswap /swapfile1GB
#RUN swapon /swapfile1GB

# install opencv
RUN mkdir -p /tmp/opencv
RUN wget -O /tmp/opencv/opencv.zip https://github.com/opencv/opencv/archive/4.0.0.zip
RUN wget -O /tmp/opencv/opencv_contrib.zip https://github.com/opencv/opencv_contrib/archive/4.0.0.zip
WORKDIR /tmp/opencv/
RUN unzip opencv_contrib.zip
RUN unzip opencv.zip
WORKDIR /tmp/opencv/opencv-4.0.0/
RUN mkdir build
WORKDIR /tmp/opencv/opencv-4.0.0/build/
RUN cmake -D CMAKE_BUILD_TYPE=RELEASE \
    -D CMAKE_INSTALL_PREFIX=/usr/local \
    -D OPENCV_EXTRA_MODULES_PATH=/tmp/opencv/opencv_contrib-4.0.0/modules \
    -D ENABLE_VFPV3=ON \
    -D BUILD_TESTS=OFF \
    -D ENABLE_NEON=ON \
    -D INSTALL_PYTHON_EXAMPLES=OFF \
    -D INSTALL_C_EXAMPLES=OFF \
    -D BUILD_EXAMPLES=OFF ..

RUN make -j2
RUN make install
RUN ldconfig
RUN rm -rf /tmp/opencv
RUN apt-get update && apt-get install -y python-opencv python-dev libffi-dev libmariadbclient-dev

RUN curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && python get-pip.py && rm get-pip.py

# init proj
WORKDIR /usr/src/idmyteam
COPY . .

RUN pip install -r requirements.txt

# background startup scripts
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf
CMD ["/usr/bin/supervisord"]