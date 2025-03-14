# Nexlify: Your Intelligent AI Companion 🚀

![Nexlify Logo](assets/images/nexlify-logo.png)

**Nexlify** transforms how you interact with AI by bringing the world's most powerful language models to your fingertips through an elegant, unified interface. More than just an AI platform, Nexlify is your personal AI companion that adapts to your needs, learns from your interactions, and delivers exceptional results—all while being completely **free**.

Imagine having a team of specialized AI experts at your command: Google's cutting-edge Gemini models for creative thinking, Groq's lightning-fast inference for time-sensitive tasks, and OpenRouter's diverse ecosystem for specialized capabilities—all accessible through a single, beautifully designed application that lives right in your system tray.

Whether you're a developer seeking AI-powered code assistance, a writer looking for creative inspiration, a researcher needing up-to-date information, or simply curious about what modern AI can do, Nexlify provides a seamless experience that grows more valuable with every interaction. With features like conversation history, bookmarking, code enhancement, and web search capabilities, Nexlify isn't just an AI tool—it's an extension of your digital workspace that evolves alongside you.

> "Nexlify bridges the gap between powerful AI technology and everyday usability, making state-of-the-art language models accessible to everyone."

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

| Icon | Feature                     | Description                                                   |
| ---- | --------------------------- | ------------------------------------------------------------- |
| 🔄   | **Unified Interface**       | Access multiple AI models through a single, elegant interface |
| 🌐   | **Online Search**           | Get up-to-date information from the web                       |
| 💾   | **Conversation History**    | Automatically save and revisit past interactions              |
| ⚡   | **Uptime Optimization**     | Ensure maximum availability with intelligent routing          |
| 📝   | **Prompt Templates**        | Create and reuse your favorite prompts                        |
| 🔖   | **Bookmarks System**        | Save important AI responses for quick access                  |
| 💻   | **Code Enhancement**        | Beautiful syntax highlighting and easy copying                |
| 🔌   | **System Tray Integration** | Quick access without desktop clutter                          |
| 🔄   | **Multi-Provider Support**  | Google, Groq, and OpenRouter integration                      |
| 🆓   | **Free to Use**             | Powerful AI capabilities at no cost                           |

Nexlify combines these powerful features into a seamless experience that adapts to your workflow. Whether you're coding, writing, researching, or exploring AI capabilities, Nexlify provides the tools you need to be more productive and creative.

![Demo Thumbnail](assets/images/demo-thumbnail.png)
_Example of Nexlify in action_

## Models Powering Nexlify 🧠

### 🌟 Google AI Models

| Model                         | Description                                                                                               | Best For                                                                    |
| ----------------------------- | --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------- |
| **Gemini 2.0 Flash Thinking** | An experimental version designed for rapid thinking and response generation with cutting-edge performance | Creative brainstorming, experimental workflows, quick insights              |
| **Gemini 2.0 Flash Lite**     | A lightweight version optimized for speed and resource efficiency                                         | Mobile applications, real-time responses, resource-constrained environments |

### ⚡ Groq Models

| Model                    | Description                                                                                | Best For                                                                            |
| ------------------------ | ------------------------------------------------------------------------------------------ | ----------------------------------------------------------------------------------- |
| **Deepseek R1 Qwen 32B** | Powerful combination of Deepseek R1 architecture and Qwen 32B model with exceptional speed | High-throughput applications, real-time content generation, complex reasoning tasks |

### 🔄 OpenRouter Models

| Model                | Description                                                                      | Best For                                                                   |
| -------------------- | -------------------------------------------------------------------------------- | -------------------------------------------------------------------------- |
| **Mistral R1**       | Based on the Mistral architecture, known for balanced performance and efficiency | General-purpose tasks, creative content, conversational AI                 |
| **Llama 3.3 70B**    | A massive 70B parameter model from Meta's Llama 3 family                         | Complex reasoning, in-depth analysis, sophisticated language tasks         |
| **Deepseek R1 671B** | A very large-scale Reasoning model with significant capabilities                 | Research tasks, cutting-edge experiments, maximum model capacity needs     |
| **Deepseek V3**      | The latest iteration in the Deepseek series with advanced architecture           | State-of-the-art applications, latest model technology                     |
| **QwQ 32B**          | A 32B parameter model from the Qwen series with strong performance               | Wide range of general AI tasks, content generation, versatile applications |

_All OpenRouter models support online search and uptime optimization features_

_Nexlify is committed to continuously expanding its model offerings. Stay tuned for more integrations!_

## Advanced Features 🔍

### 🌐 Online Search Capability

Get real-time information from the web through your AI interactions

<details>
  <summary><b>Learn More</b></summary>

- **Enabled by Default:** Online search is enabled by default for all OpenRouter models.
- **Toggle with Command:** Use the `/online` command to toggle this feature on/off.
- **Implementation:** When enabled, ":online" is appended to the model name in OpenRouter API requests.
- **Use Cases:** Current events, recent developments, fact-checking, and research queries.
</details>

### ⚡ Uptime Optimization

Ensure maximum availability with intelligent routing between providers

<details>
  <summary><b>Learn More</b></summary>

- **How It Works:** OpenRouter continuously monitors the health and availability of AI providers, tracking response times, error rates, and availability across all providers in real-time.
- **Automatic Fallback:** When enabled, if the primary provider is down or experiencing issues, requests are automatically routed to alternative providers.
- **Enabled by Default:** Uptime optimization is enabled by default for all OpenRouter models.
- **Toggle with Command:** Use the `/uptime` command to toggle this feature on/off.
- **Implementation:** When enabled, the "route": "fallback" parameter is added to OpenRouter API requests.
</details>

### 💾 Conversation History

Never lose an important conversation again

<details>
  <summary><b>Learn More</b></summary>

- **Automatic Saving:** Every conversation is automatically saved with timestamps and model information.
- **History Browser:** Access your conversation history through the history button in the interface.
- **Load Past Conversations:** Easily load any previous conversation to review or continue where you left off.
- **Delete History:** Remove unwanted conversation records to maintain privacy and organization.
- **Metadata Tracking:** Each saved conversation includes details like the model used, timestamp, and message count.
- **File-Based Storage:** Conversations are stored as JSON files in the "history" folder, making them easy to back up or transfer.
</details>

### 💻 Code Block Enhancement

Beautiful syntax highlighting and convenient functionality for developers

<details>
  <summary><b>Learn More</b></summary>

- **Syntax Highlighting:** Automatic language detection and syntax highlighting for over 20 programming languages.
- **Copy Button:** One-click copying of code blocks to your clipboard.
- **Language Identification:** Automatic identification of programming languages based on code content.
- **Visual Distinction:** Code blocks are visually distinct from regular text, making them easy to identify.
- **Scrollable Blocks:** Long code snippets are contained in scrollable blocks to maintain a clean interface.
- **Monospace Formatting:** Code is displayed in monospace font for proper alignment and readability.
</details>

### 🔖 Bookmarks System

Build your personal knowledge base of valuable AI responses

<details>
  <summary><b>Learn More</b></summary>

- **Quick Bookmarking:** Use the `/mark` command to bookmark the last AI response.
- **Bookmark Browser:** View all your bookmarks with the `/bookmark` command.
- **Persistent Storage:** Bookmarks are saved between sessions for long-term reference.
- **Delete Functionality:** Remove unwanted bookmarks to keep your collection organized.
- **Model Tracking:** Each bookmark records which model generated the response.
- **Direct Insertion:** Insert bookmarked content directly into the chat with a single click.
</details>

### 📝 Prompt Templates

Create and manage reusable prompts for consistent results

<details>
  <summary><b>Learn More</b></summary>

- **Save Templates:** Use the `/save [name]` command to save the current prompt as a template.
- **Browse Templates:** Access your saved templates with the `/prompts` command.
- **Quick Insertion:** Insert any template into the input field with a single click.
- **Delete Option:** Remove templates you no longer need.
- **Persistent Storage:** Templates are saved between sessions for long-term use.
- **Organization:** Keep your frequently used prompts organized and readily available.
</details>

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

![Dashboard Screenshot](assets/images/dashboard-screenshot.png)

## Credits 🙏

Nexlify was developed with passion and dedication by **dev-sufyaan**. All credit and gratitude are due to **Allah SWT**.

## Third-party Services 🤝

Nexlify leverages the following exceptional third-party services to deliver its powerful AI capabilities:

- **Google Cloud**: Provides access to cutting-edge API services, including the Gemini family of models.
- **Groq**: Offers high-performance inference infrastructure, enabling incredibly fast AI responses.
- **OpenRouter**: Acts as a versatile LLM routing service, providing access to a diverse range of models from various providers.

---

Thank you for exploring Nexlify! We hope you find it a valuable tool in your AI journey. If you have any questions, feedback, or contributions, please feel free to reach out. Happy AI innovating!
