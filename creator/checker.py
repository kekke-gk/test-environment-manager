#!/usr/bin/env python3
import lxc
import os
import sys
import os.path
import definevalue
from utils import *

def is_container_existed(container):
    if lxc.Container(definevalue.containers_name[container]).defined:
        print_container_exist_message(definevalue.containers_name[container])
    else:
        print_container_non_exist_message(definevalue.containers_name[container])


def check_container_exist():
    is_container_existed("base")
    is_container_existed("zabbix_server22")
    is_container_existed("zabbix_server20")
    is_container_existed("zabbix_agent22")
    is_container_existed("zabbix_agent20")
    is_container_existed("nagios_server3")
    is_container_existed("nagios_server4")
    is_container_existed("nagios_nrpe")
    is_container_existed("hatohol_build")
    is_container_existed("hatohol_rpm")
    is_container_existed("fluentd")
    is_container_existed("redmine")
    print_new_line()


def is_file_usable(file_path):
    if os.path.isfile(file_path):
        print("\"%s\" file exists: True" % file_path)
    else:
        print("\"%s\" file exists: False" % file_path)


def is_directory_usable(directory_path):
    if os.path.isdir(directory_path):
        print("\"%s\" directory exists: True" % directory_path)
    else:
        print("\"%s\" directory exists: False" % directory_path)


def check_zabbix_server_container(container_name):
    print_container_name(container_name)
    container = lxc.Container(definevalue.containers_name[container_name])
    container.start()
    container.attach_wait(is_file_usable, "/usr/sbin/zabbix_server")
    container.attach_wait(is_file_usable, "/usr/sbin/zabbix_agentd")

    shutdown_container(container)
    print_new_line()


def check_zabbix_agent_container(container_name):
    print_container_name(container_name)
    container = lxc.Container(definevalue.containers_name[container_name])
    container.start()
    container.attach_wait(is_file_usable, "/usr/sbin/zabbix_agentd")

    shutdown_container(container)
    print_new_line()

def check_nagios_server3_container():
    container_name = "nagios_server3"
    print_container_name(container_name)
    container = lxc.Container(definevalue.containers_name[container_name])
    container.start()
    container.attach_wait(is_file_usable, "/usr/sbin/nagios")
    container.attach_wait(is_file_usable, "/usr/sbin/ndo2db")

    shutdown_container(container)
    print_new_line()


def check_nagios_server4_container():
    container_name = "nagios_server4"
    print_container_name(container_name)
    container = lxc.Container(definevalue.containers_name[container_name])
    container.start()
    container.attach_wait(is_file_usable, "/usr/local/nagios/bin/nagios")
    container.attach_wait(is_file_usable, "/usr/local/nagios/bin/ndo2db")

    shutdown_container(container)
    print_new_line()


def check_nagios_nrpe_container():
    container_name = "nagios_nrpe"
    print_container_name(container_name)
    container = lxc.Container(definevalue.containers_name[container_name])
    container.start()
    container.attach_wait(is_file_usable, "/etc/nagios/nrpe.cfg")
    container.attach_wait(is_directory_usable, "/usr/lib64/nagios/plugins/")

    shutdown_container(container)
    print_new_line()


def check_hatohol_container():
    container_name = definevalue.containers_name["hatohol_rpm"]
    print_container_name(container_name)
    container = lxc.Container(container_name)
    container.start()
    container.attach_wait(is_file_usable, "/usr/sbin/hatohol")

    shutdown_container(container)
    print_new_line()


def check_redmine_container():
    container_name = definevalue.containers_name["redmine"]
    print_container_name(container_name)
    container = lxc.Container(container_name)
    container.start()
    container.attach_wait(is_directory_usable, "/var/lib/redmine")
    container.attach_wait(is_file_usable, "/usr/local/bin/ruby")

    shutdown_container(container)
    print_new_line()


def check_fluentd_container():
    container_name = definevalue.containers_name["fluentd"]
    print_container_name(container_name)
    container = lxc.Container(container_name)
    container.start()
    container.attach_wait(is_file_usable, "/usr/sbin/td-agent")

    shutdown_container(container)
    print_new_line()


def check_container_successfully():
    check_hatohol_container()
    check_zabbix_server_container("zabbix_server22")
    check_zabbix_server_container("zabbix_server20")
    check_zabbix_agent_container("zabbix_agent22")
    check_zabbix_agent_container("zabbix_agent20")
    check_nagios_server3_container()
    check_nagios_server4_container()
    check_nagios_nrpe_container()
    check_redmine_container()
    check_fluentd_container()


if __name__ == '__main__':
    if not os.geteuid() == 0:
        print("You need root permission to use this script.")
        sys.exit(1)

    check_container_exist()
    check_container_successfully()