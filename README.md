# 银行 ATM 自动取款系统 - 成员 1 至成员 4 整合版

本项目是银行 ATM 自动取款系统的最终整合作品，已整合成员 1 至成员 4 的实现内容：

- 成员 1：ATM 客户端界面、用户输入、功能入口、结果显示。
- 成员 2：Socket 通信、协议封装、状态码解析、RTT 检测与记录。
- 成员 3：银行中央服务器、命令解析、登录状态管理、业务调度、响应封装、`PING/PONG`。
- 成员 4：SQLite 数据库、账户业务函数、交易流水、SMTP 邮件发送。

## 快速运行

进入项目根目录：

```powershell
cd E:\计算机网络\大作业\code
```

初始化数据库：

```powershell
python database\init_db.py
```

启动服务器：

```powershell
python server\bank_server.py
```

新开一个终端，启动命令行客户端：

```powershell
python client\atm_client.py
```

也可以启动图形化客户端：

```powershell
python client\gui_client.py
```

默认服务器地址为 `127.0.0.1:8888`。

## 默认测试账号

| 用户名 | 密码 | 初始余额 | 邮箱 |
| --- | --- | ---: | --- |
| `zhangsan` | `123456` | `5000.00 RMB` | `zhangsan@qq.com` |
| `lisi` | `123456` | `3000.00 RMB` | `lisi@qq.com` |
| `admin` | `123456` | `10000.00 RMB` | `admin@qq.com` |

## 项目结构

```text
client/
  atm_client.py              # 命令行客户端入口
  ui.py                      # 菜单、输入校验、结果显示
  communication.py           # Socket 通信、协议封装、RTT 测试
  communication_adapter.py   # 通信模块适配器
  gui_client.py              # Tkinter 图形化客户端
server/
  bank_server.py             # 服务器启动、监听和客户端连接处理
  command_handler.py         # 命令解析、登录状态、业务调度
  response.py                # 状态码和响应报文封装
  service_adapter.py         # 数据库与邮件接口适配层
database/
  database.py                # SQLite 数据库连接
  account_service.py         # 账户校验、余额变更、交易流水、RTT 记录
  init_db.py                 # 数据库初始化脚本
  atm.db                     # SQLite 数据库文件
email_service/
  smtp_email.py              # SMTP 邮件发送与配置检查
test/
  test_member1_ui.py
  test_communication.py
  test_member3_server.py
  test_member4_service.py
docs/
  configuration_usage.md     # 详细配置使用文档
  member2_communication_module.md
  supplement_features.md
配置使用说明.md               # 根目录交付版配置使用文档
```

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

服务器响应格式：

```text
StatusCode StatusPhrase Data
```

所有请求和响应均使用 UTF-8 编码，并以 `\n` 结尾。`PING` 会立即返回 `PONG`，客户端据此统计 RTT。

## SMTP 邮件配置

取款和存款成功后，系统会尝试发送邮件提醒。真实邮件发送需要在本机设置 SMTP 环境变量：

```powershell
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
```

检查配置：

```powershell
python -m email_service.smtp_email --check
```

发送测试邮件：

```powershell
python -m email_service.smtp_email --to your@qq.com
```

未配置 SMTP 时，存款和取款仍会成功，但会显示 `Email Notice: Failed`。

## 测试

运行全部测试：

```powershell
python -m unittest discover -s test -v
```

运行编译检查：

```powershell
python -m compileall -q client database email_service server test
```

## 详细文档

完整配置、启动、演示、SMTP、RTT 导出、数据库重置和常见问题处理见：

```text
配置使用说明.md
docs/configuration_usage.md
```
