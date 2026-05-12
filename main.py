"""
AI Discord Server Setup
Developed by github.com/xdlips
"""

import copy
import json
import os
import re
import shutil
import sys
import time
from datetime import datetime

import requests
from dotenv import load_dotenv
from openai import OpenAI
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich import box

load_dotenv()

VERSION = "1.0.0"
AUTHOR_URL = "https://github.com/xdlips"
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SERVERS_DIR = os.path.join(SCRIPT_DIR, "servers")
SETTINGS_FILE = os.path.join(SCRIPT_DIR, ".settings.json")

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("MODEL", "anthropic/claude-sonnet-4-5")

console = Console()

STRINGS: dict[str, dict[str, str]] = {
    "en": {
        "subtitle": "AI-powered Discord server builder",
        "by": "Developed by",
        "version": "Version",
        "main_menu": "Main Menu",
        "opt_setup": "Setup",
        "opt_setup_desc": "Design and build a new server with AI",
        "opt_edit": "Edit",
        "opt_edit_desc": "Modify an existing server with AI",
        "opt_rebuild": "Rebuild",
        "opt_rebuild_desc": "Rebuild a server from a saved configuration",
        "opt_configs": "Saved Configs",
        "opt_configs_desc": "Browse and manage saved configurations",
        "opt_settings": "Settings",
        "opt_settings_desc": "Language, token type",
        "opt_exit": "Exit",
        "choose": "Choose",
        "user_token": "User account token",
        "bot_token": "Bot token",
        "select_token_type": "Select token type",
        "enter_token": "Paste your token",
        "enter_server_id": "Enter Server ID",
        "token_valid": "Token valid — logged in as",
        "token_invalid": "Invalid token",
        "server_found": "Server found",
        "server_not_found": "Server not found",
        "setup_title": "Server Setup",
        "setup_hint": "Describe the server you want. The AI will ask questions then build it.",
        "design_complete": "Design complete — config saved",
        "build_q": "Build the server now? (wipes all existing channels & roles)",
        "skip_hint": "Skipped. Use 'Rebuild' from the menu to apply later.",
        "setup_complete": "Server setup complete",
        "config_summary": "Configuration Summary",
        "summary_roles": "Roles",
        "summary_cats": "Categories",
        "summary_channels": "Channels",
        "edit_title": "Edit Server",
        "edit_hint": "Describe what you want to change. The AI will apply it.",
        "select_server": "Select a server or enter its ID directly",
        "changes_ready": "Changes ready",
        "apply_q": "Apply changes?",
        "edit_complete": "Changes applied successfully",
        "continue_editing": "Continue editing or Ctrl+C to return to menu.",
        "rebuild_title": "Rebuild from Saved Config",
        "rebuild_select": "Select a saved configuration",
        "rebuild_id_hint": "Server ID to build into (blank = use saved ID)",
        "rebuild_q": "Rebuild the server? (wipes all existing channels & roles)",
        "rebuild_complete": "Server rebuilt successfully",
        "configs_title": "Saved Configurations",
        "no_configs": "No saved configurations found.",
        "cols_name": "Server Name",
        "cols_id": "Server ID",
        "cols_updated": "Last Updated",
        "cols_channels": "Channels",
        "cols_roles": "Roles",
        "config_actions": "Actions: [V] View  [E] Export  [I] Import  [D] Delete  [B] Back",
        "view_config": "View",
        "delete_config": "Delete",
        "delete_q": "Delete this configuration? This cannot be undone.",
        "config_deleted": "Configuration deleted",
        "config_not_found": "Configuration not found",
        "config_detail": "Configuration Detail",
        "export_success": "Exported successfully",
        "import_path": "Path to JSON config file",
        "import_name": "Server name for this config",
        "import_id": "Server ID (for labeling, can be changed later)",
        "import_success": "Config imported successfully",
        "import_error": "Invalid config file — must contain 'roles' key",
        "file_not_found": "File not found",
        "settings_title": "Settings",
        "lang_current": "Language",
        "token_pref": "Preferred token type",
        "settings_saved": "Settings saved",
        "back": "Back",
        "cancel": "Cancelled",
        "invalid": "Invalid selection, try again",
        "thinking": "Thinking...",
        "continuing": "Continuing...",
        "you": "You",
        "ai_label": "AI",
        "aborted": "Aborted",
        "wipe_warn": "Starting in 5 seconds — press Ctrl+C to abort",
        "confirm_y": "[y/N]",
        "empty_input": "Input cannot be empty",
        "incomplete": "Response incomplete, requesting continuation",
        "api_error": "API error",
        "empty_resp": "Empty API response — verify MODEL= in .env is a valid OpenRouter model ID. Current model",
        "missing_key": "OPENROUTER_API_KEY missing in .env",
        "missing_model": "MODEL missing in .env — set a valid OpenRouter model ID",
        "press_enter": "Press Enter to continue...",
    },
    "tr": {
        "subtitle": "Yapay zeka destekli Discord sunucu kurucusu",
        "by": "Geliştiren",
        "version": "Sürüm",
        "main_menu": "Ana Menü",
        "opt_setup": "Kurulum",
        "opt_setup_desc": "Yapay zeka ile yeni bir sunucu tasarla ve kur",
        "opt_edit": "Düzenle",
        "opt_edit_desc": "Mevcut bir sunucuyu yapay zeka ile düzenle",
        "opt_rebuild": "Yeniden Kur",
        "opt_rebuild_desc": "Kayıtlı bir yapılandırmadan sunucuyu yeniden kur",
        "opt_configs": "Kayıtlı Yapılandırmalar",
        "opt_configs_desc": "Kayıtlı yapılandırmaları görüntüle ve yönet",
        "opt_settings": "Ayarlar",
        "opt_settings_desc": "Dil, token türü",
        "opt_exit": "Çıkış",
        "choose": "Seçim",
        "user_token": "Kullanıcı hesabı tokeni",
        "bot_token": "Bot tokeni",
        "select_token_type": "Token türünü seçin",
        "enter_token": "Tokeninizi yapıştırın",
        "enter_server_id": "Sunucu ID girin",
        "token_valid": "Token geçerli — giriş yapıldı",
        "token_invalid": "Geçersiz token",
        "server_found": "Sunucu bulundu",
        "server_not_found": "Sunucu bulunamadı",
        "setup_title": "Sunucu Kurulumu",
        "setup_hint": "Sunucunuzu tarif edin. Yapay zeka soru sorup kuracak.",
        "design_complete": "Tasarım tamamlandı — yapılandırma kaydedildi",
        "build_q": "Sunucuyu şimdi kur? (mevcut tüm kanallar ve roller silinecek)",
        "skip_hint": "Atlandı. Sonra menüden 'Yeniden Kur' ile uygulayabilirsin.",
        "setup_complete": "Sunucu kurulumu tamamlandı",
        "config_summary": "Yapılandırma Özeti",
        "summary_roles": "Rol",
        "summary_cats": "Kategori",
        "summary_channels": "Kanal",
        "edit_title": "Sunucu Düzenleme",
        "edit_hint": "Ne değiştirmek istediğinizi açıklayın. Yapay zeka uygulayacak.",
        "select_server": "Bir sunucu seçin veya ID'sini direkt girin",
        "changes_ready": "Değişiklikler hazır",
        "apply_q": "Değişiklikler uygulanacak?",
        "edit_complete": "Değişiklikler başarıyla uygulandı",
        "continue_editing": "Düzenlemeye devam edin veya menüye dönmek için Ctrl+C.",
        "rebuild_title": "Kayıtlı Yapılandırmadan Yeniden Kur",
        "rebuild_select": "Bir yapılandırma seçin",
        "rebuild_id_hint": "Kurulacak sunucu ID (boş = kayıtlı ID kullanılır)",
        "rebuild_q": "Sunucuyu yeniden kur? (mevcut her şey silinecek)",
        "rebuild_complete": "Sunucu başarıyla yeniden kuruldu",
        "configs_title": "Kayıtlı Yapılandırmalar",
        "no_configs": "Kayıtlı yapılandırma bulunamadı.",
        "cols_name": "Sunucu Adı",
        "cols_id": "Sunucu ID",
        "cols_updated": "Son Güncelleme",
        "cols_channels": "Kanal",
        "cols_roles": "Rol",
        "config_actions": "İşlemler: [V] Görüntüle  [E] Dışa Aktar  [I] İçe Aktar  [D] Sil  [B] Geri",
        "view_config": "Görüntüle",
        "delete_config": "Sil",
        "delete_q": "Bu yapılandırma silinecek. Geri alınamaz.",
        "config_deleted": "Yapılandırma silindi",
        "config_not_found": "Yapılandırma bulunamadı",
        "config_detail": "Yapılandırma Detayı",
        "export_success": "Başarıyla dışa aktarıldı",
        "import_path": "JSON config dosyasının yolu",
        "import_name": "Bu yapılandırma için sunucu adı",
        "import_id": "Sunucu ID (etiketleme için, sonra değiştirilebilir)",
        "import_success": "Yapılandırma başarıyla içe aktarıldı",
        "import_error": "Geçersiz config dosyası — 'roles' anahtarı eksik",
        "file_not_found": "Dosya bulunamadı",
        "settings_title": "Ayarlar",
        "lang_current": "Dil",
        "token_pref": "Tercih edilen token türü",
        "settings_saved": "Ayarlar kaydedildi",
        "back": "Geri",
        "cancel": "İptal",
        "invalid": "Geçersiz seçim, tekrar deneyin",
        "thinking": "Düşünüyor...",
        "continuing": "Devam ediyor...",
        "you": "Sen",
        "ai_label": "Yapay Zeka",
        "aborted": "İptal edildi",
        "wipe_warn": "5 saniye içinde başlıyor — durdurmak için Ctrl+C",
        "confirm_y": "[e/H]",
        "empty_input": "Boş bırakılamaz",
        "incomplete": "Cevap eksik, devam isteniyor",
        "api_error": "API hatası",
        "empty_resp": "Boş API yanıtı — .env'deki MODEL= geçerli bir OpenRouter model ID'si mi kontrol edin. Mevcut model",
        "missing_key": ".env dosyasında OPENROUTER_API_KEY eksik",
        "missing_model": ".env dosyasında MODEL eksik — geçerli bir OpenRouter model ID'si girin",
        "press_enter": "Devam etmek için Enter'a basın...",
    },
}

_settings: dict = {}


def load_settings() -> dict:
    global _settings
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, encoding="utf-8") as f:
                _settings = json.load(f)
        except Exception:
            _settings = {}
    _settings.setdefault("language", "en")
    _settings.setdefault("token_type", "user")
    return _settings


def save_settings():
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump(_settings, f, indent=2)


def t(key: str) -> str:
    lang = _settings.get("language", "en")
    return STRINGS.get(lang, STRINGS["en"]).get(key, key)


def current_model() -> str:
    return MODEL



# system prompts

SETUP_SYSTEM_PROMPT = """\
You are an expert Discord server architect. Your job is to design a complete, \
production-ready Discord server structure through a conversation with the user.

DISCOVERY PHASE
If the user's first message already covers roles, categories, channels, permissions,
and language in sufficient detail, skip questions and go directly to OUTPUT PHASE.
Only ask follow-up questions when critical information is genuinely missing.
Ask at most 2-3 targeted questions at a time.

OUTPUT PHASE
Once you have all necessary information output the complete configuration.
Signal readiness by writing exactly this marker on its own line:

READY_TO_BUILD
```json
{ ... }
```

STRICT JSON SCHEMA — follow exactly:

{
  "roles": [
    {
      "name": "string",
      "color": "#RRGGBB",
      "hoist": true,
      "mentionable": true,
      "permissions": ["administrator"]
    }
  ],
  "categories": [
    {
      "name": "STRING",
      "role_overrides": {
        "@everyone": { "view_channel": true, "send_messages": false }
      },
      "channels": [
        {
          "name": "channel-name",
          "type": "text",
          "topic": "Channel description",
          "slowmode": 0,
          "nsfw": false,
          "user_limit": null,
          "bitrate": null,
          "forum_tags": [],
          "role_overrides": {}
        }
      ]
    }
  ]
}

TYPE VALUES: "text" | "voice" | "announcement" | "forum" | "stage"
OVERWRITE VALUES: true (allow), false (deny), null (inherit)
CHANNEL NAMES: lowercase-with-hyphens for text/forum/announcement; Title Case for voice/stage
CATEGORIES: UPPERCASE recommended
"""

EDIT_SYSTEM_PROMPT = """\
You are an expert Discord server editor. You will help modify an existing Discord server.

SERVER: {server_name}

CURRENT ROLES:
{roles_list}

CURRENT CATEGORIES AND CHANNELS:
{channels_list}

ORIGINAL SETUP DESCRIPTION:
{original_prompt}

EDIT PHASE
If the user's message clearly describes what to change, go directly to output.
Otherwise ask 1-2 focused clarifying questions.

OUTPUT PHASE
When ready, output the change set using this marker:

READY_TO_APPLY
```json
{{
  "action": "edit",
  "roles_to_add": [],
  "roles_to_delete": [],
  "roles_to_edit": [],
  "categories_to_add": [],
  "categories_to_delete": [],
  "channels_to_add": [],
  "channels_to_delete": [],
  "channels_to_edit": []
}}
```

SCHEMAS:
roles_to_add       — {{"name","color","hoist","mentionable","permissions":[]}}
roles_to_delete    — ["Role Name"]
roles_to_edit      — [{{"name":"Existing Role","fields":{{"color":"#AABBCC"}}}}]
categories_to_add  — same as setup category (includes channels array)
categories_to_delete — ["CATEGORY NAME"]
channels_to_add    — [{{"category_name":"CAT NAME","channel":{{...}}}}]
channels_to_delete — ["channel-name"]
channels_to_edit   — [{{"name":"channel-name","fields":{{"topic":"new","slowmode":5}}}}]

RULES:
- Only include items that actually change; empty arrays can be omitted
- Use exact names as shown in the current state
- Deleting a category also deletes its channels
"""


# openrouter / ai


def get_ai_client() -> OpenAI:
    return OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")


def ai_chat(client: OpenAI, messages: list) -> tuple[str, bool]:
    resp = client.chat.completions.create(
        model=current_model(),
        messages=messages,
        max_tokens=16000,
    )
    if not resp.choices:
        return "", False
    choice = resp.choices[0]
    return choice.message.content or "", choice.finish_reason == "length"


def ai_continue_json(client: OpenAI, messages: list, partial: str) -> str:
    tail = partial[-2500:] if len(partial) > 2500 else partial
    cont = messages + [
        {"role": "assistant", "content": tail},
        {"role": "user", "content": (
            "Your JSON response was cut off. Continue from the exact character where it stopped. "
            "Output ONLY the raw JSON continuation — no markdown fences, no explanation, no preamble. "
            "Do not repeat any part already written."
        )},
    ]
    content, _ = ai_chat(client, cont)
    return content



# json extraction


def _fix_json_text(raw: str) -> str:
    result, in_str, escaped = [], False, False
    for ch in raw:
        if escaped:
            result.append(ch); escaped = False
        elif ch == "\\" and in_str:
            result.append(ch); escaped = True
        elif ch == '"':
            in_str = not in_str; result.append(ch)
        elif ch == "\n" and in_str:
            result.append("\\n")
        else:
            result.append(ch)
    return "".join(result)


def _try_parse(raw: str, require_key: str | None = None) -> dict | None:
    for text in (raw, _fix_json_text(raw)):
        try:
            data = json.loads(text)
            if isinstance(data, dict):
                if require_key and require_key not in data:
                    continue
                return data
        except (json.JSONDecodeError, ValueError):
            pass
    return None


def _extract_json_blob(text: str, require_key: str | None = None) -> dict | None:
    for pat in (r"```json\s*(.*?)\s*```", r"```\s*(.*?)\s*```"):
        m = re.search(pat, text, re.DOTALL)
        if m:
            r = _try_parse(m.group(1), require_key)
            if r:
                return r

    start = text.find("{")
    if start != -1:
        depth = end = 0
        for i, ch in enumerate(text[start:], start):
            if ch == "{": depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    end = i + 1
                    break
        if end:
            r = _try_parse(text[start:end], require_key)
            if r:
                return r
    return None


def extract_config(text: str) -> dict | None:
    return _extract_json_blob(text, require_key="roles")


def extract_changeset(text: str) -> dict | None:
    data = _extract_json_blob(text)
    if data and data.get("action") == "edit":
        return data
    return None


def _complete_json(ai: OpenAI, messages: list, reply: str,
                   extractor, marker: str) -> tuple[str, dict | None]:
    if marker not in reply and "```json" not in reply:
        return reply, None
    accumulated = reply
    for attempt in range(10):
        result = extractor(accumulated)
        if result:
            return accumulated, result
        console.print(f"  [dim]{t('incomplete')} ({attempt+1}/10)...[/dim]")
        with console.status(f"[dim]{t('continuing')}[/dim]", spinner="dots"):
            try:
                cont = ai_continue_json(ai, messages, accumulated)
            except Exception:
                break
        if not cont:
            break
        accumulated += cont
    return accumulated, extractor(accumulated)



# discord api

DISCORD_API = "https://discord.com/api/v10"

PERM_BITS: dict[str, int] = {
    "create_instant_invite": 1 << 0,
    "kick_members": 1 << 1,
    "ban_members": 1 << 2,
    "administrator": 1 << 3,
    "manage_channels": 1 << 4,
    "manage_guild": 1 << 5,
    "add_reactions": 1 << 6,
    "view_audit_log": 1 << 7,
    "priority_speaker": 1 << 8,
    "stream": 1 << 9,
    "view_channel": 1 << 10,
    "send_messages": 1 << 11,
    "send_tts_messages": 1 << 12,
    "manage_messages": 1 << 13,
    "embed_links": 1 << 14,
    "attach_files": 1 << 15,
    "read_message_history": 1 << 16,
    "mention_everyone": 1 << 17,
    "use_external_emojis": 1 << 18,
    "view_guild_insights": 1 << 19,
    "connect": 1 << 20,
    "speak": 1 << 21,
    "mute_members": 1 << 22,
    "deafen_members": 1 << 23,
    "move_members": 1 << 24,
    "use_voice_activation": 1 << 25,
    "change_nickname": 1 << 26,
    "manage_nicknames": 1 << 27,
    "manage_roles": 1 << 28,
    "manage_webhooks": 1 << 29,
    "manage_emojis_and_stickers": 1 << 30,
    "use_application_commands": 1 << 31,
    "request_to_speak": 1 << 32,
    "manage_events": 1 << 33,
    "manage_threads": 1 << 34,
    "create_public_threads": 1 << 35,
    "create_private_threads": 1 << 36,
    "use_external_stickers": 1 << 37,
    "send_messages_in_threads": 1 << 38,
    "use_embedded_activities": 1 << 39,
    "moderate_members": 1 << 40,
    "view_creator_monetization_analytics": 1 << 41,
    "use_soundboard": 1 << 42,
    "create_guild_expressions": 1 << 43,
    "create_events": 1 << 44,
    "use_external_sounds": 1 << 45,
    "send_voice_messages": 1 << 46,
    "set_voice_channel_status": 1 << 48,
    # aliases
    "read_messages": 1 << 10,
    "use_vad": 1 << 25,
}

CHANNEL_TYPES = {"text": 0, "voice": 2, "category": 4,
                 "announcement": 5, "stage": 13, "forum": 15}


class DiscordClient:
    def __init__(self, token: str, is_bot: bool = False):
        prefix = "Bot " if is_bot else ""
        self.headers = {
            "Authorization": f"{prefix}{token}",
            "Content-Type": "application/json",
        }

    def _req(self, method: str, path: str, data: dict | list | None = None):
        url = f"{DISCORD_API}{path}"
        for _ in range(5):
            resp = requests.request(method, url, headers=self.headers, json=data)
            if resp.status_code == 429:
                wait = float(resp.json().get("retry_after", 1.0))
                console.print(f"  [dim]Rate limited — waiting {wait:.1f}s[/dim]")
                time.sleep(wait)
                continue
            return resp
        return resp

    def get(self, p):
        return self._req("GET", p)

    def post(self, p, d=None):
        return self._req("POST", p, d)

    def patch(self, p, d=None):
        return self._req("PATCH", p, d)

    def delete(self, p):
        return self._req("DELETE", p)

    def perms_to_bits(self, lst: list) -> str:
        bits = 0
        for p in lst:
            bits |= PERM_BITS.get(p, 0)
        return str(bits)

    def overrides_to_list(self, overrides: dict, role_map: dict, guild_id: str) -> list:
        result = []
        for name, perms in overrides.items():
            rid = guild_id if name == "@everyone" else role_map.get(name)
            if not rid:
                continue
            allow = deny = 0
            for k, v in perms.items():
                bit = PERM_BITS.get(k, 0)
                if v is True:    allow |= bit
                elif v is False: deny  |= bit
            result.append({"id": rid, "type": 0, "allow": str(allow), "deny": str(deny)})
        return result

    def fetch_state(self, guild_id: str) -> dict:
        ch = self.get(f"/guilds/{guild_id}/channels").json()
        ro = self.get(f"/guilds/{guild_id}/roles").json()
        return {
            "channels": ch if isinstance(ch, list) else [],
            "roles":    ro if isinstance(ro, list) else [],
        }

    def whoami(self) -> dict | None:
        r = self.get("/users/@me")
        return r.json() if r.status_code == 200 else None

    def get_guild(self, guild_id: str) -> dict | None:
        r = self.get(f"/guilds/{guild_id}")
        return r.json() if r.status_code == 200 else None


def _connect(token: str, is_bot: bool, guild_id: str) -> tuple[DiscordClient, str] | None:
    api = DiscordClient(token, is_bot)
    me = api.whoami()
    if not me:
        console.print(f"  [red]{t('token_invalid')}[/red]")
        return None
    console.print(f"  {t('token_valid')}: [bold]{me.get('username')}[/bold]")
    guild = api.get_guild(guild_id)
    if not guild:
        console.print(f"  [red]{t('server_not_found')}[/red]")
        return None
    console.print(f"  {t('server_found')}: [bold]{guild.get('name')}[/bold]")
    return api, guild.get("name", guild_id)



# discord executor


def _create_channel(api: DiscordClient, guild_id: str, ch: dict,
                    cat_id: str, fallback_ow: list, role_map: dict):
    ch_type = ch.get("type", "text")
    ow = (api.overrides_to_list(ch["role_overrides"], role_map, guild_id)
          if ch.get("role_overrides") is not None else fallback_ow)
    p: dict = {
        "name": ch["name"],
        "type": CHANNEL_TYPES.get(ch_type, 0),
        "parent_id": cat_id,
        "permission_overwrites": ow,
    }
    if ch_type in ("text", "announcement"):
        p["topic"] = ch.get("topic", "")
        p["rate_limit_per_user"] = ch.get("slowmode") or 0
        p["nsfw"] = ch.get("nsfw", False)
    elif ch_type == "voice":
        p["bitrate"] = ch.get("bitrate") or 64000
        p["user_limit"] = ch.get("user_limit") or 0
    elif ch_type == "stage":
        p["topic"] = ch.get("topic", "")
    elif ch_type == "forum":
        p["topic"] = ch.get("topic", "")
        p["available_tags"] = [{"name": tg, "moderated": False}
                               for tg in ch.get("forum_tags", [])]
    resp = api.post(f"/guilds/{guild_id}/channels", p)
    if resp.status_code in (200, 201):
        console.print(f"    + {ch['name']}  [{ch_type}]")
    else:
        console.print(f"    [red]x {ch['name']}: {resp.status_code}[/red]")
    time.sleep(0.3)


def wipe_guild(api: DiscordClient, guild_id: str):
    console.print("[dim]  Removing existing channels...[/dim]")
    for ch in api.get(f"/guilds/{guild_id}/channels").json() or []:
        api.delete(f"/channels/{ch['id']}")
        time.sleep(0.1)
    console.print("[dim]  Removing existing roles...[/dim]")
    for role in api.get(f"/guilds/{guild_id}/roles").json() or []:
        if role["id"] == guild_id or role.get("managed"):
            continue
        api.delete(f"/guilds/{guild_id}/roles/{role['id']}")
        time.sleep(0.1)


def create_roles(api: DiscordClient, guild_id: str, roles_cfg: list) -> dict:
    console.print(f"\n[bold]Creating roles[/bold]")
    role_map: dict[str, str] = {}
    created: list[str] = []

    for r in roles_cfg:
        try:
            color = int(r["color"].lstrip("#"), 16)
        except (ValueError, KeyError):
            color = 0
        resp = api.post(f"/guilds/{guild_id}/roles", {
            "name":        r["name"],
            "permissions": api.perms_to_bits(r.get("permissions", [])),
            "color":       color,
            "hoist":       r.get("hoist", False),
            "mentionable": r.get("mentionable", False),
        })
        if resp.status_code in (200, 201):
            rid = resp.json()["id"]
            role_map[r["name"]] = rid
            created.append(rid)
            console.print(f"  + {r['name']}")
        else:
            console.print(f"  [red]x {r['name']}: {resp.status_code}[/red]")
        time.sleep(0.2)

    # roles_cfg[0] = highest priority → highest position number
    if created:
        positions = [
            {"id": rid, "position": len(created) - i}
            for i, rid in enumerate(created)
        ]
        api.patch(f"/guilds/{guild_id}/roles", positions)

    return role_map


def create_categories(api: DiscordClient, guild_id: str, role_map: dict, cats: list):
    console.print(f"\n[bold]Creating categories and channels[/bold]")
    for cat in cats:
        ow = api.overrides_to_list(cat.get("role_overrides") or {}, role_map, guild_id)
        resp = api.post(f"/guilds/{guild_id}/channels", {
            "name": cat["name"], "type": 4, "permission_overwrites": ow,
        })
        if resp.status_code not in (200, 201):
            console.print(f"  [red]x {cat['name']}: {resp.status_code}[/red]")
            continue
        cat_id = resp.json()["id"]
        console.print(f"\n  [{cat['name']}]")
        time.sleep(0.2)
        for ch in cat.get("channels", []):
            _create_channel(api, guild_id, ch, cat_id, ow, role_map)


def _apply_changeset_to_config(config: dict, changeset: dict) -> dict:
    cfg = copy.deepcopy(config)
    roles = cfg.get("roles", [])
    categories = cfg.get("categories", [])

    for name in changeset.get("roles_to_delete", []):
        roles = [r for r in roles if r["name"] != name]

    for r in changeset.get("roles_to_add", []):
        roles.append(r)

    for re_ in changeset.get("roles_to_edit", []):
        for r in roles:
            if r["name"] == re_["name"]:
                r.update(re_.get("fields", {}))

    for name in changeset.get("categories_to_delete", []):
        categories = [c for c in categories if c["name"] != name]

    for cat in changeset.get("categories_to_add", []):
        categories.append(cat)

    for ch_name in changeset.get("channels_to_delete", []):
        for cat in categories:
            cat["channels"] = [ch for ch in cat.get("channels", []) if ch["name"] != ch_name]

    for item in changeset.get("channels_to_add", []):
        cat_name = item.get("category_name", "")
        for cat in categories:
            if cat["name"] == cat_name:
                cat.setdefault("channels", []).append(item["channel"])
                break

    for ce in changeset.get("channels_to_edit", []):
        for cat in categories:
            for ch in cat.get("channels", []):
                if ch["name"] == ce["name"]:
                    ch.update(ce.get("fields", {}))

    cfg["roles"] = roles
    cfg["categories"] = categories
    return cfg


def apply_changeset(api: DiscordClient, guild_id: str, changes: dict):
    state = api.fetch_state(guild_id)
    ch_list = state["channels"]
    r_list = state["roles"]

    role_map = {r["name"]: r["id"] for r in r_list}
    ch_map = {c["name"]: c["id"] for c in ch_list}
    cat_map = {c["name"]: c["id"] for c in ch_list if c["type"] == 4}

    for name in changes.get("categories_to_delete", []):
        cid = cat_map.get(name)
        if not cid:
            console.print(f"  [yellow]Category '{name}' not found[/yellow]"); continue
        for ch in ch_list:
            if ch.get("parent_id") == cid:
                api.delete(f"/channels/{ch['id']}"); time.sleep(0.1)
        api.delete(f"/channels/{cid}")
        console.print(f"  - category: {name}"); time.sleep(0.1)

    for name in changes.get("channels_to_delete", []):
        cid = ch_map.get(name)
        if not cid:
            console.print(f"  [yellow]Channel '{name}' not found[/yellow]"); continue
        api.delete(f"/channels/{cid}")
        console.print(f"  - channel: {name}"); time.sleep(0.1)

    for name in changes.get("roles_to_delete", []):
        rid = role_map.get(name)
        if not rid:
            console.print(f"  [yellow]Role '{name}' not found[/yellow]"); continue
        api.delete(f"/guilds/{guild_id}/roles/{rid}")
        console.print(f"  - role: {name}"); time.sleep(0.1)

    for r in changes.get("roles_to_add", []):
        try:
            color = int(r["color"].lstrip("#"), 16)
        except (ValueError, KeyError):
            color = 0
        resp = api.post(f"/guilds/{guild_id}/roles", {
            "name": r["name"], "permissions": api.perms_to_bits(r.get("permissions", [])),
            "color": color, "hoist": r.get("hoist", False),
            "mentionable": r.get("mentionable", False),
        })
        if resp.status_code in (200, 201):
            role_map[r["name"]] = resp.json()["id"]
            console.print(f"  + role: {r['name']}")
        else:
            console.print(f"  [red]x role {r['name']}: {resp.status_code}[/red]")
        time.sleep(0.2)

    for re_ in changes.get("roles_to_edit", []):
        rid = role_map.get(re_["name"])
        if not rid:
            console.print(f"  [yellow]Role '{re_['name']}' not found[/yellow]"); continue
        fields = dict(re_.get("fields", {}))
        if "color" in fields:
            try: fields["color"] = int(str(fields["color"]).lstrip("#"), 16)
            except ValueError: pass
        if "permissions" in fields:
            fields["permissions"] = api.perms_to_bits(fields["permissions"])
        api.patch(f"/guilds/{guild_id}/roles/{rid}", fields)
        console.print(f"  ~ role: {re_['name']}"); time.sleep(0.2)

    for cat in changes.get("categories_to_add", []):
        ow = api.overrides_to_list(cat.get("role_overrides") or {}, role_map, guild_id)
        resp = api.post(f"/guilds/{guild_id}/channels",
                        {"name": cat["name"], "type": 4, "permission_overwrites": ow})
        if resp.status_code not in (200, 201):
            console.print(f"  [red]x category {cat['name']}: {resp.status_code}[/red]"); continue
        new_cat_id = resp.json()["id"]
        cat_map[cat["name"]] = new_cat_id
        console.print(f"  + category: {cat['name']}"); time.sleep(0.2)
        for ch in cat.get("channels", []):
            _create_channel(api, guild_id, ch, new_cat_id, ow, role_map)

    for item in changes.get("channels_to_add", []):
        cat_name = item.get("category_name", "")
        cat_id = cat_map.get(cat_name)
        if not cat_id:
            console.print(f"  [yellow]Category '{cat_name}' not found[/yellow]"); continue
        _create_channel(api, guild_id, item["channel"], cat_id, [], role_map)

    for ce in changes.get("channels_to_edit", []):
        cid = ch_map.get(ce["name"])
        if not cid:
            console.print(f"  [yellow]Channel '{ce['name']}' not found[/yellow]"); continue
        fields = dict(ce.get("fields", {}))
        if "slowmode" in fields:
            fields["rate_limit_per_user"] = fields.pop("slowmode")
        if "role_overrides" in fields:
            fields["permission_overwrites"] = api.overrides_to_list(
                fields.pop("role_overrides"), role_map, guild_id)
        api.patch(f"/channels/{cid}", fields)
        console.print(f"  ~ channel: {ce['name']}"); time.sleep(0.2)



# session management


def _session_dir(guild_id: str) -> str:
    return os.path.join(SERVERS_DIR, str(guild_id))


def save_session(guild_id: str, guild_name: str, prompt: str, config: dict):
    d = _session_dir(guild_id)
    os.makedirs(d, exist_ok=True)
    now = datetime.utcnow().isoformat()

    meta_path = os.path.join(d, "meta.json")
    meta: dict = {}
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            meta = json.load(f)
    meta.update({"guild_id": guild_id, "guild_name": guild_name, "updated_at": now})
    meta.setdefault("created_at", now)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)
    with open(os.path.join(d, "config.json"), "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    if prompt:
        with open(os.path.join(d, "prompt.txt"), "w", encoding="utf-8") as f:
            f.write(prompt)


def load_session(guild_id: str) -> dict | None:
    d = _session_dir(str(guild_id))
    meta_path = os.path.join(d, "meta.json")
    if not os.path.exists(meta_path):
        return None
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)
    cfg_path = os.path.join(d, "config.json")
    if os.path.exists(cfg_path):
        with open(cfg_path, encoding="utf-8") as f:
            meta["config"] = json.load(f)
    pmt_path = os.path.join(d, "prompt.txt")
    if os.path.exists(pmt_path):
        with open(pmt_path, encoding="utf-8") as f:
            meta["prompt"] = f.read()
    return meta


def list_sessions() -> list[dict]:
    if not os.path.exists(SERVERS_DIR):
        return []
    sessions = []
    for name in os.listdir(SERVERS_DIR):
        s = load_session(name)
        if s:
            sessions.append(s)
    return sorted(sessions, key=lambda s: s.get("updated_at", ""), reverse=True)


def delete_session(guild_id: str):
    d = _session_dir(str(guild_id))
    if os.path.exists(d):
        shutil.rmtree(d)



# ui helpers


def show_header():
    console.clear()
    header = Text()
    header.append("  AI Discord Server Setup", style="bold cyan")
    header.append(f"  v{VERSION}\n", style="dim")
    header.append(f"  {t('by')} ", style="dim")
    header.append(AUTHOR_URL, style="dim underline")
    header.append(f"\n  {t('subtitle')}", style="dim")
    console.print(Panel(header, box=box.DOUBLE_EDGE, border_style="cyan", padding=(0, 1)))
    console.print()


def ask(prompt_text: str, password: bool = False) -> str:
    while True:
        try:
            if password:
                import getpass
                val = getpass.getpass(f"  {prompt_text}: ")
            else:
                val = input(f"  {prompt_text}: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print(f"\n  [yellow]{t('aborted')}[/yellow]")
            raise KeyboardInterrupt
        if val:
            return val
        console.print(f"  [yellow]{t('empty_input')}[/yellow]")


def confirm(prompt_text: str) -> bool:
    try:
        raw = input(f"  {prompt_text} {t('confirm_y')}: ").strip().lower()
    except (EOFError, KeyboardInterrupt):
        return False
    return raw in ("y", "e", "yes", "evet")


def show_sessions_table(sessions: list[dict]):
    if not sessions:
        console.print(f"  [dim]{t('no_configs')}[/dim]")
        return
    table = Table(box=box.SIMPLE_HEAD, show_header=True, header_style="bold cyan")
    table.add_column("#", style="dim", width=3)
    table.add_column(t("cols_name"), style="bold")
    table.add_column(t("cols_id"), style="dim")
    table.add_column(t("cols_updated"), style="dim")
    table.add_column(t("cols_roles"), justify="right", style="cyan")
    table.add_column(t("cols_channels"), justify="right", style="cyan")
    for i, s in enumerate(sessions, 1):
        cfg     = s.get("config", {})
        n_roles = len(cfg.get("roles", []))
        n_ch    = sum(len(c.get("channels", [])) for c in cfg.get("categories", []))
        table.add_row(
            str(i),
            s.get("guild_name", "?"),
            s.get("guild_id",   "?"),
            s.get("updated_at", "")[:10],
            str(n_roles),
            str(n_ch),
        )
    console.print(table)


def _show_config_summary(config: dict):
    n_roles = len(config.get("roles", []))
    n_cats = len(config.get("categories", []))
    n_ch = sum(len(c.get("channels", [])) for c in config.get("categories", []))
    console.print(Panel(
        f"  {t('summary_roles')}: [bold cyan]{n_roles}[/bold cyan]   "
        f"{t('summary_cats')}: [bold cyan]{n_cats}[/bold cyan]   "
        f"{t('summary_channels')}: [bold cyan]{n_ch}[/bold cyan]",
        title=f"[bold]{t('config_summary')}[/bold]",
        border_style="cyan",
    ))


def pick_token_type() -> bool:
    pref = _settings.get("token_type", "user")
    console.print(f"\n  [bold]{t('select_token_type')}[/bold]")
    console.print(f"  [1] {t('user_token')}" + (" [dim](saved)[/dim]" if pref == "user" else ""))
    console.print(f"  [2] {t('bot_token')}" + (" [dim](saved)[/dim]" if pref == "bot" else ""))
    raw = input("  > ").strip()
    if not raw:
        return pref == "bot"  # respect saved preference on Enter
    return raw == "2"


def pick_token_and_server(need_server: bool = True) -> tuple[str, str, bool] | None:
    is_bot = pick_token_type()
    try:
        token = ask(t("enter_token"), password=True)
        guild_id = ask(t("enter_server_id")) if need_server else ""
    except KeyboardInterrupt:
        return None
    return token, guild_id, is_bot


def _format_state_for_prompt(state: dict) -> tuple[str, str]:
    type_names = {0: "text", 2: "voice", 4: "category", 5: "announcement",
                  13: "stage", 15: "forum"}
    roles_lines = [
        f'  "{r["name"]}"  (id: {r["id"]})'
        for r in state.get("roles", []) if r["name"] != "@everyone"
    ]
    channels = state.get("channels", [])
    cats = {c["id"]: c for c in channels if c["type"] == 4}
    lines = []
    for cat in sorted(cats.values(), key=lambda c: c.get("position", 0)):
        lines.append(f'  [{cat["name"]}]  (id: {cat["id"]})')
        for ch in sorted(
            [c for c in channels if c.get("parent_id") == cat["id"]],
            key=lambda c: c.get("position", 0),
        ):
            lines.append(
                f'    {ch["name"]}  [{type_names.get(ch["type"], "?")}]  (id: {ch["id"]})'
            )
    return "\n".join(roles_lines) or "  (none)", "\n".join(lines) or "  (none)"



# chat loop


def _chat_loop(ai: OpenAI, messages: list,
               extractor, marker: str) -> tuple[dict, str] | None:
    first_prompt = ""
    while True:
        try:
            user_input = input(f"  {t('you')}: ").strip()
        except (EOFError, KeyboardInterrupt):
            console.print(f"\n  [yellow]{t('aborted')}[/yellow]")
            return None
        if not user_input:
            continue
        if not first_prompt:
            first_prompt = user_input
        messages.append({"role": "user", "content": user_input})

        with console.status(f"[dim]{t('thinking')}[/dim]", spinner="dots"):
            try:
                reply, _ = ai_chat(ai, messages)
            except Exception as e:
                console.print(f"  [red]{t('api_error')}: {e}[/red]")
                continue
        if not reply:
            console.print(f"  [red]{t('empty_resp')}: [bold]{current_model()}[/bold][/red]")
            continue

        reply, result = _complete_json(ai, messages, reply, extractor, marker)
        messages.append({"role": "assistant", "content": reply})

        display = re.sub(rf"{marker}.*", "", reply, flags=re.DOTALL)
        display = re.sub(r"```json.*", "", display, flags=re.DOTALL).strip()
        if display:
            console.print(f"\n  [bold cyan]{t('ai_label')}:[/bold cyan] {display}\n")

        if result:
            return result, first_prompt



# flows


def flow_setup():
    show_header()
    console.print(Panel(f"[bold]{t('setup_title')}[/bold]\n[dim]{t('setup_hint')}[/dim]",
                        border_style="cyan"))
    console.print()

    creds = pick_token_and_server()
    if not creds:
        return
    token, guild_id, is_bot = creds

    conn = _connect(token, is_bot, guild_id)
    if not conn:
        input(f"\n  {t('press_enter')}")
        return
    api, guild_name = conn

    ai = get_ai_client()
    messages = [{"role": "system", "content": SETUP_SYSTEM_PROMPT}]
    console.print()

    result = _chat_loop(ai, messages, extract_config, "READY_TO_BUILD")
    if not result:
        return
    config, first_prompt = result

    _show_config_summary(config)
    console.print(Panel(f"[bold green]{t('design_complete')}[/bold green]", border_style="green"))

    if not confirm(t("build_q")):
        save_session(guild_id, guild_name, first_prompt, config)
        console.print(f"  [yellow]{t('skip_hint')}[/yellow]")
        input(f"\n  {t('press_enter')}")
        return

    console.print(f"\n  [yellow]{t('wipe_warn')}[/yellow]")
    time.sleep(5)

    wipe_guild(api, guild_id)
    role_map = create_roles(api, guild_id, config.get("roles", []))
    create_categories(api, guild_id, role_map, config.get("categories", []))
    save_session(guild_id, guild_name, first_prompt, config)
    console.print(Panel(f"[bold green]{t('setup_complete')}[/bold green]", border_style="green"))
    input(f"\n  {t('press_enter')}")


def flow_edit():
    show_header()
    console.print(Panel(f"[bold]{t('edit_title')}[/bold]\n[dim]{t('edit_hint')}[/dim]",
                        border_style="cyan"))
    sessions = list_sessions()
    show_sessions_table(sessions)
    console.print(f"\n  {t('select_server')}")

    try:
        raw = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not raw:
        return

    session: dict | None = None
    if raw.isdigit() and 1 <= int(raw) <= len(sessions):
        session = sessions[int(raw) - 1]
    else:
        session = load_session(raw) or {"guild_id": raw, "guild_name": raw, "prompt": "", "config": {}}

    guild_id = session["guild_id"]
    creds = pick_token_and_server(need_server=False)
    if not creds:
        return
    token, _, is_bot = creds

    conn = _connect(token, is_bot, guild_id)
    if not conn:
        return
    api, guild_name = conn

    state = api.fetch_state(guild_id)
    roles_list, channels_list = _format_state_for_prompt(state)
    system = EDIT_SYSTEM_PROMPT.format(
        server_name=guild_name,
        roles_list=roles_list,
        channels_list=channels_list,
        original_prompt=session.get("prompt", "(no original description saved)"),
    )
    ai = get_ai_client()
    messages = [{"role": "system", "content": system}]
    console.print()

    while True:
        result = _chat_loop(ai, messages, extract_changeset, "READY_TO_APPLY")
        if not result:
            break
        changeset, _ = result
        console.print(Panel(f"[bold green]{t('changes_ready')}[/bold green]", border_style="green"))
        if not confirm(t("apply_q")):
            console.print(f"  [yellow]{t('cancel')}[/yellow]")
        else:
            apply_changeset(api, guild_id, changeset)
            updated_config = _apply_changeset_to_config(session.get("config", {}), changeset)
            session["config"] = updated_config
            save_session(guild_id, guild_name, session.get("prompt", ""), updated_config)
            console.print(Panel(f"[bold green]{t('edit_complete')}[/bold green]", border_style="green"))
        console.print(f"  [dim]{t('continue_editing')}[/dim]\n")


def flow_rebuild():
    show_header()
    console.print(Panel(f"[bold]{t('rebuild_title')}[/bold]", border_style="cyan"))
    sessions = list_sessions()
    if not sessions:
        console.print(f"  [dim]{t('no_configs')}[/dim]")
        input(f"\n  {t('press_enter')}")
        return

    show_sessions_table(sessions)
    console.print(f"\n  {t('rebuild_select')}")
    try:
        raw = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    if not raw:
        return

    session: dict | None = None
    if raw.isdigit() and 1 <= int(raw) <= len(sessions):
        session = sessions[int(raw) - 1]
    else:
        session = load_session(raw)
    if not session or not session.get("config"):
        console.print(f"  [red]{t('config_not_found')}[/red]")
        input(f"\n  {t('press_enter')}")
        return

    config = session["config"]
    saved_id = session["guild_id"]

    console.print(f"\n  {t('rebuild_id_hint')} [dim](saved: {saved_id})[/dim]")
    try:
        new_id_raw = input("  > ").strip()
    except (EOFError, KeyboardInterrupt):
        return
    guild_id = new_id_raw if new_id_raw else saved_id

    creds = pick_token_and_server(need_server=False)
    if not creds:
        return
    token, _, is_bot = creds

    conn = _connect(token, is_bot, guild_id)
    if not conn:
        input(f"\n  {t('press_enter')}")
        return
    api, guild_name = conn

    _show_config_summary(config)

    if not confirm(t("rebuild_q")):
        console.print(f"  [yellow]{t('cancel')}[/yellow]")
        input(f"\n  {t('press_enter')}")
        return

    console.print(f"\n  [yellow]{t('wipe_warn')}[/yellow]")
    time.sleep(5)

    wipe_guild(api, guild_id)
    role_map = create_roles(api, guild_id, config.get("roles", []))
    create_categories(api, guild_id, role_map, config.get("categories", []))
    save_session(guild_id, guild_name, session.get("prompt", ""), config)
    console.print(Panel(f"[bold green]{t('rebuild_complete')}[/bold green]", border_style="green"))
    input(f"\n  {t('press_enter')}")


def flow_configs():
    while True:
        show_header()
        console.print(Panel(f"[bold]{t('configs_title')}[/bold]", border_style="cyan"))
        sessions = list_sessions()
        if sessions:
            show_sessions_table(sessions)
        else:
            console.print(f"  [dim]{t('no_configs')}[/dim]")
        console.print(f"\n  {t('config_actions')}")
        try:
            raw = input("  > ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            return

        if raw == "b":
            return

        elif raw == "v":
            if not sessions:
                continue
            try:
                idx = int(input("  # : ").strip()) - 1
                s   = sessions[idx]
            except (ValueError, IndexError, KeyboardInterrupt):
                continue
            cfg = s.get("config", {})
            n_roles = len(cfg.get("roles", []))
            n_ch = sum(len(c.get("channels", [])) for c in cfg.get("categories", []))
            info = (
                f"[bold]{s.get('guild_name')}[/bold]  (ID: {s.get('guild_id')})\n"
                f"Created : {s.get('created_at','?')[:19]}\n"
                f"Updated : {s.get('updated_at','?')[:19]}\n"
                f"Roles   : {n_roles}    Channels: {n_ch}\n"
            )
            if s.get("prompt"):
                info += f"\nPrompt  :\n[dim]{s['prompt'][:400]}[/dim]"
            console.print(Panel(info, title=t("config_detail"), border_style="cyan"))
            input(f"\n  {t('press_enter')}")

        elif raw == "e":
            if not sessions:
                continue
            try:
                idx = int(input("  # : ").strip()) - 1
                s   = sessions[idx]
            except (ValueError, IndexError, KeyboardInterrupt):
                continue
            safe_name = re.sub(r'[<>:"/\\|?*]', "_", s.get("guild_name", s.get("guild_id", "config")))
            export_path = os.path.join(SCRIPT_DIR, f"{safe_name}_config.json")
            try:
                with open(export_path, "w", encoding="utf-8") as f:
                    json.dump(s.get("config", {}), f, indent=2, ensure_ascii=False)
                console.print(f"  [green]{t('export_success')}:[/green] {export_path}")
            except Exception as e:
                console.print(f"  [red]{e}[/red]")
            input(f"\n  {t('press_enter')}")

        elif raw == "i":
            try:
                path = ask(t("import_path")).strip('"').strip("'")
            except KeyboardInterrupt:
                continue
            if not os.path.exists(path):
                console.print(f"  [red]{t('file_not_found')}[/red]")
                input(f"\n  {t('press_enter')}")
                continue
            try:
                with open(path, encoding="utf-8") as f:
                    imported_config = json.load(f)
            except Exception as e:
                console.print(f"  [red]{e}[/red]")
                input(f"\n  {t('press_enter')}")
                continue
            if "roles" not in imported_config:
                console.print(f"  [red]{t('import_error')}[/red]")
                input(f"\n  {t('press_enter')}")
                continue
            try:
                name = ask(t("import_name"))
                guild_id = ask(t("import_id"))
            except KeyboardInterrupt:
                continue
            save_session(guild_id, name, "", imported_config)
            console.print(f"  [green]{t('import_success')}[/green]")
            time.sleep(1)

        elif raw == "d":
            if not sessions:
                continue
            try:
                idx = int(input("  # : ").strip()) - 1
                s   = sessions[idx]
            except (ValueError, IndexError, KeyboardInterrupt):
                continue
            console.print(f"  [red]{s.get('guild_name')} ({s.get('guild_id')})[/red]")
            if confirm(t("delete_q")):
                delete_session(s["guild_id"])
                console.print(f"  [green]{t('config_deleted')}[/green]")
                time.sleep(1)


def flow_settings():
    show_header()
    console.print(Panel(f"[bold]{t('settings_title')}[/bold]", border_style="cyan"))

    lang = _settings.get("language", "en")
    tt = _settings.get("token_type", "user")

    console.print(f"\n  [bold]1. {t('lang_current')}[/bold]  [dim](current: {lang})[/dim]")
    console.print(f"     [1] English  [2] Türkçe")

    console.print(f"\n  [bold]2. {t('token_pref')}[/bold]  [dim](current: {tt})[/dim]")
    console.print(f"     [1] {t('user_token')}  [2] {t('bot_token')}")

    console.print()
    try:
        lang_in = input(f"  {t('lang_current')} [1/2]: ").strip()
        tok_in = input(f"  {t('token_pref')} [1/2]: ").strip()
    except (EOFError, KeyboardInterrupt):
        return

    if lang_in == "2":
        _settings["language"] = "tr"
    elif lang_in == "1":
        _settings["language"] = "en"

    if tok_in == "2":
        _settings["token_type"] = "bot"
    elif tok_in == "1":
        _settings["token_type"] = "user"

    save_settings()
    console.print(f"\n  [green]{t('settings_saved')}[/green]")
    time.sleep(1)



# entry point


def main():
    load_settings()

    if not OPENROUTER_API_KEY:
        console.print(f"[red]{t('missing_key')}[/red]")
        sys.exit(1)

    if not MODEL:
        console.print(f"[red]{t('missing_model')}[/red]")
        sys.exit(1)

    while True:
        show_header()
        console.print(Panel(
            f"  [bold][1][/bold]  {t('opt_setup')}    — {t('opt_setup_desc')}\n"
            f"  [bold][2][/bold]  {t('opt_edit')}     — {t('opt_edit_desc')}\n"
            f"  [bold][3][/bold]  {t('opt_rebuild')}  — {t('opt_rebuild_desc')}\n"
            f"  [bold][4][/bold]  {t('opt_configs')}  — {t('opt_configs_desc')}\n"
            f"  [bold][5][/bold]  {t('opt_settings')} — {t('opt_settings_desc')}\n"
            f"  [bold][0][/bold]  {t('opt_exit')}",
            title=f"[bold]{t('main_menu')}[/bold]",
            border_style="cyan",
            padding=(0, 2),
        ))

        try:
            choice = input(f"\n  {t('choose')}: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if choice == "1":
            flow_setup()
        elif choice == "2":
            flow_edit()
        elif choice == "3":
            flow_rebuild()
        elif choice == "4":
            flow_configs()
        elif choice == "5":
            flow_settings()
        elif choice == "0":
            break
        else:
            console.print(f"  [yellow]{t('invalid')}[/yellow]")
            time.sleep(0.8)

    console.print(f"\n  [dim]{t('opt_exit')}.[/dim]\n")


if __name__ == "__main__":
    main()
