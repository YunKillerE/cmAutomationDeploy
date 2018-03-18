#!/usr/bin/env python2

import os
import sys
import time
import shutil
import commands
import yaml
from cm_api.api_client import ApiResource


'''
1,stop cluster
        > stop app
        > stop flink
        > stop ignite
        > stop tomcat
        > stop schedule
        > stop eft

2,deploy application
        > deploy eft
        > deploy schedule
        > deploy tomcat
        > deploy ignite
        > deploy flink
        > deploy app
3,start clouster
        > start app
        > start flink
        > start ignite
        > start tomcat
        > start schedule
        > start eft
'''

'''
function:

        1,stopService: if $1=stop ;then stop service $2;fi
          stopAllService: if $1=stopAll ;then stop ALL service;fi
        2,startService: if $1=start;then start service $2;fi
          startAllService: if $1=startAll;then start all servic;fi
        3,deployApp: if $1=deploy;then deploy app $2;fi
          deployAll: if $2=all;then deploy all app;fi
        4,automation: stopAllService deployAll startAllService

'''


API_VERSION = "7"
CLUSTER_NAME = "cluster"
ANSIBLE_GIT_URL = "git@10.134.6.38:zhangxl/ansible-prepare.git"
ALLINONE_GIT_URL = "git@10.134.6.38:zhangxl/all_in_one.git"
APPLICATION_LIST = ["flink", "eft", "schedule", "tomcat", "ignite", "app"]
listSh = ["00_ping.sh", "30_deploy_es.sh", "31_deploy_monitor.sh",
        "32_deploy_jmxtrans.sh", "33_deploy_logstash.sh", "34_monit_tools.sh",
        "35_deploy_csd.sh", "51_deploy_tomcat.sh", "53_deploy_eft.sh",
        "93_deploy_schedule.sh", "94_deploy_batch.sh", "95_deploy_ignite.sh",
        "96_deploy_flink.sh", "97_deploy_app.sh"]
TODAY_TIME = commands.getoutput("date +%Y%m%d")
APP_PROCESSING_LIST = ["Stop_01_FBX_Transaction", "Stop_00_Compute","Stop_00_Compute_1001","Stop_04_Compute_1002","Stop_03_Record_Preprocessing"]

SCRIPT_ROOT = os.getcwd()
envirement = sys.argv[1]
ansible_path = str.format(SCRIPT_ROOT)+"/ansible-prepare/env/"+envirement
allinone_path = str.format(SCRIPT_ROOT)+"/all_in_one" #/build_bin/build_release.py"

os.system("ls "+ansible_path)
os.system("ls "+allinone_path)

print("============================== variable =================================")
print("current root path: "+SCRIPT_ROOT)
print("current envirenment: "+envirement)
print("current ansible root path: "+ansible_path)
print("current time: "+TODAY_TIME)
for i in APPLICATION_LIST:
    print("application list: "+i+"\t")
for i in  listSh:
    print("execute ansible shell list: "+i+"\t")
print("============================== variable =================================")


#Action Command Function
def action_command(SERVICE_NAME,COMMAND_NAME):
    try:
        CLUSTER = create_cluster()
        service_command = CLUSTER.get_service(SERVICE_NAME)
        service_command.service_command_by_name(COMMAND_NAME)
    except:
        print("may be "+SERVICE_NAME+" or "+COMMAND_NAME+" dosn't exist")

#Stop service
def stop_service(SERVICE_NAME):
    CLUSTER = create_cluster()
    service_command = CLUSTER.get_service(SERVICE_NAME)
    if SERVICE_NAME == "ignite":
        action_command("ignite","DeactivateIgnite")
        print("DeactivateIgnite.........")
        time.sleep(5)
        service_command.stop()
    elif SERVICE_NAME == "app":
        for i in APP_PROCESSING_LIST:
            print("stoping......."+i)
            action_command("app",i)
            time.sleep(10)
        time.sleep(15)
        service_command.stop()
    else:
        service_command.stop()

def stop_all_service():
    for i in APP_PROCESSING_LIST:
        action_command("app",i)	
        time.sleep(10)
    print("stoping flink app.........")
    time.sleep(15)
    action_command("ignite","DeactivateIgnite")
    print("DeactivateIgnite.........")
    time.sleep(10)
    for i in reversed(APPLICATION_LIST):
        print("stoping......."+i)
        stop_service(i)
        time.sleep(10)

#Strart Service
def start_service(SERVICE_NAME):
    CLUSTER = create_cluster()
    service_command = CLUSTER.get_service(SERVICE_NAME)
    if SERVICE_NAME == "ignite":
        service_command.start()
        time.sleep(5)
        action_command("ignite","ActivateIgnite")
        print("ActivateIgnite.........")
    else:
        service_command.start()

def start_all_service():
    for i in APPLICATION_LIST:
        print("starting......"+i)
        start_service(i)
        time.sleep(8)
        if i == "ignite":
            action_command("ignite","ActivateIgnite")

#clone ansible and all_in_one
def clone_base_envs(ANSIBLE_GIT_URL,ALLINONE_GIT_URL,ALLINONE_PATH):
    execute_command("cd $SCRIPT_ROOT")
    if os.path.exists(ANSIBLE_GIT_URL.split("/")[-1].split(".")[0]):
        shutil.rmtree(ANSIBLE_GIT_URL.split("/")[-1].split(".")[0])
    execute_command("git clone "+ANSIBLE_GIT_URL)
    if os.path.exists(ALLINONE_GIT_URL.split("/")[-1].split(".")[0]):
        shutil.rmtree(ALLINONE_GIT_URL.split("/")[-1].split(".")[0])
    execute_command("git clone "+ALLINONE_GIT_URL)
    #build all_in_one
    execute_command(ALLINONE_PATH+"/build_bin/build_release.py")

    #get vari
    IS_UNPACK_TAR = (load_cfg(ansible_path+"/group_vars/all")).get("is_unpack_tar")
    type(IS_UNPACK_TAR)
    if IS_UNPACK_TAR:
        execute_command(ALLINONE_PATH+"/release_"+TODAY_TIME+"/unpack_all.sh")

#Execute ansible shell for application
def execute_command(cmd):
    ret = os.system(cmd)
    if ret != 0:
        print("Failed to execute command :'%s'" % cmd)
        sys.exit(-1)

def load_cfg(cfg_filename):
    with open(str(cfg_filename)) as f:
        cfg = yaml.load(f.read())
        return cfg
    return None

#automation
#APPLICATION_LIST=["flink","eft","schedule","tomcat","ignite","app"]
def automation(ANSIBLE_PATH):
	#stop
	print("============================= stop cluster ....... =================================")
	stop_all_service()
	#deploy
	print("============================= deploy cluster ....... =================================")
	for i in listSh:
            execute_command("sh "+ANSIBLE_PATH+"/"+i)
	#start
	print("============================= start cluster ....... =================================")
	start_all_service()

def modify_ansible_release_dir(ALLINONE_PATH,ANSIBLE_PATH):
	for i in os.listdir(ALLINONE_PATH):
            if len(i) > 7:
                if i[:7] == "release":
                    release_dir = ALLINONE_PATH+"/"+i
	print("release_dir:"+release_dir)
	os.system("sed -i s#FAKE_RELEASE_DIR#"+release_dir+"#g "+ANSIBLE_PATH+"/group_vars/all")
	print("shell:"+"sed -i s#FAKE_RELEASE_DIR#"+release_dir+"#g "+ANSIBLE_PATH+"/group_vars/all")

def create_cluster():
    CM_HOST = (load_cfg(ansible_path+"/group_vars/all")).get("cm_host")
    USERNAME = (load_cfg(ansible_path+"/group_vars/all")).get("cm_username")
    PASSWORD = (load_cfg(ansible_path+"/group_vars/all")).get("cm_password")
    api = ApiResource(CM_HOST, version=API_VERSION, username=USERNAME, password=PASSWORD)
    cluster = api.get_cluster(CLUSTER_NAME)
    return cluster

def deploy_service(service_name,ansible_path):
    if service_name == "app":
        execute_command("sh "+ansible_path+"/97_deploy_app.sh")
    elif service_name == "flink":
        execute_command("sh "+ansible_path+"/96_deploy_flink.sh")
    elif service_name == "ignite":
        execute_command("sh "+ansible_path+"/95_deploy_ignite.sh")
    elif service_name == "schedule":
        execute_command("sh "+ansible_path+"/93_deploy_schedule.sh")
        execute_command("sh "+ansible_path+"/94_deploy_batch.sh")
    elif service_name == "eft":
        execute_command("sh "+ansible_path+"/53_deploy_eft.sh")
    elif service_name == "tomcat":
        execute_command("sh "+ansible_path+"/51_deploy_tomcat.sh")
    elif service_name == "csd":
        execute_command("sh "+ansible_path+"/34_monit_tools.sh")
    elif service_name == "logstash":
        execute_command("sh "+ansible_path+"/33_deploy_logstash.sh")
    else:
        execute_command("sh "+ansible_path+"/00_ping.sh")

def usage():
    print("input args num error!!")
    print("\t Usage1: argv[1]: vmuat/vmpef/vmsit/prod \t argv[2]: envs/stopAllService/startAllService/automation")
    print("\t Usage2: argv[1]: vmuat/vmpef/vmsit/prod \t argv[2]: stopService/startService \t argv[3]: service_name")
    print("\t Usage3: argv[1]: vmuat/vmpef/vmsit/prod \t argv[2]: deployService \t argv[3]: csd/tomcat/eft/schedule/ignite/flink/app")

def main():

    if sys.argv[1] == "help":
        usage()
    elif sys.argv[2] == "envs":
        clone_base_envs(ANSIBLE_GIT_URL, ALLINONE_GIT_URL, allinone_path)
        modify_ansible_release_dir(allinone_path, ansible_path)
    elif sys.argv[2] == "stopAllService":
        stop_all_service()
    elif sys.argv[2] == "startAllService":
        start_all_service()
    elif sys.argv[2] == "automation":
        automation(ansible_path)
    elif sys.argv[2] == "stopService":
        stop_service(sys.argv[3])
    elif sys.argv[2] == "startService":
        start_service(sys.argv[3])
    elif sys.argv[2] == "test":
        print(0)
    elif sys.argv[2] == "deployService":
        deploy_service(sys.argv[3], ansible_path)
    elif sys.argv[2] == "help":
        usage()
    else:
        usage()

if __name__ == "__main__":
        main()
