helm upgrade --install gateway-api-controller \
  oci://public.ecr.aws/aws-application-networking-k8s/aws-gateway-controller-chart \
  --version=v2.1.3 \
  --create-namespace \
  --namespace aws-application-networking-system \
  --set clusterName=vitalforge-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=gateway-api-controller \
  --set clusterVpcId=vpc-0c9724d43eaed906a \
  --set awsRegion=us-east-1 \
  --set awsAccountId=471208936033

eksctl utils associate-iam-oidc-provider --cluster vitalforge-cluster --region us-east-1 --approve


eksctl create iamserviceaccount \
    --cluster=vitalforge-cluster \
    --namespace=aws-application-networking-system \
    --name=gateway-api-controller \
    --attach-policy-arn=arn:aws:iam::471208936033:policy/VPCLatticeControllerIAMPolicy \
    --override-existing-serviceaccounts \
    --region us-east-1 \
    --approve

helm upgrade --install gateway-api-controller \
  oci://public.ecr.aws/aws-application-networking-k8s/aws-gateway-controller-chart \
  --version=v2.1.3 \
  --create-namespace \
  --namespace aws-application-networking-system \
  --set clusterName=vitalforge-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=gateway-api-controller \
  --set clusterVpcId=vpc-0c9724d43eaed906a \
  --set awsRegion=us-east-1 \
  --set awsAccountId=471208936033



eksctl create iamserviceaccount \
  --name api-sa \
  --namespace app \
  --cluster vitalforge-cluster \
  --role-name api_role \
  --attach-policy-arn arn:aws:iam::471208936033:policy/api_policy \
  --approve \
  --region us-east-1