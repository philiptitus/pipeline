# CI/CD Dashboard

This project is a CI/CD Dashboard that triggers builds, performs tests, deploys artifacts, and displays the progress and results in real-time. It is designed to work with Django projects.

## Features

- Clone repository
- Checkout specific branch
- Install dependencies
- Build project
- Run tests
- Build distribution artifact
- Deploy artifact
- Display real-time updates and logs

## How to Use

### Prerequisites

- Python 3.x
- RabbitMQ

### Setup

1. **Clone the Repository**

    ```bash
    git clone <your-repo-url>
    cd <your-repo-name>
    ```

2. **Install Python Dependencies**

    ```bash
    pip install -r requirements.txt
    pip install wheel
    ```

3. **Start RabbitMQ**

    Ensure RabbitMQ is running on your local machine. If not installed, you can download it from [RabbitMQ website](https://www.rabbitmq.com/download.html).

4. **Run the CI/CD Server**

    ```bash
    python cicd_dashboard.py
    ```

5. **Start Live Server for Frontend**

    Navigate to the directory containing your HTML file and start a live server there. You can use VS Code's Live Server extension or any other tool that can serve static HTML files.

6. **Access the Dashboard**

    Open your browser and go to `http://localhost:5500` (or the appropriate port where your live server is running) to access the CI/CD Dashboard.

### Trigger a Build

1. Enter your GitHub repository URL and the branch you want to build.
2. Click on "Trigger Build" to start the process.
3. The progress and logs will be displayed in real-time on the dashboard.

### Deployment Server

Ensure to provide your own deployment server URL in the `deploy_artifact` function within the `cicd_dashboard.py` file. Replace the placeholder URL with your actual deployment server endpoint:

```python
def deploy_artifact(artifact_path):
    url = "http://your-deployment-server-url/upload"
    ...
Project Setup
This CI/CD process is designed to work with Django projects. Your project should be set up exactly like this repository: feedback.

setup.py
Ensure your setup.py looks like this:

python
Copy code
from setuptools import setup, find_packages

# Read the requirements file to install dependencies
with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
    name='myproject',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=requirements,
    setup_requires=['wheel'],  # Ensures wheel is available during setup
    entry_points={
        'console_scripts': [
            'manage.py = manage:main',  # Assumes manage.py has a main function
        ],
    },
)
requirements.txt
Ensure all your dependencies are listed in the requirements.txt file.

Tests
Create tests for your Django apps. Ensure your tests are in the appropriate directories and are discoverable by the unittest framework. Refer to the feedback repository for examples of how tests should be structured