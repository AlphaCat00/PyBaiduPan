# PyBaiduPan
A python client for Baidu Pan to download, upload, and sync files.  Mainly design to use on NAS.

## Feature
+ recurse download/upload
+ bypass 50M download limitation using app_id
+ rapid upload
+ directory sync
+ use a newer version of [baidu pan API](https://pan.baidu.com/union/document/basic)

## Requirements
python3 (>=3.6)
## Installation
    pip install pyBaiduPan
## Get Started
    BdPan [action] [pan_path] [local_path]
**action** available actions: list, download, upload, sync, logout. (default: "list")

|  action      |                   description                  |
| :----------- | :--------------------------------------------- |
| list         | list files and directories in the pan_path. |
| download     | download all files and directories in the pan_path to local_path. |
| upload       | upload all files and directories in the local_path to pan_path. |
| sync         | local_path and pan_path sync to each other. |
| logout       | delete all credentials. |

**pan_path** absolute path in Baidu Pan, which can be file or directory.

**local_path** local path, which can be file or directory.
### First Time Use
Need to specify username and password for authorization.

     BdPan -u your_username -P your_password
captcha or email/phone verification may be required.
### List
list files and directories in the path.

    BdPan list /test
result:

    D   0.0B folder_1
    F 120.9K IMG_20151105_182551_1448110780674.jpg
    F   1.2M 07-03-15 19.49.06.png
    F   1.3M 07-03-15 19.49.00.png
    F   1.2M 07-03-15 19.48.44.png
    F   1.2M 07-03-15 19.48.24.png

### Download
#### download File
    BdPan download "/test/07-03-15 19.48.24.png"
#### download directory
    BdPan download /test
#### download to specify path
    BdPan download /test <local-path>
### Upload
#### upload file
    BdPan upload /test 1.txt
#### upload file and rename
    BdPan upload /test/2.txt 1.txt
#### upload directory
    BdPan upload /test <local-directory>
### Sync
#### sync two directory
    BdPan sync /test test_folder
sync action has the same effect as following commands:

    BdPan download /test test_folder
    BdPan upload /test test_folder
use -o mtime option to overwrite old files:

    BdPan sync /test test_folder -o mtime
#### sync up
    BdPan upload /test test_folder -o mtime -d
this command will make sure /test is same as test_folder.
#### sync down
    BdPan download /test test_folder -o mtime -d
this command will make sure test_folder is same as /test.
## Usage
### Overwrite
    -o/--overwrite <mode>
overwrite option can use with upload/download/sync.

    BdPan upload /test 1.txt -o mtime
    
*warning: this option may lead to **permanent** file loss. use it with caution.*

**mode** available mode: none, mtime, force. (default: "none")

|  mode        |                   description                  |
| :----------- | :--------------------------------------------- |
| none         | never overwrite. |
| mtime        | overwrite when a newer version of file(base on last modify time) is found. |
| force        | always overwrite.|
### Delete Extra
delete all extra files and directories in dst_path(pan_path for upload, local_path for download).

this option will make sure that dst_path is same as src_path.

    -d/--delete-extra
    
delete extra option can use with upload/download.

*warning: this option may lead to **permanent** file loss. use it with caution.*
 
### Full Usage 
    usage: bdpan.py [-h] [-p LOCAL_PATH] [-b PAN_PATH] [-c CONF] [-s SESSION] [-u USERNAME] [-P PASSWORD] [-a APP_ID] [-o {none,mtime,force}] [-l LOG_FILE] [-d]
                    [action] [pan_path] [local_path]
    
     a Python client for Baidu Pan.
    
    positional arguments:
      action                available actions: list, download, upload, sync, logout. (default: "list")
                            list            list files and directories in the pan_path.
                            download        download all files and directories in the pan_path to local_path.
                            upload          upload all files and directories in the local_path to pan_path.
                            sync            local_path and pan_path sync to each other.
                            logout          delete all credentials.
      pan_path              absolute path in Baidu Pan, which can be file or directory.
      local_path            local path, which can be file or directory.
    
    optional arguments:
      -h, --help            show this help message and exit
      -p LOCAL_PATH, --local-path LOCAL_PATH
                            an alias of local_path. (default: ".")
      -b PAN_PATH, --pan-path PAN_PATH
                            an alias of pan_path. (default: "/")
      -c CONF, --conf CONF  the path of config file.
      -s SESSION, --session SESSION
                            the path to save session information.
      -u USERNAME, --username USERNAME
                            baidu username, only needed once for authorization.
      -P PASSWORD, --password PASSWORD
                            baidu password, only needed once for authorization. Warning: for security reason, don't save this in config file.
      -a APP_ID, --app-id APP_ID
                            baidu app id. recommended IDs: 498065, 309847, 778750, 250528(official), 265486, 266719. Some of them can bypass 50M download limitation.
      -o {none,mtime,force}, --overwrite {none,mtime,force}
                            none    never overwrite
                            mtime   overwrite when a newer version of file(base on last modify time) is found.
                            force   always overwrite.
      -l LOG_FILE, --log-file LOG_FILE
                            specify where to save log.
      -d, --delete-extra    delete all extra files and directories in dst_path. do NOT use this option unless you know exactly what you are doing.
## TODO List
+ ~~upload~~
+ ~~sync~~
+ ~~better exception handling~~
+ support external downloader (aria2)
+ robust request
+ proxy
+ tests