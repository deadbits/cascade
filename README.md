# cascade
Facilitates a conversation between two LLMs (OpenAI, Anthropic, Ollama)

Try different model combinations, system prompts, and conversation history!

![example](/data/assets/1.png)

## Installation 🛠️
```bash
git clone https://github.com/deadbits/cascade.git
cd cascade
pyenv virtualenv 3.11.7 cascade
pyenv activate cascade
pip install -r requirements.txt
```

* Make sure Ollama is running if you're using it for inference
* If using OpenAI/Anthropic, set your API keys with environment variables `ANTHROPIC_API_KEY` and `OPENAI_API_KEY`

## Usage 🚀

The application now uses a YAML configuration file for easier setup and reusability.

```bash
python main.py --config data/config.yaml
```

### YAML Configuration

Modify the YAML config file data/config.yaml or create your own with the following structure:

```yaml
# LLM type options: anthropic, openai, ollama:*
llm1:
  type: anthropic
  system_prompt_file: path/to/system_prompt1.txt

llm2:
  type: openai
  system_prompt_file: path/to/system_prompt2.txt

# Conversation Settings
rounds: 5
output_file: path/to/output.json

# Conversation history in JSON format
history_file: path/to/conversation_history.json

# Or conversation history in YAML format
# Better for short conversations / quick tests
# history:
#  - role: user
#    content: "Hello, how are you?"
#  - role: assistant
#    content: "I'm doing well, thank you for asking. How can I assist you today?"
```

* `history_file` takes a JSON file containing the conversation history
* For an example conversation history, see [data/prompts/simulation.json](data/prompts/simulation.json)
* You can optionally specify a short conversation history directly in the YAML file using the `history` key

## Examples

**Claude and Mixtral**  
```yaml
llm1:
  type: anthropic
  system_prompt_file: path/to/prompt.txt
llm2:
  type: ollama:dolphin-mixtral
  system_prompt_file: path/to/prompt.txt
rounds: 5
output_file: output.json
history_file: path/to/chat.json
```

**Run a [virtual CLI simulation](https://twitter.com/AndyAyrey/status/1769942282168664104) between Anthropic and OpenAI**  
```yaml
llm1:
  type: anthropic
  system_prompt_file: data/prompts/simulation.txt
llm2:
  type: openai
  system_prompt_file: data/prompts/simulation.txt
rounds: 5
output_file: output.json
history_file: data/prompts/simulation.json
```

**Virtual CLI simulation with one LLM responding like a pirate**
```yaml
llm1:
  type: anthropic
  system_prompt_file: data/prompts/simulation.txt
llm2:
  type: anthropic
  system_prompt_file: data/prompts/pirate.txt
rounds: 5
output_file: output.json
history_file: data/prompts/simulation.json
```

## Credit
Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for inspiration and [original code and prompt](https://www.codedump.xyz/py/ZfkQmMk8I7ecLbIk).  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).