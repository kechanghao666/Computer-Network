# 银行 ATM 自动取款系统 - 成员3服务器模块

本目录完成成员3负责的银行中央服务器框架、命令解析、登录状态管理、业务调度、响应封装、PING/PONG 和异常处理。

## 目录结构

```text
server/
  bank_server.py       # 服务器启动、监听和客户端连接处理
  command_handler.py   # 命令解析、登录状态、业务调度
  response.py          # 状态码和响应报文封装
  service_adapter.py   # 成员4数据库与邮件接口适配层
test/
  test_member3_server.py
```

## 运行方式

在项目根目录执行：

```powershell
python server\bank_server.py
```

默认监听地址为 `127.0.0.1:8888`。也可以指定地址和端口：

```powershell
python server\bank_server.py --host 127.0.0.1 --port 8888
```

## 支持命令

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

所有响应都使用 UTF-8 编码，并以 `\n` 结尾。`PING` 会立即返回 `PONG`，便于成员2计算 RTT。

登录时 `HELO username` 只表示用户名存在，成功返回 `200 OK HELO accepted, User: username`；
只有 `PASS password` 校验成功后才返回 `200 OK Login success`，此时服务器才设置登录状态。

## 与成员4接口对接

`server/service_adapter.py` 会优先导入成员4的真实模块：

```text
database/account_service.py
email_service/smtp_email.py
```

成员4需要提供以下函数：

```python
check_user(username)
check_password(username, password)
get_balance(username)
withdraw_money(username, amount)
deposit_money(username, amount)
get_flow(username)
get_email(username)
send_email(to_email, subject, content)
```

如果成员4模块暂未接入，服务器会自动使用内存版测试账号，保证成员3模块可以独立运行。

## 测试

```powershell
python -m unittest discover -s test
```

测试覆盖登录、未登录限制、余额查询、取款、存款、流水查询、PING/PONG、退出和非法金额处理。
