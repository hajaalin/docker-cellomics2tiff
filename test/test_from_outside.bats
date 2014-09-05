#!/usr/bin/env bats

if [ "$io_root" != "$HOME/tmp/bats-cellomics2tiff-test" ]; then
  export io_root="$HOME/tmp/bats-cellomics2tiff-test"
  mkdir $io_root
  mkdir $io_root/input0
  mkdir $io_root/input
  mkdir $io_root/output
  mkdir $io_root/archive
  cd $io_root/input0
  wget -O tmp.tgz http://bit.ly/1CpK2CC
  tar xf tmp.tgz
  rm tmp.tgz
  chmod -R a+rwx $io_root/input*
  chmod -R a+rwx $io_root/archive $io_root/output
fi

# download test dataset
setup () {
  rsync -a $io_root/input0/ $io_root/input/ 
}

# cleanup
teardown () {
  rm -rf $io_root/input/*
  rm -rf $io_root/output/*
  rm -rf $io_root/archive/*
}

@test "testdata" {
  c01s=`find $io_root/input -name "*.C01" | wc -l`
  [ "$c01s" -ne "0" ]
}

@test "amount of tifs vs c01s" {
  # run conversion
  docker run --rm -v $io_root/input:/input -v $io_root/output:/output hajaalin/cellomics2tiff
  tifs=`find $io_root/output -name "*.tif" | wc -l`
  c01s=`find $io_root/input -name "*.C01" | wc -l`
  [ "$tifs" -eq "$c01s" ]
}

@test "archive" {
  # run archival
  c01s=`find $io_root/input -name "*.C01" | wc -l`
  docker run --rm -v $io_root/input:/input -v $io_root/archive:/archive hajaalin/cellomics2tiff -a /archive
  archived=`find $io_root/archive -name "*.C01" | wc -l`
  [ "$archived" -eq "$c01s" ]
}


