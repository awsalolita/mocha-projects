terraform {
  backend "s3" {
    bucket       = "mng-states-209384"
    key          = "terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
