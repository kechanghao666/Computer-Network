# 银行 ATM 自动取款系统

本项目统一使用 Python、TCP Socket、SQLite 和 SMTP 实现银行 ATM 自动取款系统。当前已完成成员4负责的数据库、账户业务函数、交易流水和邮件发送模块。

## 成员4模块

目录结构：

```text
database/
  database.py          # SQLite 数据库连接
  account_service.py   # 账户校验、余额变更、交易流水、邮箱查询
  init_db.py           # 数据库初始化脚本
  atm.db               # SQLite 数据库文件
email_service/
  smtp_email.py        # SMTP 邮件发送
tests/
  test_member4_service.py
```

成员4对成员3提供的主要函数：

- `init_database()`
- `connect_database()`
- `check_user(username)`
- `check_password(username, password)`
- `get_balance(username)`
- `withdraw_money(username, amount)`
- `deposit_money(username, amount)`
- `add_flow(username, transaction_type, amount, balance_after)`
- `get_flow(username)`
- `get_email(username)`
- `send_email(to_email, subject, content)`

## 初始化数据库

```powershell
python database/init_db.py
```

默认数据库路径为 `database/atm.db`，初始化后包含统一测试账号：

| 用户名 | 密码 | 初始余额 | 邮箱 |
| --- | --- | ---: | --- |
| zhangsan | 123456 | 5000.00 | zhangsan@qq.com |
| lisi | 123456 | 3000.00 | lisi@qq.com |
| admin | 123456 | 10000.00 | admin@qq.com |

## SMTP 配置

邮件发送配置通过环境变量读取。未配置或发送失败时，`send_email()` 返回 `False`，不影响存款和取款主流程。

```powershell
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
```

## 测试

项目当前成员4测试使用 Python 标准库 `unittest`，不需要额外安装依赖。

```powershell
python -m unittest tests.test_member4_service -v
```
