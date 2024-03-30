# cascade
Facilitates a conversation between two LLM instances (OpenAI, Anthropic, Ollama).

Start the conversation with a chat history, system prompt, and user prompt.  

Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for the original code/idea and prompt.  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).

To run a variation of the [worldsim prompt](https://twitter.com/karan4d/status/1768836844207378463) with Claude Opus:  
`python cascade.py -r 5 --chat data/prompts/simulation.json --system_propt data/prompts/simulation.txt`

Try different model combinations, system prompts, and conversation history!

## Installation 🛠️
```
git clone https://github.com/deadbits/cascade.git
cd cascade
pyenv virtualenv 3.11.7 cascade
pyenv activate cascade
pip install -r requirements.txt
```

## Usage 🚀
Make sure Ollama is running if you are using it for inference and/or set your API keys using environment variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`

```
python cascade.py --help
usage: cascade.py [-h] [--llm1 LLM1] [--llm2 LLM2] [-r ROUNDS] [-c CHAT] [-s SYSTEM_PROMPT] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  --llm1 LLM1           First LLM (anthropic, openai, ollama:*)
  --llm2 LLM2           Second LLM (anthropic, openai, ollama:*)
  -r ROUNDS, --rounds ROUNDS
                        Number of exchanges between the instances
  -c CHAT, --chat CHAT  Initial chat history
  -s SYSTEM_PROMPT, --system_prompt SYSTEM_PROMPT
                        System prompt
  -o OUTPUT, --output OUTPUT
                        File to save conversation to
```

* `--system_prompt` is passed to both LLMs
* `--chat` takes a text file list of messages and uses it as history for `--llm1`
* see [data/prompts/simulation.json](data/prompts/simulation.json) for an example conversation

## Examples

**Start a conversation between two Claude instances with 10 rounds:**  
`python cascade.py --rounds 10`

**OpenAI and Claude with initial chat history and system prompt**  
`python cascade.py --llm1 openai --llm2 anthropic -c data/prompts/simulation.json -s data/prompts/simulation.txt`

**Claude and Mixtral**  
`python cascade.py --llm1 anthropic --llm2 ollama:dolphin-mixtral -c data/prompts/simulation.json -s data/prompts/simulation.txt`

