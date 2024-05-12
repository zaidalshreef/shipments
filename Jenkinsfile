pipeline {
    agent any
    tools {
        // Specify the Docker tool and its version
        dockerTool 'docker'
    }
    stages {
        stage('Build') {
            steps {
                // Build Docker images for Django app and database
                // Docker Compose is already installed using the tool declaration
                sh 'docker compose build'
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
