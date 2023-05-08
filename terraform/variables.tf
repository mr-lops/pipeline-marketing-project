# Nome do bucket S3 que será criado para armazenar os dados em CSV
variable "marketing_bucket_name" {
  description = "Nome do bucket onde será armazenado os arquivos CSV"
  type        = string
  default     = "bucket-projeto-marketing"

  validation {
    condition     = length(var.marketing_bucket_name) > 2 && length(var.marketing_bucket_name) < 64 && can(regex("^[0-9A-Za-z-]+$", var.marketing_bucket_name))
    error_message = "O bucket não segue as regras de nomenclatura. Para mais informações visite: https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucketnamingrules.html"
  }
}