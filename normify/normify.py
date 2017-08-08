import discord
from discord.ext import commands
from cogs.utils import checks
from cogs.utils.dataIO import dataIO
from cogs.utils.chat_formatting import box, pagify
from copy import deepcopy
import asyncio
import logging
import os


log = logging.getLogger("red.admin")


class Normify:
    """Normifies people. This cog is property of Jordan"""

    def __init__(self, bot):
        self.bot = bot
        self._announce_msg = None
        self._announce_server = None
        self._settings = dataIO.load_json('data/normify/settings.json')
        self._settable_roles = self._settings.get("ROLES", {})

    

    def _get_selfrole_names(self, server):
        if server.id not in self._settable_roles:
            return None
        else:
            return self._settable_roles[server.id]

    def _is_server_locked(self):
        return self._settings.get("SERVER_LOCK", False)

    def _role_from_string(self, server, rolename, roles=None):
        if roles is None:
            roles = server.roles

        roles = [r for r in roles if r is not None]
        role = discord.utils.find(lambda r: r.name.lower() == rolename.lower(),
                                  roles)
        try:
            log.debug("Role {} found from rolename {}".format(
                role.name, rolename))
        except:
            log.debug("Role not found for rolename {}".format(rolename))
        return role

    def _save_settings(self):
        dataIO.save_json('data/admin/settings.json', self._settings)

    def _set_selfroles(self, server, rolelist):
        self._settable_roles[server.id] = rolelist
        self._settings["ROLES"] = self._settable_roles
        self._save_settings()

    def _set_serverlock(self, lock=True):
        self._settings["SERVER_LOCK"] = lock
        self._save_settings()

    @commands.command(no_pm=True, pass_context=True)
    @checks.mod_or_permissions(kick_members=True)
    async def normify(self, ctx, user: discord.Member=None):
        """Normifies a user who got in trouble"""
        author = ctx.message.author
        channel = ctx.message.channel
        server = ctx.message.server

        if user is None:
            await self.bot.say("As punishment for not saying anyone, I'll make YOU a normie")
            user = author

        role = self._role_from_string(server, "Normie")

        #if role is None:
         #   await self.bot.say('That role cannot be found.')
          #  return

        #if not channel.permissions_for(server.me).manage_roles:
        #    await self.bot.say('I don\'t have manage_roles.')
        #    return

        await self.bot.add_roles(user, role)
        await self.bot.say('{} is now a normie.'.format(user.mention))

    @commands.command(pass_context=True)
    async def jordanisstillcool(self, ctx):
        """Continues to state the truth"""
        await self.bot.say("Hey @everyone, Jordan is STILL COOL!")

    

    @commands.command(no_pm=True, pass_context=True)
    @checks.admin_or_permissions(manage_roles=True)
    async def denormify(self, ctx, rolename, user: discord.Member=None):
        """Pardons the user of being a normie."""
        server = ctx.message.server
        author = ctx.message.author

        role = self._role_from_string(server, "Normie")
        if role is None:
            await self.bot.say("uhh")
            return

        if user is None:
            user = author

        if role in user.roles:
            try:
                await self.bot.remove_roles(user, role)
                await self.bot.say("Done, they are no longer a normie. But WATCH OUT!")
            except discord.Forbidden:
                await self.bot.say("I CANT CHANGE THE ROLES YOU DUMBASS!")
        else:
            await self.bot.say("They were never a normie unlike you.")

    
def check_files():
    if not os.path.exists('data/normify/settings.json'):
        try:
            os.mkdir('data/normify')
        except FileExistsError:
            pass
        else:
            dataIO.save_json('data/normify/settings.json', {})

    


def setup(bot):
    check_files()
    n = Normify(bot)
    bot.add_cog(n)
    #bot.add_listener(n.server_locker, "on_server_join")
    #bot.loop.create_task(n.announce_manager())
