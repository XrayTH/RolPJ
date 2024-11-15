import os
import discord
from discord.ext import commands
from flask import Flask, jsonify
import threading
from dotenv import load_dotenv

load_dotenv()  

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

app = Flask(__name__)

personajes = {}

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
        personajes[nombre.lower()] = personaje
        await ctx.send(f"Personaje {nombre} creado.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al crear el personaje: {e}")

@bot.command()
async def añadir(ctx, nombre: str, nombre_atributo: str, tipo_atributo: str):
    try:
        nombre = nombre.lower()
        if nombre not in personajes:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        tipo_atributo = tipo_atributo.lower()
        partes = nombre_atributo.split('.')
        valor = personajes[nombre]

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

        await ctx.send(f"Atributo {nombre_atributo} de tipo {tipo_atributo} añadido al personaje {nombre}.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al añadir el atributo: {e}")

@bot.command()
async def ver(ctx, nombre: str, nombre_atributo: str = None):
    try:
        nombre = nombre.lower()

        if nombre not in personajes:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        if nombre_atributo:
            partes = nombre_atributo.split('.')
            valor = personajes[nombre]

            for parte in partes:
                if isinstance(valor, dict) and parte in valor:
                    valor = valor[parte]
                else:
                    await ctx.send(f"El atributo {nombre_atributo} no existe en el personaje {nombre}.")
                    return

            await ctx.send(f"Atributo {nombre_atributo}: {valor}")
        else:
            personaje_info = f"Personaje: {nombre}\n"
            for atributo, valor in personajes[nombre].items():
                personaje_info += f"- {atributo}: {valor}\n"
            await ctx.send(personaje_info)
    except Exception as e:
        await ctx.send(f"Ocurrió un error al visualizar el personaje o atributo: {e}")

@bot.command()
async def borrar(ctx, nombre: str, nombre_atributo: str = None):
    try:
        nombre = nombre.lower()

        if nombre not in personajes:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        if nombre_atributo:
            partes = nombre_atributo.split('.')
            valor = personajes[nombre]

            for i, parte in enumerate(partes):
                if isinstance(valor, dict) and parte in valor:
                    if i == len(partes) - 1:
                        del valor[parte]
                        await ctx.send(f"Atributo {nombre_atributo} borrado del personaje {nombre}.")
                        return
                    valor = valor[parte]
                else:
                    await ctx.send(f"El atributo {nombre_atributo} no existe en el personaje {nombre}.")
                    return
        else:
            del personajes[nombre]
            await ctx.send(f"Personaje {nombre} borrado.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al borrar el personaje o atributo: {e}")

@bot.command()
async def editar(ctx, nombre: str, nombre_atributo: str, nuevo_valor: str):
    try:
        nombre = nombre.lower()

        if nombre not in personajes:
            await ctx.send(f"El personaje {nombre} no existe.")
            return

        partes = nombre_atributo.split('.')
        valor = personajes[nombre]

        for i, parte in enumerate(partes):
            if isinstance(valor, dict) and parte in valor:
                if i == len(partes) - 1:
                    valor[parte] = nuevo_valor
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
        if personajes:
            all_personajes = "Personajes y sus atributos:\n"
            for nombre, atributos in personajes.items():
                all_personajes += f"ID: {nombre}\n"
                for atributo, valor in atributos.items():
                    all_personajes += f"- {atributo}: {valor}\n"
            await ctx.send(all_personajes)
        else:
            await ctx.send("No hay personajes creados.")
    except Exception as e:
        await ctx.send(f"Ocurrió un error al visualizar todos los personajes: {e}")

@app.route('/')
def api_ver_todos():
    try:
        if personajes:
            all_personajes = []
            for nombre, atributos in personajes.items():
                all_personajes.append({"id": nombre, "atributos": atributos})
            return jsonify(all_personajes), 200
        else:
            return jsonify({"message": "No hay personajes creados."}), 200
    except Exception as e:
        return jsonify({"error": f"Ocurrió un error al visualizar todos los personajes: {str(e)}"}), 500

def run_flask():
    app.run(host='0.0.0.0', port=5000)

flask_thread = threading.Thread(target=run_flask)
flask_thread.start()

bot.run(os.getenv('TOKEN'))
