# ============================================================================
# Complete LlamaIndex Multi-Document Annual Report Query System
# ============================================================================

# Install required packages first:
# pip install llama-index llama-index-llms-openai llama-index-embeddings-openai
# pip install pypdf  # for PDF parsing
# pip install python-dotenv  # for loading environment variables

import os
import time
from dotenv import load_dotenv
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, Settings
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.core.tools import QueryEngineTool, ToolMetadata
from llama_index.core.query_engine import SubQuestionQueryEngine
from llama_index.llms.openai import OpenAI
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core.prompts import PromptTemplate

# ============================================================================
# STEP 1: Configuration and Setup
# ============================================================================

# Load environment variables from .env file
load_dotenv()

# Configure the LLM with better accuracy settings
# Using gpt-4-turbo-preview for larger context window (128k tokens)
Settings.llm = OpenAI(
    model="gpt-4-turbo-preview",  # 128k context vs 8k for gpt-4
    temperature=0,  # Deterministic responses
    max_retries=5,  # Retry on rate limit errors with exponential backoff
    timeout=120.0,  # Longer timeout for complex queries
    additional_kwargs={"max_tokens": 1500}  # Balanced response length
)

# Use the LARGE embedding model for better accuracy
# text-embedding-3-large has 3072 dimensions vs 1536 for small
# This significantly improves retrieval accuracy for complex documents
Settings.embed_model = OpenAIEmbedding(
    model="text-embedding-3-large",  # Best accuracy (3072 dimensions)
    embed_batch_size=10  # Process in smaller batches to avoid rate limits
)

# Configure chunk settings for better context preservation
# Balanced chunk size to fit within context window while preserving meaning
Settings.node_parser = SimpleNodeParser.from_defaults(
    chunk_size=800,  # Balanced size for financial data
    chunk_overlap=150,  # Overlap to preserve context across chunks
)

# ============================================================================
# STEP 2: Load Annual Reports
# ============================================================================

print("Loading annual reports...")

# Load your 4 annual reports
infosys_docs = SimpleDirectoryReader(
    input_files=["infosysar25.pdf"]
).load_data()

company2_docs = SimpleDirectoryReader(
    input_files=["tcs2024.pdf"]  # Example: TCS
).load_data()

company3_docs = SimpleDirectoryReader(
    input_files=["MSFT_Report.pdf"]  # Example: MSFT
).load_data()

company4_docs = SimpleDirectoryReader(
    input_files=["hcl2024.pdf"]  # Example: HCL
).load_data()

print(f"✓ Loaded {len(infosys_docs)} pages from Infosys")
print(f"✓ Loaded {len(company2_docs)} pages from TCS")
print(f"✓ Loaded {len(company3_docs)} pages from MSFT")
print(f"✓ Loaded {len(company4_docs)} pages from HCL")

# ============================================================================
# STEP 3: Create Vector Store Indexes
# ============================================================================

print("\nCreating vector indexes (this may take a few minutes)...")

# Create indexes for each company
infosys_index = VectorStoreIndex.from_documents(
    infosys_docs,
    show_progress=True
)

company2_index = VectorStoreIndex.from_documents(
    company2_docs,
    show_progress=True
)

company3_index = VectorStoreIndex.from_documents(
    company3_docs,
    show_progress=True
)

company4_index = VectorStoreIndex.from_documents(
    company4_docs,
    show_progress=True
)

print("✓ All indexes created successfully")

# ============================================================================
# STEP 4: Create Query Engines with Detailed Metadata
# ============================================================================

print("\nSetting up query engines...")

# Custom prompt to improve accuracy and reduce hallucinations
qa_prompt_template = PromptTemplate(
    "Context information from the annual report is below.\n"
    "---------------------\n"
    "{context_str}\n"
    "---------------------\n"
    "Given the context information and not prior knowledge, "
    "answer the query. If the information is not in the context, "
    "clearly state 'This information is not available in the annual report' "
    "rather than making up an answer. Always cite specific numbers and facts "
    "from the context when available.\n"
    "Query: {query_str}\n"
    "Answer: "
)

# Improved query engine configuration for better accuracy
query_engine_tools = [
    QueryEngineTool(
        query_engine=infosys_index.as_query_engine(
            similarity_top_k=6,  # Balanced: enough context without exceeding limits
            response_mode="tree_summarize",  # Better for complex queries
            text_qa_template=qa_prompt_template,
            streaming=False
        ),
        metadata=ToolMetadata(
            name='infosys_2024',
            description=(
                'Provides information about Infosys annual report 2024-25 '
                'including financial data (revenue, profit, margins), '
                'executive compensation, business segments, risk factors, '
                'and strategic initiatives.'
            )
        )
    ),
    QueryEngineTool(
        query_engine=company2_index.as_query_engine(
            similarity_top_k=6,
            response_mode="tree_summarize",
            text_qa_template=qa_prompt_template,
            streaming=False
        ),
        metadata=ToolMetadata(
            name='tcs_2024',
            description=(
                'Provides information about TCS annual report 2024 '
                'including financial data (revenue, profit, margins), '
                'executive compensation, business segments, risk factors, '
                'and strategic initiatives.'
            )
        )
    ),
    QueryEngineTool(
        query_engine=company3_index.as_query_engine(
            similarity_top_k=6,
            response_mode="tree_summarize",
            text_qa_template=qa_prompt_template,
            streaming=False
        ),
        metadata=ToolMetadata(
            name='msft_2024',
            description=(
                'Provides information about MSFT annual report 2024 '
                'including financial data (revenue, profit, margins), '
                'executive compensation, business segments, risk factors, '
                'and strategic initiatives.'
            )
        )
    ),
    QueryEngineTool(
        query_engine=company4_index.as_query_engine(
            similarity_top_k=6,
            response_mode="tree_summarize",
            text_qa_template=qa_prompt_template,
            streaming=False
        ),
        metadata=ToolMetadata(
            name='hcl_2024',
            description=(
                'Provides information about HCL annual report 2024 '
                'including financial data (revenue, profit, margins), '
                'executive compensation, business segments, risk factors, '
                'and strategic initiatives.'
            )
        )
    ),
]

# ============================================================================
# STEP 5: Build Multi-Document Query Engine
# ============================================================================

s_engine = SubQuestionQueryEngine.from_defaults(
    query_engine_tools=query_engine_tools,
    verbose=True  # Shows sub-questions being generated
)

print("✓ Multi-document query engine ready!")

# ============================================================================
# STEP 6: Example Queries
# ============================================================================

print("\n" + "="*80)
print("READY TO QUERY! Here are some example queries:")
print("="*80 + "\n")

# Example 1: Compare CEO Compensation
print("\n📊 QUERY 1: CEO Compensation Comparison")
print("-" * 80)
response = s_engine.query(
    "Compare the CEO compensation across all 4 companies in 2024. "
    "Include base salary, bonuses, stock awards, and total compensation. "
    "Which company has the highest CEO compensation?"
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 2: Revenue Comparison
print("\n\n📊 QUERY 2: Revenue Comparison")
print("-" * 80)
response = s_engine.query(
    "What was the total revenue for each of the 4 companies in 2024? "
    "List them in descending order and calculate the percentage "
    "year-over-year growth for each."
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 3: Profit Margins
print("\n\n📊 QUERY 3: Profit Margin Analysis")
print("-" * 80)
response = s_engine.query(
    "Compare the operating profit margins and net profit margins "
    "for all 4 companies. Which company is most profitable?"
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 4: Executive Compensation Summary
print("\n\n📊 QUERY 4: Top 5 Executive Compensation")
print("-" * 80)
response = s_engine.query(
    "For each company, what was the total compensation for the "
    "top 5 highest-paid executives? Provide a summary table."
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 5: Risk Factors
print("\n\n📊 QUERY 5: Key Risk Factors")
print("-" * 80)
response = s_engine.query(
    "Summarize the top 3 risk factors mentioned in each company's "
    "annual report. Are there common risks across all companies?"
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 6: Geographic Revenue Distribution
print("\n\n📊 QUERY 6: Geographic Revenue Breakdown")
print("-" * 80)
response = s_engine.query(
    "What is the geographic revenue distribution (by region/country) "
    "for each of the 4 companies? Which markets contribute most to revenue?"
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 7: R&D Spending
print("\n\n📊 QUERY 7: R&D Investment")
print("-" * 80)
response = s_engine.query(
    "How much did each company spend on Research & Development in 2024? "
    "Express as both absolute amount and percentage of revenue."
)
print(response)
time.sleep(3)  # Wait to avoid rate limits

# Example 8: Employee Metrics
print("\n\n📊 QUERY 8: Employee Statistics")
print("-" * 80)
response = s_engine.query(
    "What is the total employee count for each company? "
    "Calculate the revenue per employee for comparison."
)
print(response)

# ============================================================================
# STEP 7: Interactive Query Loop (Optional)
# ============================================================================

print("\n\n" + "="*80)
print("INTERACTIVE MODE - Ask your own questions!")
print("="*80)
print("Type 'quit' or 'exit' to stop\n")

while True:
    user_query = input("\n💬 Your question: ").strip()
    
    if user_query.lower() in ['quit', 'exit', 'q']:
        print("Goodbye!")
        break
    
    if not user_query:
        continue
    
    print("\n🔍 Analyzing documents...\n")
    try:
        response = s_engine.query(user_query)
        print("\n📝 Answer:")
        print("-" * 80)
        print(response)
    except Exception as e:
        print(f"❌ Error: {str(e)}")

# ============================================================================
# BONUS: Save Indexes for Future Use (Optional)
# ============================================================================

# Uncomment to save indexes to disk for faster loading next time
"""
print("\nSaving indexes to disk...")

infosys_index.storage_context.persist(persist_dir="./storage/infosys")
company2_index.storage_context.persist(persist_dir="./storage/company2")
company3_index.storage_context.persist(persist_dir="./storage/company3")
company4_index.storage_context.persist(persist_dir="./storage/company4")

print("✓ Indexes saved! Next time, load them with:")
print("from llama_index.core import StorageContext, load_index_from_storage")
print("storage_context = StorageContext.from_defaults(persist_dir='./storage/infosys')")
print("infosys_index = load_index_from_storage(storage_context)")
"""