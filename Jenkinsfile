pipeline {
    agent any
    tools {
        // Specify the Docker tool and its version
        dockerTool 'docker'
    }
    environment {
        DOCKER_CONFIG = "${HOME}/.docker"
        DOCKER_COMPOSE_URL = 'https://github.com/docker/compose/releases/download/1.29.2/docker-compose-Linux-x86_64'
    }
    stages {
        stage('Install Docker Compose') {
            steps {
                script {
                    // Download Docker Compose binary
                    sh "curl -L ${DOCKER_COMPOSE_URL} -o ${DOCKER_CONFIG}/cli-plugins/docker-compose"
                    // Make Docker Compose binary executable
                    sh "chmod +x ${DOCKER_CONFIG}/cli-plugins/docker-compose"
                }
            }
        }
        stage('Build') {
            steps {
                // Build Docker images for Django app and database
                // Docker Compose is already installed using the tool declaration
                sh 'docker-compose build'
            }
        }
        stage('Deploy to Staging') {
            steps {
                // Start the Docker containers
                sh 'docker-compose up -d'
            }
        }
    }
}
