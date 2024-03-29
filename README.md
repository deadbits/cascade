# cascade 🚪🌌
Facilitates a conversation between two LLM instances
Supports OpenAI, Anthropic, and Ollama

Start the conversation with a chat history, system prompt, and/or user prompt.  

Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for the original code/idea and prompt.  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).

## Installation 🛠️
```
git clone https://github.com/deadbits/cascade.git
cd cascade
pyenv virtualenv 3.11.7 cascade
pyenv activate cascade
pip install -r requirements.txt
```

## Usage 🚀
Before running `cascade.py`, set your Anthropic and OpenAI API keys using the environment variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.

```
usage: cascade.py [-h] [--llm1 {anthropic,openai,mixtral}] [--llm2 {anthropic,openai,mixtral}] [-r ROUNDS] [-s SYSTEM_PROMPT] [-u USER_PROMPT] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  --llm1 {anthropic,openai,mixtral}
                        First LLM
  --llm2 {anthropic,openai,mixtral}
                        Second LLM
  -r ROUNDS, --rounds ROUNDS
                        Number of exchanges between the instances
  -s SYSTEM_PROMPT, --system_prompt SYSTEM_PROMPT
                        System prompt
  -u USER_PROMPT, --user_prompt USER_PROMPT
                        User prompt
  -o OUTPUT, --output OUTPUT
                        File to save conversation to
```
