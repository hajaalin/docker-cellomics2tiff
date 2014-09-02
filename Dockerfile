FROM ubuntu:14.04

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    python2.7 \
    wget \
    && apt-get autoremove \
    && apt-get clean

RUN apt-get install -y unzip
RUN apt-get install -y mdbtools
RUN apt-get install -y rsync
RUN apt-get install -y openjdk-6-jre-headless

RUN wget http://downloads.openmicroscopy.org/bio-formats/5.0.2/artifacts/bftools.zip
RUN mkdir /bftools; cd bftools; unzip ../bftools.zip; rm ../bftools.zip
ENV PATH $PATH:/bftools

ADD python /python
WORKDIR python

# run as non-root user
RUN adduser --disabled-login lmu
#USER lmu

# run the conversion script when container is run
ENTRYPOINT ["python2.7", "stage_cellomics2tiff.py"]

