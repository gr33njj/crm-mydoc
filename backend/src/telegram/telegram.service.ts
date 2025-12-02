import { Injectable, OnModuleInit } from '@nestjs/common';
import { Telegraf } from 'telegraf';
import { PrismaService } from '../prisma/prisma.service';

@Injectable()
export class TelegramService implements OnModuleInit {
  private bot: Telegraf;

  constructor(private prisma: PrismaService) {
    const token = process.env.TELEGRAM_BOT_TOKEN;
    if (token) {
        this.bot = new Telegraf(token);
    }
  }

  async onModuleInit() {
    if (this.bot) {
        this.bot.start((ctx) => {
            ctx.reply('Привет! Я бот CRM MyDoctor. Чтобы привязать аккаунт, отправьте /link <email>');
        });

        this.bot.command('link', async (ctx) => {
            const email = ctx.payload;
            if (!email) return ctx.reply('Укажите email: /link email@example.com');
            
            const user = await this.prisma.user.findUnique({ where: { email } });
            if (!user) return ctx.reply('Пользователь с таким email не найден.');

            await this.prisma.user.update({
                where: { id: user.id },
                data: { telegramId: ctx.from.id.toString() },
            });

            ctx.reply(`Аккаунт ${email} успешно привязан!`);
        });

        this.bot.launch();
        console.log('Telegram bot started');
    } else {
        console.warn('TELEGRAM_BOT_TOKEN not found');
    }
  }

  async sendMessage(telegramId: string, message: string) {
      if (!this.bot) return;
      try {
          await this.bot.telegram.sendMessage(telegramId, message);
      } catch (e) {
          console.error(`Failed to send telegram message to ${telegramId}`, e);
      }
  }
}
