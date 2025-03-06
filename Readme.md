# Nexlify: Your Unified AI Gateway 🚀

[![Nexlify Logo](assets/images/nexlify-logo.png)](/)

**Nexlify** is an advanced AI integration platform designed to simplify your access to the world of language models. Imagine a single, streamlined API that unlocks the power of multiple state-of-the-art AI models, all for **free**. Nexlify provides enterprise-grade infrastructure, making it incredibly easy to deploy cutting-edge AI in your production environments. Whether you're leveraging the robust Google API, the blazing-fast Groq infrastructure, or the diverse ecosystem of OpenRouter, Nexlify is your intelligent gateway to the future of AI.

## Table of Contents

1.  [Features ✨](#features-)
2.  [Models Powering Nexlify 🧠](#models-powering-nexlify-)

3.  [Usage 🛠️](#usage-️)
    - [Google API Integration](#google-api-integration)
    - [Groq Implementation](#groq-implementation)
    - [OpenRouter Configuration](#openrouter-configuration)
4.  [Credits 🙏](#credits-)
5.  [Third-party Services 🤝](#third-party-services-)

## Features ✨

- **Unified API Access:** Say goodbye to juggling multiple APIs! Nexlify provides a single, consistent interface to interact with various leading language models.
- **Free to Use:** Access powerful AI capabilities without breaking the bank. Nexlify is committed to providing a free and open platform for AI innovation.
- **Enterprise-Grade Infrastructure:** Built for reliability and scalability, ensuring your AI applications perform flawlessly in production.
- **Multi-Provider Integration:** Seamlessly integrates with Google API, Groq, and OpenRouter, giving you access to a wide range of models and capabilities.
- **Quick and Portable:** Nexlify is designed for rapid deployment and easy setup. Get your AI projects up and running in minutes, regardless of your environment.
- **Versatile Model Selection:** Choose the perfect AI model for your specific task from a curated list of high-performance options. Experiment with different models to find the optimal balance of speed, cost, and quality.
- **Intelligent Routing (Implicit):** While not explicitly a routing feature you configure, Nexlify allows you to _implicitly_ route your requests by selecting different models, effectively choosing the best engine for your current need. This promotes intelligent and flexible AI usage.
- **Constantly Evolving:** Nexlify is continuously being updated with new models, features, and improvements to stay at the forefront of AI innovation.

[![Demo Thumbnail](assets/images/demo-thumbnail.png)](/)
_Example of Nexlify in action_

## Models Powering Nexlify 🧠

Nexlify harnesses the power of a diverse selection of cutting-edge language models to provide you with the best possible AI experience. Here's a breakdown of the models currently integrated:

| Model Name                         | Provider   | Description                                                                                                                                                                                                         | Ideal Use Cases                                                                                                                                                                                                          |
| :--------------------------------- | :--------- | :------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gemini 2.0 Flash thinking Exp.** | Google API | An experimental version of Gemini 2.0 Flash, designed for rapid thinking and response generation. Expect cutting-edge performance with a focus on speed and innovation.                                             | Tasks requiring quick insights, experimental AI workflows, and exploring the latest advancements from Google AI.                                                                                                         |
| **Gemini 2.0 Flash lite**          | Google API | A lightweight and efficient version of Gemini 2.0 Flash, optimized for speed and resource efficiency. Ideal for applications where latency and cost are critical.                                                   | Real-time applications, mobile integrations, scenarios with limited computational resources, and cost-sensitive projects.                                                                                                |
| **Deepseek R1 Qwen 32B - Groq**    | Groq       | A powerful combination of Deepseek R1 architecture and the Qwen 32B model, accelerated by Groq's high-performance inference infrastructure. Delivers exceptional speed and quality, especially for demanding tasks. | High-throughput applications, real-time content generation, complex reasoning tasks where speed and accuracy are paramount, and leveraging Groq's unparalleled inference speed.                                          |
| **Mistral R1**                     | OpenRouter | Based on the Mistral architecture, known for its balanced performance and efficiency. Offers a strong combination of speed, quality, and cost-effectiveness through the OpenRouter platform.                        | General-purpose AI tasks, creative content generation, conversational AI, and applications seeking a balance between performance and cost.                                                                               |
| **Llama 3.3 70B**                  | OpenRouter | A massive 70 billion parameter model from Meta's Llama 3 family. Provides state-of-the-art performance for complex tasks and nuanced understanding. Accessible via OpenRouter for flexible integration.             | Highly complex reasoning, in-depth analysis, sophisticated language tasks, applications requiring the highest level of language understanding and generation, and pushing the boundaries of AI capabilities.             |
| **Deepseek R1 671B**               | OpenRouter | A very large-scale Reasoning model, part of the Deepseek R1 series. Offers significant capabilities for advanced AI tasks through OpenRouter.                                                                       | Demanding research tasks, cutting-edge AI experiments, exploring the potential of extremely large models 671B, and scenarios where maximum model capacity is desired.                                                    |
| **Deepseek V3**                    | OpenRouter | The latest iteration in the Deepseek series, representing advanced advancements in model architecture and performance. Available through OpenRouter for versatile applications.                                     | State-of-the-art AI applications, tasks requiring the most current model technology, exploring the cutting edge of Deepseek's model development, and scenarios demanding peak performance and the latest AI innovations. |
| **QwQ 32B**                        | OpenRouter | A 32 billion parameter model from the Qwen series, known for its strong performance in various language tasks. Integrated via OpenRouter for broad accessibility and utility.                                       | Wide range of general AI tasks, content generation, conversational agents, applications seeking robust performance and a versatile model for diverse language-related needs.                                             |

_Nexlify is committed to continuously expanding its model offerings. Stay tuned for more integrations!_

## Usage 🛠️

To start using Nexlify, you'll need to configure API keys for the services you intend to use. Follow the steps below for each integration:

### Google API Integration

1.  **Obtain Google API credentials** from the [Google Cloud Console](https://console.cloud.google.com/). You'll need to create a project and enable the Generative Language API.
2.  **Add your API key to the `.env` file:**

    ```env
    GOOGLE_API_KEY=your_google_api_key_here
    ```

### Groq Implementation

1.  **Sign up for Groq access** at [groq.com](https://groq.com).
2.  **Add your Groq API key to the `.env` file:**

    ```env
    GROQ_API_KEY=your_groq_api_key_here
    ```

### OpenRouter Configuration

1.  **Create an account at [OpenRouter](https://openrouter.ai/)**.
2.  **Generate an API key** from your OpenRouter account.
3.  **Add your OpenRouter API key to the `.env` file:**

    ```env
    OPENROUTER_API_KEY=your_openrouter_api_key_here
    ```

**Running Nexlify:**

1.  **Ensure you have Python installed** (version 3.7 or higher is recommended).
2.  **Create a virtual environment** (optional but recommended):
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Linux/macOS
    .venv\Scripts\activate     # On Windows
    ```
3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
4.  **Run Nexlify:**
    ```bash
    python Nexlify.py
    ```
    Nexlify will start in your system tray. Click the system tray icon to open the application.

[![Dashboard Screenshot](assets/images/dashboard-screenshot.png)](/)

## Credits 🙏

Nexlify was developed with passion and dedication by **dev-sufyaan**. All credit and gratitude are due to **Allah SWT**.

## Third-party Services 🤝

Nexlify leverages the following exceptional third-party services to deliver its powerful AI capabilities:

- **Google Cloud**: Provides access to cutting-edge API services, including the Gemini family of models.
- **Groq**: Offers high-performance inference infrastructure, enabling incredibly fast AI responses.
- **OpenRouter**: Acts as a versatile LLM routing service, providing access to a diverse range of models from various providers.

---

Thank you for exploring Nexlify! We hope you find it a valuable tool in your AI journey. If you have any questions, feedback, or contributions, please feel free to reach out. Happy AI innovating!
