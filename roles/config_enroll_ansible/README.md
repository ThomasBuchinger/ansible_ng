config_enroll_ansible
=========

Create an unpriviledged user without password and with sudo for ansible to use

Requirements
------------

None

Role Variables
--------------

Name | Description
---|---
enroll_username | Name of the user (default: "ansible")
ansible_public_key | A public key to authenticate the user

Dependencies
------------

None

Example Playbook
----------------

Just add it to your roles

    - hosts: servers
      vars:
        ansible_public_key: <key>
      roles:
         - config_enroll_ansible

License
-------

Apache 2.0

