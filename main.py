import telebot
import requests
from bs4 import BeautifulSoup
import time
import threading
import os
from dotenv import load_dotenv

load_dotenv()

CHAVE_API = os.environ.get("TELEGRAM_API_KEY")
chat_id_usuario = os.environ.get("TELEGRAM_CHAT_ID")

bot = telebot.TeleBot(CHAVE_API)

vagas_notificadas = set()

palavras_chave = ["frontend", "react", "javascript", "html", "css", "mysql", "postgresql", "python"]

def buscar_vagas():
    query = "%20".join(palavras_chave)
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location=Brasil&sortBy=DD"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    vagas = []
    for vaga in soup.select("li"):
        titulo = vaga.select_one("h3").text.strip() if vaga.select_one("h3") else "Sem título"
        empresa = vaga.select_one("h4").text.strip() if vaga.select_one("h4") else "Sem empresa"
        link = vaga.select_one("a")["href"] if vaga.select_one("a") else ""

        if link and link not in vagas_notificadas:
            vagas.append((titulo, empresa, link))
    return vagas

def verificar_novas_vagas():
    while True:
        vagas = buscar_vagas()
        for titulo, empresa, link in vagas:
            if link not in vagas_notificadas:
                mensagem = f"💼 *{titulo}*\n🏢 {empresa}\n🔗 {link}"
                bot.send_message(chat_id_usuario, mensagem, parse_mode="Markdown")
                vagas_notificadas.add(link)
        time.sleep(1800)  # Verifica a cada 30 minutos

# Roda em thread separada
threading.Thread(target=verificar_novas_vagas, daemon=True).start()

@bot.message_handler(commands=["start"])
def start(mensagem):
    texto = f"""
👋 Bem-vindo!

Este bot vai te avisar quando surgirem novas vagas no LinkedIn com base nas palavras-chave: `{", ".join(palavras_chave)}`

Você será notificado automaticamente com as vagas mais recentes no Brasil.
"""
    bot.send_message(mensagem.chat.id, texto, parse_mode="Markdown")

bot.polling()