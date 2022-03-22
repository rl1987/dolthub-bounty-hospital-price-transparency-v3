terraform {
  required_providers {
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = "1c6508e264c30fcc6249f937d2d4eb2cacd6ebbf25b1b7cd300b777cb2339195"
}


