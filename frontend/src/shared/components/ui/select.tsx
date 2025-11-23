import React from 'react'
import { cn } from '@/shared/utils'

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  error?: string
  options: { value: string; label: string }[]
}

export function Select({ label, error, options, className, ...props }: SelectProps) {
  return (
    <div className="w-full">
      {label && (
        <label className="block text-sm font-medium text-gray-700 mb-1">
          {label}
        </label>
      )}
      <select
        className={cn(
          "w-full px-3 py-2 border border-gray-300 rounded-lg",
          "bg-white text-gray-900",
          "focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500",
          "hover:border-gray-400 transition-colors",
          error && "border-red-500 focus:ring-red-500 focus:border-red-500",
          "disabled:bg-gray-100 disabled:text-gray-500 disabled:cursor-not-allowed",
          className
        )}
        {...props}
      >
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && (
        <p className="mt-1 text-sm text-red-500">{error}</p>
      )}
    </div>
  )
}



