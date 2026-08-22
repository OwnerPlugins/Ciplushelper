#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# CI+ Helper + CI modules auto off/on - All in one
# Thank's Dimitrij and team Openatv & OpenPLi comunity
# the code refactory from lululla 20260822 (last update)

from os import popen, system as os_system
from os.path import exists
from Components.ActionMap import ActionMap
from Components.config import ConfigYesNo, config, getConfigListEntry, ConfigSubsection, ConfigSelection, ConfigNothing
from enigma import getDesktop, eTimer
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Screens import Standby
from Plugins.Plugin import PluginDescriptor
from Components.Sources.StaticText import StaticText
from Components.ConfigList import ConfigListScreen

from . import _, __version__


class ConfigAction(ConfigNothing):
    def __init__(self, action):
        ConfigNothing.__init__(self)
        self.action = action


# ----------------------------------------------------------------------
# CI auto off/on configuration
# ----------------------------------------------------------------------
config.plugins.cionoff = ConfigSubsection()
config.plugins.cionoff.ci_auto_check_module = ConfigYesNo(False)
config.plugins.cionoff.ci1delay = ConfigSelection(
    default="off",
    choices=[
        ("off",
         _("off")),
        ("1800",
         _("30 min")),
        ("3600",
         _("1 hour")),
        ("7200",
         _("2 hour")),
        ("10800",
         _("3 hour")),
        ("14400",
         _("4 hour"))])
config.plugins.cionoff.ci2delay = ConfigSelection(
    default="off",
    choices=[
        ("off",
         _("off")),
        ("1800",
         _("30 min")),
        ("3600",
         _("1 hour")),
        ("7200",
         _("2 hour")),
        ("10800",
         _("3 hour")),
        ("14400",
         _("4 hour"))])
config.plugins.cionoff.cimessage = ConfigYesNo(default=True)
config.plugins.cionoff.ci1restartservice = ConfigSelection(
    default="off",
    choices=[
        ("off",
         _("off")),
        ("1000",
         _("1 sec")),
        ("2000",
         _("2 sec")),
        ("3000",
         _("3 sec")),
        ("4000",
         _("4 sec")),
        ("5000",
         _("5 sec")),
        ("6000",
         _("6 sec")),
        ("7000",
         _("7 sec")),
        ("8000",
         _("8 sec")),
        ("9000",
         _("9 sec")),
        ("10000",
         _("10 sec")),
        ("11000",
         _("11 sec")),
        ("12000",
         _("12 sec"))])
config.plugins.cionoff.ci2restartservice = ConfigSelection(
    default="off",
    choices=[
        ("off",
         _("off")),
        ("1000",
         _("1 sec")),
        ("2000",
         _("2 sec")),
        ("3000",
         _("3 sec")),
        ("4000",
         _("4 sec")),
        ("5000",
         _("5 sec")),
        ("6000",
         _("6 sec")),
        ("7000",
         _("7 sec")),
        ("8000",
         _("8 sec")),
        ("9000",
         _("9 sec")),
        ("10000",
         _("10 sec")),
        ("11000",
         _("11 sec")),
        ("12000",
         _("12 sec"))])
config.plugins.cionoff.ci1onoffdelay = ConfigSelection(
    default="500",
    choices=[
        ("500",
         _("0.5 sec")),
        ("1000",
         _("1 sec")),
        ("2000",
         _("2 sec")),
        ("3000",
         _("3 sec")),
        ("4000",
         _("4 sec")),
        ("5000",
         _("5 sec")),
        ("6000",
         _("6 sec"))])
config.plugins.cionoff.ci2onoffdelay = ConfigSelection(
    default="500",
    choices=[
        ("500",
         _("0.5 sec")),
        ("1000",
         _("1 sec")),
        ("2000",
         _("2 sec")),
        ("3000",
         _("3 sec")),
        ("4000",
         _("4 sec")),
        ("5000",
         _("5 sec")),
        ("6000",
         _("6 sec"))])


try:
    CImodule1 = config.ci[0].enabled
except BaseException:
    CImodule1 = None
try:
    CImodule2 = config.ci[1].enabled
except BaseException:
    CImodule2 = None

CImodule1onoffdelay = False
CImodule2onoffdelay = False
_OnSession = None


# ----------------------------------------------------------------------
# Debug
# ----------------------------------------------------------------------
ciplushelper = "/etc/init.d/ciplushelper"
DEBUG_FILE = "/home/root/ciplus_debug.log"


def debug_log(msg):
    try:
        with open(DEBUG_FILE, "a") as f:
            f.write("[CI+ Helper] %s\n" % msg)
    except BaseException:
        pass


class Ciplushelper(Screen, ConfigListScreen):
    if getDesktop(0).size().width() >= 2560:
        skin = """
        <screen position="center,center" size="1360,700" title="CI+ Helper">
            <widget name="config" position="10,10" size="1340,580" font="Regular;40" itemHeight="60" scrollbarMode="showOnDemand" />
            <ePixmap pixmap="skin_default/buttons/red.png" position="10,640" size="200,6" alphatest="blend" transparent="1" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="220,640" size="200,6" alphatest="blend" transparent="1" />
            <widget source="key_red" render="Label" position="10,600" zPosition="1" size="200,40" font="Regular;30" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
            <widget source="key_green" render="Label" position="220,600" zPosition="1" size="200,40" font="Regular;30" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
        </screen>"""
    elif getDesktop(0).size().width() >= 1920:
        skin = """
        <screen position="center,center" size="1020,600" title="CI+ Helper">
            <widget name="config" position="10,10" size="1000,500" font="Regular;30" itemHeight="50" scrollbarMode="showOnDemand" />
            <ePixmap pixmap="skin_default/buttons/red.png" position="10,560" size="150,6" alphatest="blend" transparent="1" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="170,560" size="150,6" alphatest="blend" transparent="1" />
            <widget source="key_red" render="Label" position="10,530" zPosition="1" size="150,30" font="Regular;25" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
            <widget source="key_green" render="Label" position="170,530" zPosition="1" size="150,30" font="Regular;25" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
        </screen>"""
    else:
        skin = """
        <screen position="center,center" size="670,550" title="CI+ Helper">
            <widget name="config" position="10,10" size="650,350" font="Regular;24" itemHeight="40" scrollbarMode="showOnDemand" />
            <ePixmap pixmap="skin_default/buttons/red.png" position="10,395" size="120,6" alphatest="blend" transparent="1" />
            <ePixmap pixmap="skin_default/buttons/green.png" position="140,395" size="120,6" alphatest="blend" transparent="1" />
            <widget source="key_red" render="Label" position="10,370" zPosition="1" size="120,25" font="Regular;20" halign="center" valign="center" backgroundColor="#9f1313" foregroundColor="#ffffff" transparent="1" />
            <widget source="key_green" render="Label" position="140,370" zPosition="1" size="120,25" font="Regular;20" halign="center" valign="center" backgroundColor="#1f771f" foregroundColor="#ffffff" transparent="1" />
        </screen>"""

    def __init__(self, session):
        debug_log("=== CI+ Helper ConfigList opened ===")
        debug_log("CI+ Helper v" + __version__)
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("CI+ Helper") + " v" + __version__)
        self["key_red"] = StaticText(_("Cancel"))
        self["key_green"] = StaticText(_("Save"))
        self["shortcuts"] = ActionMap(
            [
                "SetupActions",
                "ShortcutActions"
            ],
            {
                "cancel": self.keyCancel,
                "red": self.keyCancel,
                "green": self.keySave,
                "ok": self.keyOK,
            }, -2
        )

        self.list = []
        self.build_list()
        ConfigListScreen.__init__(self, self.list, session=session)

        debug_log("ConfigList built with %d items" % len(self.list))

    def build_list(self):
        self.list = []

        # Model detection
        model = ""
        info_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/info.txt"
        if exists(info_path):
            try:
                with open(info_path, 'r') as f:
                    lines = f.read()
                    if "ciplushelper-arm" in lines:
                        model = "ciplushelper-arm"
                    elif "ciplushelper-mipsel32" in lines:
                        model = "ciplushelper-mipsel32"
                    elif "ciplushelper-zgemma-arm" in lines:
                        model = "ciplushelper-zgemma-arm"
                    else:
                        model = "Unknown"
            except Exception:
                pass
        self.model = model

        # Check if daemon is running
        self.ret = popen("pgrep -f ciplushelper").read()
        debug_log("pgrep output: '%s'" % self.ret.strip())

        # CI modules status
        ci_status = _("CI modules detected:") + " "
        if CImodule1 is not None and CImodule2 is not None:
            ci_status += _("Slot1: present, Slot2: present")
        elif CImodule1 is not None:
            ci_status += _("Slot1: present, Slot2: not present")
        elif CImodule2 is not None:
            ci_status += _("Slot1: not present, Slot2: present")
        else:
            ci_status += _("None")
        self.list.append(
            getConfigListEntry(
                ci_status,
                ConfigAction("separator")))

        # Auto-check module
        self.list.append(
            getConfigListEntry(
                _("Enable auto-check module"),
                config.plugins.cionoff.ci_auto_check_module))

        # Daemon status
        status = _("Running") if "ciplushelper" in self.ret else _(
            "Not running")
        self.list.append(
            getConfigListEntry(
                _("CI+ Helper status:") +
                " " +
                status,
                ConfigAction("separator")))

        # Autostart and binary management
        if model:
            if exists("/etc/rc2.d/S50ciplushelper"):
                self.list.append(
                    getConfigListEntry(
                        _("Disable ciplushelper autostart"),
                        ConfigAction("disable_autostart")))
            else:
                self.list.append(
                    getConfigListEntry(
                        _("Enable ciplushelper autostart"),
                        ConfigAction("enable_autostart")))

            # Start/Stop
            if "ciplushelper" in self.ret:
                self.list.append(
                    getConfigListEntry(
                        _("Stop ciplushelper"),
                        ConfigAction("stop")))
            else:
                self.list.append(
                    getConfigListEntry(
                        _("Start ciplushelper"),
                        ConfigAction("start")))

            # ARM binary installation - use the working binary from hd51/6.new/
            if "ciplushelper-arm" in model or "ciplushelper-zgemma-arm" in model:
                self.list.append(
                    getConfigListEntry(
                        _("Install WORKING binary (recommended)"),
                        ConfigAction("install_working_bin")))

        # Certificates
        cert_paths = [
            "/etc/ciplus/customer.pem",
            "/etc/ciplus/device.pem",
            "/etc/ciplus/root.pem",
            "/etc/ciplus/param",
            "/etc/ssl/certs/customer.pem"]
        if all(exists(p) for p in cert_paths):
            self.list.append(
                getConfigListEntry(
                    _("Remove /etc/ciplus"),
                    ConfigAction("remove_sert")))
        else:
            self.list.append(
                getConfigListEntry(
                    _("Install /etc/ciplus"),
                    ConfigAction("install_sert")))

        # Other actions
        self.list.append(
            getConfigListEntry(
                _("Open CI Assignment"),
                ConfigAction("open_ci_assignment")))

        # CI auto off/on settings (only if CI modules exist)
        if CImodule1 is not None or CImodule2 is not None:
            self.list.append(
                getConfigListEntry(
                    _("--- CI auto off/on settings ---"),
                    ConfigAction("separator")))
            if CImodule1 is not None:
                self.list.append(
                    getConfigListEntry(
                        _("Pause CI 1"),
                        config.plugins.cionoff.ci1delay))
                if config.plugins.cionoff.ci1delay.value != "off":
                    self.list.append(
                        getConfigListEntry(
                            _("  - Delay off-->on (CI 1)"),
                            config.plugins.cionoff.ci1onoffdelay))
                    self.list.append(
                        getConfigListEntry(
                            _("  - Restart service after off/on (CI 1)"),
                            config.plugins.cionoff.ci1restartservice))
            if CImodule2 is not None:
                self.list.append(
                    getConfigListEntry(
                        _("Pause CI 2"),
                        config.plugins.cionoff.ci2delay))
                if config.plugins.cionoff.ci2delay.value != "off":
                    self.list.append(
                        getConfigListEntry(
                            _("  - Delay off-->on (CI 2)"),
                            config.plugins.cionoff.ci2onoffdelay))
                    self.list.append(
                        getConfigListEntry(
                            _("  - Restart service after off/on (CI 2)"),
                            config.plugins.cionoff.ci2restartservice))
            if any(c is not None for c in (CImodule1, CImodule2)):
                self.list.append(
                    getConfigListEntry(
                        _("Show message after off/on"),
                        config.plugins.cionoff.cimessage))

        # Other actions
        self.list.append(
            getConfigListEntry(
                _("Update plugin"),
                ConfigAction("update_plugin")))
        self.list.append(
            getConfigListEntry(
                _("Supported models"),
                ConfigAction("about_ciplushelper")))

    def keyOK(self):
        current = self["config"].getCurrent()
        if current is None:
            return
        entry = current[1]
        if isinstance(entry, ConfigAction):
            action = entry.action
            self.execute_action(action)
        else:
            ConfigListScreen.keyOK(self)

    def execute_action(self, action):
        if not action or action == "separator":
            return
        debug_log("Action executed: %s" % action)
        plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

        if action == "enable_autostart":
            os_system("ln -sf /etc/init.d/ciplushelper /etc/rc2.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc3.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc4.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc5.d/S50ciplushelper")
            self.close()
        elif action == "disable_autostart":
            os_system(
                "rm -f /etc/rc2.d/S50ciplushelper /etc/rc3.d/S50ciplushelper /etc/rc4.d/S50ciplushelper /etc/rc5.d/S50ciplushelper")
            self.close()
        elif action == "start":
            debug_log("Starting ciplushelper...")
            os_system("%s start" % ciplushelper)
            ret = popen("pgrep -f ciplushelper").read()
            if ret:
                debug_log("Daemon started (PID: %s)" % ret.strip())
            else:
                debug_log("ERROR: daemon not started!")
            self.close()
        elif action == "stop":
            os_system("%s stop" % ciplushelper)
            self.close()
        elif action == "install_sert":
            debug_log("Installing certificates...")
            os_system("cp -R %s/ciplus /etc/ciplus" % plugin_path)
            os_system("cp /etc/ciplus/*.pem /etc/ssl/certs/ 2>/dev/null")
            self.close()
        elif action == "remove_sert":
            os_system("rm -rf /etc/ciplus")
            self.close()

        elif action == "install_working_bin":
            debug_log("Installing WORKING binary from hd51/6.new/...")
            # Install certificates in both places
            os_system("cp -R %s/ciplus /etc/ciplus" % plugin_path)
            os_system("cp /etc/ciplus/*.pem /etc/ssl/certs/ 2>/dev/null")
            # Copy init script from plugin to /etc/init.d/
            os_system(
                "cp %s/ciplushelper.sh /etc/init.d/ciplushelper && sed -i 's/\\r$//' /etc/init.d/ciplushelper && chmod 755 /etc/init.d/ciplushelper" %
                plugin_path)
            # Use the binary from hd51/6.new/ (1010KB) - the one that works
            os_system(
                "cp %s/ciplushelper_bin/hd51/6.new/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper" %
                plugin_path)
            # Debug: check file info
            os_system(
                "ls -la /usr/bin/ciplushelper >> /home/root/ciplus_debug.log")
            # Kill any existing instance and start
            os_system("killall ciplushelper 2>/dev/null || true")
            os_system("%s start" % ciplushelper)
            # Verify
            ret = popen("pgrep -f ciplushelper").read()
            if ret:
                debug_log("SUCCESS: Daemon started with PID: %s" % ret.strip())
                self.session.open(
                    MessageBox, _("CI+ Helper installed and running!\nPID: %s") %
                    ret.strip(), MessageBox.TYPE_INFO)
            else:
                debug_log("ERROR: Daemon not started!")
                # Try to run binary directly to see error
                debug_log("Trying to run /usr/bin/ciplushelper directly:")
                os_system(
                    "/usr/bin/ciplushelper 2>&1 | head -20 >> /home/root/ciplus_debug.log")
                self.session.open(
                    MessageBox,
                    _("ERROR: CI+ Helper not running!\nCheck /home/root/ciplus_debug.log"),
                    MessageBox.TYPE_ERROR)
            self.close()

        elif action == "open_ci_assignment":
            try:
                from Plugins.SystemPlugins.CommonInterfaceAssignment.plugin import CIselectMainMenu
                self.session.openWithCallback(self.close, CIselectMainMenu)
            except ImportError:
                self.session.open(
                    MessageBox,
                    _("Common Interface Assignment plugin not found. Please install it from System Plugins."),
                    MessageBox.TYPE_INFO)
                self.close()
        elif action == "update_plugin":
            cmd = "wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash"
            self.session.open(Console, _("Updating plugin..."), [cmd])
            self.close()
        elif action == "about_ciplushelper":
            installed = self.model if self.model else _("Unknown")
            message = _("CI+ Helper Plugin") + " v" + __version__ + "\n\n" + \
                _("Supported devices:") + "\n" + \
                "ARM: HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Pulse 4K(mini) / h17 / 8100s / hd61\n" + \
                "MIPSEL: Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Triplex / Cube\n\n" + \
                _("Other models may need '/etc/ciplus'") + "\n\n" + \
                _("Installed:") + " " + installed
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)

    def keySave(self):
        config.plugins.cionoff.save()
        global CImodule1onoffdelay, CImodule2onoffdelay
        pause_checkOffOnCi1Timer.stop()
        pause_checkOffOnCi2Timer.stop()
        CImodule1onoffdelayTimer.stop()
        CImodule2onoffdelayTimer.stop()
        CImodule1onoffdelay = False
        CImodule2onoffdelay = False
        if CImodule1 is not None and config.plugins.cionoff.ci1delay.value != "off":
            pause_checkOffOnCi1Timer.start(
                int(config.plugins.cionoff.ci1delay.value) * 1000, True)
        if CImodule2 is not None and config.plugins.cionoff.ci2delay.value != "off":
            pause_checkOffOnCi2Timer.start(
                int(config.plugins.cionoff.ci2delay.value) * 1000, True)
        self.close()

    def keyCancel(self):
        for x in self["config"].list:
            x[1].cancel()
        self.close()


# ----------------------------------------------------------------------
# Timers and callbacks for CI auto off/on
# ----------------------------------------------------------------------
pause_checkOffOnCi1Timer = eTimer()
pause_checkOffOnCi2Timer = eTimer()
pause_restartserviceTimer = eTimer()
CImodule1onoffdelayTimer = eTimer()
CImodule2onoffdelayTimer = eTimer()


def delayCI1moduleState():
    setCI1moduleState(force=True)


def setCI1moduleState(force=False):
    global CImodule1onoffdelay
    try:
        if CImodule1 is not None:
            prev = CImodule1.value
            if force or prev:
                if not force:
                    CImodule1.value = not CImodule1.value
                    CImodule1.save()
                if not CImodule1onoffdelay:
                    CImodule1onoffdelay = True
                    CImodule1onoffdelayTimer.start(
                        int(config.plugins.cionoff.ci1onoffdelay.value), True)
                    return
                else:
                    CImodule1.value = CImodule1onoffdelay
                    CImodule1.save()
                    CImodule1onoffdelay = False
                    extra_text = ""
                    if config.plugins.cionoff.ci1restartservice.value != "off" and _OnSession is not None:
                        pause_restartserviceTimer.start(
                            int(config.plugins.cionoff.ci1restartservice.value), True)
                        extra_text = "\n\n" + _("Restart service!")
                    if config.plugins.cionoff.cimessage.value and _OnSession is not None and Standby.inStandby is None:
                        _OnSession.open(
                            MessageBox,
                            _("CI 1 - auto off/on") +
                            extra_text,
                            MessageBox.TYPE_INFO,
                            timeout=3)
            if config.plugins.cionoff.ci1delay.value != "off":
                pause_checkOffOnCi1Timer.start(
                    int(config.plugins.cionoff.ci1delay.value) * 1000, True)
    except Exception as e:
        debug_log("setCI1moduleState error: %s" % e)


def delayCI2moduleState():
    setCI2moduleState(force=True)


def setCI2moduleState(force=False):
    global CImodule2onoffdelay
    try:
        if CImodule2 is not None:
            prev = CImodule2.value
            if force or prev:
                if not force:
                    CImodule2.value = not CImodule2.value
                    CImodule2.save()
                if not CImodule2onoffdelay:
                    CImodule2onoffdelay = True
                    CImodule2onoffdelayTimer.start(
                        int(config.plugins.cionoff.ci2onoffdelay.value), True)
                    return
                else:
                    CImodule2.value = CImodule2onoffdelay
                    CImodule2.save()
                    CImodule2onoffdelay = False
                    extra_text = ""
                    if config.plugins.cionoff.ci2restartservice.value != "off" and _OnSession is not None:
                        pause_restartserviceTimer.start(
                            int(config.plugins.cionoff.ci2restartservice.value), True)
                        extra_text = "\n\n" + _("Restart service!")
                    if config.plugins.cionoff.cimessage.value and _OnSession is not None and Standby.inStandby is None:
                        _OnSession.open(
                            MessageBox,
                            _("CI 2 - auto off/on") +
                            extra_text,
                            MessageBox.TYPE_INFO,
                            timeout=3)
            if config.plugins.cionoff.ci2delay.value != "off":
                pause_checkOffOnCi2Timer.start(
                    int(config.plugins.cionoff.ci2delay.value) * 1000, True)
    except Exception as e:
        debug_log("setCI2moduleState error: %s" % e)


def restartStartServiceCallback():
    if _OnSession is not None:
        try:
            start_ref = _OnSession.nav.getCurrentlyPlayingServiceOrGroup()
        except BaseException:
            start_ref = _OnSession.nav.getCurrentlyPlayingServiceReference()
        if start_ref:
            str_ref = start_ref.toString()
            if '%3a//' not in str_ref and str_ref.startswith("1:"):
                try:
                    _OnSession.nav.playService(
                        start_ref, checkParentalControl=False, forceRestart=True)
                except BaseException:
                    pass


pause_checkOffOnCi1Timer.callback.append(setCI1moduleState)
pause_checkOffOnCi2Timer.callback.append(setCI2moduleState)
CImodule1onoffdelayTimer.callback.append(delayCI1moduleState)
CImodule2onoffdelayTimer.callback.append(delayCI2moduleState)
pause_restartserviceTimer.callback.append(restartStartServiceCallback)


def OnSessionStart(reason, session):
    global _OnSession
    if reason == 0 and session and _OnSession is None:
        _OnSession = session
        if CImodule1 is not None and config.plugins.cionoff.ci1delay.value != "off":
            pause_checkOffOnCi1Timer.start(
                int(config.plugins.cionoff.ci1delay.value) * 1000, True)
        if CImodule2 is not None and config.plugins.cionoff.ci2delay.value != "off":
            pause_checkOffOnCi2Timer.start(
                int(config.plugins.cionoff.ci2delay.value) * 1000, True)


def main(session, **kwargs):
    session.open(Ciplushelper)


def menu(menuid, **kwargs):
    if menuid == "cam":
        return [(_("CI+ Helper"), main, "ci_helper", 30)]
    return []


def Plugins(**kwargs):
    pList = []
    pList.append(PluginDescriptor(
        name=_("CI+ Helper"),
        description=_("CI+ Helper and auto off/on for CI modules"),
        where=PluginDescriptor.WHERE_MENU,
        needsRestart=False,
        fnc=menu
    ))
    pList.append(PluginDescriptor(
        name=_("CI+ Helper"),
        description=_("CI+ Helper and auto off/on"),
        icon="plugin.png",
        where=PluginDescriptor.WHERE_PLUGINMENU,
        fnc=main
    ))
    pList.append(PluginDescriptor(
        where=PluginDescriptor.WHERE_SESSIONSTART,
        fnc=OnSessionStart
    ))
    return pList
