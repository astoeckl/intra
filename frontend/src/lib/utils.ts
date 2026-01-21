/**
 * Utility Functions.
 *
 * Common helpers used throughout the application.
 */

import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

/**
 * Merge Tailwind CSS classes with proper precedence.
 *
 * Combines clsx for conditional classes with tailwind-merge
 * to handle conflicting utility classes correctly.
 *
 * @param inputs - Class values to merge (strings, arrays, objects).
 * @returns Merged class string.
 */
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
