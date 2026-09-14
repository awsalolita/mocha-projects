eksctl utils associate-iam-oidc-provider --cluster mealmint-eks --region us-east-1 --approve

export NAMESPACE="kube-system"
export CLUSTER_NAME="mealmint-eks"
export VPC_ID="vpc-08317e834a039b210"
export REGION="us-east-1"
PUBLIC_SUBNETS="subnet-088ed44d2cf0c8191 subnet-0819a053c80ebf4dc"
PRIVATE_SUBNETS="subnet-06461510ab0cbf1d3 subnet-0ebe6c3e7012d6805"


aws ec2 create-tags --resources $PUBLIC_SUBNETS --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared Key=kubernetes.io/role/elb,Value=1

aws ec2 create-tags --resources $PRIVATE_SUBNETS --tags Key=kubernetes.io/cluster/$CLUSTER_NAME,Value=shared Key=kubernetes.io/role/internal-elb,Value=1


aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-support

# Enable DNS hostnames
aws ec2 modify-vpc-attribute --vpc-id $VPC_ID --enable-dns-hostnames

curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/main/docs/install/iam_policy.json

aws iam create-policy \
  --policy-name AWSLoadBalancerControllerIAMPolicy \
  --policy-document file://iam_policy.json

eksctl create iamserviceaccount \
  --cluster ${CLUSTER_NAME} \
  --region ${REGION} \
  --namespace kube-system \
  --name aws-lb \
  --attach-policy-arn arn:aws:iam::471208936033:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve



mongoimport --host mealmint-recipes.c8t8o4e8myfc.us-east-1.docdb.amazonaws.com:27018 --ssl --sslCAFile global-bundle.pem --username awsmongo --password "nn_x_Vl(~a)_nAI?5y0V4|7K_-Q5"  --db mealmint --collection recipes --file seed_recipes.json --jsonArray

mongoimport --host <cluster-endpoint>:27017 \
  --ssl \
  --sslCAFile global-bundle.pem \
  --username <your-username> \
  --password <your-password> \
  --db <database-name> \
  --collection <collection-name> \
  --file data.json