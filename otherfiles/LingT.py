import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.environ["HF_TOKEN"],
)

completion = client.chat.completions.create(
    model="inclusionAI/Ling-1T:featherless-ai",
    messages=[
        {
            "role": "user",
            "content": "write a rust code to convert numbers into english words"
        }
    ],
)

# Structured output formatting
print("=" * 80)
print("LING-1T RESPONSE")
print("=" * 80)
print()

# Extract the response message
message = completion.choices[0].message

# Print formatted response
print(f"Role: {message.role}")
print(f"\nContent:\n{'-' * 80}")
print(message.content)
print(f"{'-' * 80}")

# Print additional metadata if available
print(f"\nMetadata:")
print(f"  - Model: inclusionAI/Ling-1T")
print(f"  - Finish Reason: {completion.choices[0].finish_reason}")
if hasattr(completion, 'usage'):
    print(f"  - Tokens Used: {completion.usage.total_tokens if completion.usage else 'N/A'}")
    if completion.usage:
        print(f"    - Prompt Tokens: {completion.usage.prompt_tokens}")
        print(f"    - Completion Tokens: {completion.usage.completion_tokens}")

print("\n" + "=" * 80)

# Optional: Save to file in formatted plain text
with open("ling_output.txt", "w") as f:
    f.write("=" * 80 + "\n")
    f.write("LING-1T RESPONSE\n")
    f.write("=" * 80 + "\n\n")
    f.write(f"Role: {message.role}\n")
    f.write(f"\nContent:\n")
    f.write("-" * 80 + "\n")
    f.write(message.content + "\n")
    f.write("-" * 80 + "\n")
    f.write(f"\nMetadata:\n")
    f.write(f"  - Model: inclusionAI/Ling-1T\n")
    f.write(f"  - Finish Reason: {completion.choices[0].finish_reason}\n")
    if hasattr(completion, 'usage') and completion.usage:
        f.write(f"  - Tokens Used: {completion.usage.total_tokens}\n")
        f.write(f"    - Prompt Tokens: {completion.usage.prompt_tokens}\n")
        f.write(f"    - Completion Tokens: {completion.usage.completion_tokens}\n")
    f.write("\n" + "=" * 80 + "\n")

print("Response also saved to: ling_output.txt")