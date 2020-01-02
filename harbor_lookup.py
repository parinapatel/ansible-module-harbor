#!/usr/bin/python3

# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: harbor_lookup

short_description: This is module to interact with harbor registry.

version_added: "2.8"

description:
    - "This module provides latest tags for harbor registry for given tag."

options:
    registry_host:
        description:
            - This url for harbor registry.
        required: true
    registry_username:
        description:
            - This is username for login in harbor registry to access private repository
        required: false
    registry_password:
        description:
            - This is password for login in harbor registry to access private repository
        required: false
    src_tag:
        description:
            - Provide tag which you want to get duplicate tags.
        required: true
    repository:
        description:
            - This is repository name.
        required: true
requirements:
    - pydash
    - requests

author:
    - Parin Patel (@parinapatel)
'''

EXAMPLES = '''
# Find listed tags for given registry
- name: Find listed tags for given registry
  harbor_lookup:
    registry_host: hello world
    src_tag: develop
    repository: test_project/my_repo
  register : result

- debug:
  msg: "duplicate tags for given tag develop are {{ result.tags }}"

# Find listed tags for given registry in private repo
- name: Find listed tags for given registry
  harbor_lookup:
    registry_host: hello world
    src_tag: develop
    repository: test_project/my_repo
    registry_username: testuser
    registry_password: testpassword
  register : result

# fail the module
- name: Test failure of the module
  my_test:
    name: fail me
'''

RETURN = '''
src_tag:
    description: source tag which was provided by user
    type: str
    returned: always
tags:
    description: list of duplicate tags for given source file including source tag
    type: list
    returned: always
alternative_tags:
    description: list of duplicate tags for given source file
    type: list
    returned: always
'''

from ansible.module_utils.basic import AnsibleModule
from requests import get
from requests.auth import HTTPBasicAuth
from copy import deepcopy
import pydash as _


def find_registry_tags(registry_url, repo_name, src_tag, cred):
    url = "https://{}/api/repositories/{}/tags".format( registry_url, repo_name )
    payload = ""
    headers = {
        'Accept': "application/json",
        'Content-Type': "application/json",
        'Authorization': "Basic YWRtaW46SGFyYm9yMTIzNDU="
    }
    if cred:
        response = get( url, data=payload, headers=headers, auth=HTTPBasicAuth( cred['username'], cred['password'] ) )
    else:
        response = get( url, data=payload, headers=headers )
    # if response.status_code != 200:
    #     raise requests.ConnectTimeout
    response = response.json()
    replicated_tags = []
    digest = _.filter_( response, {"name": src_tag} )
    if not digest:
        return [src_tag]
    replicated_tags = _.filter_( response, {"digest": digest[0]['digest']} )
    return _.map_( replicated_tags, 'name' )


def run_module():
    # define available arguments/parameters a user can pass to the module
    module_args = dict(
        registry_host=dict( type='str', required=True ),
        registry_username=dict( type='str', required=False ),
        registry_password=dict( type='str', required=False ,no_log=True),
        src_tag=dict( type='str', required=True ),
        repository=dict( type='str', required=True )
    )

    # seed the result dict in the object
    # we primarily care about changed and state
    # change is if this module effectively modified the target
    # state will include any data that you want your module to pass back
    # for consumption, for example, in a subsequent task
    result = dict(
        changed=False,
        src_tag='',
        tags=[]
    )

    # the AnsibleModule object will be our abstraction working with Ansible
    # this includes instantiation, a couple of common attr would be the
    # args/params passed to the execution, as well as if the module
    # supports check mode
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=False
    )

    # if the user is working with this module in only check mode we do not
    # want to make any changes to the environment, just return the current
    # state with no modifications
    if module.check_mode:
        module.exit_json( **result )

    # manipulate or modify the state as needed (this is going to be the
    # part where your module will do what it needs to do)
    result['src_tag'] = module.params['src_tag']
    result['alternative_tags']= []
    try:
        if module.params['registry_username'] or module.params['registry_password']:
            result['tags'] = find_registry_tags( module.params['registry_host'], module.params['repository'],
                                                    module.params['src_tag'],
                                                    {'username': module.params['registry_username'],
                                                     'password': module.params['registry_password']
                                                     } )
        else:
            result['tags'] = find_registry_tags( module.params['registry_host'], module.params['repository'],
                                                    module.params['src_tag'], None )

        # use whatever logic you need to determine whether or not this module
        # made any modifications to your target
        if len(result['tags']) > 1:
            result['changed'] = True
            result['alternative_tags'] = deepcopy(result['tags'])
            result['alternative_tags'].remove(result['src_tag'])
    except Exception as e:
        module.fail_json(msg=str(e))

    # in the event of a successful module execution, you will want to
    # simple AnsibleModule.exit_json(), passing the key/value results
    module.exit_json( **result )


def main():
    run_module()


if __name__ == '__main__':
    main()
