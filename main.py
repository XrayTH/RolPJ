import os
import discord
from discord.ext import commands
from flask import Flask, jsonify
import threading
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

# Configurar MongoDB
mongo_uri = os.getenv("MONGO_URI")
client = MongoClient(mongo_uri)
db = client['RolPJ']
collection = db['personajes']

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

bot_connected = False

@bot.event
async def on_ready():
    global bot_connected
    bot_connected = True
    print(f'Conectado como {bot.user.name} ({bot.user.id})')

@bot.command()
async def status(ctx):
    if bot_connected:
        await ctx.send("El bot está en línea.")
    else:
        await ctx.send("El bot está conectando...")

@bot.command()
async def crear(ctx, nombre: str):
    try:
        personaje = {'nombre': nombre}
        collection.insert_one(personaje)
        await ctx.send(f"Personaje {nombre} creado.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al crear el personaje: {e}")

@bot.command()
async def añadir(ctx, nombre: str, nombre_atributo: str, tipo_atributo: str):
    try:
        personaje = collection.find_one({"nombre": nombre})
        if not personaje:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        tipo_atributo = tipo_atributo.lower()
        partes = nombre_atributo.split('.')
        valor = personaje

        for i, parte in enumerate(partes):
            if isinstance(valor, dict):
                if parte not in valor:
                    if i == len(partes) - 1:
                        if tipo_atributo == 'str':
                            valor[parte] = ""
                        elif tipo_atributo == 'obj':
                            valor[parte] = {}
                        else:
                            await ctx.send(f"Tipo de atributo no válido para {nombre_atributo}.")
                            return
                    else:
                        valor[parte] = {}
                valor = valor[parte]
            else:
                await ctx.send(f"No se puede acceder al atributo {nombre_atributo} porque no es un objeto.")
                return

        collection.update_one({"nombre": nombre}, {"$set": personaje})
        await ctx.send(f"Atributo {nombre_atributo} de tipo {tipo_atributo} añadido al personaje {nombre}.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al añadir el atributo: {e}")

@bot.command()
async def ver(ctx, nombre: str, nombre_atributo: str = None):
    try:
        personaje = collection.find_one({"nombre": nombre})
        if not personaje:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        if nombre_atributo:
            partes = nombre_atributo.split('.')
            valor = personaje

            for parte in partes:
                if isinstance(valor, dict) and parte in valor:
                    valor = valor[parte]
                else:
                    await ctx.send(f"El atributo {nombre_atributo} no existe en el personaje {nombre}.")
                    return

            await ctx.send(f"Atributo {nombre_atributo}: {valor}")
        else:
            personaje_info = f"Personaje: {nombre}\n"
            for atributo, valor in personaje.items():
                if atributo != '_id':
                    personaje_info += f"- {atributo}: {valor}\n"
            await ctx.send(personaje_info)
    except Exception as e:
        await ctx.send(f"Ocurrió un error al visualizar el personaje o atributo: {e}")

@bot.command()
async def borrar(ctx, nombre: str, nombre_atributo: str = None):
    try:
        personaje = collection.find_one({"nombre": nombre})
        if not personaje:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        if nombre_atributo:
            partes = nombre_atributo.split('.')
            valor = personaje

            for i, parte in enumerate(partes):
                if isinstance(valor, dict) and parte in valor:
                    if i == len(partes) - 1:
                        del valor[parte]
                        collection.update_one({"nombre": nombre}, {"$set": personaje})
                        await ctx.send(f"Atributo {nombre_atributo} borrado del personaje {nombre}.")
                        return
                    valor = valor[parte]
                else:
                    await ctx.send(f"El atributo {nombre_atributo} no existe en el personaje {nombre}.")
                    return
        else:
            collection.delete_one({"nombre": nombre})
            await ctx.send(f"Personaje {nombre} borrado.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al borrar el personaje o atributo: {e}")

@bot.command()
async def editar(ctx, nombre: str, nombre_atributo: str, nuevo_valor: str):
    try:
        personaje = collection.find_one({"nombre": nombre})
        if not personaje:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        partes = nombre_atributo.split('.')
        valor = personaje

        for i, parte in enumerate(partes):
            if isinstance(valor, dict) and parte in valor:
                if i == len(partes) - 1:
                    valor[parte] = nuevo_valor
                    collection.update_one({"nombre": nombre}, {"$set": personaje})
                    await ctx.send(f"Atributo {nombre_atributo} del personaje {nombre} actualizado a: {nuevo_valor}")
                    return
                valor = valor[parte]
            else:
                await ctx.send(f"El atributo {nombre_atributo} no existe en el personaje {nombre}.")
                return
    except Exception as e:
        await ctx.send(f"Ocurrió un error al editar el atributo: {e}")

@bot.command()
async def verTodos(ctx):
    try:
        personajes = collection.find()
        all_personajes = "Personajes y sus atributos:\n"
        for personaje in personajes:
            all_personajes += f"ID: {personaje['nombre']}\n"
            for atributo, valor in personaje.items():
                if atributo != '_id':
                    all_personajes += f"- {atributo}: {valor}\n"
        await ctx.send(all_personajes)
    except Exception as e:
        await ctx.send(f"Ocurrió un error al visualizar todos los personajes: {e}")

@app.route('/')
def api_ver_todos():
    try:
        personajes = collection.find()
        all_personajes = []
        for personaje in personajes:
            personaje_data = {key: value for key, value in personaje.items() if key != '_id'}
            all_personajes.append({"id": personaje['nombre'], "atributos": personaje_data})
        return jsonify(all_personajes), 200
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error al visualizar todos los personajes: {str(e)}"}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

bot.run(os.getenv('TOKEN'))
