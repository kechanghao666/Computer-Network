# 银行 ATM 自动取款系统 - 成员2通信模块

本分支 `jiangzihan` 完成的是项目第2部分：客户端 Socket 通信、通信协议实现、状态码解析和 RTT 检测模块。

## 已完成工作

### 1. Socket 通信模块

文件位置：

```text
client/communication.py
```

主要功能：

- 建立客户端与服务器的 TCP Socket 连接，默认连接 `127.0.0.1:8888`。
- 按项目统一协议发送请求，格式为 `COMMAND [data]`。
- 每条请求和响应统一使用 `\n` 作为结束符。
- 使用 UTF-8 编码发送和接收数据。
- 处理服务器连接失败、服务器断开、响应超时、编码错误等异常情况。

### 2. 协议请求封装

已实现的客户端请求命令：

| 函数 | 发送命令 | 说明 |
|---|---|---|
| `login(username, password)` | `HELO username`、`PASS password` | 用户登录 |
| `query_balance()` | `BALA` | 查询余额 |
| `withdraw(amount)` | `WITHDRAW amount` | 取款 |
| `deposit(amount)` | `DEPOSIT amount` | 存款 |
| `query_flow()` | `FLOW` | 查询交易流水 |
| `test_rtt(count=5)` | `PING` | RTT 往返时延检测 |
| `quit_system()` | `QUIT` | 退出系统 |

### 3. 服务器响应解析

服务器响应统一解析为 `AtmResponse` 对象，包含：

- `raw`：服务器原始响应内容
- `code`：状态码，例如 `200`、`201`、`400`
- `phrase`：状态短语，例如 `OK` 或 `ERROR`
- `message`：响应正文
- `is_success`：是否成功
- `is_error`：是否失败

支持的响应格式：

```text
StatusCode StatusPhrase Data
```

示例：

```text
200 OK Login success
201 OK Balance: 5000.00 RMB
400 ERROR Wrong password
404 ERROR Please login first
```

### 4. RTT 检测与统计

`test_rtt(count=5)` 默认至少测试 5 次。

统计内容包括：

- 每次 RTT，单位毫秒
- 最小 RTT
- 最大 RTT
- 平均 RTT
- 网络状态描述

服务器收到 `PING` 后应立即返回：

```text
PONG
```

### 5. 对接说明文档

文件位置：

```text
docs/member2_communication_module.md
```

该文档说明了成员2模块提供给成员1调用的接口、返回值格式，以及与成员3服务器对接时需要遵守的协议规则。

### 6. 本地测试

文件位置：

```text
test/test_communication.py
```

测试内容：

- 响应状态码解析
- 金额格式化与非法金额拦截
- 登录流程
- 余额查询、取款、存款、流水查询请求
- RTT 测试
- 退出系统
- 连接失败异常处理

## 运行测试

在项目根目录执行：

```powershell
python -m unittest discover -s test -v
```

当前测试结果：

```text
Ran 8 tests

OK
```

## 成员2交付文件

```text
client/__init__.py
client/communication.py
docs/member2_communication_module.md
test/test_communication.py
README.md
```

## 分工说明

本分支只完成成员2负责的通信模块。

未实现内容及对应负责人：

| 模块 | 负责人 |
|---|---|
| ATM 客户端界面与用户操作 | 成员1 |
| 银行中央服务器 | 成员3 |
| SQLite 数据库、账户业务、SMTP 邮件 | 成员4 |
| 项目文档与测试材料整理 | 成员5、成员6 |

