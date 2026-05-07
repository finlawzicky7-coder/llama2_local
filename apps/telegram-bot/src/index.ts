import { Telegraf } from 'telegraf';
import Fastify from 'fastify';
import { loadEnv } from '@agentboard/config';
import { createLogger } from '@agentboard/shared';
import { handleMessage, type IncomingMessage } from './handlers.js';

const log = createLogger('bot');
const env = loadEnv({ strict: false });

if (!env.TELEGRAM_BOT_TOKEN) {
  log.error(
    'TELEGRAM_BOT_TOKEN is not set. Bot will not start. Set it in .env to run for real.',
  );
  process.exit(1);
}

const bot = new Telegraf(env.TELEGRAM_BOT_TOKEN);

bot.on('text', async (ctx) => {
  const text = ctx.message.text;
  const incoming: IncomingMessage = {
    chat_id: ctx.chat.id,
    chat_title: 'title' in ctx.chat ? (ctx.chat.title ?? null) : null,
    chat_type: ctx.chat.type ?? null,
    user_id: ctx.from?.id ?? 0,
    username: ctx.from?.username ?? null,
    first_name: ctx.from?.first_name ?? null,
    text,
    message_id: ctx.message.message_id,
  };
  try {
    const reply = await handleMessage(incoming);
    if (reply) {
      await ctx.reply(reply.text, {
        parse_mode: 'Markdown',
        reply_parameters: reply.reply_to_message_id
          ? { message_id: reply.reply_to_message_id }
          : undefined,
      });
    }
  } catch (err) {
    log.error('handler crashed', { err: String(err) });
    await ctx.reply('_Internal error. Check the dashboard logs._', { parse_mode: 'Markdown' });
  }
});

bot.catch((err) => {
  log.error('telegraf error', { err: String(err) });
});

async function main() {
  if (env.TELEGRAM_MODE === 'webhook') {
    if (!env.TELEGRAM_WEBHOOK_URL) {
      log.error('TELEGRAM_WEBHOOK_URL is required for webhook mode');
      process.exit(1);
    }
    const app = Fastify({ logger: false });
    app.get('/health', async () => ({ ok: true }));
    app.post('/telegram/webhook', async (req, reply) => {
      const secret = req.headers['x-telegram-bot-api-secret-token'];
      if (env.TELEGRAM_WEBHOOK_SECRET && secret !== env.TELEGRAM_WEBHOOK_SECRET) {
        reply.code(401);
        return { ok: false };
      }
      try {
        await bot.handleUpdate(req.body as never);
      } catch (err) {
        log.error('webhook handle failed', { err: String(err) });
      }
      return { ok: true };
    });
    const port = Number(process.env.PORT ?? 8080);
    await app.listen({ port, host: '0.0.0.0' });
    log.info('webhook listening', { port });

    await bot.telegram.setWebhook(env.TELEGRAM_WEBHOOK_URL, {
      secret_token: env.TELEGRAM_WEBHOOK_SECRET,
      allowed_updates: ['message'],
    });
    log.info('webhook registered with Telegram');
  } else {
    log.info('starting bot in polling mode');
    await bot.launch({ dropPendingUpdates: true });
  }

  process.once('SIGINT', () => bot.stop('SIGINT'));
  process.once('SIGTERM', () => bot.stop('SIGTERM'));
}

main().catch((err) => {
  log.error('bot failed to start', { err: String(err) });
  process.exit(1);
});
