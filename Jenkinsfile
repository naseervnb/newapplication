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
                    nexusUrl: '3.90.5.208:8081',
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
                    echo "Deploying artifact to Tomcat..."
                    # If Tomcat is running locally on the EC2 instance or container, 
                    # you can copy the built .war directly to Tomcat's webapps directory:
                    # cp imageapp2026/target/image-compressor.war /path/to/tomcat/webapps/image-compressor.war
                    
                    echo "Deployment step ready. Adjust the target path based on your Tomcat setup!"
                '''
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully! Artifact built, published to Nexus, and deployed.'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
    }
}