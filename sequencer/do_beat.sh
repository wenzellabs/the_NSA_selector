#!/bin/bash

TICK=0.2

IP=192.168.1.25
#IP=nsa.gov
#IP=255.255.255.255 # use -b with broadcast ping, and sizes up to around 1400 only

if [ "$1x" == "x" ] ; then
    echo please provide a beat script as argument
    exit 1
fi

while true ; do
    for b in $(cat $1) ; do
        ping -c 1 $IP -s $b -W 0.1 &
        sleep $TICK
    done
done

