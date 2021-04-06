# Java对象内部结构

Java对象在内存中的存储布局可以分为三个部分：对象头(header), 实例数据(Instance Data)和对齐填充(Padding)

## 对象头(Header)

虚拟机的对象头包括两部分信息

### Mark Word
第一部分用于存储对象自身的运行时数据，如 hashCode 、GC分代年龄、锁状态标志、线程持有的锁、偏向线程ID、偏向时间戳等。
这部分数据的长度在 32 位和 64 位的虚拟机（未开启指针压缩）中分别为 4 bytes 和 8 bytes ，官方称之为 "Mark Word"。

### 类型指针 Klass

指向该对象的类元数据的指针。虚拟机通过这个指针来确定这个对象是那个类的实例。

如果对象是一个 Java 数组，那在对象头中还必须有一块用于记录数组长度的数据。

这部分数据的长度在 32 位和 64 的虚拟机（未开启指针压缩）中分别为 4 bytes 和 8 bytes(不包括数组长度)。

若开启指针压缩(64-bit机器)，则kclass的8 bytes指针会压缩到4 bytes。

## 实例数据

### 8中基本类型

### 对象引用

## Padding 

由于虚拟机内存管理体系要求 Java 对象内存起始地址必须为 8 的整数倍。

譬如， 64位虚拟机上的new Object()的实际大小：

Mark Word(8 bytes) + kclass(4 bytes)[开启指针压缩] = 12 bytes

但由于padding机制，实际占用空间为

Mark Word(8 bytes) + kclass(4 bytes)[开启指针压缩] + Padding(4 bytes) = 16 bytes


# Java对象大小计算
## 工具
org.apache.lucene.lucene-core
## maven
pom.xml添加依赖
```xml
<dependency>
    <groupId>org.apache.lucene</groupId>
    <artifactId>lucene-core</artifactId>
    <version>8.7.0</version>
</dependency>

mvn  dependency:resolve
```

## code
```java
import org.apache.lucene.util.RamUsageEstimator;

System.out.println(RamUsageEstimator.sizeOf("Test123"));
System.out.println(RamUsageEstimator.sizeOfMap(map123123));

```

## 数据统计

HashMap<String,String>
| count | key size | value size | mem size |  
| -- | -- | -- | -- |
| 1kw | 7 | 1 | 1360000048 |
| 1kw | 8 | 1 | 1360000048 |
| 1kw | 9 | 1 | 1440000048 |
| 1kw | 10 | 1 | 1440000048 |
| 1kw | 12 | 1 | 1440000048 |
| 1kw | 13 | 1 | 1520000048 |
| 1kw | 14 | 1 | 1520000048 |
| 1kw | 15 | 1 | 1520000048 |
| 1kw | 17 | 1 | 1600000048 |

HashMap<byte[],byte[]>
| count | key size | value size | mem size |  
| -- | -- | -- | -- |
| 1kw | 17 | 1 | 960000048 |
| 1kw | 16 | 1 | 880000048 |

 * String类型的bytes，采用StringUTF16编码，一个char占用2个byte.
 * String每增加4个char，占用内存增加77M。
 * 空String要占用40 bytes。
 * Hashmap 1kw自己，其中Hashmap结构自带内需需要760M，约50%左右。
 * 相同String，存在重复统计的可能。


## 压缩

"2014-02-01T14:00:00.000+00:00" GZIP压缩之后,长度由29->60吧

## 堆外存储

Java中分配堆外内存的方式有两种:  
一是通过ByteBuffer.java#allocateDirect得到以一个DirectByteBuffer对象;  
二是直接调用Unsafe.java#allocateMemory分配内存，但Unsafe只能在JDK的代码中调用，一般不会直接使用该方法分配内存。


### mapdb

堆外（内存、磁盘文件）嵌入式java数据库引擎，主要提供map和set形式的数据存储

* 支持事务（MVCC|WAF）
* 内存级别和磁盘级别的缓存
* 支持硬盘存储、mmap
* 支持Cache(HashMap、LRU)
* 支持entry 过期设置

#### mapdb 1.0.8

* 数据测试结果：
  * 写入：1kw   46s  占用硬盘254M，java -Xms512M -Xmx512M
  * 搜索：10w 随机搜索    1-2s
  * 更新：10w 2s

``` java
DB db = DBMaker
        .newFileDB(new File(tmpFile))
        .closeOnJvmShutdown()
        .transactionDisable()
        .deleteFilesAfterClose()
        .strictDBGet()
        .asyncWriteEnable()
        .mmapFileEnable()
        .commitFileSyncDisable()
        .cacheSize(1000000)
        .make();

// HTreeMap provides HashMap and HashSet collections for MapDB;

HTreeMap<String, String> map = db.createHashMap("dict").make();
```

#### mapdb 2.0

2.0是一个被抛弃的版本。

#### mapdb 3.0

* reference: https://mapdb.org/blog/mapdb3/
* 代码大多用Kotlin编写
* 代码中cache为TODO， 很多功能未支持
* 性能
  * 插入：1kw   57s  占用硬盘777M，java -Xms512M -Xmx512M
  * 10w 随机搜索    1-2s

``` java
DB db = DBMaker
        .fileDB("test3.0")
        .closeOnJvmShutdown()
        .fileDeleteAfterClose()
        .concurrencyDisable()
        .fileMmapEnable()
        .fileLockDisable()
        .make();

HTreeMap<String, String> map = (HTreeMap<String, String>) db.hashMap("dict").create();
```

### OHC 

* 只针对Off-Heap Memory
* 不支持事务  
* 支持缓存（LRU）
* 性能
  * 插入： 1kw   12s  java -Xms512M -Xmx512M   
  * 搜索：10w 随机搜索   1-2s

``` java
OHCache<String, String> map = OHCacheBuilder.<String, String>newBuilder()
  .keySerializer(new StringSerializer())
  .valueSerializer(new StringSerializer())
  // 堆外内存设置为2G  
  .capacity(1024L * 1024 * 1024 * 2)
  .eviction(Eviction.LRU)
  .build()
```

```
// From Git Doc
asynchronous cache loader support
optional per entry or default TTL/expireAt
entry eviction and expiration without a separate thread
capable of maintaining huge amounts of cache memory
suitable for tiny/small entries with low overhead using the chunked implementation
```

### rocksdb

 * 数据测试结果：
   * 写入：1kw   43s  占用硬盘90M，java -Xms512M -Xmx512M
   * 搜索：10w 随机搜索    3-4s

```java
Options options = new Options();
options.setCreateIfMissing(true);
rocksDB = RocksDB.open(options, dbPath);
```


### mapdb性能对比测试
| count | cache size | search count | time |  
| -- | -- | -- | -- |
| 100万 | 1 | 100万 | 2.52 |
| 100万 | 10 | 100万 | 2.52 |
| 100万 | 1000 | 100万 | 2.24 |
| 100万 | 10000 | 100万 | 2.2 |
| 100万 | 100000 | 100万 | 2.1 |
| 1000万 | 1000 | 100万 | 3.1 |
| 1000万 | 100000 | 100万 | 2.6 |
| 1亿 | 1000 | 100万 | 66 |
| 1亿 | 1000000 | 100万 | 66 |

rocksdb 1亿，100万搜索，20+s。

