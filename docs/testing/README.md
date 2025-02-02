# 测试文档

## 目录

1. [测试概述](#测试概述)
2. [测试环境](#测试环境)
3. [测试用例](#测试用例)
4. [运行测试](#运行测试)
5. [测试覆盖率](#测试覆盖率)

## 测试概述

本项目使用 Python 的 unittest 框架进行单元测试。主要测试内容包括：
- 用户认证功能
- 安全限制功能（用户锁定和IP限制）
- API 接口功能

## 测试环境

- 测试框架：Python unittest
- 数据库：SQLite（内存数据库）
- 测试客户端：Flask test_client

## 测试用例

### 认证测试 (test_auth.py)

1. `test_successful_login`
   - 测试正常登录流程
   - 验证返回状态码和成功标志

2. `test_failed_login_user_lock`
   - 测试用户多次登录失败导致账户锁定
   - 验证用户锁定状态和失败计数
   - 验证锁定后无法登录

3. `test_ip_block`
   - 测试IP多次登录失败导致封禁
   - 验证IP封禁状态和失败计数
   - 验证封禁后无法登录

4. `test_unlock_user`
   - 测试管理员解锁用户功能
   - 验证用户解锁后状态重置
   - 验证解锁后可以正常登录

5. `test_unblock_ip`
   - 测试管理员解封IP功能
   - 验证IP解封后状态重置
   - 验证解封后可以正常访问

6. `test_reset_on_successful_login`
   - 测试成功登录后重置失败计数
   - 验证用户失败计数重置
   - 验证IP失败计数重置

### 测试数据准备

每个测试用例运行前会：
1. 创建新的内存数据库
2. 初始化必要的测试数据
3. 创建测试用户

测试完成后会：
1. 清理所有测试数据
2. 关闭数据库连接

## 运行测试

### 运行所有测试

```bash
python -m unittest discover tests
```

### 运行特定测试文件

```bash
python -m unittest tests/test_auth.py
```

### 运行特定测试用例

```bash
python -m unittest tests/test_auth.py -k test_successful_login
```

### 查看详细测试输出

```bash
python -m unittest tests/test_auth.py -v
```

## 测试覆盖率

要生成测试覆盖率报告：

1. 安装 coverage：
```bash
pip install coverage
```

2. 运行测试并收集覆盖率数据：
```bash
coverage run -m unittest discover
```

3. 生成覆盖率报告：
```bash
coverage report
```

4. 生成HTML格式的详细报告：
```bash
coverage html
```

主要功能的测试覆盖率目标：
- 认证相关功能：100%
- 安全限制功能：100%
- API接口：90%以上 