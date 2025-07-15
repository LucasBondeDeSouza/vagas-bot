import os
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import telebot

load_dotenv()

CHAVE_API = os.environ.get("TELEGRAM_API_KEY")
chat_id_usuario = os.environ.get("TELEGRAM_CHAT_ID")
bot = telebot.TeleBot(CHAVE_API)

palavras_chave = ["frontend", "react", "javascript", "html", "css", "mysql", "postgresql", "python"]
ARQUIVO_VAGAS_ENVIADAS = "vagas_enviadas.txt"

def carregar_vagas_enviadas():
    if os.path.exists(ARQUIVO_VAGAS_ENVIADAS):
        with open(ARQUIVO_VAGAS_ENVIADAS, "r") as f:
            return set(linha.strip() for linha in f)
    return set()

def salvar_vaga_enviada(link):
    with open(ARQUIVO_VAGAS_ENVIADAS, "a") as f:
        f.write(link + "\n")

def buscar_vagas():
    query = "%20".join(palavras_chave)
    url = f"https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords={query}&location=Brazil&geoId=106057199&sortBy=DD"
    headers = { "User-Agent": "Mozilla/5.0" }
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")

    vagas = []
    for vaga in soup.select("li"):
        titulo = vaga.select_one("h3").text.strip() if vaga.select_one("h3") else "Sem título"
        empresa = vaga.select_one("h4").text.strip() if vaga.select_one("h4") else "Sem empresa"
        link = vaga.select_one("a")["href"] if vaga.select_one("a") else ""
        if link:
            vagas.append((titulo, empresa, link))
    return vagas

def enviar_vagas():
    vagas_enviadas = carregar_vagas_enviadas()
    vagas = buscar_vagas()
    novas_vagas = 0

    for titulo, empresa, link in vagas:
        if link not in vagas_enviadas:
            mensagem = f"💼 *{titulo}*\n🏢 {empresa}\n🔗 {link}"
            bot.send_message(chat_id_usuario, mensagem, parse_mode="Markdown")
            salvar_vaga_enviada(link)
            novas_vagas += 1
        if novas_vagas >= 5:
            break

enviar_vagas()