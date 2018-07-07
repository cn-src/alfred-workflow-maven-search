# alfred-workflow-maven-search
Maven 中央仓库搜索的 Alfred Workflow 插件
------
* 选择后会复制 pom.xml 格式的依赖到剪贴板
* 常规搜索为模糊匹配
* `a:` artifactId 匹配，自动补上 api 需要的双引号
* `g:` groupId 匹配，自动补上 api 需要的双引号
* `m:` 常用依赖的简短匹配，例如：`m:poi` 等同于 `g:"org.apache.poi"`
* [其它更多方式参照官方 REST API](http://search.maven.org/#api)

![](site/demo.png)
![](site/demo-a.png)
![](site/demo-g.png)
![](site/demo-m.png)