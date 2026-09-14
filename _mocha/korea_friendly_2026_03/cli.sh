eksctl utils associate-iam-oidc-provider --cluster app-cluster --region us-east-1 --approve

eksctl create iamserviceaccount \
  --name gift-shop-api \
  --namespace app \
  --cluster app-cluster \
  --role-name gift-shop-api-role \
  --attach-policy-arn arn:aws:iam::471112953209:policy/gift-shop-api-policy \
  --approve \
  --region us-east-1