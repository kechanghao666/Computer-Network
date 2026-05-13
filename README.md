# Bank ATM System

银行 ATM 自动取款系统，使用 Python 标准库实现。系统包含 Tkinter 图形化客户端、TCP Socket 通信、银行服务器、SQLite 数据库、交易流水、SMTP 邮件提醒和 RTT 通信链路测试。

## 功能

- 用户登录、余额查询、取款、存款、流水查询。
- 图形化客户端默认启动，命令行客户端作为备用。
- 客户端和服务器通过 TCP Socket 通信。
- 服务器使用 SQLite 保存账户、余额、交易流水和 RTT 记录。
- 取款和存款成功后后台尝试发送 SMTP 邮件提醒。
- RTT 测试通过 `PING/PONG` 统计客户端到服务器的往返时延。

## 快速启动

进入项目根目录：

```powershell
cd Computer-Network
```

初始化数据库：

```powershell
python database/init_db.py
```

启动服务器：

```powershell
python server/bank_server.py
```

新开一个终端，启动图形化客户端：

```powershell
python client/atm_client.py
```

命令行备用客户端：

```powershell
python client/atm_client.py --cli
```

默认服务器地址：`127.0.0.1:8888`。

## 默认账号

| 用户名 | 密码 | 初始余额 |
| --- | --- | ---: |
| `zhangsan` | `123456` | `5000.00 RMB` |
| `lisi` | `123456` | `3000.00 RMB` |
| `admin` | `123456` | `10000.00 RMB` |

默认邮箱为 `demo@example.com`。如果需要真实邮件提醒，请先配置 `ATM_DEMO_EMAIL` 和 SMTP 环境变量，再重新初始化数据库。

## SMTP 配置

PowerShell 示例：

```powershell
$env:ATM_DEMO_EMAIL="your@qq.com"
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="your_smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
python database/init_db.py
```

检查配置：

```powershell
python -m email_service.smtp_email --check
python -m email_service.smtp_email --to your@qq.com
```

## 项目结构

```text
client/          图形化客户端、命令行备用界面、通信封装和 RTT 测试
database/        SQLite 连接、账户业务、交易流水和 RTT 记录
email_service/   SMTP 邮件发送与配置检查
server/          TCP 服务器、协议解析和业务调度
test/            自动化测试
README.md        项目概览
配置使用说明.md   完整配置与使用说明
现场演示说明.md   现场演示步骤
requirements.txt 依赖说明
```

## 测试

```powershell
python -m unittest discover -s test -v
python -m compileall -q client database email_service server test
```
