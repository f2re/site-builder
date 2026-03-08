export interface C2CShipmentResponse {
  provider: string
  order_id: string
  recipient_name: string
  recipient_phone: string
  pvz_code: string
  pvz_address: string
  declared_value: number
  weight_kg: number
  comment: string
  deeplink: string
  instructions: string[]
}

export const useC2CShipment = (orderId: string) => {
  return useApi<C2CShipmentResponse>(`/delivery/orders/${orderId}/c2c-shipment`)
}
