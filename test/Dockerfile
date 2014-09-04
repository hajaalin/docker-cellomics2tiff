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

ADD test.bats /test/
WORKDIR /test

RUN chown lmu: test.bats
USER lmu

ENTRYPOINT ["bats", "test.bats"]

