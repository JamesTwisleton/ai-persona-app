from transformers import pipeline

def toxicity_classification(sentences):
    # Load the pre-trained toxicity classification model
    """
    Perform toxicity classification on a list of sentences.

    Parameters
    ----------
    sentences : list of str
        The sentences to classify

    Returns
    -------
    toxicity : str
        The toxicity label ("toxic" or "non-toxic")
    score : float
        The confidence score of the toxicity classification
    """
    
    
    toxicity_classifier = pipeline("text-classification", 
                                   model="unitary/toxic-bert")
    

    # Define the cutoff for classifying as toxic (e.g., 0.7)
    toxicity_cutoff = 0.7

    # Perform toxicity classification
    results = toxicity_classifier(sentences)

    # Print the results
    for sentence, result in zip(sentences, results):
        label = result['label']
        score = result['score']

        # Apply the toxicity cutoff
        if score >= toxicity_cutoff:
            toxicity = label
        else:
            toxicity = "non-toxic"

        print(f"Sentence: {sentence}")
        print(f"Toxicity: {toxicity} (Confidence: {score:.4f})\n")

        return toxicity, round(score, 3)

if __name__ == "__main__":
    toxicity_classification()
