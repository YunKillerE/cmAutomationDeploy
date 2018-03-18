#环境

在python2.7下面开发测试

http://cloudera.github.io/cm_api/docs/python-client/

    pip install cm-api
    
or

    $ git clone git://github.com/cloudera/cm_api.git
    $ cd cm_api/python
    $ sudo python setup.py install
    ## ... the distribution egg file is in ./dist/

#流程

从jenkins拉取编译后的代码包--》准备ansible自动化部署环境--》停止hadooop集群--》逐步执行集群及应用部署--》启动集群及应用
 
**注意：**

**1，所有应用需要集成到cm界面 参考项目：https://github.com/jimmy-src/cloudera-csd**

**2，ansible自动化部署脚本，后续整理好后发布**

#用法：

Usage1: argv[1]: vmuat/vmpef/vmsit/prod         argv[2]: envs/stopAllService/startAllService/automation

Usage2: argv[1]: vmuat/vmpef/vmsit/prod         argv[2]: stopService/startService       argv[3]: service_name

Usage3: argv[1]: vmuat/vmpef/vmsit/prod         argv[2]: deployService          argv[3]: csd/tomcat/eft/schedule/ignite/flink/app


#命令

1，执行前的基础环境准备

	./deploy_release.py vmuat envs

2，执行全部应用的部署

	./deploy_release.py vmuat automation

3，停止所有服务

	./deploy_release.py vmuat stopAllService

4，启动所有服务

	./deploy_release.py vmuat startAllService

5，停止单个服务 ["flink","eft","schedule","tomcat","ignite","app"]

	./deploy_release.py vmuat stopService flink

6，部署单个服务 [csd/tomcat/eft/schedule/ignite/flink/app]

	./deploy_release.py vmuat deployService flink

7，启动单个服务 ["flink","eft","schedule","tomcat","ignite","app"]

	./deploy_release.py vmuat startService flink

#TODO
1，sleep问题解决，采用pull方式

2，commands是否执行成功判断

3，写一个eansible的role，用来启停cm的服务

4，采用面向对象的写


