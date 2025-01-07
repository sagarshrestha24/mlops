from gliner import GLiNER
from collections import defaultdict

class ModelPipeline:
    def __init__(self, model_path: str):
        """Initialize the pipeline by loading the model."""
        self.model = GLiNER.from_pretrained(model_path)

    def predict(self, text: str, labels: list) -> dict:
        """
        Make predictions using the loaded model.
        
        Args:
            text (str): The input text.
            labels (list): The list of labels to predict entities for.
        
        Returns:
            dict: A dictionary of predictions grouped by label.
        """
        # Predict entities
        entities = self.model.predict_entities(text, labels)

        # Organize predictions by label
        answer = defaultdict(list)
        for entity in entities:
            answer[entity["label"]].append(entity["text"])
        
        return dict(answer)

