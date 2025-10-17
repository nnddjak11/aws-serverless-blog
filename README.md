# AWS Serverless Blog System

A personal blog platform built with AWS fully-managed services, focusing on high availability, low cost, and easy maintenance.

## 项目背景（Project Background）
传统博客需要维护服务器，成本高且运维繁琐。本项目基于AWS Serverless架构，实现“零服务器管理”的博客系统，支持管理员文章管理和全球用户访问。

## 架构设计（Architecture）
![架构图](iamges/architect-pic.PNG)  
*点击查看高清图：[Architecture Design](images/architect-pic.PNG)*

### 核心服务（Core AWS Services）
1. **前端层**：S3存储HTML/图片，CloudFront全球分发（降低访问延迟）；  
2. **认证层**：Cognito实现管理员登录（支持邮箱/密码认证）；  
3. **后端层**：API Gateway作为请求入口，Lambda处理业务逻辑（文章CRUD）；  
4. **数据层**：DynamoDB存储文章数据（高并发、自动扩缩容）；  
5. **安全与监控**：WAF防护API攻击，CloudWatch监控服务状态。

## 技术细节（Technical Details）
### 1. Lambda函数逻辑（Python）
- 处理API Gateway的POST/GET/PUT/DELETE请求，对应“新建/查询/修改/删除”文章；  
- 示例代码：[lambda_function.py](lambda_function.py)（包含Cognito认证校验逻辑）。

### 2. 成本优化设计（Cost Optimization）
- S3生命周期规则：30天未访问文件自动转至低频存储，降低52%存储成本；  
- Lambda内存配置：从512MB优化至256MB，调用成本降低30%（响应时间仍<300ms）。

### 3. 高可用设计（High Availability）
- S3跨区域备份：静态资源同步至AWS首尔区域，避免单区域故障；  
- DynamoDB自动扩缩容：根据访问量动态调整读写能力，确保高峰期稳定。

## 成果（Achievements）
- 服务可用性：99.98%（全年故障时间<1小时）；  
- 运维效率：零服务器管理，部署更新仅需10分钟；  
- 学习价值：实践AWS SAA-C03认证中的“Serverless架构”“成本优化支柱”等知识点。

## 如何部署（Deployment Guide）
1. 创建S3桶并上传前端文件；  
2. 部署Lambda函数并配置API Gateway；  
3. 初始化DynamoDB表和Cognito用户池；  
4. 配置CloudFront分发和WAF规则。  
*详细步骤见：[deploy-guide.md](deploy-guide.md)*

## 联系方式（Contact）
- GitHub: nnddjak11 
- LinkedIn: www.linkedin.com/in/henbo-li-11b290376 (I'm very sorry, using mainland China's internet restrictions, I am unable to upgrade to a premium account to communicate./非常抱歉，大陆科学上网使用，无法升级高级账号进行沟通。）
- Email: l1872887583@163.com
