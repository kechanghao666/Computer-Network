# 银行 ATM 自动取款系统配置与使用文档

本文档说明银行 ATM 自动取款系统的本地运行环境、配置方法、启动顺序、测试方法和常见问题处理。项目已整合客户端界面、Socket 通信、银行中央服务器、SQLite 数据库、交易流水和 SMTP 邮件提醒。

## 1. 运行环境

推荐环境：

| 项目 | 要求 |
| --- | --- |
| 操作系统 | Windows 10/11，PowerShell 或 CMD |
| Python | 推荐 Python 3.10 或 Python 3.11 |
| 数据库 | SQLite，Python 标准库内置支持 |
| 网络 | 本机 TCP Socket，默认 `127.0.0.1:8888` |
| 编码 | UTF-8 |
| 额外依赖 | 无，项目只使用 Python 标准库 |

检查 Python：

```powershell
python --version
```

如果电脑上同时安装多个 Python 版本，建议使用 Python 3.10 或 3.11 运行。

## 2. 项目目录

```text
client/
  atm_client.py              # 客户端入口
  ui.py                      # 菜单、输入校验、结果显示
  communication.py           # Socket 通信、协议封装、RTT 测试
  communication_adapter.py   # 客户端界面加载通信模块的适配器
server/
  bank_server.py             # 服务器启动、监听和客户端连接处理
  command_handler.py         # 命令解析、登录状态、业务调度
  response.py                # 状态码和响应报文封装
  service_adapter.py         # 数据库与邮件接口适配层
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

## 3. 快速启动

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

看到如下提示表示服务器已启动：

```text
[INFO] Bank server started on 127.0.0.1:8888
[INFO] Waiting for ATM client connections...
```

新开一个 PowerShell 或 CMD 终端，进入同一目录：

```powershell
cd E:\计算机网络\大作业\code
python client\atm_client.py
```

## 4. 默认测试账号

数据库初始化后包含以下账号：

| 用户名 | 密码 | 初始余额 | 邮箱 |
| --- | --- | ---: | --- |
| `zhangsan` | `123456` | `5000.00 RMB` | `zhangsan@qq.com` |
| `lisi` | `123456` | `3000.00 RMB` | `lisi@qq.com` |
| `admin` | `123456` | `10000.00 RMB` | `admin@qq.com` |

现场演示建议使用：

```text
username: zhangsan
password: 123456
```

## 5. 客户端功能

客户端启动后显示主菜单：

```text
1. Login
2. Balance Query
3. Withdraw
4. Deposit
5. Transaction Flow Query
6. Network RTT Test
7. Logout / Exit
```

建议演示顺序：

1. 登录：输入 `zhangsan` 和 `123456`。
2. 余额查询：查看初始余额。
3. 取款：输入合法金额，例如 `100`。
4. 存款：输入合法金额，例如 `50`。
5. 流水查询：查看 `BALANCE_QUERY`、`WITHDRAW`、`DEPOSIT`、`FLOW_QUERY` 记录。
6. RTT 测试：查看 5 次 RTT、最小值、最大值和平均值。
7. 退出系统。

## 6. 通信协议

客户端请求格式：

```text
COMMAND [data]
```

支持命令：

| 命令 | 说明 | 示例 |
| --- | --- | --- |
| `HELO` | 发送用户名 | `HELO zhangsan` |
| `PASS` | 发送密码 | `PASS 123456` |
| `BALA` | 查询余额 | `BALA` |
| `WITHDRAW` | 取款 | `WITHDRAW 100` |
| `DEPOSIT` | 存款 | `DEPOSIT 50` |
| `FLOW` | 查询交易流水 | `FLOW` |
| `PING` | RTT 检测 | `PING` |
| `QUIT` | 退出 | `QUIT` |

服务器响应格式：

```text
StatusCode StatusPhrase Data
```

常见响应：

| 响应 | 说明 |
| --- | --- |
| `200 OK Login success` | 登录成功 |
| `201 OK Balance: 5000.00 RMB` | 余额查询成功 |
| `202 OK Withdraw success, Balance: ...` | 取款成功 |
| `203 OK Deposit success, Balance: ...` | 存款成功 |
| `204 OK Flow query success: ...` | 流水查询成功 |
| `300 OK Quit success` | 退出成功 |
| `400 ERROR Wrong password` | 密码错误 |
| `401 ERROR User not found` | 用户不存在 |
| `402 ERROR Insufficient balance` | 余额不足 |
| `403 ERROR Invalid amount` | 金额非法 |
| `404 ERROR Please login first` | 未登录操作 |
| `500 ERROR Server error` | 服务器错误或非法命令 |

每条请求和响应都使用 UTF-8 编码，并以 `\n` 作为结束符。

## 7. SMTP 邮件配置

系统在存款和取款成功后会尝试发送邮件提醒。邮件配置通过环境变量读取。

QQ 邮箱示例：

```powershell
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
```

说明：

- `ATM_SMTP_PASSWORD` 应填写邮箱 SMTP 授权码，不是网页登录密码。
- 未配置 SMTP 或配置错误时，系统会显示 `Email Notice: Failed`。
- 邮件失败不会回滚存款或取款操作，账户余额和交易流水仍会正常更新。

如果不演示真实邮件发送，可以不配置 SMTP，主功能仍然可以完整运行。

## 8. 测试方法

运行全部测试：

```powershell
python -m unittest discover -s test -v
```

当前测试覆盖：

- 客户端菜单、输入校验、结果显示。
- Socket 通信、状态码解析、RTT 测试。
- 服务器命令解析、登录状态、响应封装。
- SQLite 初始化、账户验证、余额更新、交易流水。
- SMTP 成功发送和异常失败处理。

运行语法编译检查：

```powershell
python -m compileall -q client database email_service server test
```

## 9. 数据库重置

如果演示过程中做了存款、取款，数据库余额和流水会发生变化。需要恢复测试账号初始状态时，可以删除 `database/atm.db` 后重新初始化：

```powershell
Remove-Item database\atm.db
python database\init_db.py
```

如果不想删除文件，也可以直接运行：

```powershell
python database\init_db.py
```

注意：`init_db.py` 会创建表和补充默认账号，但不会清空已有交易流水。需要完全清空流水时，建议删除数据库文件后重新初始化。

## 10. 常见问题

### 10.1 客户端提示无法连接服务器

原因：

- 服务器未启动。
- 服务器端口不是 `8888`。
- 端口被其他程序占用。

处理：

```powershell
python server\bank_server.py
```

如果端口被占用，可以临时指定其他端口：

```powershell
python server\bank_server.py --port 8899
```

同时客户端通信模块也需要连接相同端口。

### 10.2 显示 Please login first

原因：未完成登录就进行余额查询、取款、存款或流水查询。

处理：先选择 `1. Login`，输入正确用户名和密码。

### 10.3 显示 Invalid amount

原因：金额为空、不是数字、为 0 或负数。

处理：输入正数，例如 `100`、`50.5`。

### 10.4 显示 Email Notice: Failed

原因：SMTP 未配置、配置错误、网络异常或授权码错误。

处理：检查第 7 节 SMTP 环境变量。若不演示邮件功能，可以忽略该提示。

### 10.5 中文乱码

原因：终端编码不支持 UTF-8。

处理：优先使用 VS Code Terminal 或 Windows Terminal，也可在 PowerShell 中执行：

```powershell
chcp 65001
```

## 11. 现场演示检查清单

演示前确认：

- 已进入 `E:\计算机网络\大作业\code`。
- 已执行 `python database\init_db.py`。
- 已启动 `python server\bank_server.py`。
- 已新开终端启动 `python client\atm_client.py`。
- 测试账号可登录。
- 能完成余额查询、取款、存款、流水查询和 RTT 测试。
- 如需演示邮件，已提前配置 SMTP 授权码并完成测试。

