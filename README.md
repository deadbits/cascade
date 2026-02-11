# cascade

Facilitates a conversation between two LLMs (OpenAI, Anthropic, Ollama) and an optional human-in-the-loop

## Quick Start

### Install

```bash
git clone https://github.com/deadbits/cascade.git
cd cascade
uv sync
```

### Configuration

**API keys:**

Set [LLM provider](https://ai.pydantic.dev/models/overview/) API keys as environment variables:

```
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
```

**YAML config:**

Modify the config file `data/config.yaml` or create your own with the following structure:

```yaml
# LLM connection strings
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

# Enable/disable
human_in_the_loop: False
```

* `history_file` takes a JSON file containing the conversation history
* For an example conversation history, see [data/prompts/simulation.json](data/prompts/simulation.json)

### Running

```bash
uv run cascade --config data/config.yaml
```

## Human-in-the-loop

When running in this mode, you'll see `msg ($LLM_NAME):` in between messages sent to/from the LLMs. You can optionally add your own message to the chat here, or press Ctrl+C to skip that round.

If you add a message, it'll be appended with the format below.

**It is up to you to use a system prompt or conversation history that handles this appropriately.**

```xml
<HUMAN>your message</HUMAN>
```

## Credit

Credit to [Andy Ayrey](https://twitter.com/AndyAyrey/status/1769942282168664104) for inspiration.  
Check out [his project here](https://dreams-of-an-electric-mind.webflow.io/).
