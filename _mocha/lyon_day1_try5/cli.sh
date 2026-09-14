aws cloudwatch put-metric-alarm \
  --alarm-name "APIGateway-High5xxErrors" \
  --alarm-description "Triggers if API Gateway returns >10 5xx errors in 5 minutes" \
  --metric-name "5XXError" \
  --namespace "AWS/ApiGateway" \
  --statistic "Sum" \
  --period 300 \
  --evaluation-periods 1 \
  --threshold 10 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=ApiName,Value=api" \
  --alarm-actions "arn:aws:sns:us-east-1:891377138880:unicorn-alerts"

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
  --dimensions "Name=NatGatewayId,Value=nat-03fc975f4103ee584" \
  --alarm-actions "arn:aws:sns:us-east-1:891377138880:unicorn-alerts"

aws cloudwatch put-metric-alarm \
  --alarm-name "ECS-HighCPUUtilization" \
  --alarm-description "Triggers if ECS cluster CPU exceeds 80% for 10 minutes" \
  --metric-name "CPUUtilization" \
  --namespace "AWS/ECS" \
  --statistic "Average" \
  --period 300 \
  --evaluation-periods 2 \
  --threshold 80 \
  --comparison-operator "GreaterThanThreshold" \
  --dimensions "Name=ClusterName,Value=AWSBatch-process-env-8f5c461d-b978-3a59-b71a-36ed40469765" \
  --alarm-actions "arn:aws:sns:us-east-1:891377138880:unicorn-alerts"



aws logs put-metric-filter \
  --log-group-name "YOUR_VPC_FLOW_LOG_GROUP" \
  --filter-name "RejectedTrafficFilter" \
  --filter-pattern '[version, account, eni, source, dest, srcport, destport, protocol, packets, bytes, start, end, action="REJECT", log_status]' \
  --metric-transformations metricName=RejectedConnections,metricNamespace=Custom/VPCFlowLogs,metricValue=1

aws cloudwatch put-metric-alarm \
  --alarm-name "VPC-High-Rejected-Traffic" \
  --alarm-description "Triggers when rejected connections exceed 100 in 5 minutes (potential scan/DDoS)" \
  --metric-name RejectedConnections \
  --namespace Custom/VPCFlowLogs \
  --statistic Sum \
  --period 300 \
  --threshold 100 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1 \
  --treat-missing-data notBreaching \
  --alarm-actions YOUR_SNS_TOPIC_ARN


aws ec2 create-flow-logs \
  --resource-type VPC \
  --resource-ids vpc-020b547f89c66e3e9 \
  --traffic-type ALL \
  --log-destination-type cloud-watch-logs \
  --log-group-name arn:aws:logs:us-east-1:891377138880:log-group:vpcflowlogs:* \
  --deliver-logs-permission-arn YOUR_IAM_ROLE_ARN \
  --destination-options "FileFormat=parquet,HiveCompatiblePartitions=true,PerHourPartition=true"