#!/usr/bin/env bats

# download test dataset
setup () {
  mkdir -p /tmp/bats/input
  mkdir -p /tmp/bats/output 
  cd /tmp/bats/input
  wget -O tmp.tgz http://bit.ly/1CpK2CC
  tar xf tmp.tgz
}

# cleanup
teardown () {
  echo rm -rf /tmp/bats
}

@test "amount of tifs vs c01s" {
  # run conversion
  docker run --rm -v /tmp/bats/input:/input -v /tmp/bats/output:/output hajaalin/cellomics2tiff
  tifs=`find /tmp/bats/output -name "*.tif" | wc -l`
  c01s=`find /tmp/bats/input -name "*.C01" | wc -l`
  [ "$tifs" -eq "$c01s" ]
}


