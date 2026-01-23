---
description: Workflow for updating AI model defaults in Pomera AI Commander as part of releases
---

# AI Model Update Workflow

This workflow ensures AI model defaults stay current with the latest available models from each provider.

## When to Run

- Before each major release
- Monthly maintenance updates
- When a provider announces significant model changes

## Steps

### 1. Research Current Models

// turbo
Check each provider's documentation for latest models:

```bash
# Provider documentation URLs
# Google AI: https://ai.google.dev/gemini-api/docs/models
# OpenAI: https://platform.openai.com/docs/models
# Anthropic: https://docs.anthropic.com/en/docs/models-overview
# Cohere: https://docs.cohere.com/docs/models
# HuggingFace: https://huggingface.co/models?inference=warm
# Groq: https://console.groq.com/docs/models
# OpenRouter: https://openrouter.ai/docs/models (check :free suffix for free models)
# AWS Bedrock: https://docs.aws.amazon.com/bedrock/latest/userguide/models.html
# Vertex AI: https://cloud.google.com/vertex-ai/generative-ai/docs/model-reference/overview
```

### 2. Update Settings Defaults Registry

Edit `core/settings_defaults_registry.py`:

1. Find the provider section (e.g., `# Google AI - Updated ...`)
2. Update the comment date to current month/year
3. Update the `MODEL` default if there's a new recommended model
4. Update `MODELS_LIST` with latest models in order of:
   - Default/recommended model first
   - Other premium models
   - Free models (if available, marked with `:free` suffix for OpenRouter)

### 3. Update Free Models (OpenRouter)

OpenRouter free models change frequently. Check https://openrouter.ai/models?pricing=free:

- Models with `:free` suffix in OpenRouter are free to use
- Popular free models to include:
  - `google/gemini-2.5-flash:free`
  - `meta-llama/llama-3.3-70b-instruct:free`
  - `qwen/qwen-2.5-72b-instruct:free`
  - `deepseek/deepseek-chat:free`

### 4. Update HuggingFace Models

HuggingFace free inference changes based on model popularity:

- Check https://huggingface.co/models?inference=warm for available models
- Prioritize models with "Instruct" or "Chat" in the name
- Include popular coding models like Qwen2.5-Coder

### 5. Verify Changes

// turbo
Run the app to verify changes load correctly:

```bash
cd P:\Pomera-AI-Commander
python pomera.py
```

1. Open AI Tools
2. Verify each provider shows updated model list
3. Verify default model is selectable
4. Test at least one API call if possible

### 6. Update Version Notes

Add model updates to release notes:

```markdown
### AI Model Updates
- Updated Google AI models to Gemini 2.5 series
- Added new free models for OpenRouter
- Added Studio LM provider for local LLM support
```

## Model Update Checklist

| Provider | Default Model | Free Options | Last Updated |
|----------|---------------|--------------|--------------|
| Google AI | gemini-2.5-pro | N/A | Jan 2026 |
| Azure AI | gpt-4.1 | N/A | Dec 2025 |
| Anthropic AI | claude-sonnet-4-5 | N/A | Dec 2025 |
| OpenAI | gpt-4.1 | N/A | Dec 2025 |
| Cohere AI | command-a-03-2025 | N/A | Dec 2025 |
| HuggingFace AI | Llama-3.3-70B-Instruct | All (free tier) | Jan 2026 |
| Groq AI | llama-3.3-70b-versatile | N/A | Dec 2025 |
| OpenRouterAI | claude-sonnet-4.5 | 7+ free models | Jan 2026 |
| AWS Bedrock | claude-3-5-sonnet | N/A | Dec 2025 |
| Vertex AI | gemini-2.5-pro | N/A | Dec 2025 |
| Studio LM | local-model | All (local) | Jan 2026 |

## Notes

- Always test API calls after updating to ensure model names are correct
- OpenRouter model names use `provider/model-name` format
- HuggingFace model names use `org/Model-Name` format (case-sensitive)
- Free models may have rate limits or be removed without notice
