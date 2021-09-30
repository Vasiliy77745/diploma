def timeout = 300

pipeline {
    agent {
        label 'master'
    }
    
    parameters {
      string(name: 'stackName', defaultValue: 'myapp-dev', description: 'How to name stack')
      imageTag(name: 'DOCKER_IMAGE', description: 'Which image tag to deploy',
             image: 'alexv77745/diploma', defaultTag: 'latest',
             registry: 'https://registry-1.docker.io')
    }
    
    stages {
        stage('Deploy') {
            steps {
                script{
                    withAWS(credentials: 'aws_admin', region: 'us-east-1') {
                        sh 'sleep 10'
                        def outputs = cfnUpdate(stack:params.stackName, file:'cfn-stack/stack.yaml', timeoutInMinutes:10, pollInterval:5000, params:["AppImage=${params.DOCKER_IMAGE}"])
                        def url = "http://${outputs.AppDnsName}/healthcheck"
                        def time = 0
                        def status
                        while( status != 200 && time < timeout) {
                            sleep time: 10, unit: 'SECONDS'
                            status = httpRequest(quiet: true, responseHandle: 'NONE', url: url, validResponseCodes: '100:599').status
                            echo "App's URL returns: ${status}"
                            time += 10
                        }
                        if (time >= timeout) {
                            unstable 'Timeout waiting for status to be OK'
                        } 
                        println "Application was deployed successfully! ${url}"
                    }
                }
            }   
        }
    }
}
