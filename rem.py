import sqlite3
import hashlib
import locale
import os
import re
from collections import Counter
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st


DB_PATH = Path(__file__).with_name("messages.db")
LOGO_PATH = Path(__file__).with_name("T.W.M.png")
SITE_NAME = "Trace.me"
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = os.getenv("ADMIN_PASSWORD_HASH", "")
TOPIC_OPTIONS = [
    "Love",
    "Life Stories",
    "Discussion",
    "Gossip",
    "Hate",
    "Personal",
    "Private",
    "School",
    "Work",
    "Relationships",
    "Health",
    "Other",
]
LANGUAGE_CODES = ["en", "it", "es"]
LANGUAGE_NAMES = {"en": "English", "it": "Italiano", "es": "Espanol"}
TRANSLATIONS = {
    "en": {
        "app_title": "Community Topics Dashboard",
        "slogan": "everything you want to comunicate",
        "language": "Language",
        "logged_in_as": "Logged in as {username}",
        "log_out": "Log out",
        "login_needed_sidebar": "You must log in to publish a message.",
        "menu": "Menu",
        "menu_dashboard": "Dashboard",
        "menu_publish": "Publish message",
        "menu_private": "Private messages",
        "sign_in_required": "Sign in required",
        "sign_in_publish": "To write and publish a comment, log in or create an account first.",
        "sign_in_private": "To send private messages, log in or create an account first.",
        "tab_login": "Log in",
        "tab_signup": "Sign up",
        "username": "Username",
        "password": "Password",
        "login": "Log in",
        "invalid_creds": "Invalid username or password.",
        "login_success": "Logged in successfully.",
        "choose_username": "Choose username",
        "first_name": "First name",
        "last_name": "Last name",
        "choose_password": "Choose password",
        "create_account": "Create account",
        "password_min": "Password must be at least 6 characters.",
        "account_created": "Account created. You can now log in.",
        "username_exists": "Username already exists. Please choose another one.",
        "publish_header": "Publish a message",
        "recent_comments": "Recent comments",
        "posting_as": "Posting as: {username}",
        "topic": "Topic",
        "private_notice": "Private category: this message will be visible only to you and the recipient.",
        "private_recipient_required": "For Private category, you must choose a recipient.",
        "post_title": "Post title",
        "post_title_placeholder": "Short summary",
        "message_info": "Message / Information",
        "message_placeholder": "Write your message here...",
        "publish": "Publish",
        "published_success": "Your message has been published to the common dashboard.",
        "publish_fee_info": "Publishing fee: {fee} EUR per comment. Your balance: {balance} EUR",
        "buy_credit_1": "Buy 1 EUR credit",
        "buy_credit_5": "Buy 5 EUR credit",
        "payment_page_ready": "Payment link generated. Click below to complete checkout.",
        "open_checkout": "Open secure checkout",
        "payment_success_amount": "Payment received. {amount} EUR has been added to your balance.",
        "payment_cancelled": "Payment canceled.",
        "payment_not_configured": "Payment is not configured yet. Set STRIPE_SECRET_KEY and APP_BASE_URL.",
        "payment_processing_error": "Unable to validate payment session.",
        "insufficient_balance": "Insufficient balance. Add credit to publish a comment.",
        "dashboard_header": "Shared dashboard",
        "surname_priority_hint": "Comments from users with your same surname are shown first ({count} found). They may be related to you.",
        "for_you_header": "For You",
        "for_you_hint": "Recommended from topics and comments similar to what you liked.",
        "for_you_empty": "Like some comments to get personalized recommendations.",
        "like": "Like",
        "unlike": "Unlike",
        "likes_count": "Likes: {count}",
        "login_to_like": "Log in to like comments and unlock your For You feed.",
        "filter_topic": "Filter by topic",
        "all_topics": "All",
        "no_posts": "No posts yet. Publish the first message.",
        "topic_by": "Topic: <b>{topic}</b> - By: <b>{username}</b>",
        "admin_actions": "Admin actions for post #{post_id}",
        "move_to_category": "Move to category",
        "move_category": "Move category",
        "delete_comment": "Delete comment",
        "category_updated": "Category updated.",
        "comment_deleted": "Comment deleted.",
        "private_header": "Private messages",
        "send_private": "Send a private message",
        "no_recipients": "No other users available yet. Ask someone to sign up first.",
        "recipient": "Recipient",
        "message_title": "Message title",
        "message_title_placeholder": "Short private subject",
        "private_message": "Private message",
        "private_placeholder": "Write your private message...",
        "send_private_btn": "Send private message",
        "cannot_self_pm": "You cannot send a private message to yourself.",
        "private_sent": "Private message sent.",
        "inbox": "Inbox",
        "sent": "Sent",
        "inbox_empty": "Your inbox is empty.",
        "sent_empty": "No sent private messages yet.",
        "from": "From",
        "to": "To",
        "empty_field": "{field_name} cannot be empty.",
        "too_long": "{field_name} is too long (max {max_len} characters).",
        "invalid_topic": "Please choose a valid topic from the list.",
        "site_logo_subtitle": "Community and Private Messages",
        "welcome_title": "Welcome",
        "welcome_message": "wellcome in a world full of stories, of lifes and experiences because each of us has the right to be reamembered.",
        "enter": "Enter",
    },
    "it": {
        "app_title": "Bacheca Argomenti",
        "slogan": "tutto quello che vuoi comunicare",
        "language": "Lingua",
        "logged_in_as": "Accesso come {username}",
        "log_out": "Esci",
        "login_needed_sidebar": "Devi accedere per pubblicare un messaggio.",
        "menu": "Menu",
        "menu_dashboard": "Bacheca",
        "menu_publish": "Pubblica messaggio",
        "menu_private": "Messaggi privati",
        "sign_in_required": "Accesso richiesto",
        "sign_in_publish": "Per scrivere e pubblicare un commento, accedi o crea un account.",
        "sign_in_private": "Per inviare messaggi privati, accedi o crea un account.",
        "tab_login": "Accedi",
        "tab_signup": "Registrati",
        "username": "Nome utente",
        "password": "Password",
        "login": "Accedi",
        "invalid_creds": "Nome utente o password non validi.",
        "login_success": "Accesso effettuato con successo.",
        "choose_username": "Scegli nome utente",
        "first_name": "Nome",
        "last_name": "Cognome",
        "choose_password": "Scegli password",
        "create_account": "Crea account",
        "password_min": "La password deve avere almeno 6 caratteri.",
        "account_created": "Account creato. Ora puoi accedere.",
        "username_exists": "Nome utente gia esistente. Scegline un altro.",
        "publish_header": "Pubblica un messaggio",
        "recent_comments": "Commenti recenti",
        "posting_as": "Pubblichi come: {username}",
        "topic": "Argomento",
        "private_notice": "Categoria privata: questo messaggio sara visibile solo a te e al destinatario.",
        "private_recipient_required": "Per la categoria Privato devi scegliere un destinatario.",
        "post_title": "Titolo",
        "post_title_placeholder": "Breve riassunto",
        "message_info": "Messaggio / Informazioni",
        "message_placeholder": "Scrivi qui il tuo messaggio...",
        "publish": "Pubblica",
        "published_success": "Il tuo messaggio e stato pubblicato nella bacheca comune.",
        "publish_fee_info": "Costo pubblicazione: {fee} EUR per commento. Il tuo saldo: {balance} EUR",
        "buy_credit_1": "Acquista 1 EUR di credito",
        "buy_credit_5": "Acquista 5 EUR di credito",
        "payment_page_ready": "Link di pagamento generato. Clicca sotto per completare il checkout.",
        "open_checkout": "Apri checkout sicuro",
        "payment_success_amount": "Pagamento ricevuto. {amount} EUR sono stati aggiunti al tuo saldo.",
        "payment_cancelled": "Pagamento annullato.",
        "payment_not_configured": "Pagamento non configurato. Imposta STRIPE_SECRET_KEY e APP_BASE_URL.",
        "payment_processing_error": "Impossibile verificare la sessione di pagamento.",
        "insufficient_balance": "Saldo insufficiente. Aggiungi credito per pubblicare un commento.",
        "dashboard_header": "Bacheca comune",
        "surname_priority_hint": "I commenti degli utenti con il tuo stesso cognome sono mostrati prima ({count} trovati). Potrebbero essere tuoi parenti.",
        "for_you_header": "Per Te",
        "for_you_hint": "Consigli basati su argomenti e commenti simili a quelli che hai messo like.",
        "for_you_empty": "Metti like ad alcuni commenti per ricevere consigli personalizzati.",
        "like": "Mi piace",
        "unlike": "Non mi piace piu",
        "likes_count": "Mi piace: {count}",
        "login_to_like": "Accedi per mettere like ai commenti e sbloccare la sezione Per Te.",
        "filter_topic": "Filtra per argomento",
        "all_topics": "Tutti",
        "no_posts": "Nessun messaggio. Pubblica il primo.",
        "topic_by": "Argomento: <b>{topic}</b> - Da: <b>{username}</b>",
        "admin_actions": "Azioni admin per post #{post_id}",
        "move_to_category": "Sposta in categoria",
        "move_category": "Sposta categoria",
        "delete_comment": "Elimina commento",
        "category_updated": "Categoria aggiornata.",
        "comment_deleted": "Commento eliminato.",
        "private_header": "Messaggi privati",
        "send_private": "Invia un messaggio privato",
        "no_recipients": "Nessun altro utente disponibile. Chiedi a qualcuno di registrarsi.",
        "recipient": "Destinatario",
        "message_title": "Titolo messaggio",
        "message_title_placeholder": "Oggetto privato breve",
        "private_message": "Messaggio privato",
        "private_placeholder": "Scrivi il tuo messaggio privato...",
        "send_private_btn": "Invia messaggio privato",
        "cannot_self_pm": "Non puoi inviare un messaggio privato a te stesso.",
        "private_sent": "Messaggio privato inviato.",
        "inbox": "Posta ricevuta",
        "sent": "Inviati",
        "inbox_empty": "La tua posta e vuota.",
        "sent_empty": "Nessun messaggio privato inviato.",
        "from": "Da",
        "to": "A",
        "empty_field": "{field_name} non puo essere vuoto.",
        "too_long": "{field_name} e troppo lungo (max {max_len} caratteri).",
        "invalid_topic": "Scegli un argomento valido dalla lista.",
        "site_logo_subtitle": "Comunita e Messaggi Privati",
        "welcome_title": "Benvenuto",
        "welcome_message": "benvenuto in un mondo pieno di storie, vite ed esperienze, perche ognuno di noi ha il diritto di essere ricordato.",
        "enter": "Entra",
    },
    "es": {
        "app_title": "Tablero de Temas",
        "slogan": "todo lo que quieres comunicar",
        "language": "Idioma",
        "logged_in_as": "Conectado como {username}",
        "log_out": "Cerrar sesion",
        "login_needed_sidebar": "Debes iniciar sesion para publicar un mensaje.",
        "menu": "Menu",
        "menu_dashboard": "Tablero",
        "menu_publish": "Publicar mensaje",
        "menu_private": "Mensajes privados",
        "sign_in_required": "Inicio de sesion requerido",
        "sign_in_publish": "Para escribir y publicar un comentario, inicia sesion o crea una cuenta.",
        "sign_in_private": "Para enviar mensajes privados, inicia sesion o crea una cuenta.",
        "tab_login": "Iniciar sesion",
        "tab_signup": "Registrarse",
        "username": "Usuario",
        "password": "Contrasena",
        "login": "Iniciar sesion",
        "invalid_creds": "Usuario o contrasena no validos.",
        "login_success": "Sesion iniciada correctamente.",
        "choose_username": "Elige usuario",
        "first_name": "Nombre",
        "last_name": "Apellido",
        "choose_password": "Elige contrasena",
        "create_account": "Crear cuenta",
        "password_min": "La contrasena debe tener al menos 6 caracteres.",
        "account_created": "Cuenta creada. Ahora puedes iniciar sesion.",
        "username_exists": "El usuario ya existe. Elige otro.",
        "publish_header": "Publicar un mensaje",
        "recent_comments": "Comentarios recientes",
        "posting_as": "Publicando como: {username}",
        "topic": "Tema",
        "private_notice": "Categoria privada: este mensaje sera visible solo para ti y para el destinatario.",
        "private_recipient_required": "Para la categoria Privado debes elegir un destinatario.",
        "post_title": "Titulo",
        "post_title_placeholder": "Resumen corto",
        "message_info": "Mensaje / Informacion",
        "message_placeholder": "Escribe tu mensaje aqui...",
        "publish": "Publicar",
        "published_success": "Tu mensaje se publico en el tablero comun.",
        "publish_fee_info": "Costo de publicacion: {fee} EUR por comentario. Tu saldo: {balance} EUR",
        "buy_credit_1": "Comprar 1 EUR de credito",
        "buy_credit_5": "Comprar 5 EUR de credito",
        "payment_page_ready": "Enlace de pago generado. Haz clic abajo para completar el checkout.",
        "open_checkout": "Abrir checkout seguro",
        "payment_success_amount": "Pago recibido. Se agregaron {amount} EUR a tu saldo.",
        "payment_cancelled": "Pago cancelado.",
        "payment_not_configured": "Pago no configurado. Define STRIPE_SECRET_KEY y APP_BASE_URL.",
        "payment_processing_error": "No se pudo validar la sesion de pago.",
        "insufficient_balance": "Saldo insuficiente. Agrega credito para publicar un comentario.",
        "dashboard_header": "Tablero comun",
        "surname_priority_hint": "Los comentarios de usuarios con tu mismo apellido se muestran primero ({count} encontrados). Podrian ser familiares tuyos.",
        "for_you_header": "Para Ti",
        "for_you_hint": "Recomendado segun temas y comentarios similares a los que te gustaron.",
        "for_you_empty": "Da like a algunos comentarios para recibir recomendaciones personalizadas.",
        "like": "Me gusta",
        "unlike": "Ya no me gusta",
        "likes_count": "Me gusta: {count}",
        "login_to_like": "Inicia sesion para dar like a comentarios y desbloquear tu seccion Para Ti.",
        "filter_topic": "Filtrar por tema",
        "all_topics": "Todos",
        "no_posts": "Aun no hay mensajes. Publica el primero.",
        "topic_by": "Tema: <b>{topic}</b> - Por: <b>{username}</b>",
        "admin_actions": "Acciones admin para post #{post_id}",
        "move_to_category": "Mover a categoria",
        "move_category": "Mover categoria",
        "delete_comment": "Eliminar comentario",
        "category_updated": "Categoria actualizada.",
        "comment_deleted": "Comentario eliminado.",
        "private_header": "Mensajes privados",
        "send_private": "Enviar mensaje privado",
        "no_recipients": "No hay otros usuarios disponibles. Pide a alguien que se registre.",
        "recipient": "Destinatario",
        "message_title": "Titulo del mensaje",
        "message_title_placeholder": "Asunto privado corto",
        "private_message": "Mensaje privado",
        "private_placeholder": "Escribe tu mensaje privado...",
        "send_private_btn": "Enviar mensaje privado",
        "cannot_self_pm": "No puedes enviarte un mensaje privado a ti mismo.",
        "private_sent": "Mensaje privado enviado.",
        "inbox": "Bandeja de entrada",
        "sent": "Enviados",
        "inbox_empty": "Tu bandeja esta vacia.",
        "sent_empty": "No hay mensajes privados enviados.",
        "from": "De",
        "to": "Para",
        "empty_field": "{field_name} no puede estar vacio.",
        "too_long": "{field_name} es demasiado largo (max {max_len} caracteres).",
        "invalid_topic": "Elige un tema valido de la lista.",
        "site_logo_subtitle": "Comunidad y Mensajes Privados",
        "welcome_title": "Bienvenido",
        "welcome_message": "bienvenido a un mundo lleno de historias, vidas y experiencias, porque cada uno de nosotros tiene derecho a ser recordado.",
        "enter": "Entrar",
    },
}
TOPIC_LABELS = {
    "en": {
        "Love": "Love",
        "Life Stories": "Life Stories",
        "Discussion": "Discussion",
        "Gossip": "Gossip",
        "Hate": "Hate",
        "Personal": "Personal",
        "Private": "Private",
        "School": "School",
        "Work": "Work",
        "Relationships": "Relationships",
        "Health": "Health",
        "Other": "Other",
    },
    "it": {
        "Love": "Amore",
        "Life Stories": "Storie di vita",
        "Discussion": "Discussione",
        "Gossip": "Pettegolezzi",
        "Hate": "Odio",
        "Personal": "Personale",
        "Private": "Privato",
        "School": "Scuola",
        "Work": "Lavoro",
        "Relationships": "Relazioni",
        "Health": "Salute",
        "Other": "Altro",
    },
    "es": {
        "Love": "Amor",
        "Life Stories": "Historias de vida",
        "Discussion": "Discusion",
        "Gossip": "Chismes",
        "Hate": "Odio",
        "Personal": "Personal",
        "Private": "Privado",
        "School": "Escuela",
        "Work": "Trabajo",
        "Relationships": "Relaciones",
        "Health": "Salud",
        "Other": "Otro",
    },
}


def t(key: str, **kwargs) -> str:
    lang = st.session_state.get("language", "en")
    text = TRANSLATIONS.get(lang, TRANSLATIONS["en"]).get(key, TRANSLATIONS["en"].get(key, key))
    if kwargs:
        return text.format(**kwargs)
    return text


def topic_label(topic: str) -> str:
    lang = st.session_state.get("language", "en")
    return TOPIC_LABELS.get(lang, TOPIC_LABELS["en"]).get(topic, topic)


def detect_system_language() -> str:
    system_locale = locale.getlocale()[0] or ""
    lowered = system_locale.lower()

    if lowered.startswith("it") or "italian" in lowered:
        return "it"
    if lowered.startswith("es") or "spanish" in lowered:
        return "es"
    return "en"


def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with get_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                first_name TEXT,
                last_name TEXT,
                password_hash TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS posts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                topic TEXT NOT NULL,
                private_recipient_username TEXT,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS private_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_username TEXT NOT NULL,
                recipient_username TEXT NOT NULL,
                title TEXT NOT NULL,
                message TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS user_wallets (
                username TEXT PRIMARY KEY,
                balance_eur REAL NOT NULL DEFAULT 0
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS payment_transactions (
                checkout_session_id TEXT PRIMARY KEY,
                username TEXT NOT NULL,
                amount_eur REAL NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS comment_likes (
                username TEXT NOT NULL,
                post_id INTEGER NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (username, post_id)
            )
            """
        )

        post_columns = [row["name"] for row in conn.execute("PRAGMA table_info(posts)").fetchall()]
        if "private_recipient_username" not in post_columns:
            conn.execute("ALTER TABLE posts ADD COLUMN private_recipient_username TEXT")

        user_columns = [row["name"] for row in conn.execute("PRAGMA table_info(users)").fetchall()]
        if "first_name" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN first_name TEXT")
        if "last_name" not in user_columns:
            conn.execute("ALTER TABLE users ADD COLUMN last_name TEXT")

        conn.commit()


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def create_user(username: str, first_name: str, last_name: str, password: str) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO users (username, first_name, last_name, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (username, first_name, last_name, hash_password(password), now),
        )
        conn.execute(
            "INSERT OR IGNORE INTO user_wallets (username, balance_eur) VALUES (?, 0)",
            (username,),
        )
        conn.commit()


def get_user_display_name(username: str) -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT first_name, last_name FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row:
        return username

    first_name = (row["first_name"] or "").strip()
    last_name = (row["last_name"] or "").strip()
    full_name = f"{first_name} {last_name}".strip()
    return full_name if full_name else username


def get_user_last_name(username: str) -> str:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT last_name FROM users WHERE username = ?",
            (username,),
        ).fetchone()
    return (row["last_name"] or "").strip() if row else ""


def ensure_user_wallet(username: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO user_wallets (username, balance_eur) VALUES (?, 0)",
            (username,),
        )
        conn.commit()


def get_user_balance(username: str) -> float:
    ensure_user_wallet(username)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT balance_eur FROM user_wallets WHERE username = ?",
            (username,),
        ).fetchone()
    return float(row["balance_eur"]) if row else 0.0


def add_user_credit(username: str, amount_eur: float) -> None:
    ensure_user_wallet(username)
    with get_connection() as conn:
        conn.execute(
            "UPDATE user_wallets SET balance_eur = balance_eur + ? WHERE username = ?",
            (amount_eur, username),
        )
        conn.commit()


def charge_publish_fee(username: str, amount_eur: float) -> bool:
    ensure_user_wallet(username)
    with get_connection() as conn:
        row = conn.execute(
            "SELECT balance_eur FROM user_wallets WHERE username = ?",
            (username,),
        ).fetchone()

        if not row or float(row["balance_eur"]) < amount_eur:
            return False

        conn.execute(
            "UPDATE user_wallets SET balance_eur = balance_eur - ? WHERE username = ?",
            (amount_eur, username),
        )
        conn.commit()
    return True


def authenticate_user(username: str, password: str) -> bool:
    if (
        username.lower() == ADMIN_USERNAME.lower()
        and ADMIN_PASSWORD_HASH
        and hash_password(password) == ADMIN_PASSWORD_HASH
    ):
        return True

    with get_connection() as conn:
        row = conn.execute(
            "SELECT password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()

    if not row:
        return False
    return row["password_hash"] == hash_password(password)


def is_admin_user(username: str) -> bool:
    return username.lower() == ADMIN_USERNAME


def add_post(
    username: str,
    topic: str,
    title: str,
    message: str,
    private_recipient_username: str | None = None,
) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO posts (username, topic, private_recipient_username, title, message, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (username, topic, private_recipient_username, title, message, now),
        )
        conn.commit()


def like_post(username: str, post_id: int) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with get_connection() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO comment_likes (username, post_id, created_at) VALUES (?, ?, ?)",
            (username, post_id, now),
        )
        conn.commit()


def unlike_post(username: str, post_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM comment_likes WHERE username = ? AND post_id = ?", (username, post_id))
        conn.commit()


def get_user_liked_post_ids(username: str) -> set[int]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT post_id FROM comment_likes WHERE username = ?",
            (username,),
        ).fetchall()
    return {int(row["post_id"]) for row in rows}


def get_like_counts_for_posts(post_ids: list[int]) -> dict[int, int]:
    if not post_ids:
        return {}

    placeholders = ",".join(["?"] * len(post_ids))
    with get_connection() as conn:
        rows = conn.execute(
            f"""
            SELECT post_id, COUNT(*) AS likes_count
            FROM comment_likes
            WHERE post_id IN ({placeholders})
            GROUP BY post_id
            """,
            tuple(post_ids),
        ).fetchall()

    counts = {int(row["post_id"]): int(row["likes_count"]) for row in rows}
    for post_id in post_ids:
        counts.setdefault(int(post_id), 0)
    return counts


def _tokenize_text(text: str) -> list[str]:
    words = re.findall(r"[a-zA-Z]{4,}", (text or "").lower())
    stop_words = {
        "this", "that", "with", "from", "have", "your", "will", "they", "them", "about",
        "pero", "sono", "porque", "della", "delle", "degli", "dello", "para", "como", "dove",
    }
    return [w for w in words if w not in stop_words]


def get_for_you_posts(posts_df: pd.DataFrame, username: str, limit: int = 8) -> pd.DataFrame:
    if posts_df.empty:
        return posts_df

    liked_ids = get_user_liked_post_ids(username)
    if not liked_ids:
        return posts_df.iloc[0:0]

    liked_df = posts_df[posts_df["id"].isin(liked_ids)]
    if liked_df.empty:
        return posts_df.iloc[0:0]

    topic_weights = Counter(liked_df["topic"].astype(str).tolist())
    liked_text = " ".join((liked_df["title"].astype(str) + " " + liked_df["message"].astype(str)).tolist())
    token_weights = Counter(_tokenize_text(liked_text))

    candidates = posts_df[~posts_df["id"].isin(liked_ids)].copy()
    if candidates.empty:
        return candidates

    def score_row(row: pd.Series) -> float:
        topic_score = float(topic_weights.get(str(row["topic"]), 0)) * 3.0
        row_tokens = _tokenize_text(f"{row['title']} {row['message']}")
        text_score = float(sum(token_weights.get(token, 0) for token in row_tokens))
        return topic_score + text_score

    candidates["_score"] = candidates.apply(score_row, axis=1)
    ranked = candidates[candidates["_score"] > 0].sort_values(by=["_score", "id"], ascending=[False, False])
    return ranked.drop(columns=["_score"]).head(limit)


def delete_post(post_id: int) -> None:
    with get_connection() as conn:
        conn.execute("DELETE FROM posts WHERE id = ?", (post_id,))
        conn.commit()


def move_post_to_topic(post_id: int, new_topic: str) -> None:
    with get_connection() as conn:
        conn.execute(
            "UPDATE posts SET topic = ? WHERE id = ?",
            (new_topic, post_id),
        )
        conn.commit()


def send_private_message(sender_username: str, recipient_username: str, title: str, message: str) -> None:
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    with get_connection() as conn:
        conn.execute(
            """
            INSERT INTO private_messages (sender_username, recipient_username, title, message, created_at)
            VALUES (?, ?, ?, ?, ?)
            """,
            (sender_username, recipient_username, title, message, now),
        )
        conn.commit()


def load_inbox_messages(username: str) -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM private_messages
            WHERE recipient_username = ?
            ORDER BY id DESC
            """,
            (username,),
        ).fetchall()

    if not rows:
        return pd.DataFrame(columns=["id", "sender_username", "recipient_username", "title", "message", "created_at"])
    return pd.DataFrame([dict(row) for row in rows])


def load_sent_messages(username: str) -> pd.DataFrame:
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT * FROM private_messages
            WHERE sender_username = ?
            ORDER BY id DESC
            """,
            (username,),
        ).fetchall()

    if not rows:
        return pd.DataFrame(columns=["id", "sender_username", "recipient_username", "title", "message", "created_at"])
    return pd.DataFrame([dict(row) for row in rows])


def get_registered_usernames() -> list[str]:
    with get_connection() as conn:
        rows = conn.execute("SELECT username FROM users ORDER BY username").fetchall()
    return [row["username"] for row in rows]


def get_all_usernames() -> list[str]:
    usernames = set(get_registered_usernames())
    usernames.add(ADMIN_USERNAME)
    return sorted(usernames, key=lambda name: name.lower())


def load_posts(topic_filter: str = "All", viewer_username: str = "") -> pd.DataFrame:
    viewer_username = viewer_username.strip()

    with get_connection() as conn:
        if topic_filter == "All":
            if viewer_username:
                rows = conn.execute(
                    """
                    SELECT p.*, u.first_name AS author_first_name, u.last_name AS author_last_name
                    FROM posts p
                    LEFT JOIN users u ON u.username = p.username
                    WHERE p.topic != 'Private' OR p.username = ? OR p.private_recipient_username = ?
                    ORDER BY p.id DESC
                    """,
                    (viewer_username, viewer_username),
                ).fetchall()
            else:
                rows = conn.execute(
                    """
                    SELECT p.*, u.first_name AS author_first_name, u.last_name AS author_last_name
                    FROM posts p
                    LEFT JOIN users u ON u.username = p.username
                    WHERE p.topic != 'Private'
                    ORDER BY p.id DESC
                    """
                ).fetchall()
        else:
            if topic_filter == "Private":
                if viewer_username:
                    rows = conn.execute(
                        """
                        SELECT p.*, u.first_name AS author_first_name, u.last_name AS author_last_name
                        FROM posts p
                        LEFT JOIN users u ON u.username = p.username
                        WHERE p.topic = 'Private' AND (p.username = ? OR p.private_recipient_username = ?)
                        ORDER BY p.id DESC
                        """,
                        (viewer_username, viewer_username),
                    ).fetchall()
                else:
                    rows = []
            else:
                rows = conn.execute(
                    """
                    SELECT p.*, u.first_name AS author_first_name, u.last_name AS author_last_name
                    FROM posts p
                    LEFT JOIN users u ON u.username = p.username
                    WHERE p.topic = ?
                    ORDER BY p.id DESC
                    """,
                    (topic_filter,),
                ).fetchall()

    if not rows:
        return pd.DataFrame(
            columns=[
                "id", "username", "topic", "private_recipient_username", "title", "message", "created_at",
                "author_first_name", "author_last_name",
            ]
        )
    return pd.DataFrame([dict(row) for row in rows])


def prioritize_posts_by_surname(posts_df: pd.DataFrame, viewer_username: str) -> tuple[pd.DataFrame, int]:
    if posts_df.empty:
        return posts_df, 0

    viewer_last_name = get_user_last_name(viewer_username).strip().lower()
    if not viewer_last_name or "author_last_name" not in posts_df.columns:
        return posts_df, 0

    ranked = posts_df.copy()
    ranked["_same_surname"] = ranked["author_last_name"].fillna("").astype(str).str.strip().str.lower() == viewer_last_name
    matches = int(ranked["_same_surname"].sum())
    ranked = ranked.sort_values(by=["_same_surname", "id"], ascending=[False, False], kind="stable")
    return ranked.drop(columns=["_same_surname"]), matches


def get_topics() -> list[str]:
    return TOPIC_OPTIONS


def validate_text(value: str, field_name: str, max_len: int) -> str:
    value = value.strip()
    if not value:
        raise ValueError(t("empty_field", field_name=field_name))
    if len(value) > max_len:
        raise ValueError(t("too_long", field_name=field_name, max_len=max_len))
    return value


def validate_topic(topic: str) -> str:
    if topic not in TOPIC_OPTIONS:
        raise ValueError(t("invalid_topic"))
    return topic


def ensure_auth_state() -> None:
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "auth_username" not in st.session_state:
        st.session_state.auth_username = ""
    if "language" not in st.session_state:
        st.session_state.language = detect_system_language()
    if "welcome_popup_seen" not in st.session_state:
        st.session_state.welcome_popup_seen = False


@st.dialog(" ")
def show_welcome_popup() -> None:
    st.markdown(
        f'<div style="text-align:center; font-size:1.35rem; font-weight:700; color:#1f4f73; margin-bottom:6px;">{t("welcome_title")}</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(155deg, #e2f3ff 0%, #ffffff 70%);
            border: 1px solid #cfe6f9;
            border-radius: 14px;
            padding: 20px;
            margin-top: 6px;
            margin-bottom: 10px;
            text-align: center;
            font-size: 1.15rem;
            line-height: 1.5;
            color: #1f4f73;
        ">
            {t("welcome_message")}
        </div>
        """,
        unsafe_allow_html=True,
    )
    if st.button(t("enter")):
        st.rerun()


def render_auth_forms() -> None:
    tab_login, tab_signup = st.tabs([t("tab_login"), t("tab_signup")])

    with tab_login:
        with st.form("login_form"):
            login_username = st.text_input(t("username"), key="login_username")
            login_password = st.text_input(t("password"), type="password", key="login_password")
            login_submit = st.form_submit_button(t("login"))

        if login_submit:
            try:
                cleaned_username = validate_text(login_username, t("username"), 40)
                cleaned_password = validate_text(login_password, t("password"), 120)
                if authenticate_user(cleaned_username, cleaned_password):
                    st.session_state.logged_in = True
                    st.session_state.auth_username = cleaned_username
                    ensure_user_wallet(cleaned_username)
                    st.success(t("login_success"))
                    st.rerun()
                st.error(t("invalid_creds"))
            except ValueError as err:
                st.error(str(err))

    with tab_signup:
        with st.form("signup_form"):
            signup_username = st.text_input(t("choose_username"), key="signup_username")
            signup_first_name = st.text_input(t("first_name"), key="signup_first_name")
            signup_last_name = st.text_input(t("last_name"), key="signup_last_name")
            signup_password = st.text_input(t("choose_password"), type="password", key="signup_password")
            signup_submit = st.form_submit_button(t("create_account"))

        if signup_submit:
            try:
                cleaned_username = validate_text(signup_username, t("username"), 40)
                cleaned_first_name = validate_text(signup_first_name, t("first_name"), 60)
                cleaned_last_name = validate_text(signup_last_name, t("last_name"), 60)
                cleaned_password = validate_text(signup_password, t("password"), 120)
                if len(cleaned_password) < 6:
                    raise ValueError(t("password_min"))
                create_user(cleaned_username, cleaned_first_name, cleaned_last_name, cleaned_password)
                st.success(t("account_created"))
            except sqlite3.IntegrityError:
                st.error(t("username_exists"))
            except ValueError as err:
                st.error(str(err))


def render_post_card(row: pd.Series) -> None:
    first_name = str(row.get("author_first_name", "") or "").strip()
    last_name = str(row.get("author_last_name", "") or "").strip()
    display_name = f"{first_name} {last_name}".strip() or row["username"]
    st.markdown(
        f"""
        <div style="border:1px solid #dddddd; border-radius:10px; padding:14px; margin-bottom:12px;">
            <div style="font-size:12px; color:#666;">#{row['id']} - {row['created_at']}</div>
            <div style="margin-top:4px; font-weight:700; font-size:18px;">{row['title']}</div>
            <div style="margin-top:2px; font-size:14px; color:#444;">{t('topic_by', topic=topic_label(row['topic']), username=display_name)}</div>
            <div style="margin-top:10px; font-size:15px; white-space:pre-wrap;">{row['message']}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_admin_controls(row: pd.Series) -> None:
    post_id = int(row["id"])
    current_topic = row["topic"]
    current_index = TOPIC_OPTIONS.index(current_topic) if current_topic in TOPIC_OPTIONS else 0

    with st.expander(t("admin_actions", post_id=post_id)):
        new_topic = st.selectbox(
            t("move_to_category"),
            options=TOPIC_OPTIONS,
            index=current_index,
            key=f"move_topic_{post_id}",
            format_func=topic_label,
        )

        col_move, col_delete = st.columns(2)
        with col_move:
            if st.button(t("move_category"), key=f"move_btn_{post_id}"):
                try:
                    validated_topic = validate_topic(new_topic)
                    move_post_to_topic(post_id, validated_topic)
                    st.success(t("category_updated"))
                    st.rerun()
                except ValueError as err:
                    st.error(str(err))

        with col_delete:
            if st.button(t("delete_comment"), key=f"delete_btn_{post_id}"):
                delete_post(post_id)
                st.success(t("comment_deleted"))
                st.rerun()


def render_posts_feed(
    posts_df: pd.DataFrame,
    is_admin: bool,
    viewer_username: str = "",
    liked_ids: set[int] | None = None,
    like_counts: dict[int, int] | None = None,
    enable_likes: bool = False,
) -> None:
    if posts_df.empty:
        st.info(t("no_posts"))
        return

    liked_ids = liked_ids or set()
    like_counts = like_counts or {}

    for _, row in posts_df.iterrows():
        render_post_card(row)

        if enable_likes:
            post_id = int(row["id"])
            col_like, col_count = st.columns([1, 3])
            with col_like:
                if viewer_username:
                    already_liked = post_id in liked_ids
                    button_label = t("unlike") if already_liked else t("like")
                    if st.button(button_label, key=f"like_btn_{post_id}"):
                        if already_liked:
                            unlike_post(viewer_username, post_id)
                        else:
                            like_post(viewer_username, post_id)
                        st.rerun()
                else:
                    st.caption(t("login_to_like"))
            with col_count:
                st.caption(t("likes_count", count=like_counts.get(post_id, 0)))

        if is_admin:
            render_admin_controls(row)


def render_private_messages_page(current_username: str) -> None:
    st.subheader(t("private_header"))

    all_usernames = get_all_usernames()
    recipients = [name for name in all_usernames if name.lower() != current_username.lower()]

    st.markdown(f"### {t('send_private')}")
    if not recipients:
        st.info(t("no_recipients"))
    else:
        with st.form("private_message_form", clear_on_submit=True):
            recipient = st.selectbox(t("recipient"), options=recipients)
            pm_title = st.text_input(t("message_title"), placeholder=t("message_title_placeholder"))
            pm_body = st.text_area(t("private_message"), height=180, placeholder=t("private_placeholder"))
            pm_submit = st.form_submit_button(t("send_private_btn"))

        if pm_submit:
            try:
                cleaned_recipient = validate_text(recipient, t("recipient"), 40)
                if cleaned_recipient.lower() == current_username.lower():
                    raise ValueError(t("cannot_self_pm"))
                cleaned_title = validate_text(pm_title, t("message_title"), 120)
                cleaned_body = validate_text(pm_body, t("private_message"), 5000)
                send_private_message(current_username, cleaned_recipient, cleaned_title, cleaned_body)
                st.success(t("private_sent"))
                st.rerun()
            except ValueError as err:
                st.error(str(err))

    st.divider()

    tab_inbox, tab_sent = st.tabs([t("inbox"), t("sent")])

    with tab_inbox:
        inbox_df = load_inbox_messages(current_username)
        if inbox_df.empty:
            st.info(t("inbox_empty"))
        else:
            for _, row in inbox_df.iterrows():
                st.markdown(
                    f"""
                    <div style="border:1px solid #d7e9f7; border-radius:10px; padding:12px; margin-bottom:10px; background:#ffffff;">
                        <div style="font-size:12px; color:#666;">{row['created_at']}</div>
                        <div style="margin-top:4px; font-weight:700; font-size:16px;">{row['title']}</div>
                        <div style="margin-top:2px; font-size:14px; color:#444;">{t('from')}: <b>{row['sender_username']}</b></div>
                        <div style="margin-top:8px; font-size:15px; white-space:pre-wrap;">{row['message']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    with tab_sent:
        sent_df = load_sent_messages(current_username)
        if sent_df.empty:
            st.info(t("sent_empty"))
        else:
            for _, row in sent_df.iterrows():
                st.markdown(
                    f"""
                    <div style="border:1px solid #d7e9f7; border-radius:10px; padding:12px; margin-bottom:10px; background:#ffffff;">
                        <div style="font-size:12px; color:#666;">{row['created_at']}</div>
                        <div style="margin-top:4px; font-weight:700; font-size:16px;">{row['title']}</div>
                        <div style="margin-top:2px; font-size:14px; color:#444;">{t('to')}: <b>{row['recipient_username']}</b></div>
                        <div style="margin-top:8px; font-size:15px; white-space:pre-wrap;">{row['message']}</div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


def apply_theme() -> None:
    st.markdown(
        """
        <style>
            .stApp {
                background: linear-gradient(160deg, #dff1ff 0%, #eef8ff 45%, #ffffff 100%);
            }
            [data-testid="stSidebar"] {
                background: #f4fbff;
            }
            div[data-testid="stMetric"] {
                background: #ffffff;
                border: 1px solid #d7e9f7;
                border-radius: 10px;
                padding: 8px;
            }
            div[role="dialog"] {
                position: fixed !important;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            div[role="dialog"] > div {
                width: min(760px, 92vw);
                margin: 0 auto;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_site_logo(container) -> None:
    container.markdown(
        """
        <div style="
            margin-bottom: 8px;
            background: linear-gradient(145deg, #ffffff 0%, #e7f4ff 100%);
            border: 1px solid #cfe6f9;
            border-radius: 12px;
            padding: 10px 12px;
        ">
        </div>
        """,
        unsafe_allow_html=True,
    )

    if LOGO_PATH.exists():
        container.image(str(LOGO_PATH), use_container_width=True)
    else:
        container.markdown(
            '<div style="text-align:center; font-size: 24px; line-height: 1;">💬</div>',
            unsafe_allow_html=True,
        )

    container.markdown(
        f'<div style="text-align:center; font-size: 12px; color: #4a6c86; margin-top: 4px; margin-bottom: 10px;">{t("site_logo_subtitle")}</div>',
        unsafe_allow_html=True,
    )


def main() -> None:
    page_icon = str(LOGO_PATH) if LOGO_PATH.exists() else "🗂️"
    st.set_page_config(page_title=SITE_NAME, page_icon=page_icon, layout="wide")
    init_db()
    apply_theme()
    ensure_auth_state()

    st.sidebar.markdown(
        f'<div style="font-size:1.1rem; font-weight:700; color:#1f4f73; margin-top:2px; margin-bottom:8px;">{SITE_NAME}</div>',
        unsafe_allow_html=True,
    )

    selected_language = st.sidebar.selectbox(
        t("language"),
        options=LANGUAGE_CODES,
        index=LANGUAGE_CODES.index(st.session_state.language),
        format_func=lambda code: LANGUAGE_NAMES[code],
    )
    st.session_state.language = selected_language

    if "site" not in st.query_params:
        st.query_params["site"] = SITE_NAME

    if not st.session_state.welcome_popup_seen:
        st.session_state.welcome_popup_seen = True
        show_welcome_popup()

    st.title(t("app_title"))
    st.markdown(
        f'<div style="font-size: 1.2rem; font-weight: 600; color: #1f4f73; margin-bottom: 0.5rem;">{t("slogan")}</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.logged_in:
        st.sidebar.success(t("logged_in_as", username=st.session_state.auth_username))
        if st.sidebar.button(t("log_out")):
            st.session_state.logged_in = False
            st.session_state.auth_username = ""
            st.rerun()
    else:
        render_site_logo(st.sidebar)
        st.sidebar.info(t("login_needed_sidebar"))

    menu_options = [t("menu_dashboard"), t("menu_publish"), t("menu_private")]
    menu = st.sidebar.radio(t("menu"), options=menu_options)

    if menu == t("menu_publish"):
        if not st.session_state.logged_in:
            st.subheader(t("sign_in_required"))
            st.write(t("sign_in_publish"))
            render_auth_forms()
            return

        st.subheader(t("recent_comments"))
        recent_posts_df = load_posts("All", st.session_state.auth_username).head(5)
        is_admin = st.session_state.logged_in and is_admin_user(st.session_state.auth_username)
        render_posts_feed(recent_posts_df, is_admin)

        st.divider()
        st.subheader(t("publish_header"))
        st.write(t("posting_as", username=st.session_state.auth_username))

        recipients = [
            name for name in get_all_usernames()
            if name.lower() != st.session_state.auth_username.lower()
        ]

        with st.form("publish_form", clear_on_submit=True):
            topic = st.selectbox(t("topic"), options=TOPIC_OPTIONS, format_func=topic_label)
            private_recipient = ""
            if topic == "Private":
                st.info(t("private_notice"))
                if recipients:
                    private_recipient = st.selectbox(t("recipient"), options=recipients)
                else:
                    st.info(t("no_recipients"))
            title = st.text_input(t("post_title"), placeholder=t("post_title_placeholder"))
            message = st.text_area(t("message_info"), height=220, placeholder=t("message_placeholder"))
            submitted = st.form_submit_button(t("publish"))

        if submitted:
            try:
                cleaned_topic = validate_topic(topic)
                cleaned_title = validate_text(title, t("post_title"), 120)
                cleaned_message = validate_text(message, t("message_info"), 5000)
                cleaned_private_recipient = None
                if cleaned_topic == "Private":
                    if not recipients:
                        raise ValueError(t("private_recipient_required"))
                    cleaned_private_recipient = validate_text(private_recipient, t("recipient"), 40)
                    if cleaned_private_recipient.lower() == st.session_state.auth_username.lower():
                        raise ValueError(t("cannot_self_pm"))

                add_post(
                    st.session_state.auth_username,
                    cleaned_topic,
                    cleaned_title,
                    cleaned_message,
                    cleaned_private_recipient,
                )
                st.success(t("published_success"))
            except ValueError as err:
                st.error(str(err))

    if menu == t("menu_dashboard"):
        st.subheader(t("dashboard_header"))
        topics = get_topics()
        selected_topic = st.selectbox(
            t("filter_topic"),
            options=["All"] + topics,
            format_func=lambda value: t("all_topics") if value == "All" else topic_label(value),
        )
        viewer_username = st.session_state.auth_username if st.session_state.logged_in else ""
        posts_df = load_posts(selected_topic, viewer_username)
        like_counts = get_like_counts_for_posts(posts_df["id"].astype(int).tolist()) if not posts_df.empty else {}
        liked_ids = get_user_liked_post_ids(viewer_username) if viewer_username else set()
        is_admin = st.session_state.logged_in and is_admin_user(st.session_state.auth_username)

        if st.session_state.logged_in:
            posts_df, same_surname_count = prioritize_posts_by_surname(posts_df, st.session_state.auth_username)
            if same_surname_count > 0:
                st.info(t("surname_priority_hint", count=same_surname_count))

            for_you_df = get_for_you_posts(posts_df, st.session_state.auth_username)
            st.markdown(f"### {t('for_you_header')}")
            st.caption(t("for_you_hint"))
            if for_you_df.empty:
                st.info(t("for_you_empty"))
            else:
                for_you_counts = get_like_counts_for_posts(for_you_df["id"].astype(int).tolist())
                render_posts_feed(
                    for_you_df,
                    is_admin,
                    viewer_username,
                    liked_ids,
                    for_you_counts,
                    enable_likes=True,
                )
            st.divider()
        st.divider()
        render_posts_feed(
            posts_df,
            is_admin,
            viewer_username,
            liked_ids,
            like_counts,
            enable_likes=True,
        )

    if menu == t("menu_private"):
        if not st.session_state.logged_in:
            st.subheader(t("sign_in_required"))
            st.write(t("sign_in_private"))
            render_auth_forms()
            return

        render_private_messages_page(st.session_state.auth_username)


if __name__ == "__main__":
    main()
