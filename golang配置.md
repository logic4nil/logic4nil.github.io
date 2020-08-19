## Golang 
参考信息 [](https://segmentfault.com/a/1190000021854441)
### 环境变量
1. 通过 go env 查看
2. GOROOT golang 的安装路径
3. GOPATH 工作目录，1.14版本之前，安装完之后一定要设置这个环境变量，包括：
   - bin(golang编译可执行文件存放路径), 
   - pkg(生成的.a文件存放路径，预编译的目标文件，加快编译速度), 
   - src(存储所有的.go文件和源代码，go run，go install等命令的当前工作路径)
4. 1.14 版本弃用GOPATH，原因：
   - GOPATH模式下，无版本信息

### golang 1.14
1. 引入Go Modules
   - 通过 GO111MODULE 环境变量控制
     - auto 项目中包含go.mod文件的话，启用go module。目前Go1.11-Go1.14均为auto。
     - on 启用
     - off 禁用
2. GOPROXY
   - go env -w GOPROXY=https://goproxy.cn,direct
3. GOSUMDB
   Go checksum database,用于拉去模块时，保证模块版本数据未经过篡改
   默认值：sum.golang.org，可以被GOPROXY代理。
   也可以设置未off，禁止GO在后续操作中验证模块版本
4. GOPRIVATE
   设置私有模块的拉取方式。一般设置公司的私有git仓库，或者github中的私有仓库。
   ```
   go env -w GOPRIVATE="github.com/eddycjy/mquote"
   ```
   则指定模块路径都将不经过Go module proxy 和 Go checksum database
5. 项目存放位置
   - 建议放在$GOPATH/src外，尤其是涉及到自身引用的问题。
   - 项目还可以放到$GOPATH/src下，但是会根据GO111MODULE不同值，采用不同的处理方式
     - auto 项目在$GOPATH/src下，会使用$GOPATH/src的依赖包，在$GOPATH/src外，就是用go.mod里的require包。
     - on 无论在$GOPATH/src里还是在外面，都会使用go.mod 里 require的包
     - off 就是老规矩。
