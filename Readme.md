# Nexlify: Your Unified AI Gateway 🚀

[![Nexlify Logo](assets/images/nexlify-logo.png)](/)

**Nexlify** is an advanced AI integration platform designed to simplify your access to the world of language models. Imagine a single, streamlined API that unlocks the power of multiple state-of-the-art AI models, all for **free**. Nexlify provides enterprise-grade infrastructure, making it incredibly easy to deploy cutting-edge AI in your production environments. Whether you're leveraging the robust Google API, the blazing-fast Groq infrastructure, or the diverse ecosystem of OpenRouter, Nexlify is your intelligent gateway to the future of AI.

## Table of Contents

1.  [Features ✨](#features-)
2.  [Models Powering Nexlify 🧠](#models-powering-nexlify-)
3.  [Advanced Features 🔍](#advanced-features-)
    - [Online Search Capability](#online-search-capability)
    - [Uptime Optimization](#uptime-optimization)
    - [Conversation History](#conversation-history)
    - [Code Block Enhancement](#code-block-enhancement)
    - [Bookmarks System](#bookmarks-system)
    - [Prompt Templates](#prompt-templates)
4.  [Usage 🛠️](#usage-️)
    - [Distribution](#distribution)
    - [Google API Integration](#google-api-integration)
    - [Groq Implementation](#groq-implementation)
    - [OpenRouter Configuration](#openrouter-configuration)
    - [Command Reference](#command-reference)
5.  [Credits 🙏](#credits-)
6.  [Third-party Services 🤝](#third-party-services-)

## Features ✨

- **Unified API Access:** Say goodbye to juggling multiple APIs! Nexlify provides a single, consistent interface to interact with various leading language models.
- **Free to Use:** Access powerful AI capabilities without breaking the bank. Nexlify is committed to providing a free and open platform for AI innovation.
- **Enterprise-Grade Infrastructure:** Built for reliability and scalability, ensuring your AI applications perform flawlessly in production.
- **Multi-Provider Integration:** Seamlessly integrates with Google API, Groq, and OpenRouter, giving you access to a wide range of models and capabilities.
- **Quick and Portable:** Nexlify is designed for rapid deployment and easy setup. Get your AI projects up and running in minutes, regardless of your environment.
- **Versatile Model Selection:** Choose the perfect AI model for your specific task from a curated list of high-performance options. Experiment with different models to find the optimal balance of speed, cost, and quality.
- **Intelligent Routing:** Nexlify allows you to route your requests by selecting different models, effectively choosing the best engine for your current need. This promotes intelligent and flexible AI usage.
- **Online Search Capability:** Enable models to search the web for up-to-date information, making them more useful for questions about current events or topics that require recent information.
- **Uptime Optimization:** Ensure maximum availability by leveraging OpenRouter's uptime optimization feature, which automatically routes requests to alternative providers if the primary provider is down.
- **Conversation History:** Automatically save and manage your chat history for future reference, with the ability to view, load, and delete past conversations.
- **Enhanced Code Blocks:** Beautiful syntax highlighting for code snippets with support for multiple programming languages and easy copy functionality.
- **Bookmarks System:** Save important AI responses for quick access later, allowing you to build a personal knowledge base of valuable information.
- **Prompt Templates:** Create and manage reusable prompt templates to streamline repetitive queries and maintain consistency in your interactions.
- **System Tray Integration:** Access Nexlify quickly from your system tray, keeping it readily available without cluttering your desktop.
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

## Advanced Features 🔍

### Online Search Capability

Nexlify's OpenRouter models come with built-in online search capability, allowing them to search the web for up-to-date information when responding to queries. This feature is particularly useful for questions about current events or topics that require recent information.

- **Enabled by Default:** Online search is enabled by default for all OpenRouter models.
- **Toggle with Command:** Use the `/online` command to toggle this feature on/off.
- **Implementation:** When enabled, ":online" is appended to the model name in OpenRouter API requests.

### Uptime Optimization

Nexlify leverages OpenRouter's uptime optimization feature to ensure maximum availability and reliability. This feature tracks provider health and makes intelligent routing decisions to maintain high uptime.

- **How It Works:** OpenRouter continuously monitors the health and availability of AI providers, tracking response times, error rates, and availability across all providers in real-time.
- **Automatic Fallback:** When enabled, if the primary provider is down or experiencing issues, requests are automatically routed to alternative providers.
- **Enabled by Default:** Uptime optimization is enabled by default for all OpenRouter models.
- **Toggle with Command:** Use the `/uptime` command to toggle this feature on/off.
- **Implementation:** When enabled, the "route": "fallback" parameter is added to OpenRouter API requests.

### Conversation History

Nexlify automatically saves your conversations, allowing you to revisit past interactions and continue discussions later.

- **Automatic Saving:** Every conversation is automatically saved with timestamps and model information.
- **History Browser:** Access your conversation history through the history button in the interface.
- **Load Past Conversations:** Easily load any previous conversation to review or continue where you left off.
- **Delete History:** Remove unwanted conversation records to maintain privacy and organization.
- **Metadata Tracking:** Each saved conversation includes details like the model used, timestamp, and message count.
- **File-Based Storage:** Conversations are stored as JSON files in the "history" folder, making them easy to back up or transfer.

### Code Block Enhancement

Nexlify features advanced code block handling with beautiful syntax highlighting and convenient functionality.

- **Syntax Highlighting:** Automatic language detection and syntax highlighting for over 20 programming languages.
- **Copy Button:** One-click copying of code blocks to your clipboard.
- **Language Identification:** Automatic identification of programming languages based on code content.
- **Visual Distinction:** Code blocks are visually distinct from regular text, making them easy to identify.
- **Scrollable Blocks:** Long code snippets are contained in scrollable blocks to maintain a clean interface.
- **Monospace Formatting:** Code is displayed in monospace font for proper alignment and readability.

### Bookmarks System

Save important AI responses for future reference with Nexlify's bookmark system.

- **Quick Bookmarking:** Use the `/mark` command to bookmark the last AI response.
- **Bookmark Browser:** View all your bookmarks with the `/bookmark` command.
- **Persistent Storage:** Bookmarks are saved between sessions for long-term reference.
- **Delete Functionality:** Remove unwanted bookmarks to keep your collection organized.
- **Model Tracking:** Each bookmark records which model generated the response.
- **Direct Insertion:** Insert bookmarked content directly into the chat with a single click.

### Prompt Templates

Create and manage reusable prompt templates to streamline your workflow.

- **Save Templates:** Use the `/save [name]` command to save the current prompt as a template.
- **Browse Templates:** Access your saved templates with the `/prompts` command.
- **Quick Insertion:** Insert any template into the input field with a single click.
- **Delete Option:** Remove templates you no longer need.
- **Persistent Storage:** Templates are saved between sessions for long-term use.
- **Organization:** Keep your frequently used prompts organized and readily available.

## Usage 🛠️

### Distribution

**Nexlify AppImage (Linux - Beta)**

For Linux users seeking a convenient, portable, and self-contained application, Nexlify is also available as an **AppImage** in beta testing.

- **Download:** You can find the Nexlify AppImage in the **"Releases"** section of our GitHub repository. Look for files named like `Nexlify-x86_64.AppImage` or similar.
- **Make Executable:** After downloading, you'll likely need to make the AppImage executable. You can do this in your terminal using:
  ```bash
  chmod +x Nexlify-x86_64.AppImage
  ```
  (Replace `Nexlify-x86_64.AppImage` with the actual filename you downloaded.)
- **Run:** Simply double-click the AppImage file to run Nexlify, or execute it from the terminal:
  ```bash
  ./Nexlify-x86_64.AppImage
  ```

**Important Note for AppImage Users:**

When using the Nexlify AppImage, it's crucial to understand how API keys are loaded. The AppImage is a single, packaged file. To ensure Nexlify can access your API keys, you **must place the `.env` file in the same directory where you have stored the Nexlify AppImage file.**

For example, if you download `Nexlify-x86_64.AppImage` and place it in your `Downloads` folder, your `.env` file (containing `GOOGLE_API_KEY`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`, etc.) must also be located in the `Downloads` folder alongside the AppImage. **Failing to place the `.env` file in the correct location will prevent Nexlify from accessing your API keys, and it will not function correctly.**

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

**Running Nexlify (from Source or Extracted ZIP):**

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

### Command Reference

Nexlify supports several slash commands that can be used in the chat interface:

| Command        | Description                        |
| :------------- | :--------------------------------- |
| `/help`        | Show available commands            |
| `/prompts`     | List or use saved prompt templates |
| `/save [name]` | Save current prompt as template    |
| `/bookmark`    | View saved bookmarks               |
| `/mark`        | Bookmark last AI response          |
| `/online`      | Toggle online search capability    |
| `/uptime`      | Toggle uptime optimization         |

To use a command, simply type it in the chat input field and press Enter.

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
