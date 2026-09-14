eksctl create iamserviceaccount \
  --name plant \
  --namespace green-tree \
  --cluster app-cluster-ap \
  --role-name plant-role \
  --attach-policy-arn arn:aws:iam::471208936033:policy/application_policy \
  --approve \
  --region ap-northeast-2


eksctl create iamserviceaccount \
  --name grow \
  --namespace green-tree \
  --cluster app-cluster-ap \
  --role-name grow-role \
  --attach-policy-arn arn:aws:iam::471208936033:policy/application_policy \
  --approve \
  --region ap-northeast-2


eksctl delete iamserviceaccount \
  --name grow \
  --namespace green-tree \
  --cluster app-cluster-ap \
  --region ap-northeast-2


aws eks update-kubeconfig --region us-east-1 --name management-cluster


aws ecr create-repository \
     --repository-name microservice \
     --region ap-northeast-2

aws ecr get-login-password \
     --region ap-northeast-2 | helm registry login \
     --username AWS \
     --password-stdin 471208936033.dkr.ecr.ap-northeast-2.amazonaws.com

helm push helm-test-chart-0.1.0.tgz oci://471208936033.dkr.ecr.ap-northeast-2.amazonaws.com/

# Source - https://stackoverflow.com/a/67566800
# Posted by tifoz
# Retrieved 2026-08-28, License - CC BY-SA 4.0

argocd repo add 471208936033.dkr.ecr.ap-northeast-2.amazonaws.com --type helm  --name dynamodb-tables-ap --enable-oci --username AWS --password $(aws ecr get-login-password --regi
on ap-northeast-2)