#!/bin/sh

VERSION=2
BIN=/usr/bin/ciplushelper

[ -x "$BIN" ] || exit 0

# NB: non usare pgrep/killall/pidof per nome: questo script, lanciato come
# /etc/init.d/ciplushelper, ha comm="ciplushelper" e troverebbe (e ucciderebbe) se stesso.
# Si confronta invece l'eseguibile reale (/proc/<pid>/exe).
get_pids() {
    for p in /proc/[0-9]*; do
        case "$(readlink "$p/exe" 2>/dev/null)" in
            "$BIN"|"$BIN (deleted)") echo "${p#/proc/}" ;;
        esac
    done
}

is_running() {
    [ -n "$(get_pids)" ]
}

case "$1" in
    start)
        if is_running; then
            echo "ciplushelper is already running!"
        else
            printf "Running ciplushelper..."
            "$BIN" &
            sleep 2
            if is_running; then
                echo "done."
            else
                echo "ciplushelper failed to start!"
            fi
        fi
        ;;
    stop)
        PIDS="$(get_pids)"
        if [ -n "$PIDS" ]; then
            kill $PIDS 2>/dev/null
            i=0
            while is_running && [ $i -lt 5 ]; do sleep 1; i=$((i+1)); done
            is_running && kill -9 $(get_pids) 2>/dev/null
        fi
        echo "done."
        ;;
    restart)
        "$0" stop
        sleep 1
        "$0" start
        ;;
    status)
        if is_running; then
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
