from flask import Flask, request, jsonify, render_template
from model_pipeline import ModelPipeline
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST

# Initialize the Flask app
app = Flask(__name__)

# Load the model at startup
model_pipeline = ModelPipeline("urchade/gliner_medium-v2.1")

# Prometheus Metrics
REQUEST_COUNT = Counter(
    'flask_request_count', 
    'Total number of requests', 
    ['method', 'endpoint', 'status_code']
)
REQUEST_LATENCY = Histogram(
    'flask_request_latency_seconds', 
    'Latency of requests in seconds', 
    ['endpoint']
)
PREDICTION_ERROR_COUNT = Counter(
    'flask_prediction_error_count', 
    'Number of errors during model predictions'
)

@app.route('/')
def index():
    """Render the home page with a form for user input."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle predictions from the model."""
    # Start measuring latency
    latency_timer = REQUEST_LATENCY.labels(endpoint='/predict').time()
    try:
        # Get input text and labels from the form
        text = request.form.get('text')
        labels = request.form.get('labels')

        # Validate inputs
        if not text:
            status_code = 400
            REQUEST_COUNT.labels(method='POST', endpoint='/predict', status_code=status_code).inc()
            return jsonify({"error": "Text is required"}), status_code
        labels = labels.split(',') if labels else []

        # Predict entities
        predictions = model_pipeline.predict(text, labels)
        status_code = 200

    except Exception as e:
        # Log prediction errors
        PREDICTION_ERROR_COUNT.inc()
        status_code = 500
        return jsonify({"error": "Prediction failed", "details": str(e)}), status_code

    finally:
        # Record request metrics
        REQUEST_COUNT.labels(method='POST', endpoint='/predict', status_code=status_code).inc()
        latency_timer.observe_duration()

    # Return predictions as JSON
    return jsonify({"data": predictions}), status_code

@app.route('/metrics')
def metrics():
    """Expose Prometheus metrics."""
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

