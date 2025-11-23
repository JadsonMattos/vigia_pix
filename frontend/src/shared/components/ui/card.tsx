import React from 'react'
import { cn } from '@/shared/utils'

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {}

export function Card({ children, className, ...props }: CardProps) {
  return (
    <div
      className={cn(
        'bg-white rounded-lg shadow-md border border-gray-200 p-6',
        className
      )}
      {...props}
    >
      {children}
    </div>
  )
}

export function CardHeader({ children, className, ...props }: CardProps) {
  return (
    <div className={cn('mb-4', className)} {...props}>
      {children}
    </div>
  )
}

export function CardTitle({ children, className, ...props }: CardProps) {
  return (
    <h3 className={cn('text-xl font-semibold text-gray-900', className)} {...props}>
      {children}
    </h3>
  )
}

export function CardContent({ children, className, ...props }: CardProps) {
  return (
    <div className={cn('text-gray-700', className)} {...props}>
      {children}
    </div>
  )
}

export function CardFooter({ children, className, ...props }: CardProps) {
  return (
    <div className={cn('mt-4 pt-4 border-t border-gray-200', className)} {...props}>
      {children}
    </div>
  )
}



