# PyBaiduPan
A python client for Baidu Pan to download, upload, and sync files.  Mainly design to use on nas.

Basically is a "reinventing wheel" project of [bypy](https://github.com/houtianze/bypy) to bypass 50M download limitation using app_id.
## requirements
1. python3
2. DecryptLogin


    pip install DecryptLogin
## installation
    git clone https://github.com/Mad-Devil/PyBaiduPan.git
## get started
    python bdpan.py [action] [pan_path] [local_path]
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
### first time use
Need to specify username and password for authorization.

     python bdpan.py -u your_username -P your_password
captcha or email/phone verification may be required.
### list
list files and directories in the path.

    python bdpan.py list /test
result:

    D   0.0B folder_1
    F 120.9K IMG_20151105_182551_1448110780674.jpg
    F   1.2M 07-03-15 19.49.06.png
    F   1.3M 07-03-15 19.49.00.png
    F   1.2M 07-03-15 19.48.44.png
    F   1.2M 07-03-15 19.48.24.png

### download
#### download file
    python bdpan.py download "/test/07-03-15 19.48.24.png"
#### download directory
    python bdpan.py download /test
#### download to specify path
    python bdpan.py download /test <local-path>
### upload
#### upload file
    python bdpan.py upload /test 1.txt
#### upload file and rename
    python bdpan.py upload /test/2.txt 1.txt
#### upload directory
    python bdpan.py upload /test <local-directory>
### sync
#### sync two directory
    python bdpan.py sync /test test_folder
sync action has the same effect as following commands:

    python bdpan.py download /test test_folder
    python bdpan.py upload /test test_folder
use -o mtime option to overwrite old files:

    python bdpan.py sync /test test_folder -o mtime
#### sync up
    python bdpan.py upload /test test_folder -o mtime -d
this command will make sure /test is same as test_folder.
#### sync down
    python bdpan.py download /test test_folder -o mtime -d
this command will make sure test_folder is same as /test.
## usage
### overwrite
    -o/--overwrite <mode>
overwrite option can use with upload/download/sync.

    python bdpan.py upload /test 1.txt -o mtime
    
*warning: this option may lead to **permanent** file loss. use it with caution.*

**mode** available mode: none, mtime, force. (default: "none")

|  mode        |                   description                  |
| :----------- | :--------------------------------------------- |
| none         | never overwrite. |
| mtime        | overwrite when a newer version of file(base on last modify time) is found. |
| force        | always overwrite.|
### delete extra
delete all extra files and directories in dst_path(pan_path for upload, local_path for download).

this option will make sure that dst_path is same as src_path.

    -d/--delete-extra
    
delete extra option can use with upload/download.

*warning: this option may lead to **permanent** file loss. use it with caution.*
 
### full usage 
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
## TODO list
+ ~~upload~~
+ ~~sync~~
+ ~~better exception handling~~
+ support external downloader (aria2)
+ robust request
+ proxy
+ test.py