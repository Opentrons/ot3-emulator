#!/bin/bash
# This script will delete SocketCan network vcan0

sudo ip link delete vcan0 2> /dev/null
if [ $? == 1 ]; then
  echo "CAN Virtual Network does not exist"
  exit 1
fi

echo "CAN Virtual Network successfully removed"