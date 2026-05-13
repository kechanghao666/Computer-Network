# 补充功能说明

本文件说明本次补充的三个实现点：图形化客户端、SMTP 配置检查和真实测试邮件、RTT 记录留存与导出。

## 1. 图形化客户端

先启动服务器：

```powershell
python server\bank_server.py
```

再启动图形化客户端：

```powershell
python client\gui_client.py
```

图形化客户端支持：

- 连接服务器。
- 登录。
- 查询余额。
- 取款。
- 存款。
- 查询流水。
- RTT 测试。
- 退出系统。

## 2. SMTP 配置检查和测试邮件

SMTP 配置仍然使用环境变量：

```powershell
$env:ATM_SMTP_HOST="smtp.qq.com"
$env:ATM_SMTP_PORT="465"
$env:ATM_SMTP_USER="your@qq.com"
$env:ATM_SMTP_PASSWORD="smtp_authorization_code"
$env:ATM_SMTP_FROM="your@qq.com"
$env:ATM_SMTP_SSL="true"
```

检查当前配置是否完整：

```powershell
python -m email_service.smtp_email --check
```

发送真实测试邮件：

```powershell
python -m email_service.smtp_email --to your@qq.com
```

如果测试邮件显示 `sent`，存款和取款后的邮件通知也会使用同一套 SMTP 配置发送。

## 3. RTT 记录与导出

客户端执行 RTT 测试后，结果会自动保存到 SQLite 数据库表 `rtt_record`，字段包含：

- 测试目标主机和端口。
- 测试次数。
- 是否成功。
- 最小 RTT、最大 RTT、平均 RTT。
- 每次 RTT 原始值。
- 网络状态。
- 测试时间。

导出 RTT 记录为 CSV：

```powershell
python -c "from database.account_service import export_rtt_records_csv; export_rtt_records_csv('rtt_records.csv')"
```

导出文件可用于展示线路传输质量统计分析。
