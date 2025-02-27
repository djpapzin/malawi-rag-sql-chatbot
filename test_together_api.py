#!/usr/bin/env python3
import os
import sys
from dotenv import load_dotenv
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

def test_together_api():
    """Test the Together API connection"""
    try:
        # Get API key from environment
        api_key = os.getenv("TOGETHER_API_KEY", "f7119711abb83c4ec5e9b2339eb06c66c87d4958f4ce6cc348ed3ad0c6cb7101")
        model = os.getenv("LLM_MODEL", "meta-llama/Meta-Llama-3-8B-Instruct-Turbo")
        
        # Import together
        try:
            import together
            logger.info("Successfully imported together module")
        except ImportError:
            logger.error("Failed to import together module. Is it installed?")
            return False
        
        # Set API key
        together.api_key = api_key
        logger.info(f"Set API key: {api_key[:5]}...{api_key[-5:]}")
        
        # Test listing models
        try:
            models = together.Models.list()
            logger.info(f"Successfully listed {len(models)} models")
            
            # Check if our model is available
            model_names = [m['name'] for m in models]
            
            # Check for exact match
            if model in model_names:
                logger.info(f"✅ Model {model} is available")
            else:
                logger.warning(f"❌ Model {model} not found in available models")
                
                # Check for similar models
                similar_models = [m for m in model_names if "llama" in m.lower() and "instruct" in m.lower()]
                if similar_models:
                    logger.info(f"Similar available models: {', '.join(similar_models)}")
                    
                    # Find best alternative
                    if any("meta-llama/Meta-Llama-3" in m for m in similar_models):
                        best_alternative = next((m for m in similar_models if "meta-llama/Meta-Llama-3" in m), similar_models[0])
                        logger.info(f"Recommended alternative: {best_alternative}")
                else:
                    logger.info(f"Available models: {', '.join(model_names[:5])}...")
                
            # Print all available Llama models
            llama_models = [m for m in model_names if "llama" in m.lower()]
            logger.info(f"All available Llama models: {', '.join(llama_models)}")
                
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return False
        
        # Test simple completion with the actual model
        try:
            prompt = "Generate a simple SQL query to count all projects in a database."
            logger.info(f"Testing completion with prompt: {prompt}")
            
            # Use the model that's actually available
            test_model = model if model in model_names else "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K"
            logger.info(f"Using model for test: {test_model}")
            
            response = together.Complete.create(
                prompt=prompt,
                model=test_model,
                temperature=0.1,
                max_tokens=100
            )
            
            # Extract the raw text from the response
            raw_text = response['output']['choices'][0]['text']
            logger.info(f"Received response: {raw_text[:100]}...")
            
            # Test SQL generation specifically
            sql_prompt = """You are a SQL expert. Generate a SQL query to answer the following question:

Question: What is the total budget for infrastructure projects?

Use this database schema:
Table: proj_dashboard
Columns: 
- projectname (TEXT)
- district (TEXT)
- projectsector (TEXT)
- projectstatus (TEXT)
- budget (NUMERIC)
- completionpercentage (NUMERIC)
- startdate (NUMERIC)
- completiondata (NUMERIC)

Return ONLY the SQL query, nothing else.
"""
            logger.info(f"Testing SQL generation...")
            
            sql_response = together.Complete.create(
                prompt=sql_prompt,
                model=test_model,
                temperature=0.1,
                max_tokens=200
            )
            
            # Extract the SQL query
            sql_text = sql_response['output']['choices'][0]['text']
            logger.info(f"Generated SQL: {sql_text}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error testing completion: {str(e)}")
            return False
            
    except Exception as e:
        logger.error(f"Error testing Together API: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_together_api()
    if success:
        logger.info("✅ Together API test successful")
        sys.exit(0)
    else:
        logger.error("❌ Together API test failed")
        sys.exit(1)
