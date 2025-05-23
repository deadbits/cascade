# cascade

Facilitates a conversation between two LLMs (OpenAI, Anthropic, Ollama) and an optional human-in-the-loop

## Installation 🛠️

```bash
git clone https://github.com/deadbits/cascade.git
cd cascade
pyenv virtualenv 3.11.7 cascade
pyenv activate cascade
pip install -r requirements.txt
```

* Make sure Ollama is running if you're using it for inference.
* If using OpenAI/Anthropic, set your API keys in a `.env` file:

_cascade/.env_
```
ANTHROPIC_API_KEY=foo
OPENAI_API_KEY=foo
```

## Usage 🚀

The application now uses a YAML configuration file for easier setup and reusability.

```bash
python main.py --config data/config.yaml
```

### YAML Configuration

Modify the config file `data/config.yaml` or create your own with the following structure:

```yaml
# LLM connection string options: anthropic:claude-3-opus-20240229, openai:gpt-4-1106-preview, ollama:dolphin-mixtral
llm1:
  connection: anthropic:claude-3-opus-20240229
  system_prompt_file: path/to/system_prompt1.txt

llm2:
  connection: openai:gpt-4-1106-preview
  system_prompt_file: path/to/system_prompt2.txt

# Conversation Settings
rounds: 5
output_file: path/to/output.json

# Conversation history in JSON format
history_file: path/to/conversation_history.json

# Optional added to chat with <HUMAN> tag
human_in_the_loop: False

# Or conversation history in YAML format
# Better for short conversations / quick tests
# history:
#  - role: user
#    content: "Hello, how are you?"
#  - role: assistant
#    content: "I'm doing well, thank you for asking. How can I assist you today?"
```

**Connection string format:**
- For Anthropic: `anthropic:claude-3-opus-20240229`
- For OpenAI: `openai:gpt-4-1106-preview`
- For Ollama: `ollama:dolphin-mixtral`

*The provider and model are separated by a colon. Only the `connection` and `system_prompt_file` fields are required for each LLM.*

* `history_file` takes a JSON file containing the conversation history
* For an example conversation history, see [data/prompts/simulation.json](data/prompts/simulation.json)
* You can optionally specify a short conversation history directly in the YAML file using the `history` key

**Human-in-the-loop**

When running in this mode, you'll see `msg ($LLM_NAME): ` in between messages sent to/from the LLMs.
You can optionally add your own message to the chat here, or press Ctrl+C to skip that round.

If you add a message, it'll be appended with the format below. 
**It is up to you to use a system prompt or conversation history that handles this appropriately.**

```xml
<HUMAN>your message</HUMAN>
```

## Examples

**Claude and Mixtral** 

```yaml
llm1:
  connection: anthropic:claude-3-opus-20240229
  system_prompt_file: path/to/prompt.txt
llm2:
  connection: ollama:dolphin-mixtral
  system_prompt_file: path/to/prompt.txt
rounds: 5
output_file: output.json
history_file: path/to/chat.json
```

**Run a [virtual CLI simulation](https://twitter.com/AndyAyrey/status/1769942282168664104) between Anthropic and OpenAI**

```yaml
llm1:
  connection: anthropic:claude-3-opus-20240229
  system_prompt_file: data/prompts/simulation.txt
llm2:
  connection: openai:gpt-4-1106-preview
  system_prompt_file: data/prompts/simulation.txt
rounds: 5
output_file: output.json
history_file: data/prompts/simulation.json
```

**Chat with human-in-the-loop**

```yaml
llm1:
  connection: anthropic:claude-3-opus-20240229
  system_prompt_file: data/prompts/guided-chat.txt
llm2:
  connection: anthropic:claude-3-5-sonnet-20241022
  system_prompt_file: data/prompts/guided-chat.txt
rounds: 5
output_file: output.json
history_file: data/prompts/simulation.json
human_in_the_loop: True
```

## Credit

Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for inspiration and [original code and prompt](https://www.codedump.xyz/py/ZfkQmMk8I7ecLbIk).  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).
