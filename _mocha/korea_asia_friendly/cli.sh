aws eks update-kubeconfig --region us-east-1 --name concert-eks

# enable OIDC provider
eksctl utils associate-iam-oidc-provider --cluster concert-eks --region us-east-1 --approve


eksctl create iamserviceaccount \
  --name book \
  --namespace skills-concert \
  --cluster concert-eks \
  --role-name book-role \
  --attach-policy-arn arn:aws:iam::605731693050:policy/application_policy \
  --approve \
  --region us-east-1

eksctl create iamserviceaccount \
  --name query \
  --namespace skills-concert \
  --cluster concert-eks \
  --role-name query-role \
  --attach-policy-arn arn:aws:iam::605731693050:policy/application_policy \
  --approve \
  --region us-east-1


eksctl delete iamserviceaccount \
  --name book \
  --namespace skills-concert \
  --cluster concert-eks \
  --region us-east-1


eksctl list iamserviceaccount \
  --namespace skills-concert \
  --cluster concert-eks \
  --region us-east-1