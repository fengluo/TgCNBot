const config = require('../config');
const Telegraf = require('telegraf')
const Model = require('./common/model');

const bot = new Telegraf(config.telegram.token)
bot.start(ctx => ctx.reply('I\'m @tgcnbot '))
bot.on('new_chat_members', async ctx => {
  if(ctx.message.chat.id === ctx.botInfo.id){
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
    await ctx.deleteMessage(ctx.message.message_id)
  } catch (error) {
    if(error.code === 400) {
      await ctx.reply('Please grant me the permission of admin')
    }
  }
})
// bot.on(
//   ['text', 'photo', 'forward', 'edited_message'],
//   async ctx => {
    
//   }
// );
bot.launch()