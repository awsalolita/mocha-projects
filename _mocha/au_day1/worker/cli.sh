eksctl create iamserviceaccount \
  --name worker \
  --namespace astra \
  --cluster titanflow-astra-cluster \
  --role-name worker_role \
  --attach-policy-arn arn:aws:iam::537275484040:policy/worker_policy \
  --approve \
  --region us-east-1


eksctl create iamserviceaccount \
  --name router \
  --namespace astra \
  --cluster titanflow-astra-cluster \
  --role-name router_role \
  --attach-policy-arn arn:aws:iam::537275484040:policy/router_policy \
  --approve \
  --region us-east-1


PUBLIC_SUBNETS="subnet-01e93e742d9eb751e subnet-0672fb69ebe47ba32"
PRIVATE_SUBNETS="subnet-04f6148c891ec93a1 subnet-021697b53d431d84a"
EKS_NAME="titanflow-astra-cluster"
VPC_ID="vpc-029ea3fabd06e4a6b"

aws ec2 create-tags --resources $PUBLIC_SUBNETS --tags Key=kubernetes.io/cluster/$EKS_NAME,Value=shared Key=kubernetes.io/role/elb,Value=1

# Tag private subnets
aws ec2 create-tags --resources $PRIVATE_SUBNETS --tags Key=kubernetes.io/cluster/$EKS_NAME,Value=shared Key=kubernetes.io/role/internal-elb,Value=1


# Enable DNS resolution
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames
