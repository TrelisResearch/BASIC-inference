from dotenv import load_dotenv
from braintrust import Eval, Dataset, init_logger
from pipeline import TouchRugbyAssistant
from config import EVAL_CONFIG
import os
from datetime import datetime
 
import braintrust
from autoevals import ClosedQA, Factuality

# Load environment variables first
load_dotenv()

# Initialize Braintrust logger with project
init_logger(
    api_key=os.getenv('BRAINTRUST_API_KEY'),
    project="touch-rugby-bot"
)

def run_evaluation():
    def task(input_data, _):
        """Task function that processes a single test case."""
        # Create a fresh assistant instance for each test case
        assistant = TouchRugbyAssistant()
        
        # Get response from assistant
        response = assistant.get_response(input_data)
        return response

    dataset = braintrust.init_dataset(project=EVAL_CONFIG["project"], name=EVAL_CONFIG["dataset"])
    
    # Run the evaluation using the pre-defined scorer
    Eval(
        name=EVAL_CONFIG["project"],
        data=dataset,
        task=task,
        scores=[Factuality]
    )

if __name__ == "__main__":
    run_evaluation() 