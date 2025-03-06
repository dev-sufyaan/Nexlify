# Nexlify

<p align="center">
  <img src="assets/images/nexlify-logo.png" alt="Nexlify Logo" width="200"/>
</p>

Nexlify is an advanced AI integration platform that streamlines access to multiple language models through a unified API for Free. It offers enterprise-grade infrastructure for deploying state-of-the-art AI models in production environments, with support for Google API, Groq, and OpenRouter integrations.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Google API Integration](#google-api-integration)
  - [Groq Implementation](#groq-implementation)
  - [OpenRouter Configuration](#openrouter-configuration)
- [Demo](#demo)
- [Contributing](#contributing)
- [License](#license)
- [Credits](#credits)

## Overview

Nexlify provides a streamlined interface for implementing multiple AI services into your industrial workflow. It simplifies the complex process of API integration for Google APIs, Groq models, and OpenRouter LLM routing services.

![Nexlify Dashboard](assets/images/dashboard-screenshot.png)

## Features

- **Google API Integration**: Seamless connection to Google Cloud services
- **Groq Models**: High-performance inferencing with Groq's accelerated models
- **OpenRouter Support**: Access to multiple language models through a single API
- **Industrial-Grade Security**: Enterprise-level data protection
- **Scalable Architecture**: Designed for high-volume industrial applications
- **Detailed Analytics**: Monitor usage and performance metrics

## Installation

```bash
# Clone the repository
git clone https://github.com/dev-sufyaan/Nexlify.git

# Navigate to the project directory
cd Nexlify

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
```

## Usage

### Google API Integration

1. Obtain Google API credentials from the [Google Cloud Console](https://console.cloud.google.com/)
2. Add your API key to the `.env` file:

```
GOOGLE_API_KEY=your_google_api_key_here
```

### Groq Implementation

1. Sign up for Groq access at [groq.com](https://groq.com)
2. Add your Groq API key to the `.env` file:

```
GROQ_API_KEY=your_groq_api_key_here
```

### OpenRouter Configuration

1. Create an account at [OpenRouter](https://openrouter.ai)
2. Generate an API key and add it to your `.env` file:

```
OPENROUTER_API_KEY=your_openrouter_api_key_here
```

## Demo

<p align="center">
  <a href="https://www.youtube.com/@Dev-Sufyaan">
    <img src="assets/images/demo-thumbnail.png" alt="Nexlify Demo Video" width="600"/>
  </a>
</p>

Watch our [demonstration video](https://www.youtube.com/@Dev-Sufyaan) to see Nexlify in action.

## Contributing

We welcome contributions to Nexlify! Please see our [contributing guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Credits

Nexlify was developed by [dev-sufyaan](https://github.com/dev-sufyaan).

### Third-party Services

- [Google Cloud](https://cloud.google.com/) - API services
- [Groq](https://groq.com/) - High-performance inference
- [OpenRouter](https://openrouter.ai/) - LLM routing services

---

<p align="center">
  <small>© 2025 Nexlify. All rights reserved.</small><br>
  <a href="https://github.com/dev-sufyaan/Nexlify">GitHub</a> |
  <a href="www.sufyaan.tech">Documentation</a> |
  <a href="mailto:dev-sufyaan@gmail.com">Contact</a>
</p>
