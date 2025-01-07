from flask import Flask, request, jsonify, render_template
from model_pipeline import ModelPipeline

# Initialize the Flask app
app = Flask(__name__)

# Load the model at startup
model_pipeline = ModelPipeline("urchade/gliner_medium-v2.1")

@app.route('/')
def index():
    """Render the home page with a form for user input."""
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    """Handle predictions from the model."""
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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

