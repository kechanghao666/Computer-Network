# Bank ATM System

这是一个基于 Python 标准库实现的银行 ATM 自动取款系统，包含客户端、TCP Socket 通信、银行服务器、SQLite 数据库、交易流水、SMTP 邮件提醒和 RTT 通信链路测试。

## 功能

- 用户登录：通过用户名和密码完成身份认证。
- 余额查询：查询当前账户余额。
- 取款和存款：更新账户余额并记录交易流水。
- 流水查询：查看账户相关操作记录。
- 邮件提醒：存款和取款成功后尝试通过 SMTP 发送邮件通知。
- RTT 测试：通过 `PING/PONG` 测试客户端与服务器之间的往返时延，并保存统计记录。
- 两种客户端：命令行客户端和 Tkinter 图形化客户端。

## 快速开始

克隆仓库后进入项目根目录：

```powershell
git clone https://github.com/kechanghao666/Computer-Network.git
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

新开一个终端，启动命令行客户端：

```powershell
python client/atm_client.py
```

或启动图形化客户端：

```powershell
python client/gui_client.py
```

默认服务器地址为 `127.0.0.1:8888`。

## 默认账号

| 用户名 | 密码 | 初始余额 |
| --- | --- | ---: |
| `zhangsan` | `123456` | `5000.00 RMB` |
| `lisi` | `123456` | `3000.00 RMB` |
| `admin` | `123456` | `10000.00 RMB` |

## 项目结构

```text
client/          客户端界面、通信封装和 RTT 测试
database/        SQLite 连接、账户业务、交易流水和 RTT 记录
email_service/   SMTP 邮件发送与配置检查
server/          TCP 服务器、协议解析和业务调度
test/            自动化测试
README.md        项目概览
配置使用说明.md   完整配置与使用文档
requirements.txt 依赖说明
```

## 测试

```powershell
python -m unittest discover -s test -v
python -m compileall -q client database email_service server test
```

## 详细文档

完整安装、配置、运行、SMTP、RTT 导出、数据库重置和故障排查说明见：

```text
配置使用说明.md
```
