import json
import os
from datetime import datetime
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TOKEN").strip()

FILE = "argent.json"

USERS = []

etat = None
personne = None

menu_principal = [
    ["🟤 Lilou", "🔵 Farah", "🟣 Hidayat"],
    ["📜 Historique"]
]

menu_action = [
    ["💰 Gain", "💸 Dépense"],
    ["⬅️ Retour"]
]

def charger():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        return {
            "solde": 740.40,
            "historique": []
        }

def sauver(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

data = charger()

async def notifier(context, message):
    for user in USERS:
        try:
            await context.bot.send_message(chat_id=user, text=message)
        except:
            pass


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_chat.id

    if user_id not in USERS:
        USERS.append(user_id)

    clavier = ReplyKeyboardMarkup(menu_principal, resize_keyboard=True)

    await update.message.reply_text(
        f"💰 Solde actuel : {data['solde']}€",
        reply_markup=clavier
    )


async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    global etat
    global personne

    texte = update.message.text

    if texte in ["🟤 Lilou", "🔵 Farah", "🟣 Hidayat"]:

        personne = texte.replace("🟤 ","").replace("🔵 ","").replace("🟣 ","")

        clavier = ReplyKeyboardMarkup(menu_action, resize_keyboard=True)

        await update.message.reply_text(
            f"{texte} sélectionné\nQue veux-tu faire ?",
            reply_markup=clavier
        )


    elif texte == "💰 Gain":
        etat = "gain"
        await update.message.reply_text("💰 Entre le montant gagné")


    elif texte == "💸 Dépense":
        etat = "depense"
        await update.message.reply_text("💸 Entre le montant dépensé")


    elif texte == "⬅️ Retour":

        clavier = ReplyKeyboardMarkup(menu_principal, resize_keyboard=True)

        await update.message.reply_text(
            "Menu principal",
            reply_markup=clavier
        )


    elif texte == "📜 Historique":

        if not data["historique"]:
            await update.message.reply_text("Aucun historique")
            return

        historique_txt = ""

        for action in data["historique"][-20:]:

            symbole = "➕" if action["type"] == "gain" else "➖"

            historique_txt += (
                f"{action['date']}\n"
                f"{action['personne']} {symbole} {action['montant']}€\n"
                f"Solde : {action['solde']}€\n\n"
            )

        await update.message.reply_text(historique_txt)


    else:

        try:

            montant = float(texte.replace(",", "."))

            if etat == "gain":
                data["solde"] += montant

            elif etat == "depense":
                data["solde"] -= montant

            else:
                await update.message.reply_text("Choisis Gain ou Dépense")
                return

            date = datetime.now().strftime("%d/%m/%Y %H:%M")

            data["historique"].append({
                "date": date,
                "personne": personne,
                "type": etat,
                "montant": montant,
                "solde": data["solde"]
            })

            sauver(data)

            symbole = "➕" if etat == "gain" else "➖"

            message_resultat = (
                f"{personne} {symbole} {montant}€\n"
                f"💰 Nouveau solde : {data['solde']}€"
            )

            await notifier(context, message_resultat)

            etat = None

        except:
            await update.message.reply_text("Entre un nombre valide")


app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

app.run_polling()
