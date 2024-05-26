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
        EMAIL_PORT = credentials('EMAIL_PORT')
        EMAIL_HOST_USER = credentials('EMAIL_HOST_USER')
        EMAIL_HOST_PASSWORD = credentials('EMAIL_HOST_PASSWORD')
        EMAIL_USE_TLS = credentials('EMAIL_USE_TLS')
        EMAIL_HOST = credentials('EMAIL_HOST')
        EMAIL_PORT = credentials('EMAIL_PORT')
        DEFAULT_FROM_EMAIL = credentials('DEFAULT_FROM_EMAIL')
        INTERNAL_STAFF_EMAILS = credentials('INTERNAL_STAFF_EMAILS')

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
