import os
from dotenv import load_dotenv
from langchain.memory import ConversationBufferMemory
from langchain_community.chains.sql_database import SQLDatabaseChain
from langchain_community.utilities import SQLDatabase
from langchain_core.prompts import PromptTemplate
from langchain_together import Together

load_dotenv()

def test_conversation_flow():
    # Initialize the LLM
    llm = Together(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo-128K",
        together_api_key=os.getenv("TOGETHER_API_KEY"),
        temperature=0.7,
        max_tokens=512
    )
    
    # Connect to the database
    db = SQLDatabase.from_uri("sqlite:///malawi_projects1.db")
    
    # Set up memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",
        return_messages=True
    )

    # Create the SQL prompt template
    sql_prompt = PromptTemplate(
        template="""Given an input question, generate a SQL query to answer the question.
        Use only the following tables and their columns:
        - projects: id, name, location, budget, start_date, end_date
        
        Question: {input}
        
        Chat History: {chat_history}
        """,
        input_variables=["input", "chat_history"]
    )

    # Create the database chain
    db_chain = SQLDatabaseChain.from_llm(
        llm=llm,
        db=db,
        prompt=sql_prompt,
        memory=memory,
        verbose=True,
        return_intermediate_steps=True
    )
    
    # First query
    print("\nExecuting first query...")
    first_result = db_chain("Show me all projects in Lilongwe")
    print("\nFirst Response:", first_result['result'])
    
    # Second query (follow-up)
    print("\nExecuting follow-up query...")
    second_result = db_chain("Which of those projects have budgets over $1M?")
    print("\nSecond Response:", second_result['result'])
    
    # Verify the responses
    assert first_result['result'] != "", "First query should return results"
    assert second_result['result'] != "", "Second query should return results"
    assert "Lilongwe" in first_result['result'].lower(), "First response should mention Lilongwe"
    assert "$1" in second_result['result'], "Second response should mention budget"
    
    # Verify that intermediate steps show SQL was generated
    assert 'intermediate_steps' in first_result, "Should include intermediate steps"
    assert 'intermediate_steps' in second_result, "Should include intermediate steps"
    
    print("\nTest completed successfully!")
    print("\nGenerated SQL queries:")
    print("First query:", first_result['intermediate_steps'])
    print("Second query:", second_result['intermediate_steps'])

if __name__ == "__main__":
    test_conversation_flow() 