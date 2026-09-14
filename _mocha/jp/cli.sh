db_dsn=postgres://awspg:XXfRdCsrZ*!BWo_$md:TIc.9mMxu@rds-proxy.proxy-c2v4sq80281m.us-east-1.rds.amazonaws.com:5432/events?sslmode=require

export RDSHOST="rds-proxy.proxy-c2v4sq80281m.us-east-1.rds.amazonaws.com" 
psql "host=$RDSHOST port=5432 dbname=events user=awspg sslmode=verify-full sslrootcert=./global-bundle.pem password=$(aws secretsmanager get-secret-value --secret-id 'arn:aws:secretsmanager:us-east-1:766769180913:secret:rds!cluster-00ee5123-c006-41e6-999c-1bb6fd4bf30e-KPmJDE' --query SecretString --output text | jq -r '.password')"