import { Controller, Get, Query } from '@nestjs/common';
import { ReportsService } from './reports.service';

@Controller('reports')
export class ReportsController {
  constructor(private readonly reportsService: ReportsService) {}

  @Get()
  async getReport(@Query('start') start: string, @Query('end') end: string) {
    const startDate = start ? new Date(start) : new Date(new Date().setDate(new Date().getDate() - 7)); // Default last 7 days
    const endDate = end ? new Date(end) : new Date();
    return this.reportsService.generateTaskReport(startDate, endDate);
  }
}
