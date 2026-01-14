// Common types
export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// Company types
export interface Company {
  id: number
  name: string
  street?: string
  zip_code?: string
  city?: string
  country: string
  website?: string
  phone?: string
  email?: string
  employee_count?: number
  potential_category?: 'A' | 'B' | 'C' | 'D'
  industry?: string
  notes?: string
  created_at: string
  updated_at: string
  contacts_count?: number
}

export interface CompanyCreate {
  name: string
  street?: string
  zip_code?: string
  city?: string
  country?: string
  website?: string
  phone?: string
  email?: string
  employee_count?: number
  potential_category?: 'A' | 'B' | 'C' | 'D'
  industry?: string
  notes?: string
}

// Contact types
export interface Contact {
  id: number
  first_name: string
  last_name: string
  email?: string
  phone?: string
  mobile?: string
  position?: string
  department?: string
  salutation?: string
  title?: string
  notes?: string
  is_primary: boolean
  is_active: boolean
  company_id?: number
  company?: Company
  full_name: string
  created_at: string
  updated_at: string
}

export interface ContactListItem {
  id: number
  first_name: string
  last_name: string
  email?: string
  phone?: string
  position?: string
  company_id?: number
  company_name?: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface ContactSearchResult {
  id: number
  full_name: string
  email?: string
  company_name?: string
}

export interface ContactCreate {
  first_name: string
  last_name: string
  email?: string
  phone?: string
  mobile?: string
  position?: string
  department?: string
  salutation?: string
  title?: string
  notes?: string
  is_primary?: boolean
  company_id?: number
}

// Lead types
export type LeadStatus = 'new' | 'contacted' | 'qualified' | 'converted' | 'disqualified'

export interface Lead {
  id: number
  status: LeadStatus
  source?: string
  utm_source?: string
  utm_medium?: string
  utm_campaign?: string
  notes?: string
  contact_id: number
  campaign_id?: number
  contact?: ContactListItem
  campaign?: Campaign
  created_at: string
  updated_at: string
}

export interface LeadListItem {
  id: number
  status: LeadStatus
  source?: string
  contact_id: number
  contact_name: string
  contact_email?: string
  company_name?: string
  campaign_id?: number
  campaign_name?: string
  created_at: string
  updated_at: string
}

export interface LeadCreate {
  contact_id: number
  campaign_id?: number
  status?: LeadStatus
  source?: string
  notes?: string
}

export interface LeadImportResult {
  total_rows: number
  imported: number
  failed: number
  errors: string[]
}

// Campaign types
export interface Campaign {
  id: number
  name: string
  description?: string
  type: string
  source?: string
  start_date?: string
  end_date?: string
  is_active: boolean
  landing_page_url?: string
  lead_magnet?: string
  created_at: string
  updated_at: string
  leads_count?: number
}

// Task types
export type TaskStatus = 'open' | 'in_progress' | 'completed' | 'cancelled'
export type TaskPriority = 'low' | 'medium' | 'high' | 'urgent'

export interface Task {
  id: number
  title: string
  description?: string
  status: TaskStatus
  priority: TaskPriority
  due_date?: string
  completed_at?: string
  contact_id?: number
  assigned_to?: string
  created_by?: string
  parent_task_id?: number
  contact?: ContactListItem
  created_at: string
  updated_at: string
}

export interface TaskListItem {
  id: number
  title: string
  status: TaskStatus
  priority: TaskPriority
  due_date?: string
  assigned_to?: string
  contact_id?: number
  contact_name?: string
  is_overdue: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
  status?: TaskStatus
  priority?: TaskPriority
  due_date?: string
  contact_id?: number
  assigned_to?: string
  parent_task_id?: number
}

// Contact History types
export type HistoryType = 'note' | 'call' | 'email' | 'meeting' | 'status_change' | 'task_created' | 'data_change' | 'lead_created'

export interface ContactHistoryItem {
  id: number
  type: HistoryType
  title: string
  content?: string
  metadata?: string
  created_by?: string
  contact_id: number
  created_at: string
  updated_at: string
}

// Email Template types
export interface EmailTemplate {
  id: number
  name: string
  subject: string
  body: string
  description?: string
  category?: string
  is_active: boolean
  variables?: string[]
  created_at: string
  updated_at: string
}

// Setting types
export type SettingValueType = 'string' | 'number' | 'boolean' | 'json'

export interface Setting {
  id: number
  key: string
  category: string
  value?: string
  value_type: SettingValueType
  created_at: string
  updated_at: string
}

export interface SettingCreate {
  key: string
  category: string
  value?: string
  value_type?: SettingValueType
}

export interface SettingUpdate {
  value?: string
  value_type?: SettingValueType
}

// Lookup Value types
export interface LookupValue {
  id: number
  category: string
  value: string
  label: string
  sort_order: number
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface LookupValueCreate {
  category: string
  value: string
  label: string
  sort_order?: number
  is_active?: boolean
}

export interface LookupValueUpdate {
  value?: string
  label?: string
  sort_order?: number
  is_active?: boolean
}
