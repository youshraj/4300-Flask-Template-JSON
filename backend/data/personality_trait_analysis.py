import openai

openai.api_key = 'your_api_key_here'

response = openai.Completion.create(
  engine="text-davinci-003",  # or "text-davinci-004" for GPT-4 if available
  prompt="your_prompt_here",
  temperature=0.7,
  max_tokens=500,
  top_p=1.0,
  frequency_penalty=0.0,
  presence_penalty=0.0
)

print(response.choices[0].text.strip())