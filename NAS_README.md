# From Zero to NAS

## TrueNAS Config
* Configure weelky SMART Test 
* Root ZFS pool must be named "/mnt/data"
  * Add Child-Datasets: bs13, ng7a, internal
* Configure weelky SNAPSHOT task per dataset
* Configure ZFS dataset "internal"
* Configure Disk Descriptions
* Configure NFS share for root pool (enable "all directories"-option)
* Configure and install 2 CentOS VMs (sparse ZFS volumes

## Setup Ansible controller
* login as root
* Install packages: epel-release, ansible, git
* Clone NAS Repo
* Generate SSH keys or ansible
* Configure NAS inventory file
  * Copy the new SSH keys to vault
