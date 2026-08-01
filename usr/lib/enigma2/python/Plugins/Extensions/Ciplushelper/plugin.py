#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# coded from lululla 20260725

from os import popen, system as os_system
from os.path import exists
from Components.ActionMap import ActionMap
from Components.config import ConfigYesNo, config
from Components.MenuList import MenuList
from enigma import getDesktop  # eTimer, eDVBCI_UI
from Screens.Console import Console
from Screens.MessageBox import MessageBox
from Screens.Screen import Screen
from Plugins.Plugin import PluginDescriptor

from . import _, __version__

config.misc.ci_auto_check_module = ConfigYesNo(False)

ciplushelper = "/etc/init.d/ciplushelper"
DEBUG_FILE = "/home/root/ciplus_debug.log"


def debug_log(msg):
    try:
        with open(DEBUG_FILE, "a") as f:
            f.write("[CI+ Helper] %s\n" % msg)
    except BaseException:
        pass


class Ciplushelper(Screen):
    if getDesktop(0).size().width() >= 2560:
        skin = """
        <screen position="center,center" size="1360,450" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="1340,430" font="Regular;40" itemHeight="60" scrollbarMode="showOnDemand" />
        </screen>"""
    elif getDesktop(0).size().width() >= 1920:
        skin = """
        <screen position="center,center" size="1020,350" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="1000,330" font="Regular;30" itemHeight="50" scrollbarMode="showOnDemand" />
        </screen>"""
    else:
        skin = """
        <screen position="center,center" size="670,280" title="CI+ helper menu" >
            <widget name="menu" position="10,10" size="660,260" scrollbarMode="showOnDemand" />
        </screen>"""

    def __init__(self, session):
        debug_log("=== CI+ Helper Menu opened ===")
        Screen.__init__(self, session)
        self.session = session
        self.setTitle(_("CI+ helper menu") + "  v" + __version__)

        menu_list = []
        menu_list.append((_("Supported models"), "about_ciplushelper"))

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
            except Exception:
                pass

        self.model = model
        self.ret = popen("pgrep ciplushelper").read()
        debug_log("Model: %s, ciplushelper running: %s" %
                  (model, "yes" if "ciplushelper" in self.ret else "no"))

        if model:
            # Autostart
            if exists("/etc/rc2.d/S50ciplushelper"):
                menu_list.append(
                    (_("Disable ciplushelper autostart"), "disable"))
            else:
                menu_list.append(
                    (_("Enable ciplushelper autostart"), "enable"))

            # Start/Stop
            if "ciplushelper" in self.ret:
                menu_list.append((_("Stop ciplushelper"), "stop"))
            else:
                menu_list.append((_("Start ciplushelper"), "start"))

            # ARM‑specific
            if "ciplushelper-arm" in model or "ciplushelper-zgemma-arm" in model:
                if not exists("/etc/cicert.bin"):
                    menu_list.append(
                        (_("Install version from Zgemma"), "install_cicert_bin"))
                else:
                    for i in range(2):
                        enable_file = "/etc/ciplus%d_enable" % i
                        disable_file = "/etc/ciplus%d_disable" % i
                        if exists(enable_file):
                            menu_list.append(
                                (_("Disable CI+ slot") +
                                 " " +
                                 str(i),
                                    "disable_ciplus%d" %
                                    i))
                        elif exists(disable_file):
                            menu_list.append(
                                (_("Enable CI+ slot") +
                                 " " +
                                 str(i),
                                    "enable_ciplus%d" %
                                    i))
                    menu_list.append(
                        (_("Install default version"), "install_default"))

            # Update init script if needed
            try:
                copy = True
                with open('/etc/init.d/ciplushelper', 'r') as f:
                    if "VERSION=1" in f.read():
                        copy = False
                if copy:
                    debug_log("Updating init script...")
                    cmd = "cp /usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper/ciplushelper.sh %s && chmod 755 %s" % (
                        ciplushelper, ciplushelper)
                    os_system(cmd)
                    debug_log("Init script updated")
            except Exception as e:
                debug_log("Error updating init script: %s" % e)

        # Certificates
        cert_paths = [
            "/etc/ciplus/customer.pem",
            "/etc/ciplus/device.pem",
            "/etc/ciplus/root.pem",
            "/etc/ciplus/param"]
        if all(exists(p) for p in cert_paths):
            menu_list.append((_("Remove") + " /etc/ciplus", "remove_sert"))
        else:
            menu_list.append((_("Install") + " /etc/ciplus", "install_sert"))

        menu_list.append((_("Open CI Assignment"), "open_ci_assignment"))
        menu_list.append((_("Update plugin"), "update_plugin"))

        self["menu"] = MenuList(menu_list)
        self["actions"] = ActionMap(
            ["OkCancelActions"], {
                "ok": self.run, "cancel": self.close}, -1)
        debug_log("Menu built with %d items" % len(menu_list))

    def run(self):
        returnValue = self["menu"].l.getCurrentSelection()
        if returnValue is None:
            return
        returnValue = returnValue[1]

        debug_log("Menu action selected: %s" % returnValue)

        plugin_path = "/usr/lib/enigma2/python/Plugins/Extensions/Ciplushelper"

        commands = {
            "enable": "ln -sf /etc/init.d/ciplushelper /etc/rc2.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc3.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc4.d/S50ciplushelper && ln -sf /etc/init.d/ciplushelper /etc/rc5.d/S50ciplushelper",
            "disable": "rm -f /etc/rc2.d/S50ciplushelper /etc/rc3.d/S50ciplushelper /etc/rc4.d/S50ciplushelper /etc/rc5.d/S50ciplushelper",
            "start": "%s start" %
            ciplushelper,
            "stop": "%s stop" %
            ciplushelper,
            "install_sert": "cp -R %s/ciplus /etc/ciplus" %
            plugin_path,
            "remove_sert": "rm -rf /etc/ciplus",
            "disable_ciplus0": "mv /etc/ciplus0_enable /etc/ciplus0_disable",
            "enable_ciplus0": "mv /etc/ciplus0_disable /etc/ciplus0_enable",
            "disable_ciplus1": "mv /etc/ciplus1_enable /etc/ciplus1_disable",
            "enable_ciplus1": "mv /etc/ciplus1_disable /etc/ciplus1_enable",
        }

        if returnValue in commands:
            debug_log("Executing command: %s" % commands[returnValue])
            os_system(commands[returnValue])
            self.close()
            return

        if returnValue == "auto_check":
            config.misc.ci_auto_check_module.value = not config.misc.ci_auto_check_module.value
            config.misc.ci_auto_check_module.save()
            self.close()
            return

        if returnValue == "install_cicert_bin":
            debug_log("Installing Zgemma binary with cicert.bin...")
            os_system("cp %s/cicert.bin /etc/cicert.bin" % plugin_path)
            for i in range(2):
                enable_file = "/etc/ciplus%d_enable" % i
                if not exists(enable_file):
                    os_system(
                        "echo 'rename ciplus*_enable to ciplus*_disable for deactivate ciplus certification of the module.' > %s" %
                        enable_file)
            if "ciplushelper" in self.ret:
                os_system("killall ciplushelper 2>/dev/null && sleep 2")
            os_system(
                "cp %s/ciplushelper_bin/zgemma-arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper" %
                plugin_path)
            if "ciplushelper" in self.ret:
                self.session.open(
                    Console,
                    _("Start ciplushelper"),
                    ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
            self.close()
            return

        if returnValue == "install_default":
            debug_log("Installing default ARM binary...")
            if "ciplushelper" in self.ret:
                os_system("killall ciplushelper 2>/dev/null && sleep 2")
            os_system(
                "cp %s/ciplushelper_bin/arm/ciplushelper /usr/bin/ciplushelper && chmod 755 /usr/bin/ciplushelper" %
                plugin_path)
            if "ciplushelper" in self.ret:
                self.session.open(
                    Console,
                    _("Start ciplushelper"),
                    ["/etc/init.d/ciplushelper start && echo 'Need restart GUI'"])
            self.close()
            return

        if returnValue == "open_ci_assignment":
            debug_log("Opening CI Assignment plugin...")
            try:
                from Plugins.SystemPlugins.CommonInterfaceAssignment.plugin import CIselectMainMenu
                self.session.openWithCallback(self.close, CIselectMainMenu)
            except ImportError:
                self.session.open(
                    MessageBox,
                    _("Common Interface Assignment plugin not found. Please install it from System Plugins."),
                    MessageBox.TYPE_INFO)
                self.close()
            return

        if returnValue == "update_plugin":
            debug_log("Updating plugin...")
            cmd = "wget -q --no-check-certificate https://raw.githubusercontent.com/OwnerPlugins/Ciplushelper/main/installer.sh -O - | /bin/bash"
            self.session.open(Console, _("Updating plugin..."), [cmd])
            self.close()
            return

        if returnValue == "about_ciplushelper":
            debug_log("Showing About...")
            installed = self.model if self.model else _("Unknown")
            message = _("CI+ Helper Plugin") + " v" + __version__ + "\n\n" + \
                _("Supported devices:") + "\n" + \
                "ARM: HD51 / VS1500 / Zgemma (H6/H7/H9combo(se)/H9twin(se)/H10) / Pulse 4K(mini) / h17 / 8100s / hd61\n" + \
                "MIPSEL: Mutant (hd1500/hd2400) / Xtrend (et8000/et10000) / Formuler (f1/f3/f4) / Triplex / Cube\n\n" + \
                _("Other models may need '/etc/ciplus'") + "\n\n" + \
                _("Installed:") + " " + installed
            self.session.open(MessageBox, message, MessageBox.TYPE_INFO)


# ----------------------------------------------------------------------
# PLUGIN REGISTRATION
# ----------------------------------------------------------------------

def main(session, **kwargs):
    session.open(Ciplushelper)


def menu(menuid, **kwargs):
    if menuid == "cicam":
        return [(_("CI+ helper"), main, "ci_helper", 30)]
    return []


def Plugins(**kwargs):
    # Forzato per test – il plugin appare sempre
    return [
        PluginDescriptor(
            name=_("CI+ helper") + " v" + __version__,
            description=_("CI+ helper for Enigma2"),
            icon="plugin.png",
            where=PluginDescriptor.WHERE_PLUGINMENU,
            fnc=main
        )
    ]


# def Plugins(**kwargs):
    # from Components.SystemInfo import SystemInfo
    # if SystemInfo.get("CommonInterface", 0):
    # return [
    # PluginDescriptor(
    # name=_("CI+ helper") + " v" + __version__,
    # description=_("CI+ helper for Enigma2"),
    # icon="plugin.png",
    # where=PluginDescriptor.WHERE_PLUGINMENU,
    # fnc=main
    # )
    # ]
    # return []
