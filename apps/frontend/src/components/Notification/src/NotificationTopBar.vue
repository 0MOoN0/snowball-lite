<script setup lang="ts">
import { useDesign } from '@/hooks/web/useDesign'
import { ElDropdown, ElDropdownItem, ElDropdownMenu } from 'element-plus'
// 导入获取通知的接口
import * as notificationApi from '@/api/snow/Notification/index'
import { reactive, ref, onMounted, onUnmounted } from 'vue'
import dayjs from 'dayjs'
// 导入路由组件
import { useRouter } from 'vue-router'
import { SnowNotification } from '@/api/snow/Notification/types'
const router = useRouter()

// 分页参数信息
const pageParam = reactive({
  page: 1,
  pageSize: 10
})

// 通知列表对象
const notificationList = ref<Array<SnowNotification>>([])

// 未读通知数量
const notificationCount = ref(0)

const { getPrefixCls } = useDesign()

const prefixCls = getPrefixCls('user-info')

// 定时器
const intervalNotice = ref<NodeJS.Timeout | null>(null)

// == 变量定义结束 ==

// 跳转到通知管理页面
const showNotice = () => {
  router.push({
    path: '/dashboard/notification',
  })
}

const getNotification = async () => {
  const res = await notificationApi.getNotificationList(pageParam)

  // 如果请求成功，则将数据赋值给通知列表对象
  if (res.data) {
    // 遍历items，将content字段转换为json对象
    res.data.items.forEach((item) => {
      item.content = JSON.parse(item.content)
    })
    notificationList.value = res.data.items
  }
}

// 获取未读通知数量
const getNotificationCount = async () => {
  const res = await notificationApi.getNotificationCount({ noticeStatus: 1 })
  if (res.data) {
    notificationCount.value = res.data
  }
}


// 使用dayjs格式化日期，当天内的数据显示为多少分钟/小时前，当天之前的数据显示为日期
const formatTime = (time: string) => {
  const date = dayjs(time)
  const now = dayjs()
  const diff = now.diff(date, 'minute')
  if (diff < 60) {
    return `${diff}分钟前`
  } else if (diff < 60 * 24) {
    return `${Math.floor(diff / 60)}小时前`
  } else {
    return date.format('YYYY-MM-DD')
  }
}

// 判断通知状态方法，如果通知状态为已读且通知类型为通知类型，返回灰色样式，否则返回空串
const getNoticeStatus = (row: SnowNotification) => {
  if (row.noticeStatus == 2 && row.noticeType == 0) {
    return { color: '#606266' }
  } else {
    return ''
  }
}

// 跳转到通知详情
const showNoticeDetail = (row: SnowNotification) => {
  // 跳转到通知详情页面
  router.push({
    path: '/dashboard/notification/detail',
    query: {
      id: row.id
    }
  })
}

// getNotification()
getNotificationCount()



// == hooks
// 开启一个定时器
onMounted(() => {
  intervalNotice.value = setInterval(() => {
    // getNotificationCount()
  }, 60 * 1000)
})

// 卸载组件时清除定时器
onUnmounted(() => {
  if (intervalNotice.value)
    clearInterval(intervalNotice.value as NodeJS.Timeout)
})

</script>

<template>
  <ElDropdown :class="prefixCls" trigger="click" type="text">
    <el-badge :value="notificationCount" class="item">
      <el-button icon="Bell" link @click="getNotification">通知</el-button>
    </el-badge>
    <template #dropdown>
      <ElDropdownMenu>
        <ElDropdownItem v-for="item in notificationList" :key="item.id">
          <div @click="showNoticeDetail(item)" :style="getNoticeStatus(item)">
            <!-- 通知标题 -->
            <div style="text-align: center;" v-bind:style="{ color: (item?.noticeStatus || 0) > 1 ? 'gray' : '' }">{{
              item.title }}
            </div>
            <!-- 通知时间 -->
            <div style="font-size: 12px;">{{ formatTime(item?.createTime || '') }}</div>
          </div>
        </ElDropdownItem>
        <ElDropdownItem divided>
          <div @click="showNotice" style="text-align: center; width: 100%;">查看更多</div>
        </ElDropdownItem>
      </ElDropdownMenu>
    </template>
  </ElDropdown>
</template>

<style>
/**灰色字体 */
.read_notice {
  color: #999;
}
</style>