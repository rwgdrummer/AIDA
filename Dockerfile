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
   curl \
   python3.6  \
   python3-pip \
   wget \
   imagemagick \
   python3-pip \
   python3-setuptools \ 
   git  \
   ffmpeg \
   libopencv-dev \
   python3-opencv \
   gradle \
   redis

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-fra tesseract-ocr-rus unzip
RUN apt-get install -y openjdk-8-jdk
RUN pip install opencv-python
RUN pip install redis


#RUN wget https://www.imagemagick.org/download/ImageMagick.tar.gz
#RUN tar xf ImageMagick.tar.gz
#WORKDIR ImageMagick-7*
#RUN ./configure && make
#RUN make install

RUN ldconfig /usr/local/lib

ADD . /opt/AIDA
WORKDIR /opt
RUN wget https://sourceforge.net/projects/ccextractor/files/ccextractor/0.85/ccextractor-src-nowin.0.85.zip
RUN unzip ccextractor-src-nowin.0.85.zip
RUN rm ccextractor-src-nowin.0.85.zip
WORKDIR  ccextractor/linux
RUN make
WORKDIR ../../
#RUN wget https://blizzard.partech.com:8888/robertsonb/AIDA/-/archive/develop/AIDA-develop.tar.gz --no-check-certificate
RUN wget https://github.com/jakevdp/klsh/archive/master.zip
RUN unzip master.zip
WORKDIR klsh-master
RUN cp /opt/AIDA/python/dependency_info/klsh_setup.py setup.py
RUN python3.6 setup.py sdist
RUN pip install -e .

WORKDIR /opt/AIDA/python/src
RUN python3.6 setup.py sdist
RUN pip install -e .

WORKDIR ../..
ADD AIDA_video_segmentation_tool_v2.tgz .
RUN unzip AIDA_video_segmentation_tool_v2.tgz
RUN tar xf AIDA_video_segmentation_tool_v2.tar
WORKDIR AIDA_video_segmentation_tool_v2/java/cineast
RUN git apply ../../../AIDA/java/cineast_patch.txt
RUN ./gradlew deploy

WORKDIR /

EXPOSE 5000

ENTRYPOINT ["python3.6"]
CMD ["aida.runner" "/opt/AIDA/init/config.json"]
#CMD ["/bin/bash"]
