aws eks update-kubeconfig --region us-east-1 --name mealmint-eks

eksctl utils associate-iam-oidc-provider --cluster mealmint-eks --region us-east-1 --approve

mongoimport  --host mealmint-recipes.cluster-c8t8o4e8myfc.us-east-1.docdb.amazonaws.com:27020 -u awsmongo --ssl --sslCAFile global-bundle.pem --jsonArray --db mealmint --collection recipes --file seed_recipes.json


db.createCollection(' recipes' );
mongodb://awsmongo:$f_8XN2jLWg7Sqeqx1HR4BI_9HOb@mealmint-recipes.cluster-c8t8o4e8myfc.us-east-1.docdb.amazonaws.com:27020/?tls=true&replicaSet=rs0&readPreference=secondaryPreferred&retryWrites=false


helm install kyverno kyverno/kyverno -n kyverno --create-namespace \
--set admissionController.replicas=1 \
--set backgroundController.enabled=false \
--set cleanupController.enabled=false \
--set reportsController.enabled=false


aws ecr create-repository \
     --repository-name microservice \
     --region us-east-1

aws ecr get-login-password \
     --region us-east-1 | helm registry login \
     --username AWS \
     --password-stdin 471208936033.dkr.ecr.us-east-1.amazonaws.com

helm push helm-test-chart-0.1.0.tgz oci://471208936033.dkr.ecr.us-east-1.amazonaws.com/

argocd login argocd.mealmint.internal --username admin --password 'dqUbM-CfUSoFeLAC' --insecure --skip-test-tls --core



FUNCTION_NAME=mealmint-spa-rewrite
for region in $(aws --output text  ec2 describe-regions | cut -f 3) 
do
    for loggroup in $(aws --output text  logs describe-log-groups --log-group-name "/aws/lambda/us-east-1.$FUNCTION_NAME" --region $region --query 'logGroups[].logGroupName')
    do
        echo $region $loggroup
    done
done


aws acm import-certificate \
  --certificate fileb://pki/issued/server.crt \
  --private-key fileb://pki/private/server.key \
  --certificate-chain fileb://pki/ca.crt \
  --region us-east-1


aws acm import-certificate \
  --certificate fileb://pki/issued/client1.domain.tld.crt \
  --private-key fileb://pki/private/client1.domain.tld.key \
  --certificate-chain fileb://pki/ca.crt \
  --region us-east-1
