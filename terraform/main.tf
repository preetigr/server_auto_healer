terraform {
    required_providers {
        dockers = {
            source = "kreuzwerker/docker"
            version= "~> 3.0"
        }
    }
}

provider "docker" {
    host = "unix:///var/run/docker.sock"
}

resource "docker_container" "target_app" {
    name = "target-app"
    image = "target_service:latest"

    ports {
        internal = 8080
        external = 8080
    }
}