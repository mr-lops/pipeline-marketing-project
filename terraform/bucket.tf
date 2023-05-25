# Cria um bucket S3
resource "aws_s3_bucket" "marketing_source_bucket" {
  # Recebe o nome do bucket atraves da variavel "marketing_bucket_name"
  bucket = var.marketing_bucket_name

  # Por padrão, não é possivel destruir o bucket que contem arquivos, então utilizamos essa opção para forçar a destruição do bucket mesmo se conter arquivos
  force_destroy = true
}

# Upload de arquivos para bucket
resource "aws_s3_object" "files_csv" {
  for_each = fileset("../dados/", "*.csv")            # filtra os arquivos .csv da pasta dados
  bucket   = aws_s3_bucket.marketing_source_bucket.id # Id do bucket que ira receber o arquivo
  key      = each.value                               # Local/Nome do arquivo no bucket
  source   = "../dados/${each.value}"                 # Local/Nome do arquivo
  etag     = filemd5("../dados/${each.value}")        # hash do arquivo

  depends_on = [
    aws_s3_bucket.marketing_source_bucket
  ]
}
