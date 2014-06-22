# taskmgr

## What is Taskmgr

Taskmgr is a task manager built around Fabric, written in python. It allows you to run checks and commands on multiple clusters in parallel (parallelization between clusters and within clusters are possible).
Taskmgr was designed to help with tasks like coordinated reboots of hundreds of machines, in a safe manner.

The main focus of Taskmgr is to allow steps of work to be described, such as:
 * check machine is up
 * check service is available
 * disable traffic
 * wait until a given state is achieved (number of sessions, req/sec are low enough)
 * do action (like reboot)
 * wait until machine goes down
 * wait until machine comes back again
 * wait until a given state is reached (number of sessions is high enough, etc)
 * move on to next machine

By default if any of the checks fails, no more machines in the given cluster will be running the commands, other clusters, however, which didn't recieve a problem, will continue working.

For the documentation, see [The Wiki](https://github.com/bdeak/taskmgr/wiki)
