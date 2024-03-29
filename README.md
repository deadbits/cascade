# endless 🚪🌌
```
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
endless backrooms
˚. ✦.˳·˖✶ ⋆.✧̣̇˚.
```

This project facilitates a conversation between two LLM instances (OpenAI, Anthropic, Ollama).

Start the conversation with a chat history, system prompt, and user prompt.  
The default settings will run a virtual CLI simulation between the two models.

Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for the original code/idea and prompt.  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).


## Installation 🛠️
```
git clone https://github.com/deadbits/endless.git
cd endless
pyenv virtualenv 3.11.7 endless
pyenv activate endless
pip install -r requirements.txt
```

## Usage 🚀
Before running `endless.py`, set your Anthropic and OpenAI API keys using the environment variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`.

```
usage: endless.py [-h] [--ai1 {anthropic,openai,ollama:*}] [--ai2 {anthropic,openai,ollama:*}] [-r ROUNDS] [-s SYSTEM_PROMPT]
                   [-u USER_PROMPT] [-o OUTPUT]

endless backrooms

options:
  -h, --help            show this help message and exit
  --ai1 {anthropic,openai,ollama:*}
                        First LLM
  --ai2 {anthropic,openai,ollama:*}
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

## Examples 🌈

**Start a conversation between two Claude instances with 10 rounds:**  
`python endless.py --rounds 10`

**Use OpenAI for the first LLM and Anthropic for the second, running in supervised mode:**  
`python endless.py --ai1 openai --ai2 anthropic --supervised`

**Provide a user prompt to start the conversation and save the output to a file:**  
`python endless.py --user_prompt "Explore the hidden depths of reality" --output conversation.json`

## Prompts
By default, the conversation starts with an initial chat history between the user and assistant that sets the stage for one LLM to act as a virtual CLI simulation and the other to act as the user of that simulation. 

If you supply a `--user_prompt`, this is added to the initial conversation from the side of the virtual CLI simulation as `f"<OOC> Let's begin! {user_prompt}"`

