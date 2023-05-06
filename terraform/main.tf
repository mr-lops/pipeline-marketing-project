terraform {

  #Define versão do Terraform que irá ser utilizada
  required_version = "~> 1.4.0"

  # Define os providers que serão utilizados
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }

  # Onde será guardado o estado do Terraform(contém informações sobre recursos que foram criados ou modificados utilizando o Terraform)
  # Recomendado guardar o estado remotamente, por exemplo em um bucket S3. Como esse projeto é para fins demonstrativos será utilizado o backend local.
  backend "local" {
    path = "terraform_state/terraform.tfstate"
  }

}

# Configurando o provider AWS no Terraform
provider "aws" {
  region = "us-east-1"

  # NÃO RECOMENDADO! Nesse projeto as credenciais de acesso estão guardadas em variaveis de ambiente.
  # access_key = "MinhaChaveDeAcesso"
  # secret_key = "MinhaChaveSecreta"

  # Essas tags serão adicionadas para todo recurso que for criado
  default_tags {
    tags = {
      owner       = "myname"
      managed-by  = "terraform"
      environment = "test"
    }
  }
}

