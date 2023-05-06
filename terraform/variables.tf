# Nome do bucket S3 que será criado para armazenar os dados em CSV
variable "marketing_bucket_name" {
  description = "Nome do bucket onde será armazenado os arquivos CSV"
  type        = string
  default     = "bucket-projeto-marketing"
}