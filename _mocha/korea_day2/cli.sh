export NAMESPACE="kube-system"
export CLUSTER_NAME="hallyu-cluster"
export VPC_ID="vpc-037b8afc0d3d77c23"
export REGION="us-east-1"


## Tag subnets for alb
PUBLIC_SUBNETS="subnet-0dfd51b0e2e2c6a4b subnet-023e0d06e89c36eaa"
PRIVATE_SUBNETS="subnet-00da02d0842a2d15c subnet-032fba9426f89f590"

aws ec2 create-tags --resources $PUBLIC_SUBNETS --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared Key=kubernetes.io/role/elb,Value=1

# Tag private subnets
aws ec2 create-tags --resources $PRIVATE_SUBNETS --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared Key=kubernetes.io/role/internal-elb,Value=1


# Enable DNS resolution
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json
aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json
# 3) Create SA + role + policy (do NOT kubectl create sa first)

eksctl create iamserviceaccount \
  --cluster ${CLUSTER_NAME} \
  --region ${REGION} \
  --namespace kube-system \
  --name aws-lb \
  --attach-policy-arn arn:aws:iam::193801312183:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve


helm repo add eks https://aws.github.io/eks-charts

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
    --set clusterName=${CLUSTER_NAME} \
    --set region=${REGION}  \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-lb \
    --set vpcId=${VPC_ID} \
    -n ${NAMESPACE}



eksctl utils associate-iam-oidc-provider --cluster hallyu-cluster --region us-east-1 --approve

eksctl create iamserviceaccount \
  --name ingest \
  --namespace app \
  --cluster hallyu-cluster \
  --role-name ingest-role \
  --attach-policy-arn arn:aws:iam::193801312183:policy/s3_policy \
  --approve \
  --region us-east-1

curl -F "project_id=456" -F "file=@" localhost:8080/ingest/upload