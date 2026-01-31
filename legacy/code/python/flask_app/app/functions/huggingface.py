from transformers import pipeline

def toxicity_classification(sentences):
    # Load the pre-trained toxicity classification model
    """
    Perform toxicity classification on a list of sentences.

    Parameters
    ----------
    sentences : list
        List containing sentences to classify

    Returns
    -------
    score : float
        The probability score of toxic classification
    """
    
    # Load the pre-trained toxicity classification model
    toxicity_classifier = pipeline("text-classification",
                                   model="unitary/toxic-bert")

    # Perform toxicity classification
    results = toxicity_classifier(sentences)
    score = results[0]['score']

    return round(score, 3)

if __name__ == "__main__":
    inputs = ["I love my dog", "I hate my cat", "This is a fucking toxic shit"]
    toxicity = toxicity_classification(inputs)
    print(toxicity)
