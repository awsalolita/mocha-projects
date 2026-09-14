
aws cloudwatch put-metric-alarm \
  --alarm-name "CloudFront-High5xxErrorRate" \
  --alarm-description "Triggers if CloudFront 5xx errors exceed 5% for 5 minutes" \
  --metric-name "5xxErrorRate" \
  --namespace "AWS/CloudFront" \
  --statistic "Average" \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 5 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=DistributionId,Value=E1X7JNGNWWJI01" "Name=Region,Value=Global" \
  --alarm-actions "arn:aws:sns:us-east-1:518286664249:Alerts"

aws cloudwatch put-metric-alarm \
  --alarm-name "ALB-HighTarget5xxErrors" \
  --alarm-description "Triggers if targets behind the ALB return >10 5xx errors in 5 minutes" \
  --metric-name "HTTPCode_Target_5XX_Count" \
  --namespace "AWS/ApplicationELB" \
  --statistic "Sum" \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=LoadBalancer,Value=app/unicorn/dccc6730ff3c240a" \
  --alarm-actions "arn:aws:sns:us-east-1:518286664249:Alerts"


aws cloudwatch put-metric-alarm \
  --alarm-name "EKS-NodeHighCPU" \
  --alarm-description "Triggers if EKS node CPU exceeds 80% for 10 minutes" \
  --metric-name "node_cpu_utilization" \
  --namespace "ContainerInsights" \
  --statistic "Average" \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=ClusterName,Value=unicorn-cluster" \
  --alarm-actions "arn:aws:sns:us-east-1:518286664249:Alerts"


aws cloudwatch put-metric-alarm \
  --alarm-name "NATGateway-ErrorPortAllocation" \
  --alarm-description "Triggers if NAT Gateway fails to allocate ports (SNAT exhaustion)" \
  --metric-name "ErrorPortAllocation" \
  --namespace "AWS/NATGateway" \
  --statistic "Sum" \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 0 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=NatGatewayId,Value=nat-1eb98bed98f49bf4c" \
  --alarm-actions "arn:aws:sns:us-east-1:518286664249:Alerts"
