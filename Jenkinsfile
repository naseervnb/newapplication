pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
        
        stage('Build Docker Image') {
            steps {
                // Navigate into the imageapp2026 directory where your Dockerfile lives
                dir('imageapp2026') {
                    sh 'docker build -t image-compressor:latest .'
                }
            }
        }
        
        stage('Deploy Python Container') {
            steps {
                sh '''
                    # Stop and remove any existing container to avoid port conflicts
                    docker stop python-compressor || true
                    docker rm python-compressor || true
                    
                    # Run the new container in detached mode on port 5000
                    docker run -d --name python-compressor -p 5000:5000 image-compressor:latest
                '''
            }
        }
    }
}



