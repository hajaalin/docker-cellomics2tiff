#!/usr/bin/env bats

# download test dataset
setup () {
  mkdir /tmp/input
  mkdir /tmp/output 
  cd /tmp/input
  wget -O tmp.tgz http://bit.ly/1CpK2CC
  tar xf tmp.tgz
}

# cleanup
teardown () {
  rm -rf /tmp/input /tmp/output
}

@test "amount of tifs vs c01s" {
  # run conversion
  python2.7 /python/stage_cellomics2tiff.py -i /tmp/input -o /tmp/output
  tifs=`find /tmp/output -name "*.tif" | wc -l`
  c01s=`find /tmp/input -name "*.C01" | wc -l`
  [ "$tifs" -eq "$c01s" ]
}

@test "archival" {
  # run archival
  c01s=`find /tmp/input -name "*.C01" | wc -l`
  python2.7 /python/stage_cellomics2tiff.py -i /tmp/input -a /tmp/output
  archived=`find /tmp/output -name "*.C01" | wc -l`
  [ "$archived" -eq "$c01s" ]
}

