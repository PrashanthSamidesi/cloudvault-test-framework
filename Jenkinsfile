pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Cloning CloudVault repository...'
                checkout scm
            }
        }

        stage('Set Up Python') {
            steps {
                echo 'Checking Python version...'
                bat 'python --version'
                bat 'python -m pip install --upgrade pip'
            }
        }

        stage('Install Dependencies') {
            steps {
                echo 'Installing required packages...'
                bat 'pip install -r requirements.txt'
            }
        }

        stage('Create Runtime Directories') {
            steps {
                echo 'Creating logs and reports folders...'
                bat 'if not exist logs mkdir logs'
                bat 'if not exist reports mkdir reports'
            }
        }

        stage('Lint Check') {
            steps {
                echo 'Running flake8 code quality check...'
                bat 'flake8 services/ utils/ tests/ --max-line-length=100 --extend-ignore=E501,W503'
            }
        }

        stage('Upload Tests') {
            steps {
                echo 'Running Upload Tests...'
                bat 'pytest tests/test_file_upload.py -v --tb=short'
            }
        }

        stage('Sync Tests') {
            steps {
                echo 'Running Sync Tests...'
                bat 'pytest tests/test_file_sync.py -v --tb=short'
            }
        }

        stage('Integration Tests') {
            steps {
                echo 'Running Integration Tests...'
                bat 'pytest tests/test_integration.py -v --tb=short'
            }
        }

        stage('Regression Tests') {
            steps {
                echo 'Running Regression Tests...'
                bat 'pytest tests/test_regression.py -v --tb=short'
            }
        }

        stage('Full Test Suite') {
            steps {
                echo 'Running Full CloudVault Test Suite...'
                bat 'pytest tests/ -v --tb=short --html=reports/test_report.html --self-contained-html'
            }
        }
    }

    post {
        always {
            echo 'Archiving test report and logs...'
            archiveArtifacts artifacts: 'reports/test_report.html', allowEmptyArchive: true
            archiveArtifacts artifacts: 'logs/**/*', allowEmptyArchive: true
        }
        success {
            echo '✅ All stages passed! CloudVault pipeline successful.'
        }
        failure {
            echo '❌ Pipeline failed. Check console output for details.'
        }
    }
}