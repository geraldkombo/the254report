const KEY = "maji:apiKey"

export function getApiKey(): string {
  return localStorage.getItem(KEY) || ""
}

export function setApiKey(v: string) {
  localStorage.setItem(KEY, v)
}

