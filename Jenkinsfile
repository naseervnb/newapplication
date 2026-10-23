pipeline {
    agent any

    stages {
        stage('Build with Maven') {
            steps {
                dir('imageapp2026') {
                    sh '''
                        # Download Maven dynamically if not present
                        if ! command -v mvn &> /dev/null; then
                            echo "Downloading Maven..."
                            curl -sO https://archive.apache.org/dist/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz
                            tar -xzf apache-maven-3.8.6-bin.tar.gz
                        fi
                        
                        export PATH=$PWD/apache-maven-3.8.6/bin:$PATH
                        mvn clean package
                    '''
                }
            }
        }

        stage('Publish to Nexus') {
            steps {
                nexusArtifactUploader(
                    credentialsId: 'nexus-credentials',
                    protocol: 'http',
                    nexusUrl: '98.81.175.140:8081',
                    nexusVersion: 'nexus3',
                    groupId: 'com.compressor',
                    version: "${env.BUILD_ID}",
                    repository: 'maven-releases',
                    artifacts: [
                        [artifactId: 'image-compressor',
                         classifier: '',
                         file: 'imageapp2026/target/image-compressor.war',
                         type: 'war']
                    ]
                )
            }
        }

        stage('Deploy to Tomcat') {
            steps {
                sh '''
                    echo "Copying artifact to Tomcat container..."
                    docker cp imageapp2026/target/image-compressor.war tomcat-server:/usr/local/tomcat/webapps/image-compressor.war
                    echo "Deployment complete!"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Build, Publish, and Deploy all passed.'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}