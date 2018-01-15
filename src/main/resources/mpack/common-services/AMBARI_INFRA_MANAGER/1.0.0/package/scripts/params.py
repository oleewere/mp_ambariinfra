#!/usr/bin/env python

"""
Licensed to the Apache Software Foundation (ASF) under one
or more contributor license agreements.  See the NOTICE file
distributed with this work for additional information
regarding copyright ownership.  The ASF licenses this file
to you under the Apache License, Version 2.0 (the
"License"); you may not use this file except in compliance
with the License.  You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

"""

import os
from ambari_commons.constants import AMBARI_SUDO_BINARY
from resource_management.libraries.functions.default import default
from resource_management.libraries.functions.format import format
from resource_management.libraries.functions.is_empty import is_empty
from resource_management.libraries.script.script import Script
import status_params

def get_port_from_url(address):
  if not is_empty(address):
    return address.split(':')[-1]
  else:
    return address

def get_name_from_principal(principal):
  if not principal:  # return if empty
    return principal
  slash_split = principal.split('/')
  if len(slash_split) == 2:
    return slash_split[0]
  else:
    at_split = principal.split('@')
    return at_split[0]

# config object that holds the configurations declared in the -site.xml file
config = Script.get_config()
tmp_dir = Script.get_tmp_dir()

# shared configs
java_home = config['hostLevelParams']['java_home']
ambari_java_home = default("/commandParams/ambari_java_home", None)
java64_home = ambari_java_home if ambari_java_home is not None else java_home
java_exec = format("{java64_home}/bin/java")


sudo = AMBARI_SUDO_BINARY
# security_enabled = status_params.security_enabled

user_group = config['configurations']['cluster-env']['user_group']

credential_store_enabled = False
if 'credentialStoreEnabled' in config:
  credential_store_enabled = config['credentialStoreEnabled']

infra_manager_conf = "/usr/lib/ambari-infra-manager/conf"

# infra-manager pid file
infra_manager_pid_dir = status_params.infra_manager_pid_dir
infra_manager_pid_file = status_params.infra_manager_pid_file

zookeeper_hosts_list = config['clusterHostInfo']['zookeeper_hosts']
zookeeper_hosts_list.sort()
# get comma separated list of zookeeper hosts from clusterHostInfo
zookeeper_hosts = ",".join(zookeeper_hosts_list)

#####################################
# Infra Manager configs
#####################################

# infra-manager-env configs
infra_manager_dir = '/usr/lib/ambari-infra-manager'
infra_manager_user = config['configurations']['infra-manager-env']['infra_manager_user']
infra_manager_log_dir = config['configurations']['infra-manager-env']['infra_manager_log_dir']
infra_manager_log = 'infra-manager.log'
# infra_manager_opts = config['configurations']['infra-manager-env']["infra_manager_opts"]
infra_manager_debug_enabled = str(config['configurations']['infra-manager-env']["infra_manager_debug_enabled"]).lower()
infra_manager_debug_suspend_enabled = str(config['configurations']['infra-manager-env']["infra_manager_debug_suspend_enabled"]).lower()
infra_manager_debug_port = config['configurations']['infra-manager-env']["infra_manager_debug_port"]
infra_manager_app_max_memory = config['configurations']['infra-manager-env']["infra_manager_app_max_memory"]
infra_manager_batch_db_dir = config['configurations']['infra-manager-env']["infra_manager_batch_db_dir"]
infra_manager_server_data_folder = config['configurations']['infra-manager-env']["infra_manager_server_data_folder"]
infra_manager_env_content = config['configurations']['infra-manager-env']['content']


infra_solr_znode = '/infra-solr'
# archive_service_logs_use_external_solr = default('/configurations/infra-manager-properties/infra-manager.jobs.solr_data_export.archive_service_logs.solr.use_external', False)
#
# if archive_service_logs_use_external_solr:
#   archive_service_logs_solr_zk_znode = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.solr.external_solr_zk_znode']
#   archive_service_logs_solr_zk_quorum = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.solr.external_solr_zk_quorum']
# else:
archive_service_logs_solr_zk_znode = infra_solr_znode

archive_service_logs_solr_zk_quorum = ""
zookeeper_port = default('/configurations/zoo.cfg/clientPort', None)
if 'zookeeper_hosts' in config['clusterHostInfo']:
  for host in config['clusterHostInfo']['zookeeper_hosts']:
    if archive_service_logs_solr_zk_quorum:
      archive_service_logs_solr_zk_quorum += ','
    archive_service_logs_solr_zk_quorum += host + ":" + str(zookeeper_port)

#Infra Manager log4j2 properties
infra_manager_log_maxfilesize = default('/configurations/infra-manager-log4j2/infra_manager_log_maxfilesize',10)
infra_manager_log_maxbackupindex = default('/configurations/infra-manager-log4j2/infra_manager_log_maxbackupindex',10)
infra_manager_log4j2_content = config['configurations']['infra-manager-log4j2']['content']


#Infra Manager
infra_manager_properties = {}

# default values
infra_manager_properties['infra-manager.batch.db.file'] = 'job-repository.db'
infra_manager_properties['infra-manager.batch.db.init'] = 'false'
infra_manager_properties['management.security.enabled'] = 'false'
infra_manager_properties['management.health.solr.enabled'] = 'false'
infra_manager_port = 61890
infra_manager_properties['infra-manager.server.port'] = infra_manager_port

# load config values
infra_manager_properties = dict(infra_manager_properties.items() + \
                            dict(config['configurations']['infra-manager-properties']).items())

# job configurations
# archive service logs
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.zoo_keeper_connection_string'] = archive_service_logs_solr_zk_quorum + archive_service_logs_solr_zk_znode
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.collection'] = config['configurations']['logsearch-properties']['logsearch.solr.collection.service.logs']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.query_text'] = 'logtime:[${start} TO ${end}]'
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.filter_query_text'] = '(logtime:${logtime} AND id:{${id} TO *]) OR logtime:{${logtime} TO ${end}]'
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.sort_column[0]'] = 'logtime'
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.solr.sort_column[1]'] = 'id'
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.read_block_size'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.read_block_size']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.write_block_size'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.write_block_size']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.destination'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.destination']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.local_destination_directory'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.local_destination_directory']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.file_name_suffix_column'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.file_name_suffix_column']
infra_manager_properties['infra-manager.jobs.solr_data_export.archive_service_logs.file_name_suffix_date_format'] = config['configurations']['infra-manager-properties']['infra-manager.jobs.solr_data_export.archive_service_logs.file_name_suffix_date_format']


#####################################
# Smoke command
#####################################
infra_manager_hosts = default('/clusterHostInfo/infra_manager_server_hosts', None)
infra_manager_host = ""
if infra_manager_hosts is not None and len(infra_manager_hosts) > 0:
  infra_manager_host = infra_manager_hosts[0]
smoke_infra_manager_cmd = format('curl -k -s -o /dev/null -w "%{{http_code}}" http://{infra_manager_host}:{infra_manager_port}/ | grep 200')
