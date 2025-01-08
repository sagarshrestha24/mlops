from flask import Flask, request, jsonify, render_template
from model_pipeline import ModelPipeline
from prometheus_flask_exporter import PrometheusMetrics

# Initialize the Flask app
app = Flask(__name__)

# Load the model at startup
model_pipeline = ModelPipeline("urchade/gliner_medium-v2.1")

# Initialize Prometheus metrics
metrics = PrometheusMetrics(app)

# Define a counter to track prediction errors
PREDICTION_ERROR_COUNT = metrics.counter(
    'prediction_error_count', 'Number of errors during model predictions',
    labels={'endpoint': '/predict'}
)

@app.route('/')
def index():
    """Render the home page with a form for user input."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle predictions from the model."""
    # Track errors during prediction
    try:
        # Get input text and labels from the form
        text = request.form.get('text')
        labels = request.form.get('labels')

        # Validate inputs
        if not text:
            return jsonify({"error": "Text is required"}), 400
        labels = labels.split(',') if labels else []

        # Predict entities
        predictions = model_pipeline.predict(text, labels)

        # Return predictions as JSON
        return jsonify({"data": predictions})

    except Exception as e:
        # Increment the error counter
        PREDICTION_ERROR_COUNT.labels(endpoint='/predict').inc()
        return jsonify({"error": "Prediction failed", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
