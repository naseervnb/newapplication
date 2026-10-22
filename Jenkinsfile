pipeline {
    agent any

    stages {
        stage('Build with Maven') {
            steps {
                sh '''
                    # Check if mvn exists, if not download via curl and set it up locally
                    if ! command -v mvn &> /dev/null; then
                        echo "Maven not found. Downloading via curl..."
                        curl -sO https://archive.apache.org/dist/maven/maven-3/3.8.6/binaries/apache-maven-3.8.6-bin.tar.gz
                        tar -xzf apache-maven-3.8.6-bin.tar.gz
                    fi
                    
                    # Add local maven to PATH for this build
                    export PATH=$PWD/apache-maven-3.8.6/bin:$PATH
                    
                    # Run the build from the root directory
                    mvn clean package
                '''
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