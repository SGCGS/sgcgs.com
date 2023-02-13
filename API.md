# 接口
|正式 API 服务器域名|测试服务器 API 域名|
|---|---|
|无|`api.scgcs.atunemic.com`|

# 鉴权
|权限等级|身份|
|---|---|
|0|游客和被封用户|
|1|已登录用户|
|2|管理员|

## 外部验证
### ManageBac 验证
|请求路径|请求方式|
|---|---|
|`/managebac`|GET|

参数：
|名称|注释|
|---|---|
|username|ManageBac 用户名|
|password|ManageBac 密码|
|rt|reCaptcha 验证令牌|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|字符串|ManageBac 验证令牌 (有效期 5 分钟)|
|失败|401|JSON|{"detail":"失败提示"}|

### ReCaptcha SiteKey
|请求路径|请求方式|
|---|---|
|`/rsk`|GET|

参数：
|名称|注释|
|---|---|
|无|无|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|字符串|ReCaptcha SiteKey|

注释：  
这么设计是为了方便更换。

## 注册
|请求路径|请求方式|
|---|---|
|`/signup`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|
|password|密码|
|managebactoken|ManageBac 验证令牌|
|rt|reCaptcha 验证令牌|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|响应头设置 Cookie|
|失败 (令牌无效或过期)|401|JSON|{"detail":"失败提示"}|
|失败 (已存在用户名)|403|JSON|{"detail":"失败提示"}|

注释：  
若失败页面需要 alert 相关信息。

## 登录
|请求路径|请求方式|
|---|---|
|`/login`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|
|password|密码|
|rt|reCaptcha 验证令牌|
|managebactoken|ManageBac 验证令牌 (单独给出即可，无需其他参数)|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|响应头设置 Cookie|
|失败 (密码错误或用户名不存在)|401|JSON|{"detail":"失败提示"}|

注释：  
若失败页面需要 alert 相关信息。

## 设置新密码
|请求路径|请求方式|
|---|---|
|`/user/changepwd`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|
|password|新密码|
|managebactoken|ManageBac 验证令牌|
|rt|reCaptcha 验证令牌|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|响应头设置 Cookie|
|失败 (令牌无效或过期)|401|JSON|{"detail":"失败提示"}|

注释：  
若失败页面需要 alert 相关信息。

# 问题与投票

## 问题
### 提问
|请求路径|请求方式|
|---|---|
|`/question/new`|GET|

参数：
|名称|注释|
|---|---|
|title|标题|
|content|内容|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|数字|问题 ID|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1+|无|

### 关闭问题
|请求路径|请求方式|
|---|---|
|`/question/close`|GET|

参数：
|名称|注释|
|---|---|
|questionid|问题 ID|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1|为提问者|
|2+|无|

### 删除问题
|请求路径|请求方式|
|---|---|
|`/question/delete`|GET|

参数：
|名称|注释|
|---|---|
|questionid|问题 ID|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1|为提问者|
|2+|无|

## 投票
### 赞成
|请求路径|请求方式|
|---|---|
|`/vote/like`|GET|

参数：
|名称|注释|
|---|---|
|questionid|问题 ID|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1+|无|

### 反对
|请求路径|请求方式|
|---|---|
|`/vote/dislike`|GET|

参数：
|名称|注释|
|---|---|
|questionid|问题 ID|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1+|无|

## 用户管理
### 查询用户信息
|请求路径|请求方式|
|---|---|
|`/user/query`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|JSON|用户信息|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1|是用户本人|
|2+|无|

### 编辑用户信息
|请求路径|请求方式|
|---|---|
|`/user/edit`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|
|info|JSON|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|无|无|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|1|是用户本人|
|2+|无|

### 封禁
|请求路径|请求方式|
|---|---|
|`/user/block`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|2+|无|

### 解封
|请求路径|请求方式|
|---|---|
|`/user/unblock`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|2+|无|

### 删除
|请求路径|请求方式|
|---|---|
|`/user/delete`|GET|

参数：
|名称|注释|
|---|---|
|username|用户名|

返回：  
|状态|响应代码|类型|内容|
|---|---|---|---|
|成功|200|空|空|

Cookie 验证：  
|权限等级|额外身份要求|
|---|---|
|2+|无|