export const formatPrice = (value: string | number): string => {
  const num = typeof value === 'string' ? parseFloat(value) : value
  if (isNaN(num)) return '0 ₽'
  return num % 1 === 0
    ? `${num.toLocaleString('ru-RU')} ₽`
    : `${num.toLocaleString('ru-RU', { minimumFractionDigits: 2, maximumFractionDigits: 2 })} ₽`
}
