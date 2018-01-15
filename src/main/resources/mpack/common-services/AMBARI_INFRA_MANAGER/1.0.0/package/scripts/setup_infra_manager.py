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

from resource_management.core.resources.system import Directory, Execute, File
from resource_management.libraries.functions.format import format
from resource_management.core.source import InlineTemplate, Template
from resource_management.libraries.resources.properties_file import PropertiesFile
from resource_management.libraries.functions.security_commons import update_credential_provider_path, HADOOP_CREDENTIAL_PROVIDER_PROPERTY_NAME


def setup_infra_manager():
  import params

  Directory([params.infra_manager_log_dir, params.infra_manager_pid_dir],
            mode=0755,
            cd_access='a',
            owner=params.infra_manager_user,
            group=params.user_group,
            create_parents=True
            )

  Directory([params.infra_manager_dir, params.infra_manager_conf],
            mode=0755,
            cd_access='a',
            owner=params.infra_manager_user,
            group=params.user_group,
            create_parents=True,
            recursive_ownership=True
            )

  File(format("{infra_manager_log_dir}/{infra_manager_log}"),
       mode=0644,
       owner=params.infra_manager_user,
       group=params.user_group,
       content=''
       )

  PropertiesFile(format("{infra_manager_conf}/infra-manager.properties"),
                 properties=params.infra_manager_properties
                 )

  File(format("{infra_manager_conf}/log4j2.xml"),
       content=InlineTemplate(params.infra_manager_log4j2_content),
       owner=params.infra_manager_user,
       group=params.user_group
       )

  File(format("{infra_manager_conf}/infra-manager-env.sh"),
       content=InlineTemplate(params.infra_manager_env_content),
       mode=0755,
       owner=params.infra_manager_user,
       group=params.user_group
       )