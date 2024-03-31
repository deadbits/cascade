# cascade
Facilitates a conversation between two LLMs (OpenAI, Anthropic, Ollama)

Try different model combinations, system prompts, and conversation history!

![example](/data/assets/1.png)

## Installation 🛠️
```
git clone https://github.com/deadbits/cascade.git
cd cascade
pyenv virtualenv 3.11.7 cascade
pyenv activate cascade
pip install -r requirements.txt
```

* Make sure Ollama is running if you're using it for inference
* If using OpenAI/Anthropic, set your API keys with environment variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`

## Usage 🚀

```
usage: cascade.py [-h] [--llm1 LLM1] [--llm2 LLM2] [-s1 SYS_PROMPT1] [-s2 SYS_PROMPT2] [-r ROUNDS] [-c CHAT] [-o OUTPUT]

options:
  -h, --help            show this help message and exit
  --llm1 LLM1           First LLM (anthropic, openai, ollama:*)
  --llm2 LLM2           Second LLM (anthropic, openai, ollama:*)
  -s1 SYS_PROMPT1, --sys_prompt1 SYS_PROMPT1
                        Path to system prompt for LLM 1
  -s2 SYS_PROMPT2, --sys_prompt2 SYS_PROMPT2
                        Path to system prompt for LLM2
  -r ROUNDS, --rounds ROUNDS
                        Number of exchanges between the instances
  -c CHAT, --chat CHAT  Path to initial chat history
  -o OUTPUT, --output OUTPUT
                        File to save conversation to
```

* `--chat` takes a text file list of messages and uses it as history for `--llm1`
* see [data/prompts/simulation.json](data/prompts/simulation.json) for an example conversation


## Examples

**Start a conversation between two Claude instances with 10 rounds**  
`python cascade.py --rounds 10`

**Run a [virtual CLI simulation](https://twitter.com/AndyAyrey/status/1769942282168664104) between Anthropic and OpenAI**  
`python cascade.py --llm1 anthropic --llm2 openai -c data/prompts/simulation.json -s1 data/prompts/simulation.txt -s2 data/prompts/simulation.txt`

**Claude and Mixtral**  
`python cascade.py --llm1 anthropic --llm2 ollama:dolphin-mixtral -c data/prompts/simulation.json -s1 data/prompts/simulation.txt -s2 data/prompts/simulation.txt`

**Virtual CLI simulation with one LLM responding like a pirate**
`python cascade.py --llm1 anthropic --llm2 anthropic -c data/prompts/simulation.json -s1 data/prompts/simulation.txt -s2 data/prompts/pirate.txt`


## Credit
Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for inspiration and [original code and prompt](https://www.codedump.xyz/py/ZfkQmMk8I7ecLbIk).  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).
