# Spark Executor 内存模型
 Version 1.6之后，支持堆外内存，并且支持Execution内存预Storage内存动态调整。

 堆内内存使用配置:  
 --executor-memory 


 堆外内存使用配置:  
 -- spark.memory.offHeap.enabled  
 -- spark.memory.offHeap.size

### Execution内存

### Storage内存

### 用户内存（User Memory)

 - 主要用来存储RDD转换操作所需要的数据，比如RDD的依赖信息（血缘信息)

### 预留内存（Reserved Memory)

 - 系统预留，用来存储Spark 内部对象

# Spark 任务调度

## DAGScheduler任务调度器，

生成taskset，并提交给TaskScheduler

action 生成Job

transformation中的 宽依赖操作生成生成stage

所有的transformation都是采用的懒策略，就是如果只是将transformation提交是不会执行计算的，计算只有在action被提交的时候才被触发。

## TaskScheduler

 - 任务调度器（Trait）
 - 底层任务调度接口，有专门的实现（TaskSchedulerImpl）。
 - 每个调度器任务需要一个单独的SparkContext对象。
 - 该调度器会从DAG调度器中得到提交的TaskSet，并负责将Task发送给cluster运行它们。如果运行出错会重试，返回事件对象给DAG调度器。
 - 维护task和executor对应关系，executor和物理资源的对应关系。在排队的task和正在运行的task。
 - 内部维护一个队列根据FIFO（先入先出）或者Fair（公平调度）策略，调度任务。

# Spark SQL
  WholeCodeGen

# Spark三大核心数据结构

## RDD

血缘关系： 宽依赖、窄依赖

缓存 & Checkpoint两种持久化方式

cache本身是MemoryOnly，存在数据丢失的可能
```
c = rdd.xxx
c.cache
c.collect
```

checkpoint是将RDD数据保存到持久化存储, 一般选择HDFS等方式
```
sc.setCheckPointDir("hdfs://")
ch = rdd.xxx
ch.checkpoint
ch.collect # 触发任务执行
```
## 广播变量

Broadcast 就是将数据从一个节点发送到其他的节点上, Executor内的所有Task都共享该变量. 

每个Executor中都有一个BlockManager， 用来管理Broadcast变量数据。

Broadcast 不会内存溢出，因为其数据的保存的 Storage Level 是 MEMORY_AND_DISK 的方式

广播方式：HttpBroadCast &  TorrentBroadcast


## 累加器

每次的action操作才会触发累加的加和。 同一个RDD多次执行action，会导致累加器翻倍


## Yarn cluster下执行流程

1. spark-submit，Client与ResoureManager建立会话
2. ResourceManager找NodeManager分配资源，并创建和启动一个ApplicationMaster, ApplicationMaster启动后，会启动一个Driver
3. Driver想RM申请资源
4. RM返回给Driver可用的Container表
5. Driver向N哥NodeManger发送启动JVM命令，每个NodeManger接受命令之后，执行并生成一个Container，这样集群中会有多个Container。
6. Container会向Driver段的TaskScheduler注册
7. DAGScheduler生成Taskset并传递给TaskScheduler执行。
