aws eks update-kubeconfig --region us-east-1 --name concert-eks

eksctl utils associate-iam-oidc-provider --cluster concert-eks --region us-east-1 --approve

eksctl create iamserviceaccount \
  --name book \
  --namespace skills-concert \
  --cluster concert-eks \
  --role-name book_role \
  --attach-policy-arn arn:aws:iam::554949496620:policy/book_policy \
  --approve \
  --region us-east-1

eksctl create iamserviceaccount \
  --name query \
  --namespace skills-concert \
  --cluster concert-eks \
  --role-name query_role \
  --attach-policy-arn arn:aws:iam::554949496620:policy/query_policy \
  --approve \
  --region us-east-1