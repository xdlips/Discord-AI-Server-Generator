# Discord-AI-Server-Generator

Terminal app that builds Discord servers from natural language. Describe what you want, the AI asks follow-up questions, then creates all roles, categories, and channels automatically.

![Main Menu](assets/preview_menu.png)

## Features

- **AI-powered design** - Describe your server in plain text, the AI handles the rest
- **Edit existing servers** - Tell the AI what to change, it detects the diff and applies only what's needed
- **Rebuild from config** - Apply a saved configuration to any server
- **Export / Import** - Share configs as JSON or import ones from others
- **Full permission support** - All Discord permission flags including threads, voice, events, and soundboard
- **Correct role ordering** - Roles are placed at the right position in the Discord hierarchy automatically
- **User & bot token** - Works with both personal account tokens and bot tokens
- **English & Turkish UI** - Full interface translation

---

## Requirements

- Python 3.11 or higher
- [OpenRouter](https://openrouter.ai) API key
- Discord user token or bot token

---

## Installation

```bash
git clone https://github.com/xdlips/Discord-AI-Server-Generator
cd Discord-AI-Server-Generator
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and fill it in:

```env
OPENROUTER_API_KEY=sk-or-...
MODEL=openai/gpt-oss-120b:free
```

Run:

```bash
python main.py
```

---

## Recommended Model

```
openai/gpt-oss-120b:free
```

---

## Usage

### 1 - New server setup

Open **Setup** from the menu, enter your Discord token and server ID, then describe the server you want in plain text.

![Setup Screen](assets/preview_setup.png)

The AI will ask any necessary follow-up questions, then generate the full configuration. A summary (role count, channel count) is shown before anything is applied.

![Build Progress](assets/preview_build.png)

### 2 - Edit an existing server

Use **Edit** to select a previously built server or enter an ID directly. Describe what you want to change - add or remove channels, update permissions, rename roles - the AI calculates only the diff and applies it.

### 3 - Rebuild from a saved config

Use **Rebuild** to apply a previously saved configuration to the same server or a completely different one.

### 4 - Manage saved configs

![Saved Configs](assets/preview_configs.png)

View, export as JSON, import an existing JSON, or delete saved configurations.

---

## How to get a token

**User token (personal account):**
Open Discord in a browser → F12 DevTools → Network tab → refresh the page → click any request to `discord.com/api` → copy the `Authorization` header value.

**Bot token:**
Go to [discord.com/developers](https://discord.com/developers/applications) → create an application → add a Bot → copy the token. Make sure the bot is invited to your server with sufficient permissions.

> Warning: Never share your tokens. A user token gives full access to your account.

---

## How to get a server ID

Discord Settings → Advanced → enable Developer Mode. Right-click the server icon → **Copy Server ID**.

---

## License

MIT
