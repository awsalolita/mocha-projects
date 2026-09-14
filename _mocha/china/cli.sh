docker run -e WORDPRESS_DB_NAME=wordpress -e WORDPRESS_TABLE_PREFIX=wp_ -e WORDPRESS_DB_HOST=database-1.ckbs6iqqk49x.us-east-1.rds.amazonaws.com -e WORDPRESS_DB_USER=awsmysql -e WORDPRESS_DB_PASSWORD="h8(c58xLw.(s-iYRtj14X2IAY0|f"

# get config for a cluster in region 
aws eks update-kubeconfig --region us-east-1 --name micro

# enable OIDC provider
eksctl utils associate-iam-oidc-provider --cluster micro --region us-east-1 --approve