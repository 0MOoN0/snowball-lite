type ColumnField = {
  /**
   * 列标题
   */
  title: string
  /**
   * 能否编辑
   */
  editable: boolean
  /**
   * 后端返回字段名
   */
  field: string
  /**
   * 是否展示
   */
  isShow: boolean
  /**
   * 是否为ID
   */
  isId: boolean
  dataFrom?: any
}
