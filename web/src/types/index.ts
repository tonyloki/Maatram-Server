/**
 * Canonical TypeScript Interfaces mirrored strictly from backend Pydantic Schemas.
 */

export type UserRole = "VOLUNTEER" | "ADMIN" | "SUPER_ADMIN";
export type UserStatus =
  | "PENDING_VERIFICATION"
  | "PENDING_APPROVAL"
  | "APPROVED"
  | "REJECTED"
  | "SUSPENDED"
  | "INACTIVE"
  | "UNVERIFIED"
  | "PENDING";
export type VolunteerCategory = "STUDENT" | "ALUMNI" | "CORPORATE";
export type EventMode = "ONLINE" | "OFFLINE";
export type EventStatus =
  | "DRAFT"
  | "PUBLISHED"
  | "REGISTRATION_CLOSED"
  | "ONGOING"
  | "COMPLETED"
  | "CANCELLED";
export type RegistrationStatus =
  | "SUBSCRIBED"
  | "SELECTED"
  | "WAITLISTED"
  | "NOT_SELECTED"
  | "DECLINED"
  | "WITHDRAWN";

// Auth & Users
export interface UserSummary {
  id: string;
  email: string;
  role: UserRole;
  status: UserStatus;
}

export interface UserMeResponse {
  id: string;
  email: string;
  role: UserRole;
  status: UserStatus;
  is_active: boolean;
  last_login_at: string | null;
  created_at: string;
  updated_at: string;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
  expires_in?: number;
  refresh_token?: string | null;
  csrf_token?: string | null;
  user: UserSummary;
}

// Registration Request Types matching backend RegisterRequest
export interface StudentDetailsInput {
  college_name: string;
  degree: string;
  department: string;
  batch_year: number;
  current_year: number;
  maatram_reg_number: string;
}

export interface AlumniDetailsInput {
  college_name: string;
  degree: string;
  department: string;
  batch_year: number;
  graduation_year: number;
  organisation: string;
  job_role: string;
  years_of_experience: number;
  location: string;
  skills: string[];
}

export interface CorporateDetailsInput {
  organisation: string;
  designation: string;
  years_of_experience: number;
  location: string;
  skills: string[];
}

export interface ConsentSettingsInput {
  leaderboard_visible: boolean;
  name_visible: boolean;
  thank_you_emails: boolean;
  linkedin_content: boolean;
  contact_available: boolean;
  media_usage: boolean;
}

export interface RegisterInput {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
  mobile_number: string;
  age: number;
  gender: "MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY";
  category: VolunteerCategory;
  parent_guardian_name?: string | null;
  parent_guardian_relationship?: string | null;
  parent_guardian_contact?: string | null;
  parental_consent_claimed?: boolean;
  parental_consent_submitted?: boolean;
  student_details?: StudentDetailsInput | null;
  alumni_details?: AlumniDetailsInput | null;
  corporate_details?: CorporateDetailsInput | null;
  consent?: ConsentSettingsInput | null;
}

export interface RegisterResponse {
  user_id: string;
  email: string;
  status: string;
  parental_consent_status: string;
  parental_consent_claimed: boolean;
  message: string;
}

// Affirmative Consent (6 Canonical Dimensions)
export interface ConsentResponse {
  id: string;
  volunteer_profile_id: string;
  leaderboard_visible: boolean;
  name_visible: boolean;
  thank_you_emails: boolean;
  linkedin_content: boolean;
  contact_available: boolean;
  media_usage: boolean;
  version: number;
  updated_at: string;
}

export interface ConsentUpdate {
  leaderboard_visible?: boolean;
  name_visible?: boolean;
  thank_you_emails?: boolean;
  linkedin_content?: boolean;
  contact_available?: boolean;
  media_usage?: boolean;
}

// Volunteer Profile & Polymorphic Categories
export interface StudentProfile {
  college_name: string;
  degree: string;
  department: string;
  batch_year: number;
  current_year: number;
  maatram_reg_number: string;
}

export interface AlumniProfile {
  organisation: string;
  job_role: string;
  years_of_experience: number;
  location: string;
  skills: string[];
  college_name: string;
  degree: string;
  department: string;
  batch_year: number;
  graduation_year: number;
}

export interface CorporateProfile {
  organisation: string;
  designation: string;
  years_of_experience: number;
  location: string;
  skills: string[];
}

export interface VolunteerProfileResponse {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  mobile_number: string;
  age: number;
  gender: string;
  category: VolunteerCategory;
  avatar_media_id?: string | null;
  bio?: string | null;
  parent_guardian_name?: string | null;
  parent_guardian_relationship?: string | null;
  parent_guardian_contact?: string | null;
  parental_consent_claimed: boolean;
  parental_consent_evidence_submitted: boolean;
  parental_consent_verified: boolean;
  parental_consent_status: "NOT_REQUIRED" | "PENDING" | "VERIFIED" | "REJECTED";
  parental_consent_notes?: string | null;
  is_minor?: boolean;
  date_of_birth?: string | null;
  address_line1?: string | null;
  address_line2?: string | null;
  city?: string | null;
  state?: string | null;
  pincode?: string | null;
  emergency_contact_name?: string | null;
  emergency_contact_relationship?: string | null;
  emergency_contact_phone?: string | null;
  college_name?: string | null;
  department?: string | null;
  graduation_year?: number | string | null;
  student_id?: string | null;
  employer_name?: string | null;
  job_title?: string | null;
  industry?: string | null;
  corporate_id?: string | null;
  skills?: string[] | null;
  student_profile?: StudentProfile | null;
  alumni_profile?: AlumniProfile | null;
  corporate_profile?: CorporateProfile | null;
  created_at: string;
  updated_at: string;
}

export interface VolunteerProfileUpdate {
  first_name?: string;
  last_name?: string;
  mobile_number?: string;
  gender?: "MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY";
  bio?: string | null;
  parent_guardian_name?: string | null;
  parent_guardian_relationship?: string | null;
  parent_guardian_contact?: string | null;
  student_details?: Partial<StudentProfile>;
  alumni_details?: Partial<AlumniProfile>;
  corporate_details?: Partial<CorporateProfile>;
}

// Events
export interface EventItem {
  id: string;
  title: string;
  category: string;
  status: EventStatus;
  mode: EventMode;
  location?: string | null;
  meeting_url?: string | null;
  start_time: string;
  end_time: string;
  capacity: number;
  description?: string | null;
  registration_deadline: string;
  withdrawal_deadline: string;
  banner_media_id?: string | null;
  registered_count: number;
  selected_count: number;
  attended_count: number;
}

export interface EventListResponse {
  items: EventItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Registrations
export interface RegistrationHistoryItem {
  id: string;
  registration_id: string;
  old_status: string;
  new_status: string;
  changed_by_user_id: string;
  reason?: string | null;
  created_at: string;
}

export interface EventSummary {
  id: string;
  title: string;
  category: string;
  mode: string;
  location: string;
  start_time: string;
  end_time: string;
  status: string;
}

export interface RegistrationResponse {
  id: string;
  event_id: string;
  volunteer_profile_id: string;
  status: RegistrationStatus;
  selected_at?: string | null;
  withdrawn_at?: string | null;
  notes?: string | null;
  created_at: string;
  updated_at: string;
  event?: EventSummary | null;
  history_entries?: RegistrationHistoryItem[];
}

export interface RegistrationListResponse {
  items: RegistrationResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Attendance
export interface AttendanceRecordResponse {
  id: string;
  event_registration_id: string;
  event_id: string;
  volunteer_profile_id: string;
  volunteer_name?: string | null;
  volunteer_email?: string | null;
  event_title?: string | null;
  check_in_time: string;
  check_out_time?: string | null;
  duration_minutes?: number | null;
  hours_credited: number | string;
  status: "ATTENDED" | "INCOMPLETE" | "ABSENT";
  verified_by_user_id?: string | null;
  created_at: string;
  updated_at: string;
  corrections_count: number;
}

export interface AttendanceListResponse {
  items: AttendanceRecordResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// Gamification & Leaderboard
export interface GamificationSummaryResponse {
  volunteer_profile_id: string;
  total_points: number | string;
  total_hours: number | string;
  completed_events_count: number;
  badges_earned_count: number;
  rank?: number | null;
  cycle_year: number;
}

export interface PointTransactionResponse {
  id: string;
  volunteer_profile_id: string;
  event_id?: string | null;
  related_transaction_id?: string | null;
  event_points: number | string;
  hour_points: number | string;
  total_points: number | string;
  hours_credited: number | string;
  transaction_type: string;
  reason?: string | null;
  cycle_year: number;
  created_at: string;
}

export interface PointLedgerResponse {
  items: PointTransactionResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
  net_points: number | string;
}

export interface LeaderboardItem {
  rank: number;
  volunteer_profile_id?: string | null;
  volunteer_name: string;
  category: string;
  total_points: number | string;
  events_attended: number;
  total_hours: number | string;
  is_anonymous: boolean;
  avatar_url?: string | null;
}

export interface LeaderboardResponse {
  cycle_year: number;
  category: string;
  items: LeaderboardItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface AchievementBadge {
  id: string;
  code: string;
  title: string;
  description: string;
  icon_url: string;
  category: string;
  criteria_type: string;
  criteria_threshold: number | string;
  is_active: boolean;
  is_earned: boolean;
  awarded_at?: string | null;
}

export interface VolunteerAchievementsListResponse {
  items: AchievementBadge[];
  total_earned: number;
  total_available: number;
}

// Notifications
export interface NotificationItem {
  id: string;
  user_id: string;
  title: string;
  message: string;
  type: string;
  action_url?: string | null;
  is_read: boolean;
  read_at?: string | null;
  created_at: string;
}

export interface NotificationListResponse {
  items: NotificationItem[];
  total: number;
  unread_count: number;
  page: number;
  limit: number;
}

export interface UnreadCountResponse {
  unread_count: number;
}

// ==========================================
// Admin Dashboard & Audit Logs
// ==========================================

export interface VolunteerStats {
  total_volunteers: number;
  active_volunteers: number;
  by_category: Record<string, number>;
}

export interface ApplicationPipelineStats {
  pending: number;
  approved: number;
  rejected: number;
  total: number;
}

export interface EventStats {
  total_events: number;
  by_status: Record<string, number>;
  completed_events: number;
}

export interface EngagementMetrics {
  total_registrations: number;
  total_hours_credited: string;
  total_points_allocated: string;
}

export interface ActivityItem {
  id: string;
  action: string;
  actor_email?: string | null;
  resource_type: string;
  resource_id: string;
  created_at: string;
}

export interface AdminDashboardResponse {
  volunteers: VolunteerStats;
  applications: ApplicationPipelineStats;
  events: EventStats;
  engagement: EngagementMetrics;
  recent_activity: ActivityItem[];
}

export interface AuditLogResponse {
  id: string;
  actor_user_id?: string | null;
  actor_email?: string | null;
  action: string;
  resource_type: string;
  resource_id: string;
  old_state?: Record<string, unknown> | null;
  new_state?: Record<string, unknown> | null;
  reason?: string | null;
  created_at: string;
}

export interface AuditLogListResponse {
  items: AuditLogResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ==========================================
// Onboarding Applications & Reviews
// ==========================================

export interface ApplicationReviewResponse {
  id: string;
  application_id: string;
  reviewer_id: string;
  action: "APPROVED" | "REJECTED";
  reason?: string | null;
  created_at: string;
}

export interface ApplicationResponse {
  id: string;
  volunteer_profile_id: string;
  status: "PENDING" | "APPROVED" | "REJECTED";
  submitted_at: string;
  current_stage: number;
  notes?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ApplicationDetailResponse extends ApplicationResponse {
  volunteer_profile: VolunteerProfileResponse;
  user_email: string;
  user_status: string;
  reviews: ApplicationReviewResponse[];
}

export interface ApplicationListResponse {
  items: ApplicationDetailResponse[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ==========================================
// Volunteer Directory
// ==========================================

export interface VolunteerListItem {
  id: string;
  user_id: string;
  first_name: string;
  last_name: string;
  email: string;
  mobile_number: string;
  category: VolunteerCategory;
  user_status: UserStatus;
  is_active: boolean;
  parental_consent_status: string;
  total_points: string;
  total_hours: string;
  events_attended: number;
  college_name?: string | null;
  degree?: string | null;
  department?: string | null;
  organisation?: string | null;
  employer_name?: string | null;
  job_role?: string | null;
  job_title?: string | null;
  skills?: string[] | null;
  is_minor?: boolean;
  created_at: string;
}

export interface VolunteerListResponse {
  items: VolunteerListItem[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

// ==========================================
// Event Participant Selection
// ==========================================

export interface SelectionRequest {
  registration_ids: string[];
}

export interface BatchSelectionResponse {
  selected_count: number;
  failed_count: number;
  errors: string[];
  message: string;
}

// ==========================================
// Attendance & Hours Correction
// ==========================================

export interface CheckInRequest {
  volunteer_profile_ids: string[];
  check_in_time?: string | null;
}

export interface CheckOutRequest {
  volunteer_profile_ids: string[];
  check_out_time?: string | null;
}

export interface AttendanceCorrectionRequest {
  hours_credited?: number | string | null;
  status?: "ATTENDED" | "INCOMPLETE" | "ABSENT" | null;
  check_in_time?: string | null;
  check_out_time?: string | null;
  reason: string;
}

export interface BulkAttendanceRequest {
  check_ins: Array<{ volunteer_profile_id: string; check_in_time?: string | null }>;
  check_outs: Array<{ volunteer_profile_id: string; check_out_time?: string | null }>;
}

export interface BulkAttendanceResponse {
  successful_check_ins: number;
  successful_check_outs: number;
  failed_records: Array<{ volunteer_profile_id: string; reason: string }>;
}

// ==========================================
// Event Completion & Gamification Preview
// ==========================================

export interface EventCompletionPreviewParticipant {
  volunteer_profile_id: string;
  volunteer_name: string;
  category: string;
  hours_credited: string;
  event_points: string;
  hour_points: string;
  total_points: string;
  status: string;
}

export interface EventCompletionPreviewResponse {
  event_id: string;
  event_title: string;
  selected_count: number;
  attended_count: number;
  incomplete_count: number;
  absent_count: number;
  total_hours_to_credit: string;
  total_points_to_award: string;
  participants: EventCompletionPreviewParticipant[];
  warnings: string[];
  is_ready_for_completion: boolean;
}

export interface EventCompletionResponse {
  event_id: string;
  event_status: string;
  total_volunteers_credited: number;
  total_hours_credited: string;
  total_points_awarded: string;
  message: string;
}

// ==========================================
// Reports & Exports
// ==========================================

export interface StudentContributionItem {
  volunteer_id: string;
  student_name: string;
  college_name: string;
  department: string;
  batch_year?: number | null;
  maatram_reg_number?: string | null;
  events_attended: number;
  hours_credited: string;
  points_earned: string;
}

export interface StudentContributionReportResponse {
  items: StudentContributionItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface AlumniContributionItem {
  volunteer_id: string;
  alumni_name: string;
  graduation_batch?: number | null;
  employer?: string | null;
  designation?: string | null;
  events_attended: number;
  hours_credited: string;
  points_earned: string;
}

export interface AlumniContributionReportResponse {
  items: AlumniContributionItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface YearlyConsistencyMetric {
  year: number;
  events_attended: number;
  hours_credited: string;
}

export interface AlumniConsistencyItem {
  volunteer_id: string;
  alumni_name: string;
  graduation_batch?: number | null;
  employer?: string | null;
  yearly_metrics: YearlyConsistencyMetric[];
  years_active_count: number;
  is_consistent: boolean;
}

export interface AlumniConsistencyReportResponse {
  items: AlumniConsistencyItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface InactiveVolunteerItem {
  volunteer_id: string;
  name: string;
  email: string;
  category: string;
  registration_date: string;
  last_activity_date?: string | null;
  days_inactive: number;
}

export interface InactiveVolunteerReportResponse {
  threshold_days: number;
  items: InactiveVolunteerItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface InterviewAvailabilityItem {
  volunteer_id: string;
  name: string;
  category: string;
  employer?: string | null;
  designation?: string | null;
  skills: string[];
  experience_years?: number | null;
  phone_number: string;
  email: string;
  is_contact_masked: boolean;
}

export interface InterviewAvailabilityReportResponse {
  items: InterviewAvailabilityItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface OrganisationContributionItem {
  organisation_name: string;
  volunteer_count: number;
  total_events_attended: number;
  total_hours_credited: string;
  total_points_earned: string;
}

export interface OrganisationContributionReportResponse {
  items: OrganisationContributionItem[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

// ==========================================
// Outbox Communication Jobs
// ==========================================

export interface OutboxJobResponse {
  id: string;
  channel: string;
  recipient: string;
  template_name: string;
  payload: Record<string, unknown>;
  status: "PENDING" | "PROCESSING" | "SENT" | "FAILED" | "DEAD_LETTER";
  attempts: number;
  max_retries: number;
  last_error?: string | null;
  idempotency_key: string;
  scheduled_at: string;
  locked_at?: string | null;
  worker_id?: string | null;
  sent_at?: string | null;
  created_at: string;
}

export interface OutboxJobListResponse {
  items: OutboxJobResponse[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

export interface OutboxRetryResponse {
  job_id: string;
  status: string;
  message: string;
}

