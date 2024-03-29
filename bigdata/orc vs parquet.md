# ORC
https://www.huaweicloud.com/articles/76e423ad4ee18b909b7788c8d8004d1a.html
## Format
![ORC](./orc.png)
![ORC](./orc_1.jpg)

```
Stripes:  
    Index Data  
	Row Data  
	Stripe Footer:元数据，记录了index和data的的长度  
Footer:
	File Footer： 它包含了每一个stripe的长度和偏移量，该文件的schema信息(将schema树按照schema中的编号保存在数组中)、整个文件的统计信息以及每一个row group的行数。
	统计信息：每一个stripe中每一列的信息，主要统计成员数、最大值、最小值、是否有空值等
	Postscript: 文件元数据信息（压缩格式，Footer长度、版本信息等）
```

## ORC统计信息

在ORC文件中保存了三个层级的统计信息，分别为文件级别、stripe级别和row group级别的，他们都可以用来根据Search ARGuments（谓词下推条件）判断是否可以跳过某些数据，在统计信息中都包含成员数和是否有null值，并且对于不同类型的数据设置一些特定的统计信息。

 1. file level

	在ORC文件的末尾会记录文件级别的统计信息，会记录整个文件中columns的统计信息。这些信息主要用于查询的优化，也可以为一些简单的聚合查询比如max, min, sum输出结果。 

 2. stripe level

	ORC文件会保存每个字段stripe级别的统计信息，ORC reader使用这些统计信息来确定对于一个查询语句来说，需要读入哪些stripe中的记录。比如说某个stripe的字段max(a)=10，min(a)=3，那么当where条件为a >10或者a <3时，那么这个stripe中的所有记录在查询语句执行时不会被读入。 

 3 row level 

	为了进一步的避免读入不必要的数据，在逻辑上将一个column的index以一个给定的值(默认为10000，可由参数配置)分割为多个index组。以10000条记录为一个组，对数据进行统计。Hive查询引擎会将where条件中的约束传递给ORC reader，这些reader根据组级别的统计信息，过滤掉不必要的数据。如果该值设置的太小，就会保存更多的统计信息，用户需要根据自己数据的特点权衡一个合理的值。

## 数据访问：
	读取ORC文件是从尾部开始的，第一次读取16KB的大小，尽可能的将Postscript和Footer数据都读入内存。
	文件的最后一个字节保存着PostScript的长度，它的长度不会超过256字节。
	PostScript中保存着整个文件的元数据信息，它包括文件的压缩格式、文件内部每一个压缩块的最大长度(每次分配内存的大小)、Footer长度，以及一些版本信息。

	在Postscript和Footer之间存储着整个文件的统计信息;
	这部分的统计信息包括每一个stripe中每一列的信息，主要统计成员数、最大值、最小值、是否有空值等。

	处理stripe时首先从File Footer中获取每一个stripe的其实位置和长度、每一个stripe的Footer数据(元数据，记录了index和data的的长度)，
	整个striper被分为index和data两部分，stripe内部是按照row group进行分块的(每一个row group中多少条记录在Stripe的Footer中存储)，
	row group内部按列存储。每一个row group由多个stream保存数据和索引信息。每一个stream的数据会根据该列的类型使用特定的压缩算法保存。在ORC中存在如下几种stream类型：
		PRESENT：每一个成员值在这个stream中保持一位(bit)用于标示该值是否为NULL，通过它可以只记录部位NULL的值
		DATA：该列的中属于当前stripe的成员值。
		LENGTH：每一个成员的长度，这个是针对string类型的列才有的。
		DICTIONARY_DATA：对string类型数据编码之后字典的内容。
		SECONDARY：存储Decimal、timestamp类型的小数或者纳秒数等。
		ROW_INDEX：保存stripe中每一个row group的统计信息和每一个row group起始位置信息。

	在初始化阶段获取全部的元数据之后，可以通过includes数组指定需要读取的列编号，它是一个boolean数组，如果不指定则读取全部的列，
	还可以通过传递SearchArgument参数指定过滤条件，
	根据元数据首先读取每一个stripe中的index信息，然后根据index中统计信息以及SearchArgument参数确定需要读取的row group编号，
	再根据includes数据决定需要从这些row group中读取的列，通过这两层的过滤需要读取的数据只是整个stripe多个小段的区间，然后ORC会尽可能合并多个离散的区间尽可能的减少I/O次数。
	然后再根据index中保存的下一个row group的位置信息调至该stripe中第一个需要读取的row group中。

	由于ORC中使用了更加精确的索引信息，使得在读取数据时可以指定从任意一Row Group开始读取，更细粒度的统计信息使得读取ORC文件跳过整个row group，
	ORC默认会对任何一块数据和索引信息使用ZLIB压缩，因此ORC文件占用的存储空间也更小，这点在后面的测试对比中也有所印证。

	在新版本的ORC中也加入了对Bloom Filter的支持，它可以进一步提升谓词下推的效率，在Hive 1.2.0版本以后也加入了对此的支持。

## ORC文件使用两级压缩机制
首先将一个数据流使用流式编码器进行编码，然后使用一个可选的压缩器对数据流进行进一步压缩。 

### 一个column可能保存在一个或多个数据流中，可以将数据流划分为以下四种类型： 
 -  Byte Stream 
	字节流保存一系列的字节数据，不对数据进行编码。 

 - Run Length Byte Stream 
	字节长度字节流保存一系列的字节数据，对于相同的字节，保存这个重复值以及该值在字节流中出现的位置。 

 - Integer Stream 
	整形数据流保存一系列整形数据。可以对数据量进行字节长度编码以及delta编码。具体使用哪种编码方式需要根据整形流中的子序列模式来确定。 

 - Bit Field Stream 
 	比特流主要用来保存boolean值组成的序列，一个字节代表一个boolean值，在比特流的底层是用Run Length Byte Stream来实现的。 

接下来会以Integer和String类型的字段举例来说明。 

1. Integer 

	对于一个整形字段，会同时使用一个比特流和整形流。比特流用于标识某个值是否为null，整形流用于保存该整形字段非空记录的整数值。 

2. String 

	对于一个String类型字段，ORC writer在开始时会检查该字段值中不同的内容数占非空记录总数的百分比不超过0.8的话，就使用字典编码，字段值会保存在一个比特流，一个字节流及两个整形流中。比特流也是用于标识null值的，字节流用于存储字典值，一个整形流用于存储字典中每个词条的长度，另一个整形流用于记录字段值。 

	如果不能用字典编码，ORC writer会知道这个字段的重复值太少，用字典编码效率不高，ORC writer会使用一个字节流保存String字段的值，然后用一个整形流来保存每个字段的字节长度。 

	在ORC文件中，在各种数据流的底层，用户可以自选ZLIB, Snappy和LZO压缩方式对数据流进行压缩。编码器一般会将一个数据流压缩成一个个小的压缩单元，在目前的实现中，压缩单元的默认大小是256KB。

# Parquet
## Parquet Format
![Parquet](./parquet.png)


# all
![all](./all.jpg)