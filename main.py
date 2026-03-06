import json
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

import os
TOKEN = os.getenv("TOKEN")

FILE = "argent.json"

def charger():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return {"solde":740,40}

def sauver(data):
    with open(FILE,"w") as f:
        json.dump(data,f)

data = charger()
etat = None

keyboard = [["Gain","Perte"],["Solde"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"💰 Solde actuel : {data['solde']}€",
        reply_markup=reply
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global etat

    texte = update.message.text

    if texte == "Gain":
        etat = "gain"
        await update.message.reply_text("Entre le montant gagné")

    elif texte == "Perte":
        etat = "perte"
        await update.message.reply_text("Entre le montant perdu")

    elif texte == "Solde":
        await update.message.reply_text(f"💰 Ton solde : {data['solde']}€")

    else:
        try:
            montant = float(texte)

            if etat == "gain":
                data["solde"] += montant

            elif etat == "perte":
                data["solde"] -= montant

            sauver(data)

            await update.message.reply_text(f"✅ Nouveau solde : {data['solde']}€")

        except:
            await update.message.reply_text("Entre un nombre valide")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, message))

app.run_polling()
