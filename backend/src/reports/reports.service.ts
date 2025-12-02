import { Injectable } from '@nestjs/common';
import { PrismaService } from '../prisma/prisma.service';
import { TaskStatus } from '@prisma/client';
import { format } from 'date-fns';
import { ru } from 'date-fns/locale';

@Injectable()
export class ReportsService {
  constructor(private prisma: PrismaService) {}

  async generateTaskReport(startDate: Date, endDate: Date) {
    const tasks = await this.prisma.task.findMany({
      where: {
        status: TaskStatus.DONE,
        updatedAt: {
          gte: startDate,
          lte: endDate,
        },
      },
      include: {
        creator: true,
        assignee: true,
        department: true,
      },
      orderBy: {
        updatedAt: 'desc',
      },
    });

    if (tasks.length === 0) {
      return `За период с ${format(startDate, 'dd.MM.yyyy')} по ${format(endDate, 'dd.MM.yyyy')} выполненных задач не найдено.`;
    }

    let report = `Отчёт о выполненных задачах за период ${format(startDate, 'dd.MM.yyyy', { locale: ru })} - ${format(endDate, 'dd.MM.yyyy', { locale: ru })}:\n\n`;
    report += `Всего выполнено задач: ${tasks.length}.\n\n`;

    // Group by department
    const byDept: Record<string, typeof tasks> = {};
    for (const task of tasks) {
      const deptName = task.department?.name || 'Без отдела';
      if (!byDept[deptName]) byDept[deptName] = [];
      byDept[deptName].push(task);
    }

    for (const [dept, deptTasks] of Object.entries(byDept)) {
      report += `Отдел: ${dept}\n`;
      for (const task of deptTasks) {
        report += `- "${task.title}" (выполнил: ${task.assignee?.firstName} ${task.assignee?.lastName})\n`;
      }
      report += '\n';
    }

    return report;
  }
}
