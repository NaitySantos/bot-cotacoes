import requests
from bs4 import BeautifulSoup # pyright: ignore[reportMissingImports]
import smtplib
from email.mime.text import MIMEText
import time

# ============================================================
# CONFIGURAÇÕES — edite apenas este bloco
# ============================================================
PRODUTO = "teclado mecanico"          # O que você quer buscar
PRECO_ALVO = 200.00                   # Avisa quando ficar abaixo deste valor
SEU_EMAIL = "seuemail@gmail.com"      # Seu Gmail
SUA_SENHA = "sua_senha_de_app_aqui"        # Senha de app do Gmail (ver Passo 5)
EMAIL_DESTINO = "seuemail@gmail.com"  # Para onde mandar o aviso
# ============================================================


def buscar_preco(produto):
    """Busca o menor preço do produto no Mercado Livre."""
    url = f"https://lista.mercadolivre.com.br/{produto.replace(' ', '-')}"
    headers = {"User-Agent": "Mozilla/5.0"}

    resposta = requests.get(url, headers=headers)
    soup = BeautifulSoup(resposta.text, "html.parser")

    precos = []
    for item in soup.select(".andes-money-amount__fraction"):
        texto = item.get_text().replace(".", "").replace(",", ".")
        try:
            precos.append(float(texto))
        except ValueError:
            continue

    if precos:
        return min(precos)
    return None


def enviar_email(preco, produto):
    """Envia um e-mail de alerta com o preço encontrado."""
    assunto = f"[ALERTA] Preco baixo: {produto}"
    corpo = f"""
Oi! Seu bot encontrou uma oferta:

Produto: {produto}
Preço atual: R$ {preco:.2f}
Seu alvo:   R$ {PRECO_ALVO:.2f}

Confira agora: https://lista.mercadolivre.com.br/{produto.replace(' ', '-')}
    """

    msg = MIMEText(corpo)
    msg["Subject"] = assunto
    msg["From"] = SEU_EMAIL
    msg["To"] = EMAIL_DESTINO

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as servidor:
        servidor.login(SEU_EMAIL, SUA_SENHA)
        servidor.sendmail(SEU_EMAIL, EMAIL_DESTINO, msg.as_string())

    print("[BOT] E-mail enviado!")


def rodar_bot():
    """Loop principal — verifica o preço a cada hora."""
    print(f"[BOT] Iniciado! Monitorando: {PRODUTO}")
    print(f"      Alvo: R$ {PRECO_ALVO:.2f}\n")

    while True:
        print("[BOT] Buscando preco...")
        preco = buscar_preco(PRODUTO)

        if preco:
            print(f"      Menor preco encontrado: R$ {preco:.2f}")
            if preco <= PRECO_ALVO:
                print("[BOT] Preco abaixo do alvo! Enviando e-mail...")
                enviar_email(preco, PRODUTO)
            else:
                print("      Ainda acima do alvo. Aguardando...")
        else:
            print("      Nao foi possivel buscar o preco agora.")

        print("[BOT] Proxima verificacao em 1 hora.\n")
        time.sleep(3600)


if __name__ == "__main__":
    rodar_bot()