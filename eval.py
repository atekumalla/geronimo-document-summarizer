from langsmith.evaluation import evaluate, LangChainStringEvaluator
from langsmith.schemas import Run, Example
from openai import OpenAI
import json

from dotenv import load_dotenv
load_dotenv()

from langsmith.wrappers import wrap_openai
from langsmith import traceable

client = wrap_openai(OpenAI())

# This script is used to evaluate a model's ability to generate a summary of a document and to ensure that the summary does not exceed 50% of the size of the original document.

@traceable
def summary_content_evaluator(run: Run, example: Example) -> dict:
    inputs = example.inputs['input']
    outputs = example.outputs['output']

    # Extract system prompt
    system_prompt = next((msg['data']['content'] for msg in inputs if msg['type'] == 'system'), "")

    # Extract message history
    message_history = []
    for msg in inputs:
        if msg['type'] in ['human', 'ai']:
            message_history.append({
                "role": "user" if msg['type'] == 'human' else "assistant",
                "content": msg['data']['content']
            })

    # Extract latest user message and model output
    latest_message = message_history[-1]['content'] if message_history else ""
    model_output = outputs['data']['content']

    evaluation_prompt = f"""
    System Prompt: {system_prompt}

    Message History:
    {json.dumps(message_history, indent=2)}

    Latest User Message: {latest_message}

    Model Output: {model_output}

    Based on the above information, evaluate the model's ability to summarize a document that was provided to it as an input.
    The summary should be in simple wording and should be of a level that a middle school student will be able to follow.
    The summary should be concise and should capture the main ideas of the document.
    The summary should be accurate and true to the source material.
    The summary should be comprehensive and should capture all the important details of the document.
    The summary should be well-structured and should be easy to understand.
    The model should not use the same words and phrases repeatedly.
    The model should not start multiple paragraphs with the same words.
    The model should do only document summaries and should refuse to do other tasks.
    If the input is not a document, the model should indicate that it is not a document and should not summarize it.
    If the input is in a different language, the model should translate the document to English and then summarize it ensuring that the summary adheres to all the rules and guidelines already mentioned.
    Also provide a brief explanation for your score.
    
    Here is the scale you should use to build your answer:
    1: The model's summary is terrible: the summary is incorrect and has information that is not present in the original document.
    4: The model's summary  is mostly not helpful: the summary does not capture the main ideas of the document and does not provide any important details or does not adhere to the rules and guidelines mentioned.
    8: The model's summary  is mostly helpful: the summary captures the main ideas of the document and provides some important details but is not comprehensive and misses out some details.
    10: The model's summary  is excellent: the summary captures the main ideas of the document and provides all the important details while being concise and accurate.


    Respond in the following JSON format:
    {{
        "score": <int>,
        "explanation": "<string>"
    }}
    """

    response = client.chat.completions.create(
        # Using gpt-4o-mini since we are hitting rate limits with gpt-4o
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are an AI assistant tasked with evaluating the outputs of a model that summarizes documents."},
            {"role": "user", "content": evaluation_prompt}
        ],
        temperature=0.2
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return {
            "key": "summary_content_evaluator",
            "score": result["score"] / 10,  # Normalize to 0-1 range
            "reason": result["explanation"]
        }
    except json.JSONDecodeError:
        return {
            "key": "summary_content_evaluator",
            "score": 0,
            "reason": "Failed to parse evaluator response"
        }


@traceable
def summary_size_evaluator(run: Run, example: Example) -> dict:
    inputs = example.inputs['input']
    outputs = example.outputs['output']

    # Extract system prompt
    system_prompt = next((msg['data']['content'] for msg in inputs if msg['type'] == 'system'), "")

    # Extract message history
    message_history = []
    for msg in inputs:
        if msg['type'] in ['human', 'ai']:
            message_history.append({
                "role": "user" if msg['type'] == 'human' else "assistant",
                "content": msg['data']['content']
            })

    # Extract latest user message and model output
    latest_message = message_history[-1]['content'] if message_history else ""
    model_output = outputs['data']['content']

    evaluation_prompt = f"""
    System Prompt: {system_prompt}

    Message History:
    {json.dumps(message_history, indent=2)}

    Latest User Message: {latest_message}

    Model Output: {model_output}

    Based on the above information, evaluate the model's ability to summarize a document that was provided to it as an input.
    The summary should be concise and should capture the main ideas of the document.
    The summary should be accurate and true to the source material.
    The summary should not be more than 50% of the size of the original document.
    If the input is not a document, the model should indicate that it is not a document and should not summarize it.
    If the input is in a different language, the model should translate the document to English and then summarize it ensuring that the summary adheres to all the rules and guidelines already mentioned.
    Also provide a brief explanation for your score.
    
    Here is the scale you should use to build your answer:
    1: The model's summary is terrible: the summary is empty or has garbage information.
    4: The model's summary is mostly not helpful: the summary is not concise and its size is more than 50% of the original document.
    8: The model's summary is mostly helpful: the summary's size is less than 50% of the original document but it misses out on some important details.
    10: The model's summary is excellent: the summary captures the main ideas of the document and provides all the important details while being concise and accurate and its size is less than 50% of the original document.


    Respond in the following JSON format:
    {{
        "score": <int>,
        "explanation": "<string>"
    }}
    """

    response = client.chat.completions.create(
        # Using gpt-4o-mini since we are hitting rate limits with gpt-4o
        model="gpt-4o-mini", 
        messages=[
            {"role": "system", "content": "You are an AI assistant tasked with evaluating the outputs of a model that summarizes documents."},
            {"role": "user", "content": evaluation_prompt}
        ],
        temperature=0.2
    )

    try:
        result = json.loads(response.choices[0].message.content)
        return {
            "key": "summary_size_evaluator",
            "score": result["score"] / 10,  # Normalize to 0-1 range
            "reason": result["explanation"]
        }
    except json.JSONDecodeError:
        return {
            "key": "summary_size_evaluator",
            "score": 0,
            "reason": "Failed to parse evaluator response"
        }


# The name or UUID of the LangSmith dataset to evaluate on.
data = "geronimo-training"

# A string to prefix the experiment name with.
experiment_prefix = "Geronimo Document Summarization Tool Evaluation"

# List of evaluators to score the outputs of target task
evaluators = [
    summary_content_evaluator,
    summary_size_evaluator
]

# Evaluate the target task
results = evaluate(
    lambda inputs: inputs,
    data=data,
    evaluators=evaluators,
    experiment_prefix=experiment_prefix,
)

print(results)
