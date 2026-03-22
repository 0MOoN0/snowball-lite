export interface Category {
  id?: number
  categoryName?: string
  children?: Category[]
  pid?: number
}
