# API 文档

## 目录

1. [认证相关](#认证相关)
2. [分类管理](#分类管理)
3. [链接管理](#链接管理)
4. [用户管理](#用户管理)

## 认证相关

### 登录

```
POST /admin/login

请求体：
{
    "username": "用户名",
    "password": "密码"
}

成功响应：
{
    "success": true
}

失败响应：
{
    "success": false,
    "message": "错误信息"
}
```

### 获取登录状态

```
GET /api/auth/status

成功响应：
{
    "authenticated": true,
    "username": "当前用户名"
}

未登录响应：
{
    "authenticated": false
}
```

### 退出登录

```
POST /api/auth/logout

成功响应：
{
    "success": true
}
```

## 分类管理

### 获取所有分类

```
GET /api/categories

响应：
[
    {
        "id": 1,
        "title": "分类标题",
        "section_name": "分区名称",
        "links": [...]
    }
]
```

### 添加分类

```
POST /api/admin/categories

请求体：
{
    "title": "分类标题",
    "section_name": "分区名称"
}

响应：
{
    "id": 1,
    "title": "分类标题",
    "section_name": "分区名称"
}
```

### 更新分类

```
PUT /api/admin/categories/<id>

请求体：
{
    "title": "新标题",
    "section_name": "新分区名称"
}

响应：
{
    "id": 1,
    "title": "新标题",
    "section_name": "新分区名称"
}
```

### 删除分类

```
DELETE /api/admin/categories/<id>

响应：
{
    "message": "Category deleted successfully"
}
```

## 链接管理

### 获取分类下的链接

```
GET /api/categories/<id>/links

响应：
[
    {
        "id": 1,
        "name": "链接名称",
        "url": "链接地址",
        "category_id": 1
    }
]
```

### 添加链接

```
POST /api/admin/links

请求体：
{
    "name": "链接名称",
    "url": "链接地址",
    "category_id": 1
}

响应：
{
    "id": 1,
    "name": "链接名称",
    "url": "链接地址",
    "category_id": 1
}
```

### 更新链接

```
PUT /api/admin/links/<id>

请求体：
{
    "name": "新名称",
    "url": "新地址",
    "category_id": 1
}

响应：
{
    "id": 1,
    "name": "新名称",
    "url": "新地址",
    "category_id": 1
}
```

### 删除链接

```
DELETE /api/admin/links/<id>

响应：
{
    "message": "Link deleted successfully"
}
```

## 用户管理

### 获取所有用户

```
GET /api/admin/users

响应：
[
    {
        "id": 1,
        "username": "用户名",
        "created_at": "创建时间"
    }
]
```

### 添加用户

```
POST /api/admin/users

请求体：
{
    "username": "新用户名",
    "password": "密码"
}

响应：
{
    "id": 1,
    "username": "新用户名",
    "created_at": "创建时间"
}
```

### 更新用户

```
PUT /api/admin/users/<id>

请求体：
{
    "username": "新用户名",
    "password": "新密码"  // 可选
}

响应：
{
    "id": 1,
    "username": "新用户名",
    "created_at": "创建时间"
}
```

### 解锁用户

```
POST /api/admin/users/<id>/unlock

响应：
{
    "message": "用户已解锁"
}
```

### 解封IP

```
POST /api/admin/ip-blocks/<id>/unblock

响应：
{
    "message": "IP已解封"
}
``` 