import React from 'react'
import { cn } from '@/shared/utils'

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
  error?: string
}

export function Input({ label, error, className, ...props }: InputProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <input
        className={cn(
          "w-full px-3 py-2 border border-gray-300 rounded-lg",
          "bg-white text-gray-900 placeholder-gray-400",
          "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
          "hover:border-gray-400 transition-colors",
          error && "border-red-500 focus:ring-red-500 focus:border-red-500",
          "disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed",
          className
        )}
        {...props}
      />
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}



