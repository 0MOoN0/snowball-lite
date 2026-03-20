import { nextTick, unref, ref, type Ref } from 'vue'
import { cloneDeep } from 'lodash-es'
import type { FormExpose } from '@/components/Form'
import { BASE_FIELD_NAMES, FUND_FIELD_NAMES, ETF_FIELD_NAMES, LOF_FIELD_NAMES } from './assetFormSchemas'

export const useAssetForm = (
  formRef: Ref<FormExpose | undefined>,
  updateSchema: (schema: FormSchema[]) => void,
  buildSchema: (onChange: (val: number) => void, assetType: number) => FormSchema[]
) => {
  const formDataCache = ref<Record<number, Recordable>>({})

  const handleAssetTypeChange = (val: number) => {
    const formRefEl = unref(formRef)
    if (!formRefEl) return

    const currentValues = formRefEl.formModel
    const currentAssetType = currentValues.assetType

    if (currentAssetType && currentAssetType !== val) {
      formDataCache.value[currentAssetType] = cloneDeep(currentValues)
    }

    const newSchema = buildSchema(handleAssetTypeChange, val)
    updateSchema(newSchema)

    const newValues: Recordable = {}

    BASE_FIELD_NAMES.forEach((fieldName) => {
      if (currentValues[fieldName] !== undefined) {
        newValues[fieldName] = currentValues[fieldName]
      }
    })

    newValues.assetType = val

    if (formDataCache.value[val]) {
      const cachedData = formDataCache.value[val]
      const newFieldNames = newSchema.map((field) => field.field)
      newFieldNames.forEach((fieldName) => {
        if (cachedData[fieldName] !== undefined) {
          newValues[fieldName] = cachedData[fieldName]
        }
      })
    }

    nextTick(() => {
      formRefEl.setValues(newValues)
    })
  }

  const mapAssetData = (val: any) => {
    if (!val) return {}
    const mappedValues = { ...val }
    if (val.assetType === 1 || val.assetType === 4 || val.assetType === 5) {
      FUND_FIELD_NAMES.forEach((field) => {
        if (val[field] !== undefined) mappedValues[field] = val[field]
      })
    }
    if (val.assetType === 4) {
      ETF_FIELD_NAMES.forEach((field) => {
        if (val[field] !== undefined) mappedValues[field] = val[field]
      })
    }
    if (val.assetType === 5) {
      LOF_FIELD_NAMES.forEach((field) => {
        if (val[field] !== undefined) mappedValues[field] = val[field]
      })
    }
    return mappedValues
  }

  return {
    handleAssetTypeChange,
    mapAssetData,
    formDataCache,
  }
}