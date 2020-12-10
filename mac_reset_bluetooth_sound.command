#!/bin/bash

# needs blueutil, `brew install blueutil` if not present

AIRPODS_ID=14-88-e6-93-14-29

echo -n "Resetting Bluetooth and Core Audio..."

# disconnect AirPods
/usr/local/bin/blueutil --disconnect $AIRPODS_ID 2>/dev/null

# stop/reset Bluetooth and Core Audio
sudo /bin/launchctl stop com.apple.bluetoothaudiod
sudo /bin/launchctl stop com.apple.bluetoothd
sudo /bin/launchctl stop com.apple.audio.coreaudiod

# this would work too instead of stopping bluetoothd
# blueutil -p 0 && sleep 1 && blueutil -p 1

# this is another option instead of stopping
# bluetoothaudiod and coreaudiod
# sudo killall -9 bluetoothaudiod coreaudiod

sleep 1

# start Bluetooth and Core Audio
sudo /bin/launchctl start com.apple.audio.coreaudiod
# sudo /bin/launchctl stop com.apple.bluetoothd
# sudo /bin/launchctl start com.apple.bluetoothaudiod

sleep 3

# reconnect AirPods
/usr/local/bin/blueutil --connect $AIRPODS_ID

echo "   done."
sleep 1
