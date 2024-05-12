pipeline {
    agent any
    stages {
        stage('Build') {
            steps {
                // Build Docker images for Django app and database
                sh 'docker compose build'
            }
        }
        stage('Deploy to Staging') {
            steps {
                // Start the Docker containers
                sh 'docker compose up -d'
            }
        }
    }
   
}
