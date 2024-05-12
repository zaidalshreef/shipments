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
                // Install Docker Compose
                sh 'curl -L https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose'
                sh 'chmod +x /usr/local/bin/docker-compose'
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
