# Mostra o nome do bucket criado quando a infraestrutura for provisionada
output "bucket_name" {
  value = aws_s3_bucket.marketing_source_bucket.bucket
}

# Mostra a chave de acesso do usuario airflow
output "airflow_access_key" {
  value = aws_iam_access_key.airflow_credentials.id
}

# Mostra a chave secreta do usuario airflow
output "airflow_secret_key" {
  value     = aws_iam_access_key.airflow_credentials.secret
  sensitive = true
}

# terraform output -json