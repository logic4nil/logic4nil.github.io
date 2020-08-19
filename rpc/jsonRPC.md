## golang 
### net/rpc
- net/rpc库默认采用gob进行序列化, 但是由于gob编码是Golang独有的所以它只支持Golang开发的服务器与客户端之间的交互。

### net/rpc/jsonrpc
- net/rpc/jsonrpc这个包支持跨语言的RPC
- json-rpc是基于TCP协议实现的，目前它还不支持HTTP方式。
