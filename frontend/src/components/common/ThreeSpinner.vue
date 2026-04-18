<script setup lang="ts">
import { onMounted, onUnmounted, useTemplateRef } from 'vue'
import * as THREE from 'three'
import { LineSegmentsGeometry } from 'three/examples/jsm/lines/LineSegmentsGeometry.js'
import { LineMaterial } from 'three/examples/jsm/lines/LineMaterial.js'
import { LineSegments2 } from 'three/examples/jsm/lines/LineSegments2.js'

const props = withDefaults(
  defineProps<{
    size?: number
    /** 十六进制颜色，如 0x2f6b53 */
    color?: number
    /** 线宽 */
    lineWidth?: number
    /** 是否播放动画，false 时停在最后一帧 */
    active?: boolean
  }>(),
  {
    size: 44,
    color: 0x2f6b53,
    lineWidth: 1.8,
    active: true,
  },
)

const canvasRef = useTemplateRef<HTMLCanvasElement>('canvas')

// 提升到 setup 顶层，onUnmounted 才能访问释放
let rafId = 0
let renderer: THREE.WebGLRenderer | null = null
let scene: THREE.Scene | null = null
let geometry: LineSegmentsGeometry | null = null
let material: LineMaterial | null = null

onMounted(() => {
  const canvas = canvasRef.value!
  const W = props.size
  const H = props.size
  const dpr = window.devicePixelRatio || 1

  renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true })
  renderer.setPixelRatio(dpr)
  renderer.setSize(W, H)

  scene = new THREE.Scene()
  const camera = new THREE.PerspectiveCamera(38, 1, 0.1, 100)
  camera.position.set(0, 0, 6.5)

  // ---- 顶点定义 ----
  const T = [0, 1.7, 0],
    B = [0, -1.7, 0]
  const L = [-1.7, 0, 0],
    R = [1.7, 0, 0]
  const F = [0, 0, 1.7],
    BK = [0, 0, -1.7]
  const s = 0.88
  const M0 = [s, 0, s],
    M1 = [-s, 0, s]
  const M2 = [-s, 0, -s],
    M3 = [s, 0, -s]
  const U = 0.72,
    UH = 0.72
  const U0 = [U, UH, 0],
    U1 = [0, UH, U]
  const U2 = [-U, UH, 0],
    U3 = [0, UH, -U]
  const D0 = [U, -UH, 0],
    D1 = [0, -UH, U]
  const D2 = [-U, -UH, 0],
    D3 = [0, -UH, -U]

  const v = [T, B, L, R, F, BK, M0, M1, M2, M3, U0, U1, U2, U3, D0, D1, D2, D3]
  const edges: [number, number][] = [
    // 上尖 → 上腰
    [0, 10],
    [0, 11],
    [0, 12],
    [0, 13],
    // 下尖 → 下腰
    [1, 14],
    [1, 15],
    [1, 16],
    [1, 17],
    // 前后左右尖 → 中腰
    [4, 6],
    [4, 7],
    [5, 8],
    [5, 9],
    [2, 7],
    [2, 8],
    [3, 6],
    [3, 9],
    // 上腰环
    [10, 11],
    [11, 12],
    [12, 13],
    [13, 10],
    // 下腰环
    [14, 15],
    [15, 16],
    [16, 17],
    [17, 14],
    // 中腰环
    [6, 7],
    [7, 8],
    [8, 9],
    [9, 6],
    // 上腰 → 中腰
    [10, 6],
    [11, 7],
    [12, 8],
    [13, 9],
    // 下腰 → 中腰
    [14, 6],
    [15, 7],
    [16, 8],
    [17, 9],
    // 对角穿插 ← 这4行删掉
    // [10, 15], [11, 16], [12, 17], [13, 14],
  ]

  const positions: number[] = []
  for (const [a, b] of edges) {
    positions.push(...v[a]!, ...v[b]!)
  }

  geometry = new LineSegmentsGeometry()
  geometry.setPositions(new Float32Array(positions))

  material = new LineMaterial({
    color: props.color,
    linewidth: props.lineWidth,
    resolution: new THREE.Vector2(W * dpr, H * dpr),
  })

  const mesh = new LineSegments2(geometry, material)
  const group = new THREE.Group()
  group.add(mesh)
  scene.add(group)

  // ---- 动画 ----
  let ry = 0
  let t = 0
  const speed = (tt: number) =>
    (0.05 + Math.pow(Math.sin(tt * 0.8), 2) * 0.08 + Math.pow(Math.sin(tt * 0.31), 2) * 0.03) * 1.2

  const TARGET_RY = 1.58
  const TARGET_RX = 1.09
  const TARGET_RZ = 0.49

  const animate = () => {
    rafId = requestAnimationFrame(animate)

    if (props.active) {
      t += 0.016
      ry += speed(t)
      group.rotation.y = ry
      group.rotation.x = Math.sin(t * 0.42) * 0.38 + 0.15
      group.rotation.z = Math.sin(t * 0.27) * 0.09
    } else {
      // 平滑插值归位到好看角度
      group.rotation.y += (TARGET_RY - group.rotation.y) * 0.06
      group.rotation.x += (TARGET_RX - group.rotation.x) * 0.06
      group.rotation.z += (TARGET_RZ - group.rotation.z) * 0.06
    }

    renderer!.render(scene!, camera)
  }
  animate()
})

onUnmounted(() => {
  cancelAnimationFrame(rafId)
  // 释放 GPU 资源，避免 WebGL context 泄漏
  geometry?.dispose()
  material?.dispose()
  renderer?.dispose()
  // 清空 scene 引用，让 GC 能回收
  scene = null
  renderer = null
  geometry = null
  material = null
})
</script>

<template>
  <canvas
    ref="canvas"
    :width="size"
    :height="size"
    :style="{ display: 'block', width: size + 'px', height: size + 'px' }"
  />
</template>
