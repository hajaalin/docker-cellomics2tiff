FROM hajaalin/cellomics2tiff

USER root
RUN apt-get install -y \
wget \
git \
&& apt-get autoremove \
&& apt-get clean

# install BATS
RUN git clone https://github.com/sstephenson/bats.git
RUN cd bats && ./install.sh /usr/local

RUN mkdir /test
ADD test.t /test/test.t

RUN chown lmu: /test/test.t
USER lmu

ENTRYPOINT ["bats", "/test/test.t"]

