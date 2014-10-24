#!/usr/bin/env python3
import os
import sys
import subprocess
import yaml
import lxc
sys.path.append("../common")
import definevalue
from utils import *
import clone

def prepare_setup_zabbix_server(argument):
    zabbix_conf_server = open("assets/zabbix_server.conf").read()
    zabbix_conf_httpd = open("assets/zabbix.conf").read()
    zabbix_conf_php = open("assets/zabbix.conf.php").read()
    argument.append(zabbix_conf_server)
    argument.append(zabbix_conf_httpd)
    argument.append(zabbix_conf_php)
    return argument


def install_config_files_of_zabbix(zabbix_conf_server_file,
                                   zabbix_conf_httpd_file,
                                   zabbix_conf_php_file):
    ZABBIX_CONF_SERVER_PATH = "/etc/zabbix/zabbix_server.conf"
    ZABBIX_CONF_HTTPD_PATH = "/etc/httpd/conf.d/zabbix.conf"
    ZABBIX_CONF_PHP_PATH = "/etc/zabbix/web/zabbix.conf.php"
    INSTALL_FILES = [[ZABBIX_CONF_SERVER_PATH, zabbix_conf_server_file],
                     [ZABBIX_CONF_HTTPD_PATH, zabbix_conf_httpd_file],
                     [ZABBIX_CONF_PHP_PATH, zabbix_conf_php_file]]
    for (path, content) in INSTALL_FILES:
        if os.path.exists(path):
            os.remove(path)

        install_file = open(path, "w")
        install_file.write(content)
        install_file.close()

    CMDS = [["service", "httpd", "restart"],
            ["service", "zabbix-server", "restart"]]
    for run_command in CMDS:
        subprocess.call(run_command)


def run_setup_zabbix_server(argument):
    install_config_files_of_zabbix(argument[1], argument[2], argument[3])

def prepare_setup_zabbix_agent(argument):
    zabbix_agentd_conf = open("assets/zabbix_agentd.conf").read()
    argument.append(zabbix_agentd_conf)
    return argument


def run_setup_zabbix_agent(argument):
    CONF_FILE_PATH = "/etc/zabbix/zabbix_agentd.conf"
    os.remove(CONF_FILE_PATH)

    server_ip_and_host_name = argument[0]
    output_data = argument[1]

    zabbix_agentd_conf = open(CONF_FILE_PATH, "w")
    SERVER_OLD = "Server=127.0.0.1"
    SERVER_NEW = "Server=" + server_ip_and_host_name["server_ipaddress"]
    SERVER_ACTIVE_OLD = "ServerActive=127.0.0.1"
    SERVER_ACTIVE_NEW = "Server=" + server_ip_and_host_name["server_ipaddress"]
    HOST_NAME_OLD = "Hostname=Zabbix server"
    HOST_NAME_NEW = "Hostname=" + server_ip_and_host_name["host_name"]
    replace_sequence = [[SERVER_OLD, SERVER_NEW],
                        [SERVER_ACTIVE_OLD, SERVER_ACTIVE_NEW],
                        [HOST_NAME_OLD, HOST_NAME_NEW]]
    for (old, new) in replace_sequence:
        output_data = output_data.replace(old, new)
    zabbix_agentd_conf.write(output_data)


def prepare_setup_nagios_server3(argument):
    print("Not implemented yet: prepare_setup_nagios_server3")
    return argument


def run_setup_nagios_server3(argument):
    print("Not implemented yet: run_setup_nagios_server3")


def prepare_setup_nagios_server4(argument):
    print("Not implemented yet: prepare_setup_nagios_server4")
    return argument


def run_setup_nagios_server4(argument):
    print("Not implemented yet: run_setup_nagios_server4")


def prepare_setup_nagios_nrpe(argument):
    nrpe_cfg = open("assets/nrpe.cfg").read()
    argument.append(nrpe_cfg)
    return argument


def run_setup_nagios_nrpe(argument):
    NRPE_FILE_PATH = "/etc/nagios/nrpe.cfg"
    os.remove(NRPE_FILE_PATH)

    nrpe_cfg = open(NRPE_FILE_PATH, "w")
    nrpe_cfg.write(argument[0])
    nrpe_cfg.close()


def prepare_setup_redmine(argument):
    file_list = ["database.yml", "configuration.yml", "my_setting"]

    for file_name in file_list:
        read_file = open(file_name)
        lines = read_file.readlines()
        read_file.close()

        argument.append(lines)

    return argument


def run_setup_redmine(argument):
    os.chdir("/var/lib/redmine")

    dbyml_file = open("/var/lib/redmine/config/database.yml", "w")
    dbyml_file.writelines(argument[1])
    dbyml_file.close()

    confyml_file = open("/var/lib/redmine/config/configuration.yml", "w")
    confyml_file.writelines(argument[2])
    confyml_file.close()

    subprocess.call("bundle install --without development test", shell = True)
    subprocess.call("bundle exec rake generate_secret_token", shell = True)
    subprocess.call("RAILS_ENV=production bundle exec rake db:migrate", shell = True)

    cmd = ["passenger-install-apache2-module", "--snippet"]
    subprocess.Popen(cmd,stdout = open("/etc/httpd/conf.d/passenger.conf", "w"))

    setting_file = open("my_setting", "w")
    setting_file.writelines(argument[3])
    setting_file.close()

    subprocess.call("mysql -uroot db_redmine < my_setting", shell = True)
    subprocess.call("chown -R apache /var/lib/redmine", shell = True)
    subprocess.call("chgrp -R apache /var/lib/redmine", shell = True)


def prepare_setup_fluentd(argument):
    td_agent_conf = open("assets/td-agent.conf").read()
    argument.append(td_agent_conf)
    return argument


def run_setup_fluentd(argument):
    TD_AGENT_FILE_PATH = "/etc/td-agent/td-agent.conf"
    os.remove(TD_AGENT_FILE_PATH)

    td_agent_conf = open(TD_AGENT_FILE_PATH, "w")
    td_agent_conf.write(argument[0])
    td_agent_conf.close()


SETUP_FUNCTIONS = {"zabbix-server": run_setup_zabbix_server,
                   "zabbix-agent": run_setup_zabbix_agent,
                   "nagios3": run_setup_nagios_server3,
                   "nagios4": run_setup_nagios_server4,
                   "nrpe": run_setup_nagios_nrpe,
                   "redmine": run_setup_redmine,
                   "fluentd": run_setup_fluentd}

PREPARE_FUNCTIONS = {run_setup_zabbix_server: prepare_setup_zabbix_server,
                     run_setup_zabbix_agent: prepare_setup_zabbix_agent,
                     run_setup_nagios_server3: prepare_setup_nagios_server3,
                     run_setup_nagios_server4: prepare_setup_nagios_server4,
                     run_setup_nagios_nrpe: prepare_setup_nagios_nrpe,
                     run_setup_redmine: prepare_setup_redmine,
                     run_setup_fluentd: prepare_setup_fluentd}


def get_function_and_arguments(info_of_container_name, list_of_key_in_info):
    list_of_setup_function = SETUP_FUNCTIONS.keys()
    return_list = []
    for key_in_info in list_of_key_in_info:
        if not key_in_info in list_of_setup_function:
            continue
        else:
            info_of_function = info_of_container_name[key_in_info]
            function_argument = []
            if info_of_function is not None:
                function_argument.append(info_of_function)
            return_list.append([SETUP_FUNCTIONS[key_in_info], function_argument])

    return return_list


def get_container_name_and_function_to_setup(config_info_name):
    list_of_container_name = config_info_name.keys()
    return_list = []
    for container_name in list_of_container_name:
        info_of_container_name = config_info_name[container_name]
        list_of_key_in_info = info_of_container_name.keys()
        setup_functions = get_function_and_arguments(info_of_container_name,
                                                     list_of_key_in_info)
        return_list.append([container_name, setup_functions])

    return return_list


def setup_container(container_name, run_function_names):
    print("Start setup process: %s" % container_name)
    container = lxc.Container(container_name)
    container.start()
    container.get_ips(timeout=definevalue.TIMEOUT_VALUE)

    for (run_function_name, argument) in run_function_names:
        run_argument = PREPARE_FUNCTIONS[run_function_name](argument)
        container.attach_wait(run_function_name, run_argument)

    shutdown_container(container)


def setup_containers(list_of_setup_containers):
    for (container_name, setup_function) in list_of_setup_containers:
        setup_container(container_name, setup_function)


def start_setup(yaml_file_path):
    config_info = get_config_info(yaml_file_path)
    list_of_setup_containers = \
        get_container_name_and_function_to_setup(config_info)
    setup_containers(list_of_setup_containers)


if __name__ == '__main__':
    argvs = sys.argv
    exit_if_user_run_this_as_general_user()
    exit_if_argument_is_not_given(len(argvs))

    start_setup(argvs[1])
