// Shared utilities

export function cn(...classes: (string | undefined | null | false)[]): string {
  return classes.filter(Boolean).join(' ')
}

export function formatDate(date: string): string {
  return new Date(date).toLocaleDateString('pt-BR')
}




