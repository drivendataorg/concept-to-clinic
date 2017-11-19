Brief ECS introduction
------------------------
ECS is basically a copy of Docker Swarm except it has a nice UI. This conveniently makes the concepts easy to get. An ECS task definition is the same as a docker-compose file. It defines the relationship between containers and defines some settings for each one. ECS task definitions and docker-compose files use many of the same fields. An ECS task is a running instance of a task definition.

The c2c application is deployed as a four container ECS task. An ECS Service is the same as a Docker Swarm service in that it is only responsible for launching ECS tasks for you.

An ECS cluster is the same thing as a Docker Swarm cluster, except instead of a bunch of docker daemons running in swarm mode its a bunch of machines running the ECS agent (the ECS agent is itself a docker container).


c2c Infrastructure
------------------------
All the infrastructure is defined in code via CloudFormation, which is just YAML. There are three CloudFormation templates:

1. ecs.yaml - This creats an ECS cluster. The cluster is totally unaware of what application it hosts. It's just an auto-scale group that makes instances and joins them to a cluster called 'c2c'. If the machines die for any reason they will come right back up.

2. alb.yaml - This makes an 'application' elastic load balancer (ALB). It works with ECS to spread traffic between multiple tasks. It decides where to route traffic based on the path of the request. In this case there is only one path, '/', so it sends any and all traffic to its 'target groups'. There is only one target group in this deployment and it will point to all instances of the c2c task.

3. c2c.yaml - This defines the ECS task with all four containers and makes an ECS Service to baby-sit that task. It also makes four CloudwatchLogs groups, one for each container in the task.

Tips/Notes
----------------------------
1. If you need to see what the containers are doing, look at CloudwatchLogs. The logs are captured by the docker daemon itself so you will see them no matter how hard the container crashes. You can NOT use 'docker logs' on the ECS instance. The logs are already captured by ECS and sent to Cloudwatch Logs.
2. You can see lots of interesting metrics by looking at the target group. It will tell you things like 200s, 400s, total requests, latency, etc. It's very helpful.


Sceptre
---------------
Sceptre is just a very small tool for launching CloudFormation scripts. It is usually used for deployments across multiple environments. This is currently a one environment scenario but the user experience is quite pleasant so I used it anyway. You can just do 'pip install sceptre'.


How to deploy
---------------
1. You can pass the image version in with the '--var' flag. The Postgres version is hardcoded in the template since that will not likely change.

 sceptre --var "ImageVersion=somegithash" update-stack dev c2c

2. ECS will spin up a new task with the new containers, put the new task in the target group, and then kill the old task. It will connection drain any connections to the old task so users should never notice.
