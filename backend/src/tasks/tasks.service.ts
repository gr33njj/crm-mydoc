import { Injectable } from '@nestjs/common';
import { CreateTaskDto } from './dto/create-task.dto';
import { UpdateTaskDto } from './dto/update-task.dto';
import { PrismaService } from '../prisma/prisma.service';
import { TelegramService } from '../telegram/telegram.service';

@Injectable()
export class TasksService {
  constructor(
    private prisma: PrismaService,
    private telegramService: TelegramService,
  ) {}

  async create(createTaskDto: CreateTaskDto) {
    const task = await this.prisma.task.create({
      data: createTaskDto,
      include: { assignee: true },
    });

    if (task.assignee && task.assignee.telegramId) {
        this.telegramService.sendMessage(
            task.assignee.telegramId, 
            `Вам назначена новая задача: ${task.title}`
        );
    }

    return task;
  }

  findAll() {
    return this.prisma.task.findMany({
        include: {
            assignee: true,
            creator: true,
            department: true,
        }
    });
  }

  findOne(id: string) {
    return this.prisma.task.findUnique({
      where: { id },
      include: { subTasks: true, comments: true, files: true },
    });
  }

  update(id: string, updateTaskDto: UpdateTaskDto) {
    return this.prisma.task.update({
      where: { id },
      data: updateTaskDto,
    });
  }

  remove(id: string) {
    return this.prisma.task.delete({
      where: { id },
    });
  }
}
