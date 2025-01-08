# GLiNER Zero-shot NER Model Deployment Pipeline

## Overview

This project provides an MLOps pipeline to deploy the zero-shot Named Entity Recognition (NER) model GLiNER, which uses a bidirectional transformer encoder (BERT-like architecture). The GLiNER model identifies entities of any type, providing a flexible alternative to traditional NER models limited to predefined entities.

The pipeline includes a Flask-based web application to serve the model, with monitoring integrated via Prometheus. This document explains the components and steps to deploy and run the application.

## Model URL

Model used: **urchade/gliner_medium-v2.1**

## Directory Structure

project/
├── app.py
├── model_pipeline.py
├── templates/
│   └── index.html
├── requirements.txt
└── README.md

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


