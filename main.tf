terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
}

provider "digitalocean" {
  token = "1c6508e264c30fcc6249f937d2d4eb2cacd6ebbf25b1b7cd300b777cb2339195"
}

resource "digitalocean_droplet" "server" {
  image    = "debian-11-x64"
  name     = "dhdb"
  region   = "sfo3"
  size     = "s-8vcpu-16gb"
  ssh_keys = ["50:ba:8f:a6:1a:e5:82:f8:57:5b:a0:c5:6e:00:f6:99"]

  connection {
    host        = self.ipv4_address
    user        = "root"
    type        = "ssh"
    timeout     = "2m"
    private_key = file("~/.ssh/id_rsa")
  }

  provisioner "remote-exec" {
    inline = [
      "apt-get update",
      "apt-get install -y python3 python3-pip tmux git vim",
      "curl -L https://github.com/dolthub/dolt/releases/latest/download/install.sh > /tmp/install.sh && bash /tmp/install.sh",
      "dolt config --global --add user.email rimantas@keyspace.lt",
      "dolt config --global --add user.name \"rl1987\"",
      "pip3 install openpyxl requests lxml js2xml doltpy",
    ]
  }

  provisioner "file" {
    source      = "~/.dolt"
    destination = "/root/.dolt"
  }
}

output "server_ip" {
  value = resource.digitalocean_droplet.server.ipv4_address
}

