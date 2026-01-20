import os
import random
import string
import asyncio
import discord
import smtplib
from email.message import EmailMessage
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

dc_token = os.getenv('DISCORD_TOKEN')
domain = os.getenv('ALLOWED_DOMAIN')
guild_id = int(os.getenv('GUILD_ID') or "0")
role_name = os.getenv('ROLE_NAME')
smtp_host = os.getenv('SMTP_HOST')
smtp_port = int(os.getenv('SMTP_PORT') or "587")
smtp_user = os.getenv('SMTP_USER')
smtp_pass = os.getenv('SMTP_PASS')
from_email = os.getenv('FROM_EMAIL')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

#dict for pending verification users
pending_verification = {}

def generate_code(length: int = 6) -> str:
    digits = []
    for _ in range(length):
        digits.append(str(random.randint(0, 9)))
    return "".join(digits)

def send_verification_email(email: str, code: str):
    msg = EmailMessage()
    msg['Subject'] = 'GDG on campus VIT-AP discord verification. Do not reply to this email.'
    msg['From'] = from_email
    msg['To'] = email
    msg.set_content(f"Your verification code is {code}\n\n"
    "Please use this code to verify your email address. If you did not request this code, please ignore this email.")

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_pass)
        server.send_message(msg)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("--------------------------------")


@bot.command(name="verify")
async def verify(ctx):
    try:
        await ctx.author.send(
            "Hi! Please enter your **email address** "
            f"(must be of the `{domain}` domain)."
        )
        await ctx.reply("I’ve sent you a DM to continue verification.", mention_author=False)
    except discord.Forbidden:
        await ctx.reply(
            "I couldn't DM you. Please enable DMs from server members and try again.",
            mention_author=False,
        )

@bot.event
async def on_message(message):
    await bot.process_commands(message) #process commands first

    if message.author.bot or not isinstance(message.channel, discord.DMChannel): #handle dms
        return

    user = message.author
    content = (message.content or "").strip()

    # Step 1: Collect email if no pending verification
    if user.id not in pending_verification:
        if "@" not in content:
            await user.send("That doesn’t look like an email. Please send a valid email address.")
            return

        try:
            _local, email_domain = content.rsplit("@", 1)
        except ValueError:
            await user.send("That doesn’t look like an email. Please send a valid email address.")
            return

        if not domain:
            await user.send("Bot is misconfigured: `domain` is not set. Contact an admin.")
            return

        if email_domain.lower() != domain.lower():
            await user.send(f"Email domain must be `{domain}`. Please send an email from that domain.")
            return

        code = generate_code()
        try:
            # Avoid blocking the event loop on SMTP
            await asyncio.to_thread(send_verification_email, content, code)
        except Exception as e:
            print("Error sending email:", repr(e))
            await user.send("I couldn't send the verification email. Please try again later.")
            return

        pending_verification[user.id] = {"code": code, "email": content}
        await user.send(f"I’ve sent a verification code to `{content}`. Reply here with the code.")
        return

    # Step 2: Validate code and assign role
    expected = pending_verification[user.id]["code"]
    if content != expected:
        await user.send("Incorrect code. Please try again (or run `!verify` again to restart).")
        return

    guild = bot.get_guild(guild_id) if guild_id else None
    if guild is None:
        await user.send("I couldn't find the server (check `GUILD_ID`). Contact an admin.")
        pending_verification.pop(user.id, None)
        return

    member = guild.get_member(user.id)
    if member is None:
        try:
            member = await guild.fetch_member(user.id)
        except discord.NotFound:
            member = None

    if member is None:
        await user.send("I couldn't find you in the server. Join the server, then run `!verify` again.")
        pending_verification.pop(user.id, None)
        return

    if not role_name:
        await user.send("Bot is misconfigured: `ROLE_NAME` is not set. Contact an admin.")
        pending_verification.pop(user.id, None)
        return

    role = discord.utils.get(guild.roles, name=role_name)
    if role is None:
        await user.send(f"The role `{role_name}` does not exist. Contact an admin.")
        pending_verification.pop(user.id, None)
        return

    try:
        await member.add_roles(role, reason="Email verified")
    except discord.Forbidden:
        await user.send("I don't have permission to assign that role. Contact an admin.")
        pending_verification.pop(user.id, None)
        return

    await user.send(f"Success! Verified `{pending_verification[user.id]['email']}` and assigned `{role_name}`.")
    pending_verification.pop(user.id, None)


if __name__ == "__main__":
    if not dc_token:
        raise RuntimeError("Missing DISCORD_TOKEN")
    bot.run(dc_token)