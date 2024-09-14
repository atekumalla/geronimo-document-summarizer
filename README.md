# geronimo-document-summarizer
Geronimo is a Chainlit-based application that serves as a cliff notes style document summrizer that uses LLMs to compress the content of a document

## Features

## Prerequisites

- Python 3.7+
- API keys for OpenAI and/or RunPod (depending on chosen model)

## Installation and Setup

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create a Virtual Environment**:
   ```sh
   python -m venv .venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install Dependencies**:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

1. **API Keys**: 
   - Copy the `.env.sample` file and rename it to `.env`
   - Replace the placeholder values with your actual API keys and Runpod endpoints
   - Note: Runpod keys are optional

2. **Model Selection**:
   - Choose the desired model by setting the `config_key` variable in `app.py`.

3. **System Prompts Context**:
   - Adjust the `ENABLE_SYSTEM_PROMPT`.

4. **Customize Prompts**:
   - Modify the prompt templates in the `prompts.py` file to suit your context.

## Running the Application

1. **Activate the Virtual Environment** (if not already activated):
   ```sh
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

2. **Run the Chainlit App**:
   ```sh
   chainlit run app.py -w
   ```

3. Open your browser and navigate to the URL displayed in the terminal.

## Usage

- Start a conversation with the Geronimo by typing a message and giving it the text of a document to summarize.
- The application will process your input, summarize your document and return a summary.

## Key Components

- `app.py`: Main application file containing the Chainlit setup and message handling logic.
- `prompts.py`: Contains prompt templates for the model instructing it to summarize docuemnts.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request with your proposed changes.

## License

This project is licensed under the MIT License.
