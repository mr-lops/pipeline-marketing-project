# Cria usuario airflow
resource "aws_iam_user" "airflow_user" {
  name = "airflow"

  force_destroy = true
}

# Cria politica para o usuario airflow ter acesso ao bucket marketing
resource "aws_iam_policy" "marketing_bucket_policy_for_airflow" {
  name        = "bucket_policy_airflow"
  path        = "/"
  description = "Permissões para o bucket de marketing"

  policy = jsonencode(
    {
      "Version" : "2012-10-17",
      "Statement" : [
        {
          "Sid" : "Stmt1683161920999",
          "Action" : [
            "s3:GetObject",
            "s3:ListBucket"
          ],
          "Effect" : "Allow",
          "Resource" : "${aws_s3_bucket.marketing_source_bucket.arn}"
        }
      ]
    }
  )
}

# Atribui a politica criada anteriormente ao usuario airflow
resource "aws_iam_user_policy_attachment" "marketing_policy_to_airflow" {
  user       = aws_iam_user.airflow_user.name
  policy_arn = aws_iam_policy.marketing_bucket_policy_for_airflow.arn

  depends_on = [
    aws_iam_user.airflow_user,
    aws_iam_policy.marketing_bucket_policy_for_airflow
  ]
}

# Cria chave de acesso para o usuario airflow
resource "aws_iam_access_key" "airflow_credentials" {
  user    = aws_iam_user.airflow_user.name

  depends_on = [
    aws_iam_user.airflow_user
  ]
}
