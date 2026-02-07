# AI Integration Tools

> Multi-provider AI interface supporting 11 providers with generate, research, and deep reasoning capabilities.

---

## AI Integration Tools Documentation

### AI Tools Widget

**Category**: AI Integration Tools  
**Availability**: Conditional (requires ai_tools.py module and API keys)  
**Implementation**: `tools/ai_tools.py` - `AIToolsWidget` class  
**Supported Providers**: 11 AI providers (Google AI, Vertex AI, Azure AI, Anthropic AI, OpenAI, AWS Bedrock, Cohere AI, HuggingFace AI, Groq AI, OpenRouter AI, LM Studio)

#### Description

The AI Tools Widget is a comprehensive multi-provider AI interface that integrates **11 major AI services** into a unified tabbed interface. It provides seamless access to state-of-the-art language models from Google AI Studio, Google Vertex AI, Azure AI, Anthropic, OpenAI, AWS Bedrock, Cohere, HuggingFace, Groq, OpenRouter, and local LM Studio instances, with provider-specific configuration, parameter tuning capabilities, and **enhanced security features** including API key encryption at rest and service account JSON file support for Vertex AI.

#### Key Features

- **Multi-Provider Support**: 11 AI providers in a single unified interface
- **Tabbed Interface**: Easy switching between different AI services with persistent settings
- **Model Selection**: Provider-specific model dropdown with custom model support and model refresh capabilities
- **Parameter Tuning**: Advanced parameter configuration for each provider with tabbed organization
- **System Prompts**: Customizable system prompts for each provider (provider-specific naming)
- **API Key Management**: 🔒 **Encrypted API key storage at rest** with direct links to provider dashboards
- **Async Processing**: Non-blocking AI requests with progress indication and cancellation support
- **Error Handling**: Comprehensive error handling with intelligent validation and user-friendly error messages
- **Local AI Support**: LM Studio integration for running local models without API keys
- **AWS Integration**: Full AWS Bedrock support with multiple authentication methods and intelligent model filtering
- **Security**: Encryption at rest for API keys using cryptography library (optional but recommended)
- **AI Research Mode**: Deep research with extended reasoning + web search (OpenAI GPT-5.2, Anthropic Claude Opus 4.5, OpenRouter)
- **Deepreasoning Mode**: 6-step structured reasoning protocol with Claude Opus 4.5 Extended Thinking

#### AI Research Action (New)

The AI Tools Widget now supports advanced research capabilities through the `research` action:

| Provider | Model | Features |
|----------|-------|----------|
| OpenAI | GPT-5.2 | `reasoning_effort` (xhigh), deep reasoning |
| Anthropic AI | Claude Opus 4.5 | `thinking_budget`, `search_count`, web search |
| OpenRouterAI | Various (gemini-3-flash, sonar-deep-research) | `max_results`, web search |

**Research Parameters:**
- `research_mode`: `two-stage` (search→reason) or `single` (combined)
- `reasoning_effort`: OpenAI effort level (none/low/medium/high/xhigh)
- `thinking_budget`: Anthropic thinking tokens (1000-128000)
- `search_count`: Anthropic web search uses
- `max_results`: OpenRouter web search results (1-20)
- `style`: Output format (analytical/concise/creative/report)

#### Deepreasoning Action (New - Anthropic Only)

6-step structured reasoning protocol using Claude Opus 4.5 Extended Thinking:
1. **Decompose** - Break down complex queries
2. **Search** - Optional web search during reasoning
3. **Decide** - Make key determinations
4. **Analyze** - Deep analysis
5. **Verify** - Check conclusions
6. **Synthesize** - Compile final answer

#### Supported AI Providers

The AI Tools Widget supports 11 different AI providers, each with unique capabilities, pricing models, and configuration requirements. This section provides detailed information about each provider.

##### 1. Google AI (Gemini Models)

**Overview**: Google's Gemini models provide advanced multimodal AI capabilities with strong reasoning and code generation.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://aistudio.google.com/apikey
- **API Endpoint**: `https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}`
- **System Prompt Field**: `system_prompt`

**Default Model**: `gemini-1.5-pro-latest`

**Available Models**: 
- `gemini-1.5-pro-latest` - Latest Pro model with advanced reasoning, 2M token context
- `gemini-1.5-flash-latest` - Fast model optimized for speed, 1M token context
- `gemini-1.0-pro` - Stable production model, 32K token context
- `gemini-2.5-flash` - Current fast and efficient model

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness in responses
- **topK** (1-100): Limits vocabulary to top K tokens
- **topP** (0.0-1.0): Nucleus sampling threshold
- **candidateCount** (1-8): Number of response candidates to generate
- **maxOutputTokens** (1-8192): Maximum response length
- **stopSequences**: Array of strings that stop generation

**Best For**: Complex reasoning, code generation, multimodal tasks, long context understanding

##### 2. Vertex AI (Gemini Models)

**Overview**: Google Cloud Vertex AI provides enterprise-grade access to Gemini models with OAuth2 service account authentication, offering the same powerful capabilities as Google AI Studio but with enterprise security, billing control, and regional deployment options.

**Configuration**:
- **Authentication Method**: Service Account JSON file (🔒 encrypted at rest)
- **Documentation URL**: https://cloud.google.com/vertex-ai/docs/authentication
- **API Endpoint**: `https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent`
- **System Prompt Field**: `system_prompt`
- **Authentication**: OAuth2 access tokens via `google-auth` library

**Default Model**: `gemini-2.5-flash`

**Available Models**: 
- `gemini-2.5-flash` - Fast and efficient model optimized for speed
- `gemini-2.5-pro` - Advanced Pro model with enhanced reasoning capabilities

**Setup Requirements**:
1. **Service Account JSON File**: Download from Google Cloud Console
   - Go to IAM & Admin > Service Accounts
   - Create or select a service account
   - Create and download a JSON key
2. **Required Permissions**: Service account must have "Vertex AI User" role
3. **API Enablement**: Vertex AI API must be enabled for the project
4. **Billing**: Billing must be enabled for the project (required for Vertex AI)

**Configuration Steps**:
1. Select "Vertex AI" tab
2. Click "Upload JSON" button
3. Select your service account JSON file
4. The system will automatically:
   - Parse and store all JSON fields securely
   - Encrypt the private key
   - Extract and set project_id
   - Set default location to `us-central1`
5. Select your preferred location from the dropdown (if different from default)
6. Select model from dropdown (default: `gemini-2.5-flash`)

**Key Parameters** (same as Google AI):
- **temperature** (0.0-2.0): Controls randomness in responses
- **topK** (1-100): Limits vocabulary to top K tokens
- **topP** (0.0-1.0): Nucleus sampling threshold
- **candidateCount** (1-8): Number of response candidates to generate
- **maxOutputTokens** (1-8192): Maximum response length
- **stopSequences**: Comma-separated list of strings that stop generation

**Supported Locations**:
- `us-central1`, `us-east1`, `us-east4`, `us-west1`, `us-west4`
- `europe-west1`, `europe-west4`, `europe-west6`
- `asia-east1`, `asia-northeast1`, `asia-southeast1`, `asia-south1`

**Best For**: Enterprise deployments, organizations requiring billing control, regional compliance requirements, same use cases as Google AI but with enterprise-grade authentication

**Differences from Google AI**:
- Uses OAuth2 service account authentication instead of API keys
- Requires billing to be enabled
- Supports regional deployment for compliance
- Uses Vertex AI Platform endpoint instead of AI Studio endpoint
- Better suited for production enterprise workloads

##### 3. Azure AI (Azure AI Foundry & Azure OpenAI)

**Overview**: Azure AI provides enterprise-grade access to AI models through Azure AI Foundry (supporting multiple model providers) and Azure OpenAI (OpenAI models on Azure infrastructure), with automatic endpoint detection, flexible deployment options, and enterprise security features.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://learn.microsoft.com/en-us/azure/ai-foundry/foundry-models/how-to/quickstart-ai-project
- **API Endpoint**: Auto-detected based on endpoint format
  - **Azure AI Foundry**: `https://{resource}.services.ai.azure.com/models/chat/completions?api-version={api_version}` (model in request body)
  - **Azure OpenAI**: `https://{resource}.openai.azure.com/openai/deployments/{model}/chat/completions?api-version={api_version}` (model in URL path)
  - **Azure OpenAI (Cognitive Services)**: `https://{resource}.cognitiveservices.azure.com/openai/deployments/{model}/chat/completions?api-version={api_version}` (model in URL path)
- **System Prompt Field**: `system_prompt`
- **Headers**: `api-key: {api_key}`, `Content-Type: application/json`
- **API Format**: OpenAI-compatible

**Default Model**: `gpt-4.1`

**Available Models**: 
- `gpt-4.1` - Latest GPT-4.1 model with enhanced capabilities
- `gpt-4o` - GPT-4 Omni model, multimodal, 128K context
- `gpt-4-turbo` - High-performance GPT-4 variant, 128K context
- `gpt-35-turbo` - Fast and cost-effective model, 16K context

**Setup Requirements**:
1. **Azure AI Resource**: Create an Azure AI resource in Azure Portal
   - Go to Azure Portal > Create a resource > Azure AI services
   - Choose between Azure AI Foundry (multiple models) or Azure OpenAI (OpenAI models only)
   - Note your resource endpoint URL
2. **Deployment**: Deploy your desired model(s) in the Azure Portal
   - For Azure OpenAI: Create a deployment with your model name
   - For Azure AI Foundry: Models are available through the Foundry endpoint
3. **API Key**: Retrieve your API key from the Azure Portal
   - Go to your resource > Keys and Endpoint
   - Copy either Key 1 or Key 2

**Configuration Steps**:
1. Select "Azure AI" tab
2. Enter your **API Key** in the "API Key" field
3. Enter your **Resource Endpoint** URL:
   - Azure AI Foundry: `https://{resource-name}.services.ai.azure.com` or `https://{resource-name}.services.ai.azure.com/api/projects/{project-name}`
   - Azure OpenAI: `https://{resource-name}.openai.azure.com` or `https://{resource-name}.cognitiveservices.azure.com`
4. Enter **API Version** (default: `2024-10-21`):
   - Common versions: `2024-10-21`, `2025-01-01-preview`, `2024-02-15-preview`
   - The system will automatically detect endpoint type and construct the correct URL
5. Select **Model (Deployment Name)** from dropdown (default: `gpt-4.1`)
6. Configure system prompt and parameters as needed
7. Click "Process" to test

**Endpoint Auto-Detection**:
The system automatically detects your endpoint type based on the URL:
- **Azure AI Foundry** (`.services.ai.azure.com`): Uses `/models/chat/completions` format with model in request body
- **Azure OpenAI** (`.openai.azure.com` or `.cognitiveservices.azure.com`): Uses `/openai/deployments/{model}/chat/completions` format with model in URL path

**Key Parameters** (OpenAI-compatible):
- **temperature** (0.0-2.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling (optional)
- **stop**: Comma-separated list of strings to stop generation

**Best For**: Enterprise deployments, organizations requiring Azure infrastructure, compliance with Azure security standards, production workloads with Azure integration, accessing both OpenAI models and Foundry models

**Differences between Azure AI Foundry and Azure OpenAI**:
- **Azure AI Foundry**: 
  - Supports multiple model providers (OpenAI, Meta, Mistral, etc.)
  - Uses `/models/chat/completions` endpoint format
  - Model name specified in request body, not URL
  - More flexible for accessing diverse model ecosystem
- **Azure OpenAI**:
  - Focuses on OpenAI models (GPT-4, GPT-3.5, etc.)
  - Uses `/openai/deployments/{model}/chat/completions` endpoint format
  - Model name (deployment name) specified in URL path
  - Simpler if only using OpenAI models

**Troubleshooting**:
- **404 Error**: Ensure your endpoint URL is correct and matches your resource type (Foundry vs. OpenAI)
- **401 Error**: Verify your API key is correct and has proper permissions
- **Deployment Not Found**: Check that your model deployment name matches exactly (case-sensitive)
- **API Version Issues**: Try updating to the latest API version (e.g., `2025-01-01-preview`)

##### 4. Anthropic AI (Claude Models)

**Overview**: Anthropic's Claude models excel at nuanced understanding, creative writing, and following complex instructions with strong safety features.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://console.anthropic.com/settings/keys
- **API Endpoint**: `https://api.anthropic.com/v1/messages`
- **System Prompt Field**: `system` (Anthropic-specific naming)
- **Headers**: `x-api-key`, `anthropic-version: 2023-06-01`

**Default Model**: `claude-3-5-sonnet-20241022-v2:0`

**Available Models**:
- `claude-3-5-sonnet-20241022-v2:0` - Latest Sonnet with enhanced capabilities, 200K context
- `claude-3-5-sonnet-20240620` - Previous Sonnet version, 200K context
- `claude-3-opus-20240229` - Most capable model for complex tasks, 200K context
- `claude-3-sonnet-20240229` - Balanced performance and speed, 200K context
- `claude-3-haiku-20240307` - Fast model for simple tasks, 200K context
- `claude-3-5-haiku-20241022-v1:0` - Latest fast model, 200K context

**Key Parameters**:
- **max_tokens** (1-4096): Maximum response length (required parameter)
- **temperature** (0.0-1.0): Controls randomness in responses
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **top_k** (1-500): Limits vocabulary to top K tokens
- **stop_sequences**: Array of strings that stop generation

**Best For**: Creative writing, detailed analysis, instruction following, ethical AI applications

##### 5. OpenAI (GPT Models)

**Overview**: OpenAI's GPT models are industry-leading language models with broad capabilities across text generation, analysis, and reasoning.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://platform.openai.com/settings/organization/api-keys
- **API Endpoint**: `https://api.openai.com/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`

**Default Model**: `gpt-4o`

**Available Models**:
- `gpt-4o` - Latest GPT-4 Omni model, multimodal, 128K context
- `gpt-4o-mini` - Compact version of GPT-4o, cost-effective, 128K context
- `gpt-4-turbo` - High-performance GPT-4 variant, 128K context
- `gpt-4` - Standard GPT-4 model, 8K context
- `gpt-3.5-turbo` - Fast and cost-effective model, 16K context
- `gpt-3.5-turbo-16k` - Extended context version, 16K context

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling
- **response_format**: JSON mode for structured outputs

**Best For**: General-purpose text generation, code assistance, broad knowledge tasks, structured outputs

##### 6. AWS Bedrock (Multi-Provider Models) 🆕 ENHANCED

**Overview**: AWS Bedrock provides access to multiple foundation models from various providers through a unified AWS API, with **intelligent model filtering** that excludes embedding and image models.

**Configuration**:
- **API Key/Credentials Required**: Yes (multiple authentication methods supported)
- **API Key URL**: https://console.aws.amazon.com/bedrock/home
- **API Endpoint**: `https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke`
- **System Prompt Field**: `system_prompt`
- **AWS Service**: True (requires AWS authentication)

**Authentication Methods**:
1. **API Key (Bearer Token)**: Simple API key authentication
2. **IAM (Explicit Credentials)**: AWS Access Key ID + Secret Access Key
3. **Session Token (Temporary Credentials)**: Access Key + Secret Key + Session Token
4. **IAM (Implied Credentials)**: Uses system-configured AWS credentials

**AWS Configuration Fields**:
- **AWS Region**: Select from 20+ AWS regions (default: us-west-2)
- **Context Window**: Model context window size (default: 8192)
- **Max Output Tokens**: Maximum response length (default: 4096)

**Default Model**: `amazon.nova-pro-v1:0`

**Available Text Generation Models** (🔒 Embedding and Image models automatically filtered):
- **Amazon Nova**:
  - `amazon.nova-pro-v1:0` - Advanced reasoning and generation
  - `amazon.nova-lite-v1:0` - Fast and cost-effective
  - `amazon.nova-micro-v1:0` - Ultra-fast for simple tasks
- **Anthropic Claude**:
  - `anthropic.claude-3-5-sonnet-20241022-v2:0` - Latest Claude Sonnet
  - `anthropic.claude-3-5-haiku-20241022-v1:0` - Fast Claude model
  - `anthropic.claude-3-opus-20240229` - Most capable Claude
- **Meta Llama**:
  - `meta.llama3-1-70b-instruct-v1:0` - Large Llama 3.1 model
  - `meta.llama3-2-90b-instruct-v1:0` - Largest Llama 3.2 model
  - `meta.llama3-1-8b-instruct-v1:0` - Compact Llama 3.1
- **Mistral AI**:
  - `mistral.mistral-large-2402-v1:0` - Large Mistral model
  - `mistral.mistral-7b-instruct-v0:2` - Compact Mistral
- **AI21 Labs**:
  - `ai21.jamba-1-5-large-v1:0` - Jamba large model
- **Cohere**:
  - `cohere.command-r-plus-v1:0` - Command R Plus
  - `cohere.command-r-v1:0` - Command R

**Filtered Out Models** (Not shown in dropdown):
- ❌ **Embedding Models**: `cohere.embed-*`, `amazon.titan-embed-*`
- ❌ **Image Models**: `amazon.titan-image-*`, `amazon.nova-canvas-*`, `amazon.nova-reel-*`, `stability.stable-diffusion-*`

**Model Refresh Feature**:
- Click "Refresh Models" button to fetch latest available models from AWS Bedrock
- Automatically filters out non-text-generation models
- Updates dropdown with only compatible text generation models

**Intelligent Model Validation**:
If you manually enter an embedding or image model ID, the system will display a helpful error:
```
Error: 'cohere.embed-multilingual-v3' is not a text generation model.

You've selected an embedding or image model which cannot generate text.

Please select a text generation model such as:
• amazon.nova-pro-v1:0
• anthropic.claude-3-5-sonnet-20241022-v2:0
• meta.llama3-1-70b-instruct-v1:0
• mistral.mistral-large-2402-v1:0

Use the 'Refresh Models' button to get an updated list.
```

**Key Parameters**:
- **temperature** (0.0-1.0): Controls randomness (model-specific)
- **max_tokens**: Maximum response length (configured separately)
- **top_p** (0.0-1.0): Nucleus sampling (model-specific)
- **top_k**: Top-k sampling (model-specific)

**Best For**: Enterprise AI applications, multi-model access, AWS-integrated workflows, compliance requirements

**Reference**: See `archive/AWS_BEDROCK_MODEL_FILTER_FIX.md` for implementation details

##### 7. Cohere AI (Command Models)

**Overview**: Cohere's Command models specialize in enterprise applications with strong retrieval-augmented generation (RAG) capabilities.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://dashboard.cohere.com/api-keys
- **API Endpoint**: `https://api.cohere.com/v1/chat`
- **System Prompt Field**: `preamble` (Cohere-specific naming)
- **Headers**: `Authorization: Bearer {api_key}`

**Default Model**: `command-r-plus`

**Available Models**:
- `command-r-plus` - Enhanced Command model with improved capabilities, 128K context
- `command-r` - Standard Command model, 128K context
- `command` - Base Command model, 4K context
- `command-light` - Lightweight version for simple tasks, 4K context
- `command-nightly` - Experimental latest features

**Key Parameters**:
- **temperature** (0.0-5.0): Controls randomness in responses
- **max_tokens** (1-4096): Maximum response length
- **k** (0-500): Top-k sampling parameter
- **p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (0.0-1.0): Reduces repetition
- **presence_penalty** (0.0-1.0): Encourages new topics
- **citation_quality**: Controls citation accuracy in RAG

**Best For**: Enterprise applications, RAG systems, document analysis, citation-heavy tasks

##### 9. HuggingFace AI (Open Source Models)

**Overview**: HuggingFace provides access to thousands of open-source models through their Inference API, supporting community-driven AI development.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://huggingface.co/settings/tokens
- **Implementation**: Uses `huggingface_hub.InferenceClient`
- **System Prompt Field**: `system_prompt`
- **Dependency**: Requires `huggingface_hub` library

**Default Model**: `meta-llama/Meta-Llama-3-8B-Instruct`

**Available Models**:
- `meta-llama/Meta-Llama-3-8B-Instruct` - Meta's Llama 3 instruction-tuned, 8K context
- `meta-llama/Meta-Llama-3-70B-Instruct` - Large Llama 3 model, 8K context
- `mistralai/Mistral-7B-Instruct-v0.2` - Mistral instruction-tuned, 32K context
- `mistralai/Mixtral-8x7B-Instruct-v0.1` - Mixture of experts model, 32K context
- `google/gemma-7b-it` - Google's Gemma instruction-tuned, 8K context
- `microsoft/phi-2` - Microsoft's compact model, 2K context
- Custom models: Any HuggingFace model with inference API enabled

**Key Parameters**:
- **max_tokens** (1-2048): Maximum response length
- **temperature** (0.0-2.0): Controls randomness
- **top_p** (0.0-1.0): Nucleus sampling threshold

**Availability Check**:
```python
if HUGGINGFACE_AVAILABLE:
    # HuggingFace features enabled
else:
    # Install with: pip install huggingface_hub
```

**Best For**: Open-source AI, custom models, research applications, cost-effective inference

##### 8. Groq AI (High-Speed Inference)

**Overview**: Groq provides ultra-fast inference using custom LPU (Language Processing Unit) hardware, delivering industry-leading speed for open-source models.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://console.groq.com/keys
- **API Endpoint**: `https://api.groq.com/openai/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`
- **API Format**: OpenAI-compatible

**Default Model**: `llama3-70b-8192`

**Available Models**:
- `llama3-70b-8192` - Large Llama 3 model, 8K context, ultra-fast
- `llama3-8b-8192` - Compact Llama 3 model, 8K context
- `mixtral-8x7b-32768` - Mixtral MoE model, 32K context
- `gemma2-9b-it` - Gemma 2 instruction-tuned, 8K context
- `llama-3.1-70b-versatile` - Llama 3.1 large model, 128K context
- `llama-3.1-8b-instant` - Llama 3.1 compact, 128K context

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-32768): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for deterministic sampling
- **response_format**: JSON mode for structured outputs

**Best For**: Speed-critical applications, real-time inference, high-throughput workloads, latency-sensitive tasks

##### 8. OpenRouter AI (Model Aggregator)

**Overview**: OpenRouter provides unified access to 100+ models from multiple providers through a single API, with transparent pricing and free tier options.

**Configuration**:
- **API Key Required**: Yes (🔒 encrypted at rest)
- **API Key URL**: https://openrouter.ai/settings/keys
- **API Endpoint**: `https://openrouter.ai/api/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Headers**: `Authorization: Bearer {api_key}`
- **API Format**: OpenAI-compatible

**Default Model**: `anthropic/claude-3.5-sonnet`

**Available Models** (100+ models, popular examples):
- `anthropic/claude-3.5-sonnet` - Claude 3.5 Sonnet via OpenRouter
- `anthropic/claude-3-opus` - Claude 3 Opus
- `google/gemini-flash-1.5:free` - Free Gemini Flash model
- `google/gemini-pro-1.5` - Gemini Pro 1.5
- `meta-llama/llama-3-8b-instruct:free` - Free Llama 3 model
- `meta-llama/llama-3-70b-instruct` - Large Llama 3
- `openai/gpt-4o` - GPT-4o via OpenRouter
- `openai/gpt-4o-mini` - GPT-4o Mini
- `mistralai/mistral-large` - Mistral Large
- `cohere/command-r-plus` - Cohere Command R Plus

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-unlimited): Maximum response length (model-dependent)
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **top_k** (1-100): Top-k sampling parameter
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **repetition_penalty** (0.0-2.0): OpenRouter-specific repetition control

**Best For**: Model comparison, cost optimization, accessing multiple providers, free tier experimentation

##### 11. LM Studio (Local AI Models) 🆕

**Overview**: LM Studio enables running AI models locally on your machine without API keys, providing privacy, offline access, and no usage costs.

**Configuration**:
- **API Key Required**: No (local service)
- **Base URL**: Configurable (default: `http://127.0.0.1:1234`)
- **API Endpoint**: `{base_url}/v1/chat/completions`
- **System Prompt Field**: `system_prompt`
- **Local Service**: True (requires LM Studio running)
- **API Format**: OpenAI-compatible

**Setup Requirements**:
1. Download and install LM Studio from http://lmstudio.ai/
2. Download a model in LM Studio (e.g., Llama 3, Mistral, Phi-3)
3. Start the local server in LM Studio
4. Configure base URL in Pomera AI Commander (default works for standard setup)

**Model Refresh Feature**:
- Click "Refresh Models" button to fetch currently loaded models from LM Studio
- Automatically detects models available in your local LM Studio instance
- Updates dropdown with loaded model names

**Configuration Fields**:
- **Base URL**: LM Studio server address (default: `http://127.0.0.1:1234`)
- **Model**: Select from loaded models or enter custom model name
- **Max Tokens**: Maximum response length (default: 2048)

**Available Models** (depends on what you've downloaded in LM Studio):
- Llama 3 variants (8B, 70B)
- Mistral variants (7B, Mixtral)
- Phi-3 variants (mini, small, medium)
- Gemma variants
- Any GGUF format model compatible with LM Studio

**Key Parameters**:
- **temperature** (0.0-2.0): Controls randomness
- **max_tokens** (1-32768): Maximum response length
- **top_p** (0.0-1.0): Nucleus sampling threshold
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition
- **presence_penalty** (-2.0 to 2.0): Encourages new topics

**Best For**: Privacy-sensitive applications, offline AI access, no API costs, local development, custom model experimentation

#### Architecture

##### Multi-Provider Support System

The AI Tools Widget implements a **unified interface** for multiple AI providers through a common abstraction layer. This architecture enables:

- **Provider Abstraction**: Common interface for different AI APIs
- **Configuration Management**: Provider-specific settings stored separately
- **Dynamic UI Generation**: Tab-based interface with provider-specific controls
- **Encryption Layer**: Optional API key encryption at rest
- **Async Processing**: Non-blocking requests with threading

##### Widget Structure
```
AIToolsWidget (ttk.Frame)
├── Notebook (ttk.Notebook)
│   ├── Google AI Tab
│   ├── Vertex AI Tab (with JSON upload)
│   ├── Anthropic AI Tab
│   ├── OpenAI Tab
│   ├── AWS Bedrock Tab (with auth method selection)
│   ├── Cohere AI Tab
│   ├── HuggingFace AI Tab
│   ├── Groq AI Tab
│   ├── OpenRouter AI Tab
│   └── LM Studio Tab (local, no API key)
├── Provider Configuration Dictionary
│   ├── url_template / url
│   ├── headers_template
│   ├── api_url (for "Get API Key" links)
│   ├── local_service (for LM Studio)
│   └── aws_service (for AWS Bedrock)
└── Settings Storage (settings.json)
    └── tool_settings[provider_name]
        ├── API_KEY (encrypted)
        ├── MODEL
        ├── MODELS_LIST
        ├── system_prompt / system / preamble
        └── provider-specific parameters
```

##### Provider Configuration Dictionary

Each provider is defined in the `ai_providers` dictionary:

```python
self.ai_providers = {
    "Google AI": {
        "url_template": "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}",
        "headers_template": {'Content-Type': 'application/json'},
        "api_url": "https://aistudio.google.com/apikey"
    },
    "Vertex AI": {
        "url_template": "https://{location}-aiplatform.googleapis.com/v1/projects/{project_id}/locations/{location}/publishers/google/models/{model}:generateContent",
        "headers_template": {'Content-Type': 'application/json', 'Authorization': 'Bearer {access_token}'},
        "api_url": "https://cloud.google.com/vertex-ai/docs/authentication"
    },
    "AWS Bedrock": {
        "url": "https://bedrock-runtime.{region}.amazonaws.com/model/{model}/invoke",
        "headers_template": {"Content-Type": "application/json"},
        "api_url": "https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html",
        "aws_service": True
    },
    "LM Studio": {
        "url_template": "{base_url}/v1/chat/completions",
        "headers_template": {"Content-Type": "application/json"},
        "api_url": "http://lmstudio.ai/",
        "local_service": True
    },
    # ... other providers
}
```

##### Tab Components

**Standard Provider Tab** (Google AI, Anthropic, OpenAI, Cohere, Groq, OpenRouter, HuggingFace):
1. **API Configuration Section** (LabelFrame with 🔒 encryption indicator)
   - API Key input field (masked with `show="*"`)
   - "Get API Key" button linking to provider dashboard
   
**Vertex AI Tab** (Special Configuration):
1. **API Configuration Section** (LabelFrame with 🔒 encryption indicator)
   - "Upload JSON" button to upload service account JSON file
   - Status label showing loaded project ID
   - "Get API Key" button (links to documentation)
   
2. **Location Configuration Section** (LabelFrame)
   - Location dropdown with 12 regional options
   - Default: `us-central1`

**Standard Provider Tab** (Google AI, Anthropic, OpenAI, Cohere, Groq, OpenRouter, HuggingFace):
2. **Model Configuration Section** (LabelFrame)
   - Model selection dropdown (Combobox)
   - Model editor button (✎) for custom models
   
3. **Process Button**
   - Triggers AI request processing via `run_ai_in_thread()`
   
4. **System Prompt Section** (LabelFrame)
   - Multi-line text area (tk.Text, height=2)
   - Provider-specific field name (system_prompt/system/preamble)
   
5. **Parameter Configuration Notebook** (ttk.Notebook, height=120)
   - Tabbed parameter interface
   - Provider-specific parameter controls
   - Scrollable parameter frames

**AWS Bedrock Tab** (Special Configuration):
1. **AWS Bedrock Configuration Section**
   - Authentication Method dropdown (4 options)
   - AWS Region dropdown (20+ regions)
   
2. **Model Configuration Section**
   - Model selection dropdown
   - "Refresh Models" button (fetches from AWS)
   
3. **AWS Credentials Section** (Dynamic visibility based on auth method)
   - API Key field (for Bearer Token auth)
   - Access Key ID field (for IAM auth)
   - Secret Access Key field (for IAM auth)
   - Session Token field (for temporary credentials)
   - IAM Role info (for implied credentials)
   
4. **Content Section**
   - Context Window configuration
   - Max Output Tokens configuration
   
5. **Process Button** and **System Prompt** (standard)

**LM Studio Tab** (Local Service):
1. **LM Studio Configuration Section**
   - Base URL input field (default: http://127.0.0.1:1234)
   - "Refresh Models" button (fetches from local server)
   
2. **Model Configuration Section**
   - Model selection dropdown
   - Max Tokens input field
   
3. **Process Button** and **System Prompt** (standard)
4. **No Parameter Notebook** (simplified interface)

##### Common AI Tool Interface

All providers implement a common processing interface:

```python
def process_ai_request(self):
    """Common interface for all providers"""
    # 1. Get current provider
    provider_name = self.current_provider
    
    # 2. Validate configuration
    if not self.validate_provider_config(provider_name):
        return
    
    # 3. Prepare request
    request_data = self.prepare_request(provider_name)
    
    # 4. Execute request (provider-specific)
    if provider_name == "HuggingFace AI":
        response = self.process_huggingface_request(request_data)
    elif provider_name == "AWS Bedrock":
        response = self.process_bedrock_request(request_data)
    else:
        response = self.process_rest_api_request(request_data)
    
    # 5. Process response
    self.handle_response(response)
```

##### API Key Encryption System

**Encryption Features**:
- Uses `cryptography` library (Fernet symmetric encryption)
- PBKDF2 key derivation with 100,000 iterations
- Machine-specific salt based on computer/username
- Encrypted keys prefixed with "ENC:" for identification
- Graceful fallback if encryption unavailable

**Encryption Flow**:
```python
# On Save
api_key = "sk-1234567890abcdef"
encrypted = encrypt_api_key(api_key)
# Result: "ENC:gAAAAABh..." (stored in settings.json)

# On Load
encrypted_key = settings["API_KEY"]  # "ENC:gAAAAABh..."
decrypted = decrypt_api_key(encrypted_key)
# Result: "sk-1234567890abcdef" (used for API calls)
```

**Availability Check**:
```python
if ENCRYPTION_AVAILABLE:
    logger.info("API Key encryption is ENABLED")
else:
    logger.warning("API Key encryption is DISABLED - install cryptography")
```

#### AI Provider Setup and Configuration Guide

This comprehensive guide covers API key setup, configuration, and troubleshooting for all supported AI providers.

##### Prerequisites

**Required**:
- Python 3.7+ with tkinter
- Internet connection (except for LM Studio)
- Valid API keys for desired providers

**Optional but Recommended**:
- `cryptography` library for API key encryption: `pip install cryptography`
- `huggingface_hub` library for HuggingFace: `pip install huggingface_hub`

##### API Key Setup by Provider

###### Google AI (Gemini) Setup

**Step 1: Get API Key**
1. Visit https://aistudio.google.com/apikey
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the generated key (starts with "AIza...")

**Step 2: Configure in Pomera**
1. Select "Google AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `gemini-1.5-pro-latest`)
4. Configure system prompt (optional)
5. Click "Process" to test

**Pricing**: Free tier available with rate limits, pay-as-you-go for higher usage

###### Anthropic AI (Claude) Setup

**Step 1: Get API Key**
1. Visit https://console.anthropic.com/settings/keys
2. Sign up or log in to your Anthropic account
3. Click "Create Key"
4. Name your key and copy it (starts with "sk-ant-...")

**Step 2: Configure in Pomera**
1. Select "Anthropic AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `claude-3-5-sonnet-20241022-v2:0`)
4. Set system prompt in "System" field
5. Click "Process" to test

**Pricing**: Pay-as-you-go, no free tier (requires credit card)

###### OpenAI (GPT) Setup

**Step 1: Get API Key**
1. Visit https://platform.openai.com/settings/organization/api-keys
2. Sign in to your OpenAI account
3. Click "Create new secret key"
4. Name your key and copy it (starts with "sk-...")

**Step 2: Configure in Pomera**
1. Select "OpenAI" tab
2. Paste API key in "API Key" field
3. Select model (default: `gpt-4o`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Pay-as-you-go with $5 free credit for new accounts

###### AWS Bedrock Setup

**Step 1: AWS Account Setup**
1. Create AWS account at https://aws.amazon.com
2. Enable AWS Bedrock in your region
3. Request model access in Bedrock console
4. Choose authentication method

**Step 2: Authentication Configuration**

**Option A: API Key (Bearer Token)** - Simplest
1. Generate API key in AWS Bedrock console
2. Select "API Key (Bearer Token)" in Auth Method dropdown
3. Paste key in "AWS Bedrock API Key" field
4. Select AWS Region
5. Click "Refresh Models" to fetch available models

**Option B: IAM (Explicit Credentials)** - Most Common
1. Create IAM user with Bedrock permissions
2. Generate Access Key ID and Secret Access Key
3. Select "IAM (Explicit Credentials)" in Auth Method dropdown
4. Enter Access Key ID in "AWS Bedrock IAM Access ID"
5. Enter Secret Access Key in "AWS Bedrock IAM Access Key"
6. Select AWS Region
7. Click "Refresh Models"

**Option C: Session Token (Temporary Credentials)**
1. Generate temporary credentials (STS)
2. Select "Session Token (Temporary Credentials)"
3. Enter Access Key ID, Secret Access Key, and Session Token
4. Select AWS Region
5. Click "Refresh Models"

**Option D: IAM (Implied Credentials)** - For EC2/ECS
1. Configure AWS CLI or use EC2 instance role
2. Select "IAM (Implied Credentials)"
3. System will use configured credentials
4. Select AWS Region
5. Click "Refresh Models"

**Step 3: Model Selection**
- Click "Refresh Models" to fetch available models
- Only text generation models will appear (embedding/image models filtered)
- Select desired model from dropdown
- Configure Context Window and Max Output Tokens

**Pricing**: Pay-as-you-go, varies by model provider

###### Cohere AI Setup

**Step 1: Get API Key**
1. Visit https://dashboard.cohere.com/api-keys
2. Sign up or log in
3. Click "Create API Key"
4. Copy the generated key

**Step 2: Configure in Pomera**
1. Select "Cohere AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `command-r-plus`)
4. Set "Preamble" (Cohere's system prompt)
5. Click "Process" to test

**Pricing**: Free tier available, pay-as-you-go for production

###### HuggingFace AI Setup

**Step 1: Install Library**
```bash
pip install huggingface_hub
```

**Step 2: Get API Token**
1. Visit https://huggingface.co/settings/tokens
2. Sign up or log in
3. Click "New token"
4. Select "Read" permissions
5. Copy the generated token

**Step 3: Configure in Pomera**
1. Select "HuggingFace AI" tab
2. Paste token in "API Key" field
3. Select or enter model name (default: `meta-llama/Meta-Llama-3-8B-Instruct`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Free tier available, pay for Pro features

###### Groq AI Setup

**Step 1: Get API Key**
1. Visit https://console.groq.com/keys
2. Sign up or log in
3. Click "Create API Key"
4. Copy the generated key (starts with "gsk_...")

**Step 2: Configure in Pomera**
1. Select "Groq AI" tab
2. Paste API key in "API Key" field
3. Select model (default: `llama3-70b-8192`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Free tier with generous limits, pay-as-you-go for higher usage

###### OpenRouter AI Setup

**Step 1: Get API Key**
1. Visit https://openrouter.ai/settings/keys
2. Sign up or log in
3. Click "Create Key"
4. Copy the generated key (starts with "sk-or-...")

**Step 2: Configure in Pomera**
1. Select "OpenRouter AI" tab
2. Paste API key in "API Key" field
3. Select model (100+ available, default: `anthropic/claude-3.5-sonnet`)
4. Configure system prompt
5. Click "Process" to test

**Pricing**: Varies by model, some free models available

###### LM Studio Setup (Local AI)

**Step 1: Install LM Studio**
1. Download from http://lmstudio.ai/
2. Install for your operating system
3. Launch LM Studio

**Step 2: Download Models**
1. In LM Studio, click "Search" tab
2. Search for models (e.g., "Llama 3", "Mistral")
3. Download desired models (GGUF format)
4. Wait for download to complete

**Step 3: Start Local Server**
1. In LM Studio, click "Local Server" tab
2. Select a loaded model
3. Click "Start Server"
4. Note the server address (default: http://127.0.0.1:1234)

**Step 4: Configure in Pomera**
1. Select "LM Studio" tab
2. Enter Base URL (default: `http://127.0.0.1:1234`)
3. Click "Refresh Models" to fetch loaded models
4. Select model from dropdown
5. Set Max Tokens (default: 2048)
6. Click "Process" to test

**Pricing**: Free (runs locally, no API costs)

##### System Prompts Configuration

System prompts guide the AI's behavior and response style. Each provider uses slightly different terminology:

**Provider-Specific System Prompt Fields**:
- **Google AI, Vertex AI, Azure AI, OpenAI, HuggingFace, Groq, OpenRouter, LM Studio**: `system_prompt`
- **Anthropic AI**: `system` (Claude's message format)
- **Cohere AI**: `preamble` (Cohere's terminology)
- **AWS Bedrock**: `system_prompt` (varies by underlying model)

**Example System Prompts**:

**General Assistant**:
```
You are a helpful assistant. Provide clear, accurate, and concise responses.
```

**Technical Writer**:
```
You are a technical documentation expert. Provide clear, detailed explanations with examples. Use proper formatting and structure.
```

**Code Assistant**:
```
You are an expert programmer. Provide clean, well-commented code with explanations. Follow best practices and consider edge cases.
```

**Creative Writer**:
```
You are a creative writing assistant. Generate engaging, imaginative content with vivid descriptions and compelling narratives.
```

##### Parameter Configuration

Parameters control AI response generation. Understanding these helps optimize results:

**Common Parameters Across All Providers**:

**Temperature** (0.0-2.0):
- **0.0-0.3**: Deterministic, factual, consistent (good for technical tasks)
- **0.4-0.7**: Balanced creativity and consistency (general use)
- **0.8-1.0**: Creative, varied responses (creative writing)
- **1.1-2.0**: Highly creative, unpredictable (experimental)

**Max Tokens** (varies by provider):
- Controls maximum response length
- 1 token ≈ 0.75 words (English)
- Set based on expected response length
- Higher values = longer responses but higher cost

**Top P** (0.0-1.0) - Nucleus Sampling:
- **0.1-0.5**: More focused, deterministic
- **0.6-0.9**: Balanced (recommended: 0.9)
- **0.95-1.0**: More diverse vocabulary

**Top K** (1-100) - Vocabulary Limiting:
- Limits selection to top K most likely tokens
- **1-10**: Very focused
- **20-40**: Balanced (recommended: 40)
- **50-100**: More diverse

**Provider-Specific Parameters**:

**Google AI**:
- **candidateCount** (1-8): Number of response variations
- **stopSequences**: Array of strings to stop generation

**Anthropic AI**:
- **stop_sequences**: Custom stop strings
- **max_tokens**: Required parameter (1-4096)

**OpenAI**:
- **frequency_penalty** (-2.0 to 2.0): Reduces repetition of frequent tokens
- **presence_penalty** (-2.0 to 2.0): Encourages new topics
- **seed**: Integer for reproducible outputs
- **response_format**: `{"type": "json_object"}` for JSON mode

**Cohere AI**:
- **k** (0-500): Top-k sampling
- **p** (0.0-1.0): Nucleus sampling
- **citation_quality**: Controls citation accuracy in RAG

**Groq AI**:
- **response_format**: JSON mode support
- **seed**: Deterministic sampling

**OpenRouter AI**:
- **repetition_penalty** (0.0-2.0): OpenRouter-specific repetition control

**AWS Bedrock**:
- Parameters vary by underlying model
- Configure Context Window and Max Output Tokens separately

**LM Studio**:
- **max_tokens**: Maximum response length (1-32768)
- Standard OpenAI-compatible parameters
- **Groq AI**: response_format, seed
- **OpenRouter AI**: repetition_penalty

##### Troubleshooting Guide for Common AI Provider Issues

###### General Issues

**Issue: "Invalid API Key" Error**
- **Cause**: Incorrect or expired API key
- **Solution**:
  1. Verify key is copied correctly (no extra spaces)
  2. Check key hasn't been revoked in provider dashboard
  3. Ensure key has proper permissions
  4. Try generating a new key

**Issue: "Model Not Found" Error**
- **Cause**: Model name incorrect or unavailable
- **Solution**:
  1. Check model name spelling and capitalization
  2. Verify model is available in your region (AWS Bedrock)
  3. Use "Refresh Models" button if available
  4. Check provider documentation for current model names

**Issue: "Rate Limit Exceeded" Error**
- **Cause**: Too many requests in short time
- **Solution**:
  1. Wait before retrying (usually 60 seconds)
  2. Implement delays between requests
  3. Upgrade to higher tier plan
  4. Use different provider for high-volume tasks

**Issue: "Network Timeout" Error**
- **Cause**: Slow internet or provider issues
- **Solution**:
  1. Check internet connection
  2. Try again after a few minutes
  3. Check provider status page
  4. Increase timeout settings if available

**Issue: API Key Not Encrypted**
- **Cause**: `cryptography` library not installed
- **Solution**:
  ```bash
  pip install cryptography
  ```
- **Note**: Keys still work without encryption, but less secure

###### Provider-Specific Issues

**Google AI Issues**:

**Vertex AI Issues**:
- **403 Forbidden Error**: Usually means billing is not enabled or Vertex AI API is not enabled
  - Enable Vertex AI API in Google Cloud Console
  - Enable billing for the project
  - Ensure service account has "Vertex AI User" role
- **"Failed to obtain access token"**: Service account JSON file is invalid or missing
  - Re-upload the JSON file
  - Verify the JSON file is valid and complete
- **"Project ID not found"**: JSON file was not uploaded or parsed incorrectly
  - Click "Upload JSON" button again
  - Verify the JSON file contains a valid project_id field
- **Model not found (404)**: Model name is incorrect or not available in selected region
  - Try different model: gemini-2.5-flash or gemini-2.5-pro
  - Check if model is available in your selected location

**Issue: "API key not valid" despite correct key**
- **Solution**: Ensure API key restrictions allow your IP/application
- **Check**: Google Cloud Console → Credentials → API restrictions

**Issue: "Resource exhausted" error**
- **Solution**: Free tier quota exceeded, wait for reset or upgrade

**Anthropic AI Issues**:

**Issue: "max_tokens is required"**
- **Solution**: Anthropic requires max_tokens parameter, set in parameters tab

**Issue: "Invalid system message format"**
- **Solution**: Use "System" field (not "System Prompt") for Claude

**OpenAI Issues**:

**Issue: "Insufficient quota" error**
- **Solution**: Add payment method or wait for free credit reset

**Issue: "Model not available in your region"**
- **Solution**: Some models have regional restrictions, try different model

**AWS Bedrock Issues**:

**Issue: "Access denied" error**
- **Solution**: 
  1. Ensure IAM user has `bedrock:InvokeModel` permission
  2. Request model access in Bedrock console
  3. Verify region supports selected model

**Issue: "Model not found" after refresh**
- **Solution**: 
  1. Request access to models in Bedrock console
  2. Wait 5-10 minutes for access to propagate
  3. Try different region

**Issue: Selected embedding model error**
- **Solution**: System automatically filters these, but if manually entered:
  1. Click "Refresh Models" to see only text generation models
  2. Select a model without "embed" or "image" in name

**Cohere AI Issues**:

**Issue: "Invalid preamble" error**
- **Solution**: Use "Preamble" field (not "System Prompt") for Cohere

**HuggingFace AI Issues**:

**Issue: "Module not found: huggingface_hub"**
- **Solution**: 
  ```bash
  pip install huggingface_hub
  ```

**Issue: "Model is currently loading"**
- **Solution**: Wait 30-60 seconds and retry, free tier models may need warmup

**Issue: "Model requires authentication"**
- **Solution**: Some models require accepting terms on HuggingFace website

**Groq AI Issues**:

**Issue: "Rate limit exceeded" (common on free tier)**
- **Solution**: Groq has generous but strict rate limits, wait 60 seconds

**OpenRouter AI Issues**:

**Issue: "Insufficient credits"**
- **Solution**: Add credits to OpenRouter account

**Issue: "Model not available"**
- **Solution**: Some models have limited availability, try alternative

**LM Studio Issues**:

**Issue: "Connection refused" error**
- **Solution**:
  1. Ensure LM Studio is running
  2. Verify local server is started in LM Studio
  3. Check Base URL matches LM Studio server address
  4. Check firewall isn't blocking localhost connections

**Issue: "No models available" after refresh**
- **Solution**:
  1. Download models in LM Studio first
  2. Load a model in LM Studio
  3. Start the local server
  4. Click "Refresh Models" in Pomera

**Issue: Very slow responses**
- **Solution**:
  1. Use smaller models (8B instead of 70B)
  2. Reduce Max Tokens
  3. Ensure sufficient RAM/VRAM
  4. Close other applications

##### Usage Examples and Best Practices

###### Example 1: Basic Text Generation

**Provider**: Google AI (Gemini)
**Task**: Generate a product description

**Configuration**:
- Model: `gemini-1.5-pro-latest`
- Temperature: 0.7
- Max Tokens: 500
- System Prompt: "You are a marketing copywriter. Create engaging product descriptions."

**Input**:
```
Write a product description for a wireless Bluetooth speaker with 20-hour battery life, waterproof design, and 360-degree sound.
```

**Expected Output**:
```
Immerse yourself in premium audio with our revolutionary wireless Bluetooth speaker. 
Engineered for adventure, this powerhouse delivers crystal-clear 360-degree sound that 
fills any space. With an impressive 20-hour battery life, your music never stops. 
The rugged waterproof design means you can take the party anywhere – from poolside 
gatherings to mountain hikes. Connect seamlessly via Bluetooth 5.0 and experience 
audio freedom like never before.
```

###### Example 2: Code Generation

**Provider**: OpenAI (GPT-4o)
**Task**: Generate Python function

**Configuration**:
- Model: `gpt-4o`
- Temperature: 0.2 (lower for more deterministic code)
- Max Tokens: 1000
- System Prompt: "You are an expert Python programmer. Write clean, well-documented code."

**Input**:
```
Create a Python function that validates email addresses using regex and returns True if valid, False otherwise. Include docstring and error handling.
```

**Expected Output**:
```python
import re

def validate_email(email):
    """
    Validates an email address using regex pattern matching.
    
    Args:
        email (str): The email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
        
    Examples:
        >>> validate_email("user@example.com")
        True
        >>> validate_email("invalid.email")
        False
    """
    if not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
```

###### Example 3: Multi-Provider Comparison

**Task**: Compare response quality across providers

**Setup**: Configure identical prompts across 3 providers
- Google AI: `gemini-1.5-pro-latest`
- Anthropic AI: `claude-3-5-sonnet-20241022-v2:0`
- OpenAI: `gpt-4o`

**Common Configuration**:
- Temperature: 0.7
- Max Tokens: 500
- System Prompt: "You are a helpful assistant."

**Input**:
```
Explain quantum computing in simple terms for a 10-year-old.
```

**Workflow**:
1. Process with Google AI, save response
2. Switch to Anthropic AI tab, process same input
3. Switch to OpenAI tab, process same input
4. Compare responses for clarity, accuracy, and style

###### Example 4: AWS Bedrock Multi-Model Testing

**Provider**: AWS Bedrock
**Task**: Test different model providers through Bedrock

**Configuration**:
- Region: us-west-2
- Temperature: 0.7
- Context Window: 8192
- Max Output Tokens: 1024

**Test Models**:
1. `amazon.nova-pro-v1:0` - Amazon's model
2. `anthropic.claude-3-5-sonnet-20241022-v2:0` - Claude via Bedrock
3. `meta.llama3-1-70b-instruct-v1:0` - Llama via Bedrock

**Input**:
```
Summarize the key benefits of cloud computing for small businesses.
```

**Workflow**:
1. Click "Refresh Models" to get latest models
2. Select first model, process
3. Change model in dropdown, process again
4. Compare responses and performance

###### Example 5: Local AI with LM Studio

**Provider**: LM Studio
**Task**: Private document analysis without cloud APIs

**Configuration**:
- Base URL: `http://127.0.0.1:1234`
- Model: `llama-3-8b-instruct` (downloaded in LM Studio)
- Max Tokens: 2048
- Temperature: 0.3

**Input**:
```
Analyze this contract clause and identify potential risks:
[paste confidential contract text]
```

**Benefits**:
- No data sent to external servers
- No API costs
- Works offline
- Full privacy control

###### Best Practices Summary

**API Key Management**:
- ✅ Install `cryptography` for encryption
- ✅ Rotate keys regularly
- ✅ Use separate keys for development/production
- ✅ Monitor usage and set billing alerts
- ❌ Never share API keys publicly
- ❌ Don't commit keys to version control

**Model Selection**:
- ✅ Use smaller models for simple tasks (cost-effective)
- ✅ Use larger models for complex reasoning
- ✅ Test multiple models for your specific use case
- ✅ Consider context window size for long inputs
- ❌ Don't always use the largest/most expensive model

**Parameter Tuning**:
- ✅ Lower temperature (0.0-0.3) for factual tasks
- ✅ Higher temperature (0.7-1.0) for creative tasks
- ✅ Set appropriate max_tokens to control costs
- ✅ Use system prompts to guide behavior
- ❌ Don't use extreme parameter values without testing

**Performance Optimization**:
- ✅ Cache responses for repeated queries
- ✅ Use async processing for multiple requests
- ✅ Implement retry logic for transient failures
- ✅ Monitor rate limits and implement backoff
- ❌ Don't make unnecessary API calls

**Security**:
- ✅ Use LM Studio for sensitive data
- ✅ Enable API key encryption
- ✅ Review provider data retention policies
- ✅ Use IAM roles for AWS Bedrock in production
- ❌ Don't send PII to AI providers without consent

#### Usage Examples

##### Basic AI Request Example
**Setup:**
1. Select "Google AI" tab
2. Enter API key in the API Key field
3. Select model: `gemini-1.5-pro-latest`
4. Set system prompt: "You are a helpful writing assistant."

**Input Text:**
```
Please help me improve this sentence: "The cat was walking on the street."
```

**Expected Response:**
```
Here are several improved versions of your sentence:

1. "The cat strolled down the street." (more descriptive verb)
2. "A cat was walking along the street." (better article usage)
3. "The cat padded silently down the empty street." (more vivid and detailed)

The improvements focus on using more specific verbs and adding descriptive details to create a more engaging sentence.
```

##### Advanced Parameter Tuning Example
**Configuration:**
- Provider: OpenAI
- Model: gpt-4o
- Temperature: 0.3 (for more focused responses)
- Max Tokens: 2000
- Top P: 0.9
- Frequency Penalty: 0.2 (reduce repetition)

**System Prompt:**
```
You are a technical documentation expert. Provide clear, concise explanations with examples.
```

##### Multi-Provider Comparison Workflow
1. **Setup identical prompts** across multiple providers
2. **Configure similar parameters** (temperature, max_tokens)
3. **Process same input** with different providers
4. **Compare responses** for quality, style, and accuracy

#### Technical Implementation

##### Core Architecture
```python
class AIToolsWidget(ttk.Frame):
    def __init__(self, parent, app_instance):
        # Initialize provider configurations
        self.ai_providers = {
            "Google AI": {...},
            "Anthropic AI": {...},
            # ... other providers
        }
        
        # Create tabbed interface
        self.create_widgets()
    
    def process_ai_request(self):
        # Handle AI request processing
        # Provider-specific API calls
        # Error handling and response processing
```

##### Request Processing Flow
1. **Input Validation**: Check API key and model selection
2. **Parameter Assembly**: Gather provider-specific parameters
3. **API Request**: Make HTTP request to provider endpoint
4. **Response Processing**: Parse and format response
5. **Error Handling**: Handle API errors and network issues
6. **UI Update**: Display results in output area

##### Async Processing
- **Threading**: AI requests run in separate threads to prevent UI blocking
- **Progress Indication**: Visual feedback during processing
- **Cancellation**: Ability to cancel long-running requests
- **Error Recovery**: Graceful handling of network timeouts and API errors

#### Best Practices

##### API Key Management
- **Security**: API keys are masked in the UI
- **Storage**: Keys are stored in local settings.json file
- **Rotation**: Regularly rotate API keys for security
- **Limits**: Monitor API usage and rate limits

##### Model Selection
- **Task Matching**: Choose models appropriate for your task complexity
- **Cost Optimization**: Use smaller models for simple tasks
- **Performance**: Consider response time vs. quality trade-offs
- **Experimentation**: Test different models for your specific use cases

##### Parameter Tuning
- **Temperature**: Lower for factual tasks, higher for creative tasks
- **Max Tokens**: Set appropriate limits to control response length
- **System Prompts**: Craft clear, specific instructions
- **Testing**: Experiment with parameters to find optimal settings

##### Error Handling
- **API Limits**: Handle rate limiting and quota exceeded errors
- **Network Issues**: Implement retry logic for transient failures
- **Invalid Responses**: Validate API responses before processing
- **User Feedback**: Provide clear error messages to users

##### Common Use Cases

1. **Content Generation**: Create articles, blog posts, marketing copy, and social media content
2. **Code Assistance**: Generate, review, debug, and explain code across multiple languages
3. **Data Analysis**: Analyze and summarize large datasets, extract insights, create reports
4. **Translation**: Translate text between languages with context awareness
5. **Summarization**: Create concise summaries of long documents, articles, or research papers
6. **Question Answering**: Get detailed answers to complex questions with citations
7. **Creative Writing**: Generate stories, poetry, dialogue, and creative content
8. **Technical Documentation**: Create and improve API docs, user guides, and technical specs
9. **Research Assistance**: Literature review, concept explanation, hypothesis generation
10. **Educational Content**: Create lesson plans, study guides, practice questions
11. **Business Writing**: Draft emails, proposals, reports, and presentations
12. **Conversational AI**: Build chatbots, virtual assistants, and interactive experiences

##### Related Tools

- **Find & Replace Text**: Post-process AI-generated content with pattern replacements
- **Case Tool**: Standardize capitalization in AI responses
- **Word Frequency Counter**: Analyze vocabulary usage in AI outputs
- **Diff Viewer**: Compare responses from different AI providers
- **Email Extraction Tool**: Extract emails from AI-generated contact lists
- **URL Parser**: Analyze URLs in AI-generated content

##### See Also
- [AI Provider Setup Guide](#ai-provider-setup-and-configuration-guide)
- [Parameter Configuration](#parameter-configuration)
- [Troubleshooting Guide](#troubleshooting-guide-for-common-ai-provider-issues)
- [Usage Examples](#usage-examples-and-best-practices)
- [AWS Bedrock Model Filter Fix](archive/AWS_BEDROCK_MODEL_FILTER_FIX.md)

---



