import { Bot, webhookCallback } from 'grammy';
import { fetchProductHuntData, generateProductHTML } from './utils';
export default {
	async fetch(request, env, ctx) {
		// Set up the bot with the token and webhook URL.
		// https://api.telegram.org/bot<BOT_TOKEN>/setWebhook?url=https://<MY_BOT>.<MY_SUBDOMAIN>.workers.dev/
		// https://api.telegram.org/bot7329448395:AAGV_Mf_03RpSXhKqpFyRrPgMkhVWPYpvaI/setWebhook?url=https://nichesbot.cain-wuyi.workers.dev/

		// delete webhook
		// https://api.telegram.org/bot<BOT_TOKEN>/deleteWebhook

		try {
			// 初始化bot
			const bot = new Bot(env.BOT_TOKEN, { botInfo: JSON.parse(env.BOT_INFO) });

			let chatId;
			// 注册命令
			bot.command('start', async (ctx) => {
				chatId = ctx.chat.id;
				// await ctx.reply('Welcome to NichesBot By Local!');

				// 连接 Product Hunt API 获取最新产品信息
				const products = await fetchProductHuntData();
				for (const product of products) {
					await product.fetchOgImageUrl();
					const message = generateProductHTML(product);
					// 发送产品信息到群组或私聊
					await bot.reply(message);
				}
			});

			bot.command('help', async (ctx) => {
				await ctx.reply('Help message');
				await bot.api.sendMessage(ctx.chat.id, 'Help message By NichesBot');
			});

			// 处理其他的消息。
			// bot.on('message', (ctx) => ctx.reply('Got another message!'));

			console.log('Start command received');

			// 注册定时任务
			// registerSchedule(bot);

			return webhookCallback(bot, 'cloudflare-mod')(request);
		} catch (e) {
			console.log(e);

			return new Response('Error: ' + e.message, { status: 500 });
		}
	},
};
