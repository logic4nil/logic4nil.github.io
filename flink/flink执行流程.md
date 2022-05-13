## 流程

 - 当用户提交作业的时候，提交脚本会首先启动一个 Client进程负责作业的编译与提交
   - Env
   - StreamGraph
   - JobGraph
 - 提交集群中的Dispatcher
   - Standalone/Flink Session 模式
     - AM 会预先启动，并运行Dispatcher，此时 Client 直接与 Dispatcher 建立连接并提交作业即可
   - Per-Job 模式
     - Client 将首先向资源管理系统 （如Yarn、K8S）申请资源来启动 AM
     - AM 启动Dispatcher
     - Dispatcher、JobManager、ResourceManager 这三个组件都运行在AppMaster 进程
 - Dispatcher 启动一个 JobManager（JobMaster） 组件
 - JobManager(JobMaster) 向 ResourceManager 申请资源来启动作业中具体的任务
   - Standalone/Flink Session 模式
       - JobManager 直接向 ResourceManager 申请资源来启动作业中具体的任务
   - Per-Job模式
       - ResourceManager 首先向外部资源管理系统申请资源来启动 TaskManager
       - TaskManager会生成TaskExecutor
       - TaskExecutor 注册自己到ResourceManager
       - JobManager向ResourceManager申请资源启动任务
 - JobManager提交作业到TaskManager的slot
   - TaskExecutor 收到 JobManager 提交的 Task 之后，会启动一个新的线程来执行该 Task
   - Task 启动后就会开始进行预先指定的计算，并通过数据 Shuffle 模块互相交换数据。
    

## 注解
 - yarn环境：Dispatcher、JobManager、ResourceManager 这三个组件都运行在AppMaster 进程
 - Flink 提供了两种基本的调度逻辑，即 Eager 调度与 Lazy From Source, 默认情况下流作业使用EAGER，批作业使用LAZY。