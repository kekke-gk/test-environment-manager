#!/usr/bin/env python3
import lxc
import os
import sys

def print_success_message(name):
    print("Create Container: %s" % name)


if not os.geteuid() == 0:
    print("You need root permission to use this script.")
    sys.exit(1)


base_name = "env_base"
base = lxc.Container(base_name)
if not base.defined:
    base.create("centos")
    print_success_message("Create Container: %s" % base_name)

    base.start()
    base.get_ips(timeout=30)
    base.attach_wait(lxc.attach_run_command,
                     ["yum", "upgrade", "-y"])

    if not base.shutdown(30):
        base.stop()


zabbix_server22_name = "env_zabbix_server22"
zabbix_server22 = lxc.Container(zabbix_server22_name)
if not zabbix_server22.defined:
    zabbix_server22 = base.clone(zabbix_server22_name, bdevtype="aufs",
                                 flags=lxc.LXC_CLONE_SNAP_SHOT)
    print_success_message(zabbix_server22_name)

    rpm_url = "http://repo.zabbix.com/zabbix/2.2/rhel/6/x86_64/zabbix-release-2.2-1.el6.noarch.rpm"
    zabbix_server22.start()
    zabbix_server22.get_ips(timeout=30)
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["rpm", "-ivh", rpm_url])
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["yum", "install", "-y",
                                 "mysql-server", "httpd",
                                 "zabbix-server-mysql",
                                 "zabbix-web-mysql"])

    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["service", "mysqld", "start"])
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["chkconfig", "mysqld", "on"])

    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["mysql", "-uroot", "-e",
                                 "create database zabbix character set utf8 collate utf8_bin;"])
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["mysql", "-uroot", "-e",
                                 "grant all privileges on zabbix.* to zabbix@localhost identified by 'zabbix';"])

    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["service", "httpd", "start"])
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["chkconfig", "httpd", "on"])
    zabbix_server22.attach_wait(lxc.attach_run_command,
                                ["chkconfig", "zabbix-server", "on"])


    if not zabbix_server22.shutdown(30):
        zabbix_server22.stop()