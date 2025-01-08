# GLiNER Zero-shot NER Model Deployment Pipeline

## Overview

This project provides an MLOps pipeline to deploy the zero-shot Named Entity Recognition (NER) model GLiNER, which uses a bidirectional transformer encoder (BERT-like architecture). The GLiNER model identifies entities of any type, providing a flexible alternative to traditional NER models limited to predefined entities.

The pipeline includes a Flask-based web application to serve the model, with monitoring integrated via Prometheus. This document explains the components and steps to deploy and run the application.

## Model URL

Model used: **urchade/gliner_medium-v2.1**

## Directory Structure
```
mlops/
├── app.py
├── model_pipeline.py
├── templates/
│   └── index.html
├── requirements.txt
├── Dockerfile
├── charts/
│   └── mlops-chart/
|   ├── grafana/
│   └── prometheus/
|   └── loki-stack/
├── README.md
```

## File Descriptions
**1. app.py**

This is the main application file, which initializes the Flask server and serves the endpoints.

**Key Features:**

**Home Page (/):** Renders a form where users can input text and specify labels for entity extraction.

**Predict Endpoint (/predict):** Accepts POST requests with text and labels, processes the data using the GLiNER model, and returns the identified entities in JSON format.

**Prometheus Integration:** Tracks metrics like the number of prediction errors.

**Code Highlights:**

**Model Initialization:**
```
model_pipeline = ModelPipeline("urchade/gliner_medium-v2.1")
```
The model is loaded at startup for efficiency.

**Prediction Logic:**
```
@app.route('/predict', methods=['POST'])
def predict():
    ...
    predictions = model_pipeline.predict(text, labels)
    ...
```

Handles user input and returns model predictions.

**Monitoring with Prometheus:**

```
metrics = PrometheusMetrics(app)
PREDICTION_ERROR_COUNT = metrics.counter(
    'prediction_error_count', 'Number of errors during model predictions',
    labels={'endpoint': '/predict'}
)
```

**2. model_pipeline.py**

This file defines the ModelPipeline class that abstracts the GLiNER model's functionality.

**Key Features:**

**Model Loading:**

```
self.model = GLiNER.from_pretrained(model_path)
```

Loads the pre-trained GLiNER model.

**Prediction Logic:**

```
def predict(self, text: str, labels: list) -> dict:
    entities = self.model.predict_entities(text, labels)
    ...
```

Processes text input and organizes the predictions by label.

**3. templates/index.html**

This is the front-end template rendered by Flask for the home page.

**Key Features:**

Input Form: Allows users to enter text and specify labels.

Client-side Prediction Display: Uses JavaScript to send data to the /predict endpoint and display the response.

Code Snippet:
```
<form action="/predict" method="post" id="predictionForm">
    <textarea name="text" id="text" required></textarea>
    <input type="text" name="labels" id="labels">
    <button type="submit">Predict</button>
</form>
<script>
    document.getElementById('predictionForm').addEventListener('submit', async function(event) {
        event.preventDefault();
        const formData = new FormData(this);
        const response = await fetch('/predict', {
            method: 'POST',
            body: formData,
        });
        const result = await response.json();
        document.getElementById('output').textContent = JSON.stringify(result, null, 2);
    });
</script>
```

**4. requirements.txt**

Lists all the dependencies required to run the application.

**Dependencies:**

**flask**: Web framework.

**transformers**: For handling transformer-based models.

**gliner**: GLiNER model library.

**torch**: PyTorch backend.

**prometheus_flask_exporter**: Integration for Prometheus monitoring.

**5. Dockerfile**

Defines the containerization process for the application.

Contents:
```
FROM python:3.8-slim

WORKDIR /app
COPY . /app
RUN pip install --upgrade pip
RUN pip install  -r requirements.txt

EXPOSE 5000
CMD ["python", "app.py"]
```

**6. charts/mlops-chart**

Contains the Helm chart for deploying the containerized application to a Kubernetes cluster.

## Setup Instructions

**1. Clone the Repository**

```
git clone <repository-url>
cd <repository-directory>
```

**2. Install Dependencies**

Ensure Python 3.7+ is installed. Run:

```pip install -r requirements.txt```

**3. Run the Application**

Start the Flask server:

```python3 app.py```

The application will be available at http://127.0.0.1:5000.

**4. Access the Web Interface**

Open a browser and navigate to the URL to input text and labels for entity extraction.

**5. Monitor Metrics**

Prometheus metrics can be scraped from the /metrics endpoint for tracking prediction errors and other performance statistics.

**6. Containerization**

Build and run the Docker container for the application.

Build the Docker Image

```docker build -t gliner-ner-app . ```

Run the Docker Container

```docker run -d -p 5000:5000 gliner-ner-app```

The application will now be accessible at http://127.0.0.1:5000.

**7. Model Deployment on Kubernetes**

**Prerequisites:**
A running Kubernetes cluster.

Helm installed on your local machine.

Steps to Deploy:

Navigate to the Helm chart directory:

```cd charts/mlops-chart```

Install the Helm chart:

```helm install gliner-ner ./```

Verify the Deployment:
```
kubectl get pods
kubectl get services
```
To access the application from web browser

```
kubectl port-forward svc/svc-name 5000:5000
```
The application will now be accessible at http://127.0.0.1:5000.

**8. Monitoring & Logging**

Deploy the monitoring and logging stack using the provided Helm chart.

Steps to Deploy:

Navigate to the monitoring  directory:

```cd charts/```

Install the Helm chart:

```
helm install prometheus prometheus
helm install grafana grafana
helm install loki-stack loki-stack
```

**Access Monitoring Tools:**

**Prometheus**: To scrape and visualize metrics.

**Grafana**: For customizable dashboards and data visualization.

**Dashboard:**
![image](https://github.com/user-attachments/assets/b20a09c9-9622-4938-85cd-effa5549a4f4)

**Loki**: For centralized logging.

Verfifying the logs of gliner from grafana loki
![image](https://github.com/user-attachments/assets/59c376a2-0379-43f1-8b5d-afac6cd10fb1)


Verify the Monitoring Deployment:
```
kubectl get pods
kubectl get services
```

Integration with Prometheus

To scrape the metrics, configure Prometheus to monitor your Flask app by adding the following job to prometheus.yml:
```
scrape_configs:
  - job_name: 'flask-app'
    static_configs:
      - targets: ['<FLASK_APP_IP>:5000']
```
Restart Prometheus to apply the configuration.

Access the services using the appropriate IP addresses or port-forwarding.

**Add Data Sources via the Grafana UI**

**For Prometheus:**

    1. Access Grafana: Open your Grafana dashboard in a web browser.

    2. Navigate to Data Sources:
        - Go to the Grafana sidebar.
        - Click on Configuration (gear icon) → Data Sources.

    3. Add a New Data Source:
        - Click on the Add data source button.
        - Select Prometheus from the list of available data source types.

    4. Configure Prometheus Data Source:
        - In the URL field, provide the Prometheus server URL (e.g., http://<prometheus-server-ip>:9090).
        - Configure any additional settings like timeouts, scrape interval, and authentication if necessary.
        - Click Save & Test to verify the connection.

**For Loki:**

    1. Navigate to Data Sources:
        - Follow the same steps as above to access the data sources page.

    2. Add a New Data Source:
        - Click on the Add data source button.
        - Select Loki from the list of available data source types.

    3. Configure Loki Data Source:
        - In the URL field, provide the Loki server URL (e.g., http://<loki-server-ip>:3100).
        - Configure any additional settings like max active streams, or authentication.
        - Click Save & Test to verify the connection.


**9. Continuous Integration (CI) using GitHub Actions**

The CI pipeline you've configured in GitHub Actions automates the process of building and pushing Docker images, as well as updating your Helm chart with the new image tag. Below is a breakdown of each step:

Triggering the workflow:

```
on:
  push:
    branches:
      - main  # Run on pushes to the main branch
  workflow_dispatch:  # Allow manual triggering
```

This specifies that the workflow will trigger whenever a push is made to the main branch or when it is manually triggered (via GitHub UI).

Setting up the environment:

```
jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      # Give the default GITHUB_TOKEN write permission to commit and push the
      # added or changed files to the repository.
      contents: write
```
    This defines a job named build-and-push that will run on an ubuntu-latest runner.

Checkout the repository:

```
- name: Checkout repository
  uses: actions/checkout@v3
```

This step checks out the code from the repository to make it available for subsequent steps.

Login to Docker Registry:

```
- name: Log in to Docker Registry
  uses: docker/login-action@v2
  with:
    username: ${{ secrets.REGISTRY_USERNAME }}
    password: ${{ secrets.REGISTRY_PASSWORD }}
```

This step logs into the Docker registry using the credentials stored in GitHub Secrets (REGISTRY_USERNAME and REGISTRY_PASSWORD).

Build and push the Docker image:

```
- name: Build and Push Docker Image
  run: |
    IMAGE_TAG=$(git rev-parse --short=5 HEAD)
    IMAGE=${{ secrets.REGISTRY_USERNAME }}/${{ secrets.IMAGE_NAME }}:$IMAGE_TAG

    docker build -t $IMAGE .
    docker push $IMAGE

    echo "IMAGE=$IMAGE" >> $GITHUB_ENV
```


Update Helm chart image tag:

```
    - name: Update Helm Chart Image Tag
      run: |
        CHART_PATH="path/to/helm/chart/values.yaml"
        sed -i "s|tag:.*|tag: $IMAGE_TAG|" $CHART_PATH
         git remote set-url origin https://x-access-token:${{ secrets.GH_TOKEN }}@github.com/${{ github.repository }}.git
        git config user.name "GitHub Actions"
        git config user.email "actions@github.com"
        git add $CHART_PATH
        git commit -m "Update Helm chart image tag to $IMAGE"
        git push origin main
```

This step updates the values.yaml file of the Helm chart with the new image tag. It uses sed to replace the old image tag with the new one ($IMAGE).The change is then committed and pushed back to the main branch.

**10. Continuous Deployment (CD) using ArgoCD**

ArgoCD is a declarative, GitOps continuous delivery tool for Kubernetes. The idea behind GitOps is that the desired state of the infrastructure is stored in Git, and ArgoCD ensures that the live environment is aligned with this state.

**ArgoCD Configuration:**      

ArgoCD works by connecting to a Kubernetes cluster and monitoring a Git repository for changes. When a change (e.g., a Helm chart update or a manifest file) is detected in the repository, it automatically triggers the deployment of the application.


**Steps to Install ArgoCD via Helm:**

**Add the ArgoCD Helm Chart Repository:** First, add the ArgoCD Helm chart repository to your Helm configuration.

```
helm repo add argo https://argoproj.github.io/argo-helm
helm repo update
```
**Create a Namespace for ArgoCD (optional but recommended):** It's a good practice to install ArgoCD in its own namespace. You can create a namespace called argocd:

``` kubectl create namespace argocd ```

**Install ArgoCD using Helm:** Now, you can install ArgoCD into the Kubernetes cluster using the Helm chart.

``` helm install argocd argo/argo-cd --namespace argocd ```

This command will install ArgoCD in the argocd namespace. It will use the latest stable version of the chart.


**Creating an Application file for ArgoCD:**

ArgoCD uses an application file to describe the desired state of the application, including its source (Git repository), target cluster, and path to the Helm charts or manifests.
An example of an application file:
```
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: mlops
  namespace: argocd
spec:
  destination:
    name: ''
    namespace: default
    server: 'https://kubernetes.default.svc'
  source:
    path: charts/mlops-chart
    repoURL: 'https://github.com/sagarshrestha24/mlops.git'
    targetRevision: HEAD
  sources: []
  project: default
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
      - CreateNamespace=true
      - ServerSideApply=true
```


Apply the application file 

``` kubectl apply -f mlops-app.yaml ```

**Argocd Dashboard** 
![image](https://github.com/user-attachments/assets/3e5f4d5b-0bad-4c03-aa0d-99f08ed38fd4)

**11. Alerting**

Here is the alerting rules

```
  alerting_rules.yml: 
    groups:
    - name: Alerts
      rules:
        - alert: KubernetesPodCrashLooping
          expr: increase(kube_pod_container_status_restarts_total[5m]) > 3
          for: 2m
          labels:
            severity: warning
          annotations:
             summary: Kubernetes pod crash looping (instance {{ $labels.instance }})
             description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
        - alert: ModelDown
          expr: up{job="flask-app"} == 0
          for: 5m
          labels:
            severity: critical
          annotations:
            description: '{{ $labels.instance }} of job {{ $labels.job }} has been down for more than 5 minutes.'
            summary: 'Model {{ $labels.instance }} down'
```

This alert detects pods in a Kubernetes cluster that are repeatedly crashing and restarting within a short timeframe. Such behavior is often referred to as a "CrashLoopBackOff."
Rule Breakdown:

```
- alert: KubernetesPodCrashLooping
  expr: increase(kube_pod_container_status_restarts_total[5m]) > 3
  for: 2m
  labels:
    severity: warning
  annotations:
     summary: Kubernetes pod crash looping (instance {{ $labels.instance }})
     description: "Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}"
```
Alert Name: **KubernetesPodCrashLooping**

This is the unique identifier for the alert, used in notifications and dashboards.

**Expression:**
```
increase(kube_pod_container_status_restarts_total[5m]) > 3 
```
- kube_pod_container_status_restarts_total: A metric that counts the number of times a container has restarted.
- increase(...[5m]): Measures how much this metric has increased over the past 5 minutes.
- (> 3): The alert triggers if the restart count increases by more than 3 within 5 minutes.

**For Clause:**

```for: 2m```

The condition must persist for 2 minutes before the alert is triggered. This prevents alerts from firing due to transient issues.

**Labels:**

```
labels:
  severity: warning
```
The alert is labeled with a severity level of warning, indicating that it requires attention but is not critical.

Annotations:

**Summary:**

```
Kubernetes pod crash looping (instance {{ $labels.instance }})
```

A short description of the issue, including the affected instance.

**Description:**

```
Pod {{ $labels.namespace }}/{{ $labels.pod }} is crash looping\n  VALUE = {{ $value }}\n  LABELS = {{ $labels }}
```

A detailed message with:

- Namespace and pod information ({{ $labels.namespace }}/{{ $labels.pod }}).
- The value of the metric when the alert was triggered ({{ $value }}).
- The labels associated with the metric ({{ $labels }}).
