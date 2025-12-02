import { Typography, List, ListItem, ListItemText, Chip, Fab, Dialog, DialogTitle, DialogContent, TextField, DialogActions, MenuItem, FormControl, InputLabel, Select, Button } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import api from '../api/axios';
import { useForm } from 'react-hook-form';
import { useAuthStore } from '../store/authStore';
import { useEffect, useState } from 'react';

interface Task {
  id: string;
  title: string;
  status: string;
  priority: string;
  dueDate: string;
  assignee?: { firstName: string; lastName: string };
}

export const TaskDashboard = () => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [open, setOpen] = useState(false);
  const { register, handleSubmit, reset } = useForm();
  const { user } = useAuthStore();

  const fetchTasks = async () => {
    try {
      const res = await api.get('/tasks');
      setTasks(res.data);
    } catch (e) {
      console.error(e);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, []);

  const onSubmit = async (data: any) => {
    try {
      await api.post('/tasks', { ...data, creatorId: user?.id });
      setOpen(false);
      reset();
      fetchTasks();
    } catch (e) {
      console.error(e);
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'CRITICAL': return 'error';
      case 'IMPORTANT': return 'warning';
      default: return 'default';
    }
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>Задачи</Typography>
      <List>
        {tasks.map((task) => (
          <ListItem key={task.id} divider>
            <ListItemText
              primary={task.title}
              secondary={`Исполнитель: ${task.assignee ? task.assignee.firstName : 'Не назначен'} | Дедлайн: ${task.dueDate ? new Date(task.dueDate).toLocaleDateString() : 'Нет'}`}
            />
            <Chip label={task.status} sx={{ mr: 1 }} />
            <Chip label={task.priority} color={getPriorityColor(task.priority) as any} size="small" />
          </ListItem>
        ))}
      </List>
      <Fab color="primary" sx={{ position: 'fixed', bottom: 16, right: 16 }} onClick={() => setOpen(true)}>
        <AddIcon />
      </Fab>

      <Dialog open={open} onClose={() => setOpen(false)}>
        <DialogTitle>Новая задача</DialogTitle>
        <form onSubmit={handleSubmit(onSubmit)}>
          <DialogContent>
            <TextField fullWidth label="Заголовок" margin="dense" {...register('title', { required: true })} />
            <FormControl fullWidth margin="dense">
                <InputLabel>Приоритет</InputLabel>
                <Select defaultValue="NORMAL" {...register('priority')}>
                    <MenuItem value="CRITICAL">Критично</MenuItem>
                    <MenuItem value="IMPORTANT">Важно</MenuItem>
                    <MenuItem value="NORMAL">Нормально</MenuItem>
                    <MenuItem value="LOW">Можно позже</MenuItem>
                </Select>
            </FormControl>
            <TextField fullWidth type="date" margin="dense" InputLabelProps={{ shrink: true }} label="Дедлайн" {...register('dueDate')} />
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setOpen(false)}>Отмена</Button>
            <Button type="submit">Создать</Button>
          </DialogActions>
        </form>
      </Dialog>
    </div>
  );
};
