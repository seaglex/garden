### try_nginx
 * 演示如何使用rewrite/proxy_pass/proxy_rewrite把service deploy的子目录下

### try_react_router
 * 演示如何使用react_router实现JS控制的router

### try_sqlalchemy
 * 需要使用mysql://root@localhost/test数据库
 * 演示如何使用sqlalchemy的raw sql / ORM操作
   * Base / MetaData / Session
 * 数据库metadata lock
   * 不及时commit会产生table lock
   * 不close没有关系(但是不会返回到connection pool)
 * Lazy Session
   * 只查询出结果,不实际访问结果,不会产生交互

### try_theano
 * 演示如何使用theano使用Logistic Regression
