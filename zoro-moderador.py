import json
import os
from discord.ext import commands
import discord
from discord.ext.commands import has_permissions
import asyncio

class Crear_Respuesta():
    def __init__(self, title, content):
        self.title = title
        self.content = content

        self.respuesta = discord.Embed(
            title=self.title,
            description=self.content,
            colour=int('DC75FF', 16)
        )

    @property
    def enviar(self):
        return self.respuesta

def main():
    if os.path.exists('config.json'):
        with open('config.json') as f:
            config_data = json.load(f)
    else:
        template = {'prefix': '!', 'token': "", 'palabrasbaneadas': [], 'usuariosbaneados': [], 'acciones_mod': []}
        with open('config.json', 'w') as f:
            json.dump(template, f)

    palabrasbaneadas = config_data['palabrasbaneadas']
    prefix = config_data['prefix']
    token = config_data['token']
    intents = discord.Intents.all()
    bot = commands.Bot(command_prefix=prefix, intents=intents, description='Bot_moderador')

    # comandos 
    @bot.command(name='saludar', description='El bot te saluda')
    async def saludar(ctx):
        await ctx.send(f'¡Hola!, {ctx.author} ¿Cómo estás?')

    @bot.command(name='sumar', help='Suma dos números')
    async def sumar(ctx, num1: int, num2: int):
        suma = num1 + num2
        respuesta = Crear_Respuesta(f'El resultado de la suma es: {suma}', None)
        await ctx.send(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Banear palabras del servidor')
    async def banword(ctx, palabras):
        if palabras.lower() in palabrasbaneadas:
            await ctx.send(embed=Crear_Respuesta('Esa palabra ya está baneada.', None).enviar)
        else:
            palabrasbaneadas.append(palabras.lower())
            with open('config.json', 'r+') as f:
                datos = json.load(f)
                datos['palabrasbaneadas'] = palabrasbaneadas
                f.seek(0)
                f.write(json.dumps(datos))
                f.truncate()
            respuesta = Crear_Respuesta('Palabras baneadas correctamente del SV', None)
            await ctx.send(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Quitar esta palabra del servidor')
    async def unbanword(ctx, palabras):
        if palabras.lower() in palabrasbaneadas:
            palabrasbaneadas.remove(palabras.lower())
            with open('config.json', 'r+') as f:
                datos = json.load(f)
                datos['palabrasbaneadas'] = palabrasbaneadas
                f.seek(0)
                f.write(json.dumps(datos))
                f.truncate()
            respuesta = Crear_Respuesta('Palabra desbaneada correctamente del SV', None)
            await ctx.send(embed=respuesta.enviar)
        else:
            respuesta = Crear_Respuesta('Error', 'Esa palabra no está baneada del servidor')
            await ctx.send(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Silenciar a un usuario por un período de tiempo determinado')
    async def mute(ctx, member: discord.Member, time: int):
        role_muted = discord.utils.get(ctx.guild.roles, name="Muted")
        if not role_muted:
            role_muted = await ctx.guild.create_role(name="Muted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(role_muted, speak=False, send_messages=False)
        await member.add_roles(role_muted)
        await ctx.send(embed=Crear_Respuesta(f'{member.name} ha sido silenciado por {time} segundos', None).enviar)
        await asyncio.sleep(time)
        await member.remove_roles(role_muted)

    @has_permissions(administrator=True)
    @bot.command(help='Expulsar a un usuario del servidor')
    async def kick(ctx, member: discord.Member, *, reason=None):
        await member.kick(reason=reason)
        await ctx.send(embed=Crear_Respuesta(f'{member.name} ha sido expulsado correctamente del servidor', None).enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Advertir a un usuario por comportamiento inapropiado')
    async def warn(ctx, member: discord.Member, *, reason=None):
        await ctx.send(embed=Crear_Respuesta(f'{member.name} ha sido advertido por {reason}', None).enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Ver la lista de usuarios baneados')
    async def bannedlist(ctx):
        banlist = await ctx.guild.bans()
        banned_users = [ban.user.name for ban in banlist]
        respuesta = Crear_Respuesta('Lista de usuarios baneados:', '\n'.join(banned_users))
        await ctx.send(embed=respuesta.enviar)

    @has_permissions(administrator=True)
    @bot.command(help='Borrar mensajes en el servidor')
    async def clear(ctx, amount: int):
        await ctx.channel.purge(limit=amount + 1)
        respuesta = Crear_Respuesta(f'Se han eliminado {amount} mensajes', None)
        await ctx.send(embed=respuesta.enviar)

    # Eventos
    @bot.event
    async def on_message(message):
        message_content = message.content.lower()
        message_content = message_content.split(' ')
        for palabrabaneada in palabrasbaneadas:
            if palabrabaneada in message_content:
                respuesta = Crear_Respuesta('Se ha borrado tu comentario', None)
                await message.author.send(embed=respuesta.enviar)
                await message.delete()
                break
        await bot.process_commands(message)

    @bot.event
    async def on_member_ban(guild, user):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            usuariosbaneados = config_data['usuariosbaneados']
            usuariosbaneados.append(user.id)
            config_data['usuariosbaneados'] = usuariosbaneados
        with open('config.json', 'w') as f:
            json.dump(config_data, f)

    @bot.event
    async def on_member_unban(guild, user):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            usuariosbaneados = config_data['usuariosbaneados']
            if user.id in usuariosbaneados:
                usuariosbaneados.remove(user.id)
                config_data['usuariosbaneados'] = usuariosbaneados
        with open('config.json', 'w') as f:
            json.dump(config_data, f)

    @bot.event
    async def on_guild_remove(guild):
        with open('config.json', 'r') as f:
            config_data = json.load(f)
            acciones_mod = config_data['acciones_mod']
            acciones_mod.append(f"El bot ha sido eliminado del servidor: {guild.name}")
            config_data['acciones_mod'] = acciones_mod
        with open('config.json', 'w') as f:
            json.dump(config_data, f)

    bot.run(token)

if __name__ == "__main__":
    main()