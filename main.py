import json
import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("8099010522:AAGw-7vF2mvV9LNgNaMkn8wnO4GJQI-uO0E")

FILE = "argent.json"

def charger():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return {"solde":1000}

def sauver(data):
    with open(FILE,"w") as f:
        json.dump(data,f)

data = charger()
etat_users = {}

keyboard = [["Gain","Perte"],["Solde"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"💰 Solde actuel : {data['solde']}€",
        reply_markup=reply
    )

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.message.from_user.id
    user_name = update.message.from_user.first_name
    texte = update.message.text

    if texte == "Gain":
        etat_users[user_id] = "gain"
        await update.message.reply_text("Entre le montant du gain")

    elif texte == "Perte":
        etat_users[user_id] = "perte"
        await update.message.reply_text("Entre le montant de la perte")

    elif texte == "Solde":
        await update.message.reply_text(f"💰 Solde actuel : {data['solde']}€")

    else:
        try:
            montant = float(texte)

            etat = etat_users.get(user_id)

            if etat == "gain":
                data["solde"] += montant
                action = "gain"

            elif etat == "perte":
                data["solde"] -= montant
                action = "perte"

            else:
                return

            sauver(data)

            await update.message.reply_text(
                f"👤 {user_name} a ajouté une {action} de {montant}€\n"
                f"💰 Nouveau solde : {data['solde']}€"
            )

        except:
            await update.message.reply_text("Entre un nombre valide")

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, message))

app.run_polling()
