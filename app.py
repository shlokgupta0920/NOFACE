import streamlit as st
import streamlit.components.v1 as components
import secrets
import os
import html
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from supabase import create_client

# =========================================================
# 1. PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="NOFACE | Global Chat",
    page_icon="👤",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# 2. SUPABASE CONFIG
# =========================================================
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip()
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()

if not SUPABASE_URL or not SUPABASE_KEY:
    st.error("Supabase credentials missing. Check your .env file.")
    st.stop()

@st.cache_resource
def get_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = get_supabase()
except Exception as exc:
    st.error(f"Could not connect to Supabase: {exc}")
    st.stop()

# =========================================================
# 3. ANONYMOUS ID
# =========================================================
if "anonymous_id" not in st.session_state:
    st.session_state.anonymous_id = (
        "Anonymous #" + secrets.token_hex(3).upper()
    )

anonymous_id = st.session_state.anonymous_id

# Each new Streamlit session starts with an empty chat view.
if "chat_joined_at" not in st.session_state:
    st.session_state.chat_joined_at = datetime.now(timezone.utc).isoformat()

chat_joined_at = st.session_state.chat_joined_at

# =========================================================
# 4. CUSTOM CSS
# =========================================================
st.markdown(
    """
    <style>
    #MainMenu, footer, header { visibility: hidden; }

    .stApp {
        background: #0b0d14;
        color: #f5f6fb;
    }

    .block-container {
        max-width: 1000px;
        padding-top: 2.2rem;
        padding-bottom: 2rem;
    }

    .brand {
        color: #ffffff;
        font-size: 40px;
        font-weight: 850;
        letter-spacing: 8px;
        line-height: 1.2;
    }

    .subtitle {
        color: #85899a;
        font-size: 11px;
        letter-spacing: 2.5px;
        margin-top: 8px;
    }

    .identity {
        background: #171c29;
        border: 1px solid #30374a;
        border-radius: 11px;
        padding: 14px;
        color: #b7a5ff;
        font-size: 14px;
        margin-top: 8px;
    }

    div[data-testid="stForm"] {
        background: #0e111a;
        border: 1px solid #30374a;
        border-radius: 13px;
        padding: 16px;
    }

    div[data-testid="stTextInput"] input {
        background: #171c29;
        color: #ffffff;
        border: 1px solid #3a4053;
        border-radius: 11px;
        min-height: 46px;
    }

    div[data-testid="stFormSubmitButton"] button {
        background: #292536;
        color: white;
        border: 1px solid #49435c;
        border-radius: 10px;
        min-height: 46px;
        font-weight: 600;
    }

    div[data-testid="stFormSubmitButton"] button:hover {
        background: #39334b;
        border-color: #b7a5ff;
        color: white;
    }

    .stAlert {
        border-radius: 10px;
    }

    @media (max-width: 700px) {
        .brand {
            font-size: 32px;
            letter-spacing: 6px;
        }
        .block-container {
            padding-left: 1rem;
            padding-right: 1rem;
        }
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =========================================================
# 5. HEADER
# =========================================================
st.markdown(
    """
    <div class="brand">NOFACE</div>
    <div class="subtitle">SAY WITHOUT BEING SEEN.</div>
    """,
    unsafe_allow_html=True
)

st.write("")
st.markdown("### Global Chat")

st.markdown(
    f'<div class="identity">Your identity: '
    f'{html.escape(anonymous_id)}</div>',
    unsafe_allow_html=True
)

st.write("")

# =========================================================
# 6. SEND MESSAGE
# =========================================================
with st.form("noface_message_form", clear_on_submit=True):
    message = st.text_input(
        "Message",
        placeholder="Type your message here...",
        max_chars=500,
        label_visibility="collapsed"
    )

    send = st.form_submit_button(
        "Send Message",
        use_container_width=True
    )

    if send:
        clean_message = message.strip()

        if not clean_message:
            st.warning("Please enter a message.")
        else:
            try:
                supabase.table("messages").insert(
                    {
                        "sender_id": anonymous_id,
                        "message": clean_message
                    }
                ).execute()

                st.rerun()

            except Exception as exc:
                st.error(f"Message could not be sent: {exc}")

# =========================================================
# 7. REAL-TIME CHAT COMPONENT
# =========================================================
realtime_html = r"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">

    <script src="https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2"></script>

    <style>
        * {
            box-sizing: border-box;
        }

        body {
            margin: 0;
            padding: 0;
            background: #0b0d14;
            color: #ffffff;
            font-family: Arial, Helvetica, sans-serif;
        }

        #topbar {
            display: flex;
            justify-content: space-between;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            padding: 8px 4px 12px;
        }

        #connection {
            color: #35dc9b;
            font-size: 12px;
        }

        #online {
            color: #35dc9b;
            font-size: 13px;
            white-space: nowrap;
        }

        #messages {
            height: 520px;
            overflow-y: auto;
            padding: 9px;
            background: #141824;
            border: 1px solid #252b3b;
            border-radius: 16px;
            scroll-behavior: smooth;
        }

        #messages::-webkit-scrollbar {
            width: 8px;
        }

        #messages::-webkit-scrollbar-track {
            background: #141824;
        }

        #messages::-webkit-scrollbar-thumb {
            background: #41485d;
            border-radius: 10px;
        }

        .message {
            background: #1b2232;
            border: 1px solid #30374a;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 11px;
            overflow-wrap: anywhere;
        }

        .sender {
            color: #b7a5ff;
            font-size: 13px;
            font-weight: 700;
            margin-bottom: 8px;
        }

        .content {
            color: #ffffff;
            font-size: 15px;
            line-height: 1.5;
            white-space: pre-wrap;
        }

        .timestamp {
            color: #8190aa;
            font-size: 10px;
            margin-top: 10px;
        }

        .empty {
            text-align: center;
            color: #85899a;
            padding: 150px 15px;
        }

        @media (max-width: 600px) {
            #messages {
                height: 460px;
            }
            .message {
                padding: 12px;
            }
        }
    </style>
</head>

<body>
    <div id="topbar">
        <div id="connection">● CONNECTING...</div>
        <div id="online">● 0 ONLINE</div>
    </div>

    <div id="messages">
        <div class="empty">Loading NOFACE...</div>
    </div>

    <script>
        const SUPABASE_URL = __SUPABASE_URL__;
        const SUPABASE_KEY = __SUPABASE_KEY__;
        const USER_ID = __USER_ID__;
        const SESSION_JOINED_AT = __SESSION_JOINED_AT__;

        const client = window.supabase.createClient(
            SUPABASE_URL,
            SUPABASE_KEY
        );

        const messageBox = document.getElementById("messages");
        const connectionBox = document.getElementById("connection");
        const onlineBox = document.getElementById("online");

        const seenMessages = new Set();

        function messageKey(msg) {
            return [
                msg.created_at || "",
                msg.sender_id || "",
                msg.message || ""
            ].join("|");
        }

        function formatTime(value) {
            if (!value) return "";
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) return "";

            return date.toLocaleString([], {
                year: "numeric",
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit"
            });
        }

        function addMessage(msg) {
            const key = messageKey(msg);

            if (seenMessages.has(key)) return;
            seenMessages.add(key);

            const empty = messageBox.querySelector(".empty");
            if (empty) empty.remove();

            const card = document.createElement("div");
            card.className = "message";

            const sender = document.createElement("div");
            sender.className = "sender";
            sender.textContent = msg.sender_id || "Anonymous";

            const content = document.createElement("div");
            content.className = "content";
            // textContent prevents message text from being treated as HTML.
            content.textContent = msg.message || "";

            const timestamp = document.createElement("div");
            timestamp.className = "timestamp";
            timestamp.textContent = formatTime(msg.created_at);

            card.appendChild(sender);
            card.appendChild(content);
            card.appendChild(timestamp);

            messageBox.appendChild(card);

            // Keep the latest 100 messages visible in this chat window.
            while (messageBox.children.length > 100) {
                messageBox.removeChild(messageBox.firstChild);
            }

            messageBox.scrollTop = messageBox.scrollHeight;
        }

        async function loadMessages() {
            connectionBox.textContent = "● LOADING MESSAGES";

            // Show only messages posted after this visitor joined.
            // Older rows remain in Supabase but are hidden from this session.
            const { data, error } = await client
                .from("messages")
                .select("sender_id, message, created_at")
                .gte("created_at", SESSION_JOINED_AT)
                .order("created_at", { ascending: true })
                .limit(100);

            if (error) {
                connectionBox.textContent = "● MESSAGE LOAD ERROR";
                console.error("Message load error:", error);
                messageBox.innerHTML =
                    '<div class="empty">Unable to load messages. Check Supabase permissions.</div>';
                return;
            }

            messageBox.innerHTML = "";
            seenMessages.clear();

            if (!data || data.length === 0) {
                messageBox.innerHTML = `
                    <div class="empty">
                        <h3>Welcome to NOFACE</h3>
                        Your words. Your anonymity.<br>
                        One global room.
                    </div>
                `;
                return;
            }

            data.forEach(addMessage);
            messageBox.scrollTop = messageBox.scrollHeight;
        }

        // Listen for newly inserted chat messages.
        const chatChannel = client
            .channel("noface-chat-" + Math.random().toString(36).slice(2))
            .on(
                "postgres_changes",
                {
                    event: "INSERT",
                    schema: "public",
                    table: "messages"
                },
                (payload) => {
                    // Ignore any event created before this visitor joined.
                    if (
                        payload.new.created_at &&
                        new Date(payload.new.created_at).getTime() >=
                        new Date(SESSION_JOINED_AT).getTime()
                    ) {
                        addMessage(payload.new);
                    }
                }
            )
            .subscribe((status) => {
                if (status === "SUBSCRIBED") {
                    connectionBox.textContent =
                        "● LIVE · REAL-TIME CONNECTED";
                } else if (
                    status === "CHANNEL_ERROR" ||
                    status === "TIMED_OUT"
                ) {
                    connectionBox.textContent =
                        "● CONNECTION ISSUE · RECONNECTING";
                } else {
                    connectionBox.textContent = "● " + status;
                }
            });

        // Track online users using Supabase Realtime Presence.
        const presenceChannel = client.channel(
            "noface-online-presence",
            {
                config: {
                    presence: {
                        key: USER_ID
                    }
                }
            }
        );

        function updateOnlineCount() {
            const state = presenceChannel.presenceState();
            const count = Object.keys(state).length;
            onlineBox.textContent = "● " + count + " ONLINE";
        }

        presenceChannel
            .on("presence", { event: "sync" }, updateOnlineCount)
            .on("presence", { event: "join" }, updateOnlineCount)
            .on("presence", { event: "leave" }, updateOnlineCount)
            .subscribe(async (status) => {
                if (status === "SUBSCRIBED") {
                    try {
                        await presenceChannel.track({
                            user_id: USER_ID,
                            online_at: new Date().toISOString()
                        });
                        updateOnlineCount();
                    } catch (error) {
                        console.error("Presence tracking error:", error);
                    }
                }
            });

        // Load stored messages once when the chat opens.
        loadMessages();

        // Clean up subscriptions when this chat frame closes.
        window.addEventListener("beforeunload", () => {
            client.removeChannel(chatChannel);
            client.removeChannel(presenceChannel);
        });
    </script>
</body>
</html>
"""

# Safely insert credentials and the anonymous identity into JavaScript.
realtime_html = (
    realtime_html
    .replace("__SUPABASE_URL__", json.dumps(SUPABASE_URL))
    .replace("__SUPABASE_KEY__", json.dumps(SUPABASE_KEY))
    .replace("__USER_ID__", json.dumps(anonymous_id))
    .replace("__SESSION_JOINED_AT__", json.dumps(chat_joined_at))
)

components.html(
    realtime_html,
    height=590,
    scrolling=False
)

# =========================================================
# 8. FOOTER
# =========================================================
st.write("")
st.caption("Text only · No uploads · New visitors see messages from the time they join")
