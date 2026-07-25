#!/bin/sh

VERSION=1

[ -x /usr/bin/ciplushelper ] || exit 0

case "$1" in
    start)
        if pgrep -x ciplushelper >/dev/null 2>&1; then
            echo "ciplushelper is already running!"
        else
            echo -n "Running ciplushelper..."
            /usr/bin/ciplushelper &
            sleep 2
            if pgrep -x ciplushelper >/dev/null 2>&1; then
                echo "done."
            else
                echo "ciplushelper failed to start!"
            fi
        fi
        ;;
    stop)
        killall ciplushelper 2>/dev/null
        echo "done."
        ;;
    restart)
        $0 stop
        sleep 3
        $0 start
        ;;
    status)
        if pgrep -x ciplushelper >/dev/null 2>&1; then
            echo "ciplushelper is running"
        else
            echo "ciplushelper is stopped"
        fi
        ;;
    enable_autostart)
        update-rc.d ciplushelper defaults 50
        echo "Autostart enabled."
        ;;
    disable_autostart)
        update-rc.d -f ciplushelper remove
        echo "Autostart disabled."
        ;;
    *)
        echo " "
        echo "Options: $0 {start|stop|restart|status|enable_autostart|disable_autostart}"
        echo " "
        exit 1
        ;;
esac

exit 0
