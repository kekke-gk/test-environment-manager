#! /usr/bin/env python3
import sys
import os.path
import lxc
import traceback
import apport
import subprocess
import time
import json
import requests
import mysql.connector
sys.path.append('../common')
import utils
import definevalue
import zabbix


def add_according_key(setting_dict, container_name, setup_element_key):
    setup_functions = ['zabbix-server', 'zabbix-agent', 'nagios3',
                       'nagios4', 'nrpe', 'redmine', 'fluentd']

    if setup_element_key in setup_functions:
        if container_name in setting_dict:
            setting_dict[container_name].append(setup_element_key)
        else:
            setting_dict[container_name] = [setup_element_key]


def create_setting_dict(config_info):
    setting_dict = {}
    for container_name in config_info.keys():
        for setup_element_key in config_info[container_name].keys():
            add_according_key(setting_dict, container_name, setup_element_key)

    return setting_dict


def create_path_dict(setting_dict):
    path_dict = {}
    for container_name in setting_dict.keys():
        for setup_func_name in setting_dict[container_name]:
            add_path_to_path_dict(setup_func_name, path_dict, container_name)

    return path_dict


def add_path_to_path_dict(setup_func_name, path_dict, container_name):
    if setup_func_name in 'zabbix-agent':
        path_dict[container_name] = definevalue.ZBX_AGT_PATH
    elif setup_func_name in 'zabbix-server':
        path_dict[container_name] = definevalue.ZBX_SRV_PATH
    elif setup_func_name in 'nrpe':
        path_dict[container_name] = definevalue.NRPE_PATH
    elif setup_func_name in 'redmine':
        path_dict[container_name] = definevalue.REDMINE_PATH
    elif setup_func_name in 'fluentd':
        path_dict[container_name] = definevalue.TD_AGENT_PATH
    elif setup_func_name in 'nagios3':
        path_dict[container_name] = definevalue.NAGIOS3_PATH
    elif setup_func_name in 'nagios4':
        path_dict[container_name] = definevalue.NAGIOS4_PATH


def add_process_name_to_path_dict(setup_func_name, process_dict,
                                  container_name):
    if setup_func_name in 'zabbix-agent':
        process_dict[container_name] = ['zabbix_agentd']
    elif setup_func_name in 'zabbix-server':
        process_dict[container_name] = \
            ['httpd', 'zabbix_server', 'zabbix_agentd']
    elif setup_func_name in 'nrpe':
        process_dict[container_name] = ['nrpe']
    elif setup_func_name in 'redmine':
        process_dict[container_name] = ['Passenger']
    elif setup_func_name in 'fluentd':
        process_dict[container_name] = ['td-agent']
    elif setup_func_name in ('nagios3' or 'nagios4'):
        process_dict[container_name] = ['httpd', 'nagios', 'ndo2db']


def create_process_dict(setting_dict):
    process_dict = {}
    for container_name in setting_dict.keys():
        for setup_func_name in setting_dict[container_name]:
            add_process_name_to_path_dict(setup_func_name, process_dict,
                                          container_name)

    return process_dict


def create_zabbix_hosts_dict(config_info):
    hosts_dict = {}
    for container_name in config_info.keys():
        if 'zabbix-server' in config_info[container_name].keys():
            hosts_dict[container_name] =\
                config_info[container_name]['zabbix-server']['target']

    return hosts_dict


def create_nagios_hosts_dict(config_info):
    hosts_dict = {}
    for container_name in config_info.keys():
        if 'nagios3' in config_info[container_name].keys():
            hosts_dict[container_name] =\
                config_info[container_name]['nagios3']['target']
        elif 'nagios4' in config_info[container_name].keys():
            hosts_dict[container_name] =\
                config_info[container_name]['nagios4']['target']

    return hosts_dict


def create_redmine_project_dict(config_info):
    project_dict = {}
    for container_name in config_info.keys():
        if 'redmine' in config_info[container_name].keys():
            project_dict[container_name] = {}
            project_dict[container_name]['project_name'] = \
                config_info[container_name]['redmine']['project_name']
            project_dict[container_name]['project_id'] = \
                config_info[container_name]['redmine']['project_id']

    return project_dict


def find_file(path_dict):
    print('Check files:')
    for path in path_dict.values():
        print(path + ' : ' + str(os.path.exists(path)))


def find_process(process_names):
    print('Check processes:')
    # If this value isn't provided, find_process function shows processes
    # when init process is running.
    time.sleep(40)

    with subprocess.Popen(['ps', 'ax'],
                          stdout=subprocess.PIPE,
                          universal_newlines=True) as proc:
        output = proc.stdout.read()
        for process_name in process_names:
            result = process_name in output
            print('Process %s: %r' % (process_name, result))


def find_zabbix_hosts(list_of_host_name):
    print('Check Zabbix hosts:')
    CMDS = [['service', 'httpd', 'start'],
            ['service', 'zabbix-server', 'start']]
    for run_command in CMDS:
        subprocess.call(run_command)

    auth_token = zabbix.get_authtoken_of_zabbix_server()

    for info in list_of_host_name:
        host_id = zabbix.get_zabbix_server_id(auth_token, info['host'])
        if not host_id:
            print('Host %s: False' % info['host'])
        else:
            print('Host %s: True' % info['host'])


def find_nagios_hosts(list_of_host_name):
    print('Check Nagios hosts:')
    CMDS = [['service', 'mysqld', 'start'],
            ['service', 'nagios', 'start'],
            ['service', 'ndo2db', 'start']]
    for run_command in CMDS:
        subprocess.call(run_command)

    try:
        connector = mysql.connector.connect(db='ndoutils',
                                            user='ndoutils',
                                            password='admin')
        cur = connector.cursor()
        cur.execute('SELECT display_name, address FROM nagios_hosts')
        rows = cur.fetchall()
        for host_name_and_ip in list_of_host_name:
            result = False
            for row in rows:
                if (host_name_and_ip['host'] == row[0] and
                        host_name_and_ip['ip'] == row[1]):
                    print('Host %s: True' % host_name_and_ip['host'])
                    result = True

            if not result:
                print('Host %s: False' % host_name_and_ip['host'])
    finally:
        cur.close()
        connector.close()


def find_redmine_project(info_of_project):
    print('Check Redmine projects:')
    subprocess.call(['service', 'httpd', 'start'])

    send_data = json.dumps(info_of_project)
    request_result = requests.post(definevalue.REDMINE_SERVER_ADDRESS,
                                   data=send_data,
                                   headers=definevalue.REDMINE_API_HEADER,
                                   auth=definevalue.REDMINE_USERNAME_PASSWORD)

    return_result = request_result.status_code == 200
    print('Project: %r' % return_result)


def start_find_process(container_name, function_name, info_of_check_item):
    print('%s:' % container_name)
    container = lxc.Container(container_name)
    container.start()
    container.get_ips(timeout=definevalue.TIMEOUT_VALUE)
    container.attach_wait(function_name, info_of_check_item)

    utils.shutdown_container(container)


def start_setup_test(yaml_file_path):
    config_info = utils.get_config_info(yaml_file_path)
    setting_dict = create_setting_dict(config_info)
    path_dict = create_path_dict(setting_dict)
    process_dict = create_process_dict(setting_dict)
    zabbix_hosts_dict = create_zabbix_hosts_dict(config_info)
    nagios_hosts_dict = create_nagios_hosts_dict(config_info)
    redmine_project_dict = create_redmine_project_dict(config_info)

    for container_name in setting_dict.keys():
        start_find_process(container_name, find_file,
                           path_dict[container_name])
        start_find_process(container_name, find_process,
                           process_dict[container_name])
    for container_name in zabbix_hosts_dict:
        start_find_process(container_name, find_zabbix_hosts,
                           zabbix_hosts_dict[container_name])
    for container_name in redmine_project_dict:
        start_find_process(container_name, find_redmine_project,
                           redmine_project_dict[container_name])
    for container_name in nagios_hosts_dict:
        start_find_process(container_name, find_nagios_hosts,
                           nagios_hosts_dict[container_name])


if __name__ == '__main__':
    argvs = sys.argv
    utils.exit_if_user_run_this_as_general_user()
    utils.exit_if_argument_is_not_given(len(argvs))

    start_setup_test(argvs[1])
