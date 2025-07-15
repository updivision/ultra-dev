# UpReview

A comprehensive GitHub Action that provides intelligent code reviews using multiple AI providers with framework-specific expertise.

## 🚀 Features

- **Multi-AI Provider Support**: Choose from OpenAI, Claude, Gemini, or DeepSeek
- **Framework-Specific Reviews**: Specialized prompts for Laravel, Vue/Nuxt, and React/Next.js
- **Smart PR Analysis**: Reviews only added lines with contextual understanding
- **Confidence Scoring**: Risk assessment and confidence levels for each review
- **Professional Comments**: Evidence-based feedback following industry best practices

## 📋 Required Inputs

### Core Configuration
```yaml
inputs:
  ai_provider:
    description: 'AI provider to use for code review'
    required: true
    # Options: 'openai', 'claude', 'gemini', 'deepseek'
  
  framework:
    description: 'Framework for specialized code review'
    required: true
    # Options: 'laravel', 'vue', 'nuxt', 'react', 'nextjs'
  
  github_token:
    description: 'GitHub token for PR access'
    required: true
```

### Provider-Specific API Keys
Provide the API key corresponding to your chosen `ai_provider`:

```yaml
  # For OpenAI
  openai_api_key:
    description: 'OpenAI API key'
    required: false
  openai_assistant_id:
    description: 'OpenAI Assistant ID'
    required: true # Required when ai_provider is 'openai'
  
  # For Claude
  claude_api_key:
    description: 'Anthropic Claude API key'
    required: false
  
  # For Gemini
  gemini_api_key:
    description: 'Google Gemini API key'
    required: false
  
  # For DeepSeek
  deepseek_api_key:
    description: 'DeepSeek API key'
    required: false
```

## 🔧 Usage Examples

### OpenAI + Laravel
```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Review
        uses: your-org/code-review-action@v1
        with:
          ai_provider: 'openai'
          framework: 'laravel'
          github_token: ${{ secrets.GITHUB_TOKEN }}
          openai_api_key: ${{ secrets.OPENAI_API_KEY }}
          openai_assistant_id: ${{ secrets.OPENAI_ASSISTANT_ID }}
```

### Claude + React
```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Review
        uses: your-org/code-review-action@v1
        with:
          ai_provider: 'claude'
          framework: 'react'
          github_token: ${{ secrets.GITHUB_TOKEN }}
          claude_api_key: ${{ secrets.CLAUDE_API_KEY }}
```

### Gemini + Vue/Nuxt
```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Review
        uses: your-org/code-review-action@v1
        with:
          ai_provider: 'gemini'
          framework: 'nuxt'
          github_token: ${{ secrets.GITHUB_TOKEN }}
          gemini_api_key: ${{ secrets.GEMINI_API_KEY }}
```

### DeepSeek + Next.js
```yaml
name: Code Review
on:
  pull_request:
    types: [opened, synchronize]

jobs:
  code-review:
    runs-on: ubuntu-latest
    steps:
      - name: AI Code Review
        uses: your-org/code-review-action@v1
        with:
          ai_provider: 'deepseek'
          framework: 'nextjs'
          github_token: ${{ secrets.GITHUB_TOKEN }}
          deepseek_api_key: ${{ secrets.DEEPSEEK_API_KEY }}
```

## 🔑 Setup Instructions

### 1. Get API Keys

#### OpenAI
1. Visit [OpenAI Platform](https://platform.openai.com/)
2. Create an API key in your dashboard
3. Create a custom Assistant and note the Assistant ID

#### Claude (Anthropic)
1. Visit [Anthropic Console](https://console.anthropic.com/)
2. Generate an API key
3. Ensure you have access to Claude-3 models

#### Gemini (Google)
1. Visit [Google AI Studio](https://makersuite.google.com/)
2. Create a new API key
3. Enable the Generative AI API

#### DeepSeek
1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Create an account and generate API key
3. Access DeepSeek Coder models

### 2. Configure GitHub Secrets

Add your API keys as repository secrets:

1. Go to your repository → Settings → Secrets and variables → Actions
2. Add the following secrets:
   - `OPENAI_API_KEY` (if using OpenAI)
   - `OPENAI_ASSISTANT_ID` (required for OpenAI)
   - `CLAUDE_API_KEY` (if using Claude)
   - `GEMINI_API_KEY` (if using Gemini)
   - `DEEPSEEK_API_KEY` (if using DeepSeek)

### 3. GitHub Token Permissions

The action requires these permissions:
- `contents: read` - To access PR files
- `pull-requests: write` - To post review comments
- `issues: write` - To update PR status

## 🤝 Contributing

### Adding New AI Providers
1. Create a new provider class in `src/providers/`
2. Implement the base provider interface
3. Add configuration in `action.yml`
4. Update documentation

### Adding New Frameworks
1. Create framework-specific prompts in `src/prompts/`
2. Add framework validation in `src/config/settings.py`
3. Update documentation and examples

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- Framework-specific best practices derived from official documentation
- AI provider integrations following their respective best practices
- Community feedback and contributions
