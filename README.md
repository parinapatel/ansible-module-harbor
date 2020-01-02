# ansible-module-harbor
This ansible module for Harbor Registry 
    This module provides latest tags for harbor registry for given tag.

  * This module is maintained by The Ansible Community
OPTIONS (= is mandatory):
```
= registry_host
        This url for harbor registry.


- registry_password
        This is password for login in harbor registry to access private repository
        [Default: (null)]

- registry_username
        This is username for login in harbor registry to access private repository
        [Default: (null)]

= repository
        This is repository name.


= src_tag
        Provide tag which you want to get duplicate tags.

```

AUTHOR: Parin Patel (@parinapatel)
        METADATA:
          status:
          - preview
          supported_by: community
        

EXAMPLES:
```
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
```

RETURN VALUES:
```
src_tag:
    description: source tag which was provided by user
    type: str
    returned: always
tags:
    description: list of duplicate tags for given source file
    type: list
    returned: always
```

