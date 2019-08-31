const config = require('../config');
const Telegraf = require('telegraf')
const Model = require('./common/model');
const checkContent = require('./keyword');

const bot = new Telegraf(config.telegram.token)
bot.start(ctx => ctx.reply('I\'m @tgcnbot '))
bot.on('new_chat_members', async ctx => {
  if(ctx.message.new_chat_member.id === ctx.botInfo.id){
    const chatInfo = {
      del_join_msg: 1,
      fb_send_sticker: 0,
      fb_send_doc: 0,
      fb_send_forward: 0,
      ...ctx.message.chat
    };
    const chat = await Model('chat').save(chatInfo);
    const admins = await ctx.getChatAdministrators();
    admins.map(async admin => {
      if(!admin.user.is_bot){
        const user = await Model('user').save(admin.user)
        const chatUserInfo = {
          chat_id: chat.id,
          user_id: user.id,
          status: admin.status,
          until_date: admin.until_date
        }
        const chatUser = await Model('chat_user').save(chatUserInfo, ['chat_id', 'user_id'])
      }
    })
  }

  try {
    const name = `${ctx.message.new_chat_member.first_name} ${ctx.message.new_chat_member.last_name}`
    if(checkContent(name, 'name')){
      await ctx.kickChatMember(ctx.message.new_chat_member.id)
    }
  } catch (error) {
    console.log(error)
    console.log(ctx.message.new_chat_member)
  }
  
  try {
    await ctx.deleteMessage(ctx.message.message_id);
  } catch (error) {
    console.log(error)
  }
})
bot.on(
  ['text', 'edited_message','photo', 'forward'],
  async ctx => {
    const message = ctx.message || ctx.editedMessage
    const content = message.text || message.caption
    if(checkContent(content)){
      try {
        const resp = await ctx.reply(
          `[${message.from.first_name} ${message.from.last_name}](tg://user?id=${message.from.id}) 发现敏感内容`,
          {
            reply_to_message_id: message.message_id,
            parse_mode: 'Markdown'
          }
        )
        setTimeout(
          async ()=>{await ctx.deleteMessage(resp.message_id)},
          3000
        )
        await ctx.deleteMessage(message.message_id)
        await ctx.kickChatMember(message.from.id)
      } catch (error) {
        console.log(error)
      }
    }
  }
);
bot.catch((err) => {
  console.log('Ooops', err)
})
bot.launch()