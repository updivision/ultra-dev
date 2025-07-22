# UltraDev

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

## 📌 Action Versioning

### How to Reference This Action

When using this action in your workflows, you can choose between different versioning strategies:

#### Option 1: Use Latest Major Version (Recommended)
```yaml
uses: updivision/up-review@v1
```
- **Automatically gets**: Latest features and bug fixes within v1.x.x
- **Best for**: Most users who want convenience and latest improvements
- **Updates**: Automatically receives compatible updates

#### Option 2: Pin to Specific Version
```yaml
uses: updivision/up-review@v1.0.1
```
- **Guarantees**: Exact same behavior every time
- **Best for**: Production environments requiring strict reproducibility
- **Updates**: Manual - you control when to update

### Why This Pattern?

**Semantic versioning** encourages precise tags like `v1.0.0`, `v1.0.1`, etc., that never change once published.

But you might want a convenience tag like `v1` that always points to the latest `v1.x.x` release.

This lets you pick either:
- **A fixed version** (e.g., `v1.0.1`) to ensure stability, or
- **A moving version** (e.g., `v1`) to get the latest compatible update without changing your workflow

##  Setup Instructions

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

**Important**: You must configure your repository to grant the necessary permissions to the GITHUB_TOKEN.

#### Setting Up Workflow Permissions
1. Go to your repository → **Settings** → **Actions** → **General**
2. Scroll down to **Workflow permissions**
3. Select **"Read and write permissions"**
4. Click **Save**

The action requires these specific permissions:
- `contents: read` - To access PR files
- `pull-requests: write` - To post review comments
- `issues: write` - To update PR status

Without proper permissions, the action will fail to post review comments on your pull requests.

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
