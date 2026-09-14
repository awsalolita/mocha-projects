aws eks update-kubeconfig --region us-east-1 --name titanflow-astra-cluster

# enable OIDC provider
eksctl utils associate-iam-oidc-provider --cluster eks-cluster --region us-east-1 --approve

eksctl create iamserviceaccount \
  --name worker \
  --namespace astra \
  --cluster titanflow-astra-cluster \
  --role-name worker_role \
  --attach-policy-arn arn:aws:iam::590183988289:policy/worker_policy \
  --approve \
  --region us-east-1


eksctl create iamserviceaccount \
  --name router \
  --namespace astra \
  --cluster titanflow-astra-cluster \
  --role-name router_role \
  --attach-policy-arn arn:aws:iam::590183988289:policy/router_policy \
  --approve \
  --region us-east-1
