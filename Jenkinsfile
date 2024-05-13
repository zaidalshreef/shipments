pipeline {
    agent any
     environment {
        POSTGRES_PASSWORD = credentials('POSTGRES_PASSWORD')
        POSTGRES_NAME = credentials('POSTGRES_NAME')
        POSTGRES_USER = credentials('POSTGRES_USER')
        DJANGO_SECRET_KEY = credentials('DJANGO_SECRET_KEY')
        POSTGRES_HOST = credentials('POSTGRES_HOST')
        POSTGRES_PORT = credentials('POSTGRES_PORT')
        POSTGRES_DB = credentials('POSTGRES_DB')

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
                sh 'docker compose up -d'
            }
        }
    }
}
