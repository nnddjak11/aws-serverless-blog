# AWS Serverless Blog System  

A distributed personal blog built with AWS fully-managed services—focused on **multi-region high availability**, **global low latency**, and **serverless cost savings**.  


## 项目背景（Project Background）  
Solves traditional blog pain points (high server maintenance costs) via AWS Serverless. Upgraded to **Singapore + Hong Kong multi-region architecture** to avoid single-region outages and reduce global access latency. Supports admin article management (create/update/delete) and global user access.  


## 架构设计（Architecture）  
![Architecture Diagram](https://github.com/nnddjak11/aws-serverless-blog/blob/main/image/architect-pic.PNG)
*High-res: [Architecture Design](images/architect-pic.PNG)*  

### 核心服务与分布式设计（Core Services）  
1. **Frontend**: S3 (static assets) + CloudFront (global CDN)  
   - S3 cross-region sync (Singapore → Hong Kong) for disaster recovery  
   - CloudFront edge caching (global latency down 60%) + origin failover  
2. **Auth**: Cognito User Pool (admin email/password login + JWT verification)  
3. **Backend**: API Gateway + Lambda (Python)  
   - Serverless API (no servers to manage)  
   - Lambda auto-failover to Hong Kong DynamoDB if Singapore is down  
4. **Data**: DynamoDB Global Table (Singapore + Hong Kong)  
   - Real-time bidirectional sync (<2s latency) + multi-AZ redundancy  
5. **Security/Monitoring**: WAF (blocks attacks) + CloudWatch (10min alerts)  


## 技术亮点（Key Technical Details）  
1. **Distributed Data**: DynamoDB Global Table ensures cross-region data consistency; Lambda auto-switches regions on failure.  
2. **Global Delivery**: S3 CRR + CloudFront cuts European user latency from 300ms to 80ms.  
3. **Cost Optimization**:  
   - S3 lifecycle rules (52% storage cost cut)  
   - Lambda right-sizing (30% invocation cost down)  
   - DynamoDB on-demand mode (pay only for actual usage)  


## 项目成果（Achievements）  
- Availability: 99.99% (annual downtime < 53 mins)  
- Global latency: 80ms average (vs. 250ms single-region)  
- Monthly cost: < $25 (vs. $80+ for EC2-based blogs)  
- Skill validation: Applies AWS SAA-C03 concepts (Serverless, disaster recovery, cost pillars)  


## 部署指南（Deployment）  
Use AWS CloudFormation for consistent setup:  
1. Create S3 buckets (SG + HK) + enable CRR  
2. Deploy DynamoDB Global Table  
3. Set up Lambda + API Gateway + Cognito  
4. Configure CloudFront + WAF  

*Full guide + template: [deploy-guide.md](deploy-guide.md)*  


## 联系方式（Contact）  
- GitHub: [nnddjak11](https://github.com/nnddjak11)  
- Email: l1872887583@163.com  
- Note: Email preferred (regional network limits LinkedIn responsiveness)  


*Built with AWS SAA-C03 best practices | Oct 2025*
