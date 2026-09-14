export NAMESPACE="kube-system"
export CLUSTER_NAME="concert-eks"
export VPC_ID="vpc-0313e607266c83a19"
export REGION="us-east-1"


## Tag subnets for alb
PUBLIC_SUBNETS="subnet-018f38287497dda8d subnet-0b8030146d4652053"
PRIVATE_SUBNETS="subnet-055753d781bb477cb subnet-00b5ad5b0b88c21fd"

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
  --attach-policy-arn arn:aws:iam::554949496620:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve


helm repo add eks https://aws.github.io/eks-charts

helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
    --set clusterName=${CLUSTER_NAME} \
    --set region=${REGION}  \
    --set serviceAccount.create=false \
    --set serviceAccount.name=aws-lb \
    --set vpcId=${VPC_ID} \
    -n ${NAMESPACE}