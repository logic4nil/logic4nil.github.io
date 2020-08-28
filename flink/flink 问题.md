## 使用过程中遇到的问题
注意： 可能有多种错误均会引起同样的问题，要根据日志追查问题，切不可随意更改配置，导致南辕北辙。
### 问题一： Failure reason: Checkpoint was declined.
#### trace 思路
   - JobManager日志： 各种 Decline checkpoint xxx  
   - flink dashboard中，查看checkpoint各种失败。  
   - Google提示，checkpoint失败要查看taskmanager日志。   
   - yarn方式提交的job，通过yarn logs -applicationId xxx 只能拿到jobmanager日志，而且因为搭建方式的问题，无法通过history查看  
   - 解决办法： 在Job canceled之前，尽快在flink dashboard上查看taskmanager的logs。  
   - taskmanager的log提示
   ```
    java.io.IOException: Size of the state is larger than the maximum permitted memory-backed state. Size=5244975 , maxSize=5242880 . Consider using a different state backend, like the File System State backend.
   ```
   - 解决方案：  
    修改flink-conf.yaml文件
    ```
    # 默认为memory
    state.backend: filesystem
    # 注意，该目录chmod 777， 多个人可用。
    state.checkpoints.dir = hdfs://xxx/flink/flink-checkpoints
    ```
#### 知识点
   - flink中的checkpoint机制，状态会持久化以防止数据丢失
   - flink提供了三种状态保存方式
     - MemoryStateBackend: 默认大小显示为5M
        - 本地模式开发
        - 小状态场景
     - FsStateBackend
        - 大状态，长窗口或者大键值状态
        - 高可用场景
     - RocksDBStatebackend
        - 大状态，长窗口或者大键值状态
        - 高可用场景 
        - 增量checkpoint，超大状态。 
   - 本项目，使用FsStateBackend即可。

