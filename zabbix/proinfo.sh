#!/bin/sh
#This script get RSS& CPU time of process

function mem()
{
        lines=`ps aux |grep "$name" |grep -v "grep" |wc -l`
        if (( "$lines" > "1" ));then
                i=1
                totalmem=0
                for (( i; i<=lines; i++ ))
                        do
                                usedmem=`ps aux |grep "$name" |grep -v "grep" |awk '{print $6}'|sed -n "$i"p`
                                totalmem=$(($totalmem+$usedmem))
                        done;
                echo "scale=2; $totalmem/1024"|bc
        elif (( "$lines" == "1" )); then
                totalmem=`ps aux |grep "$name" |grep -v "grep" |awk '{print $6}'`
                echo "scale=2; $totalmem/1024"|bc
        elif (( "$lines" == "0" )); then
                echo "0"
        fi
}

function cpu()
{
        #lines=`top -n 1 -b |awk '/'$name'/{print $9}'|wc -l`
        lines=`top -n 1 -b |grep "$name" |grep -v "grep" |wc -l`
        if (( "$lines" > "1" ));then
                i=1
                totalcpu=0
                for (( i; i<=lines; i++ ))
                        do
                                #usedcpu=`top -n 1 -b |awk '/'$name'/{print $9}'|sed -n "$i"p`
        			usedcpu=`top -n 1 -b |grep "$name" |grep -v "grep" |awk '{print $9}'|sed -n "$i"p`
                                totalcpu=`echo "$totalcpu+$usedcpu"|bc`
                        done;
                echo $totalcpu
        elif (( "$lines" == "1" )); then
                #totalcpu=`top -n 1 -b |awk '/'$name'/{print $9}'`
                totalcpu=`top -n 1 -b |grep "$name" |grep -v "grep" |awk '{print $9}'`
                echo $totalcpu
        elif (( "$lines" == "0" )); then
                echo "0"
        fi
}

case $1 in
  'pr')
    name="Proxy"
  ;;
  'db')
    name="dbser"
  ;;
  'ol')
    name="Online"
  ;;
  'gw')
    name="GateWay"
  ;;
  *)
    exit 1
  ;;
esac

case $2 in
  'mem')
    mem
  ;;
  'cpu')
    cpu
  ;;
  *)
    exit 1
    ;;
esac
