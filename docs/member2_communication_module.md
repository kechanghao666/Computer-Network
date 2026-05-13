# 成员2：Socket 通信、协议实现与 RTT 检测模块说明

## 负责范围

成员2负责 `client/communication.py`，该模块负责客户端与服务器之间的 TCP Socket 通信、协议封装、响应解析、异常处理和 RTT 检测。

## 默认连接参数

- 服务器地址：`127.0.0.1`
- 服务器端口：`8888`
- 编码格式：`UTF-8`
- 消息结束符：每条请求和响应均以 `\n` 结尾

## 提供给成员1调用的函数

```python
connect_server(ip="127.0.0.1", port=8888, timeout=5.0)
send_request(request)
receive_response()
login(username, password)
query_balance()
withdraw(amount)
deposit(amount)
query_flow()
test_rtt(count=5)
quit_system()
close_connection()
```

成员1通常只需要调用业务函数，例如：

```python
from client.communication import connect_server, login, query_balance, withdraw

connect_server()
response = login("zhangsan", "123456")
if response.is_success:
    balance_response = query_balance()
    withdraw_response = withdraw(500)
```

## 响应结果格式

除 RTT 统计外，业务函数统一返回 `AtmResponse`：

- `raw`：服务器原始响应字符串
- `code`：状态码，例如 `200`、`201`、`400`
- `phrase`：状态短语，例如 `OK` 或 `ERROR`
- `message`：响应正文
- `is_success`：是否成功
- `is_error`：是否失败

## RTT 测试结果格式

`test_rtt(count=5)` 默认至少测试 5 次，返回 `RttResult`：

- `success`：测试是否成功
- `count`：成功统计的次数
- `values`：每次 RTT，单位毫秒
- `min_ms`：最小 RTT
- `max_ms`：最大 RTT
- `avg_ms`：平均 RTT
- `network_status`：网络状态描述
- `error`：失败原因

## 与成员3服务器对接要求

成员3服务器需要支持以下请求：

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

服务器返回格式应为：

```text
StatusCode StatusPhrase Data\n
```

RTT 测试中，服务器收到 `PING` 后应直接返回：

```text
PONG\n
```

客户端只将 `PONG` 作为有效 RTT 响应，其他响应会被判定为 RTT 测试失败。

## 本地验证

已提供本地测试文件 `test/test_communication.py`，使用假服务器验证成员2模块。运行命令：

```powershell
python -m unittest discover -s test -v
```

