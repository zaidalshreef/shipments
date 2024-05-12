pipeline {
    agent any
    tools {
        // Specify the Docker tool and its version
        dockerTool 'docker'
    }
    environment {
        DOCKER_CONFIG = "${HOME}/.docker"
    }
    stages {
        stage('Install Docker Compose') {
            steps {
                script {
                    // Create Docker CLI plugins directory if it doesn't exist
                    sh 'mkdir -p $DOCKER_CONFIG/cli-plugins'
                    // Download Docker Compose binary
                    sh 'curl -SL https://github.com/docker/compose/releases/download/v2.27.0/docker-compose-linux-x86_64 -o $DOCKER_CONFIG/cli-plugins/docker-compose'
                    // Make Docker Compose binary executable
                    sh 'chmod +x $DOCKER_CONFIG/cli-plugins/docker-compose'
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
