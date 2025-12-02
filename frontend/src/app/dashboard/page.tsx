'use client'

import { useQuery } from '@tanstack/react-query'
import { useAuthStore } from '@/store/authStore'
import { tasksApi } from '@/lib/api'
import { useRouter } from 'next/navigation'

export default function DashboardPage() {
  const router = useRouter()
  const { user, clearAuth } = useAuthStore()
  
  const { data: tasks, isLoading } = useQuery({
    queryKey: ['tasks'],
    queryFn: () => tasksApi.getTasks(),
  })

  const handleLogout = () => {
    clearAuth()
    router.push('/login')
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 justify-between">
            <div className="flex">
              <div className="flex flex-shrink-0 items-center">
                <h1 className="text-xl font-bold text-primary-600">CRM MyDoctor</h1>
              </div>
              <div className="ml-6 flex space-x-8">
                <a href="/dashboard" className="inline-flex items-center border-b-2 border-primary-500 px-1 pt-1 text-sm font-medium text-gray-900">
                  Задачи
                </a>
                <a href="/chat" className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700">
                  Чат
                </a>
                <a href="/reports" className="inline-flex items-center border-b-2 border-transparent px-1 pt-1 text-sm font-medium text-gray-500 hover:border-gray-300 hover:text-gray-700">
                  Отчёты
                </a>
              </div>
            </div>
            <div className="flex items-center">
              <span className="mr-4 text-sm text-gray-700">{user?.full_name}</span>
              <button
                onClick={handleLogout}
                className="rounded-md bg-primary-600 px-3 py-2 text-sm font-medium text-white hover:bg-primary-700"
              >
                Выйти
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
        <div className="mb-6 flex items-center justify-between">
          <h2 className="text-2xl font-bold text-gray-900">Мои задачи</h2>
          <button className="rounded-md bg-primary-600 px-4 py-2 text-sm font-medium text-white hover:bg-primary-700">
            + Создать задачу
          </button>
        </div>

        {isLoading ? (
          <div className="text-center">Загрузка...</div>
        ) : (
          <div className="space-y-4">
            {tasks?.length === 0 ? (
              <div className="rounded-lg bg-white p-8 text-center shadow">
                <p className="text-gray-500">У вас пока нет задач</p>
              </div>
            ) : (
              tasks?.map((task: any) => (
                <div key={task.id} className="rounded-lg bg-white p-6 shadow hover:shadow-md transition-shadow">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <h3 className="text-lg font-medium text-gray-900">{task.title}</h3>
                      {task.description && (
                        <p className="mt-1 text-sm text-gray-600">{task.description}</p>
                      )}
                      <div className="mt-3 flex items-center space-x-4 text-sm text-gray-500">
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                          task.priority === 'CRITICAL' ? 'bg-red-100 text-red-800' :
                          task.priority === 'IMPORTANT' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {task.priority === 'CRITICAL' ? 'Критично' :
                           task.priority === 'IMPORTANT' ? 'Важно' : 'Можно позже'}
                        </span>
                        <span className={`inline-flex rounded-full px-2 py-1 text-xs font-semibold ${
                          task.status === 'NEW' ? 'bg-blue-100 text-blue-800' :
                          task.status === 'IN_PROGRESS' ? 'bg-purple-100 text-purple-800' :
                          task.status === 'COMPLETED' ? 'bg-green-100 text-green-800' :
                          'bg-gray-100 text-gray-800'
                        }`}>
                          {task.status === 'NEW' ? 'Новая' :
                           task.status === 'IN_PROGRESS' ? 'В работе' :
                           task.status === 'COMPLETED' ? 'Выполнена' : task.status}
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={() => router.push(`/tasks/${task.id}`)}
                      className="ml-4 text-primary-600 hover:text-primary-900"
                    >
                      Открыть →
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </main>
    </div>
  )
}







