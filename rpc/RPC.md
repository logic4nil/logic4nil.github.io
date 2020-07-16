## RPC

Remote Procedure Call.  
### 目的
像调用本地方法一样，调用远程方法。本质上与远程服务器进行通讯。  
使用方便，但是同样要处理Connection TimeOut等Exception 

### 原理
Call ID确认，即告诉远程服务器调用哪个方法。  
信息载体的序列化与反序列化 Protobuf、Json、XML的功能  
网络协议：TCP、UDP， gRPC使用HTTP2.0
