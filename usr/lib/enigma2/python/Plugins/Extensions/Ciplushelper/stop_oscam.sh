#!/bin/sh
#
# Stop Oscam for CI+ helper
# Universal method using ps + awk

echo "========================================="
echo "   Stop Oscam for CI+ helper"
echo "========================================="

# Get all Oscam PIDs (universal method)
OSCAM_PIDS=$(ps -A | awk '/[O]SCam/ {print $1}')

if [ -z "$OSCAM_PIDS" ]; then
    echo "✅ Oscam is not running"
    exit 0
fi

echo "🔍 Found Oscam PIDs: $OSCAM_PIDS"

# Kill all Oscam processes
for pid in $OSCAM_PIDS; do
    echo "  Killing PID $pid..."
    kill -9 $pid 2>/dev/null
done

sleep 1

# Check if Oscam is still running
CHECK=$(ps -A | awk '/[O]SCam/ {print $1}')
if [ -z "$CHECK" ]; then
    echo "✅ Oscam stopped successfully"
else
    echo "⚠️ Some Oscam processes still running: $CHECK"
    echo "   Trying killall..."
    killall -9 oscam 2>/dev/null
    killall -9 OSCam 2>/dev/null
fi

echo ""
echo "🔄 Restarting CI+ helper..."
/etc/init.d/ciplushelper restart 2>/dev/null

echo ""
echo "✅ Done!"
echo "========================================="
