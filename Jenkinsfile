pipeline {
    agent {
        docker {
            image 'maven:3.8.6-eclipse-temurin-11'
        }
    }

    stages {
        stage('Build with Maven') {
            steps {
                sh 'mvn clean package'
            }
        }

        stage('Publish to Nexus') {
            steps {
                nexusArtifactUploader(
                    credentialsId: 'nexus-credentials',
                    protocol: 'http',
                    nexusUrl: '3.90.5.208:8081',
                    nexusVersion: 'nexus3',
                    groupId: 'com.compressor',
                    version: "${env.BUILD_ID}",
                    repository: 'maven-releases',
                    artifacts: [
                        [artifactId: 'image-compressor',
                         classifier: '',
                         file: 'target/image-compressor.war',
                         type: 'war']
                    ]
                )
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Artifact pushed to Nexus.'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}