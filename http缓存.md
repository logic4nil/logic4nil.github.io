## Http 浏览器缓存命中
### 强缓存：
不会向服务器发送请求，直接从缓存读取，通过Expires 和 Cache-control控制
1. Expires, (Expires: Wed, 22 Oct 2018 08:41:00 GMT)
    - 缓存过期时间，用来指定资源到期失效时间.
	- Expires是Http/1.0的产物  
		缺点，当客户端本地时间修改，会导致缓存失效。尤其是本地与服务器时间不一致，导致缓存混乱实效
2. Cache-Control, (Cache-Control:max-age=300)
	- HTTP/1.1的产物，采用相对时间，即使服务器和客户端时间不一致，也不会导致问题。
	- Cache-Control可以有多个字段组合而成。
		- max-age指定时间长度，单位为s。
		- s-maxage，同max-age, 覆盖max-age。仅适用于共享缓存，在私有缓存中失效。
		- public,可被任意对象（浏览器、代理服务器）缓存
		- private 只能被浏览器等缓存，非共享，不能被代理服务器缓存。
		- no-cache 强制所有缓存了该相应的用户，在使用缓存前，发送待验证的请求到服务器。
		- no-store 禁止任何缓存。
		- must-revalidate,
3. max-age=0  no-cache 功能相同

Cache-Control与Expires可以同时使用或启用其中给任意一个。Cache-Control优先级最高.

### 协商缓存：
若未命中强缓存，则浏览器发送请求到服务器，服务器根据http header信息（Last-Modified/If-Modified-Since 或 ETag/If-None-Match）来判断是否命中缓存。如果命中，则返回304.
1. ETag优先级高于Last-Modified
   - Last-Modified/If-Modified-Since
		- 第一次请求，Response Header会有Last-Modify字段，Last-Modified: Thu,31 Dec 2037 23:59:59 GMT
		- 在此请求该资源时，Request Header会包含If-Modified-Since。服务器会根据时间判断是否命中。
		- 缺点，只精确到秒级, 有时资源变化，但modify时间未发生变化。 所以才有了etag
   - ETag/If-None-Match
		- ETag/If-None-Match返回校验码。ETag保证每个资源唯一，资源变化都会导致ETag变化。