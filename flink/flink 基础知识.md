# Flink 


## 架构

类似Mapreduce中的JobTracker、TaskTracker

JobManager

TaskManager

## 执行计划生成

StreamGraph -> JobGraph -> ExecutionGraph

JobGraph -> JobVertex -> ExecutionVertex


## 并行度

并行度设置 四个地方： 算子级别、执行化境级别、客户端（命令行级别）、配置文件（yarn-conf.yml）


## 任务槽

可以通过参数 --yarnslots 3 设置taskmanager的任务槽数。


算子链
 - 算子链中的所有算子都会在同一个slot中执行，可以减少不必要的数据交换、序列化和上下文切换
 - 是在StreamGraph到JobGraph的过程中生成
 - 条件：
    ```
    上下游算子实例处于同一个 SlotSharingGroup 中（之后再提）；
    下游算子的链接策略（ChainingStrategy）为 ALWAYS ——既可以与上游链接，也可以与下游链接。我们常见的 map()、filter() 等都属此类；
    上游算子的链接策略为 HEAD 或 ALWAYS。HEAD 策略表示只能与下游链接，这在正常情况下是 Source 算子的专属；
    两个算子间的物理分区逻辑是 ForwardPartitioner ，可参见之前写过的《聊聊Flink DataStream 的八种物理分区逻辑》；
    两个算子间的 shuffle 方式不是批处理模式；
    上下游算子实例的并行度相同；
    没有禁用算子链。
    ```
 - 

任务槽共享


作业需要的任务槽数量肯定等于Job中最大的并行度。需要的TaskManager数=max(并行度) / yarnslot，向上取整

## 内存设置


## Flink分区逻辑

```
GlobalPartitioner
ShufflePartitioner
RebalancePartitioner
RescalePartitioner
BroadcastPartitioner
ForwardPartitioner
KeyGroupStreamPartitioner
CustomPartitionerWrapper
```

1. GlobalPartitioner 
    该分区器会将所有的数据都发送到下游的某个算子实例(subtask id = 0)
2. ShufflePartitioner
   随机选择一个下游算子实例进行发送
3. Rebalancepartitioner
   通过循环的方式依次发送到下游的task
4. RescalePartitioner
5. BroadcastPartitioner
   发送到下游所有的算子实例
6. ForwardPartitioner
    发送到下游对应的第一个task，保证上下游算子并行度一致，即上有算子与下游算子是1:1的关系
7. KeyGroupStreamPartitioner
   根据key的分组索引选择发送到相对应的下游subtask
8. CustomPartitionerWrapper


## State

1. Flink有两种基本的状态，托管状态（Managed State)和原生态（Raw State)
    -  Managed State是由Flink管理，Flink帮忙存储、恢复和优化; ValueState、ListState、MapState
        - Managed State细分为Keyed State 和 Operator State，
        - Keyed State是KeyedStream上的状态，每一个Key对应一个状态
        - Operator State是可以用在所有算子上，每个算子实例(算子链？)共享一个
    - Raw State需要开发者自己管理，自己序列化; 只支持字节数组存储



2. State Checkpoint存储方式： 

   MemoryStateBackend、FsStateBackend、RocksDBStateBackend(支持增量模式)

3. Flink 1.6开始，支持State TTL特性
   
    该特性可以允许对作业中定义的 Keyed 状态进行超时自动清理。

    State TTL 功能给每个 Flink 的 Keyed 状态增加了一个“时间戳”，而 Flink 在状态创建、写入或读取（可选）时更新这个时间戳，并且判断状态是否过期。


4. Broadcast State是Flink支持的一种Operator State。
