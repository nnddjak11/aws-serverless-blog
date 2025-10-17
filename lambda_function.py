import json
import boto3
import uuid
import re
from datetime import datetime
from botocore.exceptions import ClientError

# 初始化AWS服务客户端
dynamodb = boto3.resource('dynamodb')
cognito_idp = boto3.client('cognito-idp')
table_name = 'BlogArticles'  # 与你的DynamoDB表名一致
USER_POOL_ID = 'ap-southeast-1_JD2WBTmQV'  # 你的Cognito用户池ID


def lambda_handler(event, context):
    """主Lambda处理函数 - 仅保留文章接口，用Authorization头验证权限"""
    
    # 提取HTTP方法、路径和阶段
    http_method = event.get('requestContext', {}).get('http', {}).get('method', '').upper()
    raw_path = event.get('requestContext', {}).get('http', {}).get('path', '')
    stage = event.get('requestContext', {}).get('stage', '$default')

    print(f"Debug: 请求 - 方法={http_method}, 原始路径={raw_path}, 阶段={stage}")

    # 处理OPTIONS预检请求（允许Authorization头）
    if http_method == 'OPTIONS':
        return create_response(200, {'message': 'preflight ok'})

    # 标准化路径（移除阶段名前缀）
    normalized_path = normalize_path(raw_path, stage)
    print(f"Debug: 标准化路径 - {normalized_path}")

    # --------------------------
    # 文章相关路由（仅管理员可修改，所有人可查看）
    # --------------------------
    if normalized_path == '/articles':
        if http_method == 'GET':
            return get_articles()  # 所有人可查看
        elif http_method == 'POST':
            return create_article(event)  # 需管理员权限
        else:
            return create_response(405, {'message': 'Method not allowed'})

    elif normalized_path.startswith('/articles/'):
        article_id = normalized_path.split('/')[2] if len(normalized_path.split('/')) >= 3 else ''
        if not article_id:
            return create_response(400, {'message': 'Invalid article ID'})
        
        if http_method == 'GET':
            return get_article(article_id)  # 所有人可查看
        elif http_method == 'PUT':
            return update_article(article_id, event)  # 需管理员权限
        elif http_method == 'DELETE':
            return delete_article(article_id, event)  # 需管理员权限
        else:
            return create_response(405, {'message': 'Method not allowed'})

    # 未匹配路由
    return create_response(404, {'message': 'Resource not found'})


# --------------------------
# 核心：权限验证（从Authorization头提取Token）
# --------------------------

def verify_admin_access(event):
    """验证请求是否来自管理员（从Authorization头提取Bearer Token）"""
    # 1. 从请求头提取Token
    token = extract_token_from_header(event)
    print(f"Debug: 提取的Token = {token}")
    if not token:
        return {'authorized': False, 'message': '未提供Token（请登录）'}

    try:
        # 2. 用Cognito验证Token有效性，获取用户名
        get_user_response = cognito_idp.get_user(AccessToken=token)
        username = get_user_response.get('Username')
        print(f"Debug: 验证通过的用户 = {username}")

        # 3. 检查用户是否属于AdminGroup
        list_groups_response = cognito_idp.admin_list_groups_for_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        user_groups = [group['GroupName'] for group in list_groups_response.get('Groups', [])]
        print(f"Debug: 用户所属组 = {user_groups}")

        is_admin = "AdminGroup" in user_groups
        return {'authorized': is_admin, 'username': username}

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_msg = e.response['Error']['Message']
        print(f"Debug: Token验证失败 = {error_code}: {error_msg}")
        # 区分Token无效和其他错误
        if error_code in ['NotAuthorizedException', 'InvalidParameterException']:
            return {'authorized': False, 'message': 'Token无效（请重新登录）'}
        return {'authorized': False, 'message': f'服务器验证错误: {error_msg}'}
    except Exception as e:
        print(f"Debug: 权限验证异常 = {str(e)}")
        return {'authorized': False, 'message': '权限验证失败'}
......
# --------------------------
# 文章相关功能实现
# --------------------------

def get_articles():
    """获取所有文章（无需权限，所有人可看）"""
    try:
        table = dynamodb.Table(table_name)
        response = table.scan()
        articles = response.get('Items', [])
        return create_response(200, articles)
    except Exception as e:
        print(f"Error get_articles: {str(e)}")
        return create_response(500, {'message': '获取文章列表失败'})


def get_article(article_id):
    """获取单篇文章（无需权限）"""
    try:
        table = dynamodb.Table(table_name)
        response = table.get_item(Key={'id': article_id})
        if 'Item' in response:
            return create_response(200, response['Item'])
        else:
            return create_response(404, {'message': '文章不存在'})
    except Exception as e:
        print(f"Error get_article: {str(e)}")
        return create_response(500, {'message': '获取文章失败'})


def create_article(event):
    """创建文章（需管理员权限）"""
    # 先验证权限
    auth_result = verify_admin_access(event)
    if not auth_result['authorized']:
        return create_response(403, {'message': auth_result['message']})
    
    try:
        body = parse_body(event)
        if not body or not body.get('title') or not body.get('content'):
            return create_response(400, {'message': '标题和内容不能为空'})
        
        article_id = str(uuid.uuid4())
        table = dynamodb.Table(table_name)
        table.put_item(Item={
            'id': article_id,
            'title': body['title'],
            'content': body['content'],
            'date': datetime.utcnow().isoformat()
        })
        return create_response(201, {'message': '文章创建成功', 'articleId': article_id})
    except Exception as e:
        print(f"Error create_article: {str(e)}")
        return create_response(500, {'message': '创建文章失败'})


def update_article(article_id, event):
    """更新文章（修复保留关键字date的问题）"""
    auth_result = verify_admin_access(event)
    if not auth_result['authorized']:
        return create_response(403, {'message': auth_result['message']})
    
    try:
        body = parse_body(event)
        if not body or not body.get('title') or not body.get('content'):
            return create_response(400, {'message': '标题和内容不能为空'})
        
        table = dynamodb.Table(table_name)
        # 关键修复：用#dt作为date的别名，避开保留关键字
        table.update_item(
            Key={'id': article_id},
            # 用#dt替代date
            UpdateExpression='SET title = :t, content = :c, #dt = :d',
            # 告诉DynamoDB：#dt对应实际字段名date
            ExpressionAttributeNames={
                '#dt': 'date'
            },
            ExpressionAttributeValues={
                ':t': body['title'],
                ':c': body['content'],
                ':d': datetime.utcnow().isoformat()  # 保持原date格式
            }
        )
        return create_response(200, {'message': '文章更新成功'})
    except Exception as e:
        print(f"Error update_article: {str(e)}")  # 保留日志方便排查
        return create_response(500, {'message': '更新文章失败'})

def delete_article(article_id, event):
    """删除文章（需管理员权限）"""
    auth_result = verify_admin_access(event)
    if not auth_result['authorized']:
        return create_response(403, {'message': auth_result['message']})
    
    try:
        table = dynamodb.Table(table_name)
        table.delete_item(Key={'id': article_id})
        return create_response(200, {'message': '文章删除成功'})
    except Exception as e:
        print(f"Error delete_article: {str(e)}")
        return create_response(500, {'message': '删除文章失败'})
......
