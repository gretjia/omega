#!/usr/bin/env python3
"""
OMEGA v5.2 Weight Extractor (The QMT Bridge)
--------------------------------------------
Extracts raw coefficients from a trained Scikit-learn SGDClassifier model (.pkl)
and serializes them into a lightweight JSON file for the QMT production environment.

Usage:
    python tools/extract_weights_json.py --input models/omega_v5_model_final.pkl --output config/weights.json
"""

import argparse
import json
import pickle
import sys
import numpy as np
from pathlib import Path

def load_model(file_path):
    """Loads a pickle file."""
    try:
        with open(file_path, 'rb') as f:
            return pickle.load(f)
    except Exception as e:
        print(f"Error loading model: {e}")
        sys.exit(1)

def extract_weights(model, output_path):
    """
    Extracts weights from SGDClassifier and StandardScaler.
    Assumes model is a pipeline or a tuple/dict, but based on the prompt 
    it might be just the classifier or a pipeline.
    
    The script tries to intelligently find the classifier and scaler.
    """
    
    classifier = None
    scaler = None
    
    # Heuristic to find components if it's a pipeline or direct object
    if hasattr(model, 'coef_'):
        classifier = model
    elif hasattr(model, 'steps'): # Sklearn Pipeline
        for name, step in model.steps:
            if hasattr(step, 'coef_'):
                classifier = step
            if hasattr(step, 'mean_') and hasattr(step, 'scale_'):
                scaler = step
    elif isinstance(model, dict):
        classifier = model.get('classifier') or model.get('model')
        scaler = model.get('scaler')
    
    if classifier is None:
        print("Error: Could not find a valid linear classifier (SGDClassifier/LogisticRegression) in the pickle.")
        sys.exit(1)
        
    print(f"[*] Found Classifier: {type(classifier).__name__}")
    if scaler:
        print(f"[*] Found Scaler:     {type(scaler).__name__}")
    else:
        print("[!] Warning: No StandardScaler found. Raw features will be used.")

    # Extract coefficients
    # coef_ is usually shape (1, n_features) for binary classification
    weights = {
        "meta": {
            "model_type": type(classifier).__name__,
            "classes": classifier.classes_.tolist() if hasattr(classifier, 'classes_') else []
        },
        "classifier": {
            "coef": classifier.coef_.flatten().tolist(),
            "intercept": classifier.intercept_.tolist() if hasattr(classifier, 'intercept_') else [0.0]
        }
    }
    
    if scaler:
        weights["scaler"] = {
            "mean": scaler.mean_.tolist(),
            "scale": scaler.scale_.tolist()
        }

    # Save to JSON
    try:
        with open(output_path, 'w') as f:
            json.dump(weights, f, indent=4)
        print(f"\n[+] Successfully extracted weights to: {output_path}")
        print(f"    Feature count: {len(weights['classifier']['coef'])}")
    except Exception as e:
        print(f"Error saving JSON: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="OMEGA v5.2 Weight Extractor")
    parser.add_argument("--input", required=True, help="Path to the .pkl model file")
    parser.add_argument("--output", required=True, help="Path to save the JSON weights")

    args = parser.parse_args()

    model = load_model(args.input)
    extract_weights(model, args.output)
