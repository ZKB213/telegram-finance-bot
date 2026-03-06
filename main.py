import json
import os
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# ✅ Récupérer le token correctement et le nettoyer
TOKEN = "8099010522:AAGw-7vF2mvV9LNgNaMkn8wnO4GJQI-uO0E"

if not TOKEN:
    raise ValueError("Le token n'est pas défini dans les variables d'environnement")
TOKEN = TOKEN.strip()  # supprime espaces et sauts de ligne

# Fichier pour stocker le solde commun
FILE = "argent.json"

# Charger le solde depuis le fichier
def charger():
    try:
        with open(FILE) as f:
            return json.load(f)
    except:
        # Valeur de départ si le fichier n'existe pas
        return {"solde": 740.40}

# Sauver le solde dans le fichier
def sauver(data):
    with open(FILE, "w") as f:
        json.dump(data, f)

# Charger le solde au démarrage
data = charger()
etat = None

# Clavier du bot
keyboard = [["Gain", "Perte"], ["Solde"]]

# Commande /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"💰 Solde actuel : {data['solde']}€",
        reply_markup=reply
    )

# Gestion des messages
async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global etat

    texte = update.message.text

    if texte == "Gain":
        etat = "gain"
        await update.message.reply_text("💵 Entre le montant gagné :")

    elif texte == "Perte":
        etat = "perte"
        await update.message.reply_text("💸 Entre le montant perdu :")

    elif texte == "Solde":
        await update.message.reply_text(f"💰 Solde actuel : {data['solde']}€")

    else:
        try:
            montant = float(texte.replace(",", "."))  # support virgule ou point

            if etat == "gain":
                data["solde"] += montant

            elif etat == "perte":
                data["solde"] -= montant

            else:
                await update.message.reply_text("Choisis d'abord Gain ou Perte")
                return

            sauver(data)

            await update.message.reply_text(f"✅ Nouveau solde : {data['solde']}€")

        except ValueError:
            await update.message.reply_text("❌ Entre un nombre valide")

# Création de l'application
app = ApplicationBuilder().token(TOKEN).build()

# Ajouter les handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, message))

# Lancer le bot
app.run_polling()
