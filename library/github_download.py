#!/usr/bin/python

# Copyright: (c) 2020, Thomas Buchinger <thomas.buchinger@outlook.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

DOCUMENTATION = r'''
---
module: github_download

short_description: Download Asset from GitHub releases

# If this is part of a collection, you need to use semantic versioning,
# i.e. the version is of the form "2.5.0" and not "2.4".
version_added: "1.0.0"

description: Download a file from Github's Releases page

options:
    tag:
        description: Release Tag.
        required: true
        type: str
    name:
        description: Download first file matching this regex
        required: false
        type: str
    dest:
        description: Download destination 
        required: true
        type: str

author:
    - Thomas Buchinger (@ThomasBuchinger)
'''

EXAMPLES = r'''
# Download first asset
- github_download:
    tag: latest
    dest: /tmp/

# Download a specific file
- github_release:
    tag: latest
    name: source.tar.gz
    dest: /tmp
'''

RETURN = r'''
# These are examples of possible return values, and in general should use other names for return values.
original_message:
    description: The original name param that was passed in.
    type: str
    returned: always
    sample: 'hello world'
message:
    description: The output message that the test module generates.
    type: str
    returned: always
    sample: 'goodbye'
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.urls import fetch_url, fetch_file
import json
import re
import os

def download_file(module, url, download_dir, name):
  dest_path = os.path.join(download_dir, name)
  # Check file permissions
  if not os.access(download_dir, os.R_OK):
    module.fail_json(msg="Destination %s is not readable" % (dest_path))
  if not os.access(download_dir, os.W_OK):
    module.fail_json(msg="Destination %s is not writable" % (dest_path))

  # Download
  tmpfile = fetch_file(module, url, method='GET')

  # Move temporay file to destination raise an error if copy has no permission on dest
  os.replace(tmpfile, dest_path)
  return True

def run_module():
    module_args = dict(
        repo    = dict(type='str',required=True),
        tag     = dict(type='str', required=False, default="latest"),
        pattern = dict(type='str', required=False, default="*.tar.gz"),
        dest    = dict(type='path', required=True, aliases=['path'])
    )


    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True,
        add_file_common_args=True
    )
    # seed the result dict in the object
    result = dict(
        changed = False,
        path = '',
        asset = '',
        url = '',
        downloaded=False
    )

    repo_name    = module.params['repo']
    tag_name     = module.params['tag']
    api_uri      = "https://api.github.com/repos/{}/releases/{}".format(repo_name, tag_name)
    regex        = module.params['pattern']
    dest         = module.params['dest']

    # Find the download dir. 
    # If dest is already a directory os.path.dirname would return the parent dir
    if os.path.exists(dest) and os.path.isdir(dest):
      download_dir  = dest
      dest_filename = ''
    else:
      download_dir  = os.path.dirname(dest)
      dest_filename = os.path.basename(dst) 
    
    # Validate Parameters
    if not re.match('^[A-Za-z0-9\.\_\-]+/[A-Za-z\.\_\-]+$', repo_name):
      module.fail_json(msg="repo should be author/repo! Only alphanumeric characters, period '.', underscore '_' and dash '-' allowed") 
    if not os.path.exists(download_dir):
      module.fail_json(msg="destination directory does not exist!")

    # === Gihub API ===
    # Query Github API for release
    response, info = fetch_url(module, api_uri, method='GET')
    if info['status'] == 404:
      module.fail_json(msg="Repository https://github.com/{} has no release \"{}\"".format(repo_name, tag_name))
    elif info['status'] != 200:
      message="HTTP Error: {} | {}".format(info['status'], str(response.read()))
      module.fail_json(msg=message)
    
    # Find download link
    release_data = json.loads(response.read())
    for asset in release_data['assets']:
      if re.match(regex, asset['name']):
        result['asset']=asset['name']
        result['url']=asset['browser_download_url']
        dest_filename = asset['name'] if dest_filename == '' else dest_filename
        result['path']=os.path.join(download_dir,dest_filename)
        break
    # End for assets

    # Check if file exists
    if module.check_mode:
        result['changed']=os.path.exists(result['path'])
        module.exit_json(**result)


    # === Download file and set attributes ===
    if not os.path.exists(result['path']):
      result['downloaded'] = download_file(module, result['url'], download_dir, dest_filename)
    
    file_args = module.load_file_common_arguments(module.params)
    file_attrs_changed = module.set_fs_attributes_if_different(file_args, False)

    result['changed'] = result['downloaded'] or file_attrs_changed
    module.exit_json(**result)

def main():
    run_module()


if __name__ == '__main__':
    main()


