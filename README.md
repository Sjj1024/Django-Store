# Django_Store
本项目基于Django1.11.11等来开发一个购物商城Web程序，本项目集成注册，登录，购物，购物车，评论，搜索，第三方qq登录，微信登录，手机号登录，支付宝支付等功能


## 重点内容有：

- Redis实现购物车记录存储
- Redis实现最近浏览记录存储
- 发送注册邮件以Celery异步操作实现
- 网站优化之首页动态页面静态化——以Celery异步操作实现
- 网站优化之首页缓存——Redis存储
- 分布式存储系统FastDFS存储网站商品图片——自定义存储器类
- 商品搜索框架`Elasticsearch`
- 订单并发库存问题之悲观锁与乐观锁
- 自定义管理器实现快速查询数据
- 采用Django内置的认证系统进行登录校验——自定义用户类、校验装饰器
- session基于Redis存储
- 支付宝接口


## 项目展示：
![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E9%A6%96%E9%A1%B5.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E6%B3%A8%E5%86%8C%E9%A1%B5%E9%9D%A2.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E7%99%BB%E5%BD%95%E9%A1%B5%E9%9D%A2.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E5%88%97%E8%A1%A8%E9%A1%B5%E9%9D%A2.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E4%B8%AA%E4%BA%BA%E4%BF%A1%E6%81%AF%E9%A1%B5.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/QQ%E7%99%BB%E5%BD%95%E9%A1%B5%E9%9D%A2.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E6%94%AF%E4%BB%98%E9%A1%B5%E9%9D%A2.png)

![](https://raw.githubusercontent.com/Sjj1024/image-all/master/Django_store/%E7%A1%AE%E8%AE%A4%E8%AE%A2%E5%8D%95%E9%A1%B5.png)
