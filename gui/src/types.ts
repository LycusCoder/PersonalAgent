export interface RamStatus {
  total_gb: number
  used_gb: number
  available_gb: number
  percent: number
}

export interface CpuStatus {
  percent: number
  cores_physical: number
  cores_logical: number
  freq_current_mhz: number
}

export interface GpuStatus {
  name: string
  temperature_c: number
  utilization_percent: number
  memory_used_mb: number
  memory_total_mb: number
}

export interface StatusResponse {
  success: boolean
  data: {
    ram: RamStatus
    cpu: CpuStatus
    gpu: GpuStatus
  }
}
