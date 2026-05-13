# 银行 ATM 自动取款系统 - 成员1至成员4整合版

本目录已整合成员1至成员4的代码：

- 成员1：ATM 客户端界面、用户输入、功能入口、结果显示。
- 成员2：Socket 通信、协议封装、状态码解析、RTT 检测。
- 成员3：银行中央服务器框架、命令解析、登录状态管理、业务调度、响应封装、PING/PONG。
- 成员4：SQLite 数据库、账户业务函数、交易流水、SMTP 邮件发送。

## 目录结构

```text
client/
  atm_client.py              # 客户端入口
  ui.py                      # 菜单、输入校验、结果显示
  communication.py           # Socket 通信、协议封装、RTT 测试
  communication_adapter.py   # 成员1加载成员2通信模块的适配器
server/
  bank_server.py             # 服务器启动、监听和客户端连接处理
  command_handler.py         # 命令解析、登录状态、业务调度
  response.py                # 状态码和响应报文封装
  service_adapter.py         # 成员4数据库与邮件接口适配层
database/
  database.py                # SQLite 数据库连接
  account_service.py         # 账户校验、余额变更、交易流水、邮箱查询
  init_db.py                 # 数据库初始化脚本
  atm.db                     # SQLite 数据库文件
email_service/
  smtp_email.py              # SMTP 邮件发送
test/
  test_member1_ui.py
  test_communication.py
  test_member3_server.py
  test_member4_service.py
docs/
  configuration_usage.md
  member2_communication_module.md
```

## 运行方式

在项目根目录执行：

```powershell
python database\init_db.py
python server\bank_server.py
```

新开一个终端，再执行：

```powershell
python client\atm_client.py
```

默认服务器地址为 `127.0.0.1:8888`。

## 通信协议

客户端请求：

```text
HELO username
PASS password
BALA
WITHDRAW amount
DEPOSIT amount
FLOW
PING
QUIT
```

所有请求和响应均使用 UTF-8 编码，并以 `\n` 结尾。服务器响应格式为：

```text
StatusCode StatusPhrase Data
```

`PING` 会立即返回 `PONG`，成员2只将 `PONG` 作为有效 RTT 响应。

## 测试账号

| 用户名 | 密码 | 初始余额 | 邮箱 |
| --- | --- | ---: | --- |
| zhangsan | 123456 | 5000.00 | zhangsan@qq.com |
| lisi | 123456 | 3000.00 | lisi@qq.com |
| admin | 123456 | 10000.00 | admin@qq.com |

## SMTP 配置

邮件发送配置通过环境变量读取。未配置、配置错误或发送失败时，`send_email()` 返回 `False`，不影响存款和取款主流程。

```powershell
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
```

## 测试

```powershell
python -m unittest discover -s test -v
```

测试覆盖客户端界面、Socket 通信、服务器命令处理、数据库账户业务、交易流水和 SMTP 异常处理。

## 详细配置与使用

完整运行配置、SMTP 设置、现场演示流程和常见问题见：

```text
docs/configuration_usage.md
```
