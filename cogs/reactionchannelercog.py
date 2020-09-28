import discord
from discord.ext import commands # Bot Commands Frameworkのインポート
import datetime
from .modules.reactionchannel import ReactionChannel
from .modules import settings

# コグとして用いるクラスを定義。
class ReactionChannelerCog(commands.Cog, name="リアクションチャネラー"):
    """
    リアクションチャネラー機能のカテゴリ。
    """

    # ReactionChannelerCogクラスのコンストラクタ。Botを受取り、インスタンス変数として保持。
    def __init__(self, bot):
        self.bot = bot

    # リアクションチャネラーコマンド群
    @commands.group(aliases=['rch','reaction', 'reach'], description='リアクションチャネラーを操作するコマンド（サブコマンド必須）')
    async def reactionChanneneler(self, ctx):
        """
        リアクションチャネラーを管理するコマンド群です。このコマンドだけでは管理できません。
        リアクションチャネラーを追加したい場合は、`add`を入力し、絵文字とチャンネル名を指定してください。
        リアクションチャネラーを削除したい場合は、`delete`を入力し、絵文字とチャンネル名を指定してください。
        リアクションチャネラーを確認したい場合は、`list`を入力してください。
        """
        # サブコマンドが指定されていない場合、メッセージを送信する。
        if ctx.invoked_subcommand is None:
            await ctx.send('このコマンドにはサブコマンドが必要です。')

    # リアクションチャネラー追加
    @reactionChanneneler.command(aliases=['a','ad'], description='リアクションチャネラーを追加するサブコマンド')
    async def add(self, ctx, reaction:str=None, channel:str=None):
        # リアクション、チャンネルがない場合は実施不可
        if reaction is None or channel is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('リアクションとチャンネルを指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return
        reaction_channel = ReactionChannel()
        msg = reaction_channel.add(ctx, reaction, channel)
        await ctx.channel.send(msg)

    # リアクションチャネラー確認
    @reactionChanneneler.command(aliases=['l','ls', 'lst'], description='現在登録されているリアクションチャネラーを確認するサブコマンド')
    async def list(self, ctx):
        reaction_channel = ReactionChannel()
        msg = reaction_channel.list(ctx)
        await ctx.channel.send(msg)

    # リアクションチャネラー全削除
    @reactionChanneneler.command(aliases=['prg','pg'], description='Guildのリアクションチャネラーを全削除するサブコマンド')
    async def purge(self, ctx):
        reaction_channel = ReactionChannel()
        msg = reaction_channel.purge(ctx)
        await ctx.channel.send(msg)

    # リアクションチャネラー削除（１種類）
    @reactionChanneneler.command(aliases=['d','del'], description='リアクションチャネラーを削除するサブコマンド')
    async def delete(self, ctx, reaction:str=None, channel:str=None):
        # リアクション、チャンネルがない場合は実施不可
        if reaction is None or channel is None:
            await ctx.channel.purge(limit=1)
            await ctx.channel.send('リアクションとチャンネルを指定してください。\nあなたのコマンド：`{0}`'.format(ctx.message.clean_content))
            return
        reaction_channel = ReactionChannel()
        msg = reaction_channel.delete(ctx, reaction, channel)
        await ctx.channel.send(msg)

    # リアクション追加時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.member.bot:# BOTアカウントは無視する
            return
        await self.pin_message(payload)
        await self.reaction_channeler(payload)

    # リアクション削除時に実行されるイベントハンドラを定義
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)
        if member.bot:# BOTアカウントは無視する
            return
        await self.unpin_message(payload)

    # ピン留めする非同期関数を定義
    async def pin_message(self, payload: discord.RawReactionActionEvent):
        # 絵文字が異なる場合は対応しない
        if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
            return
        if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.pin()
            return

    # ピン留め解除する非同期関数を定義
    async def unpin_message(self, payload: discord.RawReactionActionEvent):
        # 絵文字が異なる場合は対応しない
        if (payload.emoji.name != '📌') and (payload.emoji.name != '📍'):
            return
        if (payload.emoji.name == '📌') or (payload.emoji.name == '📍'):
            guild = self.bot.get_guild(payload.guild_id)
            channel = guild.get_channel(payload.channel_id)
            message = await channel.fetch_message(payload.message_id)
            await message.unpin()
            return

    # あれする非同期関数を定義
    async def reaction_channeler(self, payload: discord.RawReactionActionEvent):
        # リアクションチャネラーを読み込む
        guild = self.bot.get_guild(payload.guild_id)
        reaction_channel = ReactionChannel()
        reaction_channel.set_rc(guild)

        # リアクションから絵文字を取り出す（ギルド絵文字への変換も行う）
        emoji = payload.emoji.name
        if payload.emoji.id is not None:
            emoji = f'<:{payload.emoji.name}:{payload.emoji.id}>'

        # 入力された絵文字でフィルターされたリストを生成する
        filtered_list = [rc for rc in reaction_channel.guild_reaction_channels if emoji in rc]

        if settings.IS_DEBUG:
            print(f'*****emoji***** {emoji}')

        # フィルターされたリストがある分だけ、チャンネルへ投稿する
        for reaction in filtered_list:
            from_channel = guild.get_channel(payload.channel_id)
            message = await from_channel.fetch_message(payload.message_id)

            if settings.IS_DEBUG:
                print('guild:'+ str(guild))
                print('from_channel: '+ str(from_channel))
                print('message: ' + str(message))

            contents = [message.clean_content[i: i+200] for i in range(0, len(message.clean_content), 200)]
            if len(contents) != 1 :
                contents[0] += ' ＊長いので分割しました＊'
            embed = discord.Embed(title = contents[0], description = '<#' + str(message.channel.id) + '>', type='rich')
            embed.set_author(name=reaction[0] + ':reaction_channeler', url='https://github.com/tetsuya-ki/discord-bot-heroku/')
            embed.set_thumbnail(url=message.author.avatar_url)

            created_at = message.created_at.replace(tzinfo=datetime.timezone.utc)
            created_at_jst = created_at.astimezone(datetime.timezone(datetime.timedelta(hours=9)))

            embed.add_field(name='作成日時', value=created_at_jst.strftime('%Y/%m/%d(%a) %H:%M:%S'))

            if len(contents) != 1 :
                for addText in contents[1:]:
                    embed.add_field(name='addText', value=addText + ' ＊長いので分割しました＊', inline=False)

            to_channel = guild.get_channel(reaction[2])
            if settings.IS_DEBUG:
                print('setting:'+str(reaction[2]))
                print('to_channel: '+str(to_channel))

            await to_channel.send(reaction[1] + ': ' + message.jump_url, embed=embed)

# Bot本体側からコグを読み込む際に呼び出される関数。
def setup(bot):
    bot.add_cog(ReactionChannelerCog(bot)) # ReactionChannelerCogにBotを渡してインスタンス化し、Botにコグとして登録する