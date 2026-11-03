"use client";

import React, { useState, Suspense } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import {
  GraduationCap,
  Briefcase,
  Users,
  ChevronRight,
  ChevronLeft,
  AlertCircle,
  ShieldCheck,
  ShieldAlert,
} from "lucide-react";
import { PublicHeader } from "@/components/navigation/public-header";
import { PublicFooter } from "@/components/navigation/public-footer";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input, Select } from "@/components/ui/input";
import { ConsentSwitch } from "@/components/ui/switch";
import { apiClient } from "@/lib/api-client";
import {
  VolunteerCategory,
  RegisterInput,
  RegisterResponse,
} from "@/types";

const TOTAL_STEPS = 6;

const STEP_LABELS = [
  "Basic Details",
  "Category",
  "Background",
  "Privacy & Safeguarding",
  "Security",
  "Review & Submit",
];

function RegisterWizard() {
  const router = useRouter();
  const searchParams = useSearchParams();
  const initialCategory = searchParams.get("category")?.toUpperCase() as VolunteerCategory;

  const [currentStep, setCurrentStep] = useState<number>(1);
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [submissionError, setSubmissionError] = useState<string | null>(null);
  const [stepErrors, setStepErrors] = useState<Record<string, string>>({});

  // 1. Basic Details
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [email, setEmail] = useState("");
  const [mobileNumber, setMobileNumber] = useState("+91");
  const [age, setAge] = useState<number>(20);
  const [gender, setGender] = useState<"MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY">("PREFER_NOT_TO_SAY");

  // 2. Category
  const [category, setCategory] = useState<VolunteerCategory>(
    ["STUDENT", "ALUMNI", "CORPORATE"].includes(initialCategory) ? initialCategory : "STUDENT"
  );

  // 3. Category Details
  // Student
  const [studentCollege, setStudentCollege] = useState("");
  const [studentDegree, setStudentDegree] = useState("");
  const [studentDepartment, setStudentDepartment] = useState("");
  const [studentBatchYear, setStudentBatchYear] = useState<number>(2024);
  const [studentCurrentYear, setStudentCurrentYear] = useState<number>(2);
  const [studentRegNumber, setStudentRegNumber] = useState("");

  // Alumni
  const [alumniCollege, setAlumniCollege] = useState("");
  const [alumniDegree, setAlumniDegree] = useState("");
  const [alumniDepartment, setAlumniDepartment] = useState("");
  const [alumniBatchYear, setAlumniBatchYear] = useState<number>(2020);
  const [alumniGradYear, setAlumniGradYear] = useState<number>(2024);
  const [alumniOrg, setAlumniOrg] = useState("");
  const [alumniRole, setAlumniRole] = useState("");
  const [alumniExp, setAlumniExp] = useState<number>(1);
  const [alumniLocation, setAlumniLocation] = useState("Chennai");
  const [alumniSkills, setAlumniSkills] = useState("");

  // Corporate
  const [corporateOrg, setCorporateOrg] = useState("");
  const [corporateDesignation, setCorporateDesignation] = useState("");
  const [corporateExp, setCorporateExp] = useState<number>(5);
  const [corporateLocation, setCorporateLocation] = useState("Chennai");
  const [corporateSkills, setCorporateSkills] = useState("");

  // 4. Affirmative Consents (All strictly default to FALSE per DPDP)
  const [consentLeaderboard, setConsentLeaderboard] = useState(false);
  const [consentNameVisible, setConsentNameVisible] = useState(false);
  const [consentThankYou, setConsentThankYou] = useState(false);
  const [consentLinkedin, setConsentLinkedin] = useState(false);
  const [consentContact, setConsentContact] = useState(false);
  const [consentMedia, setConsentMedia] = useState(false);

  // Minor Safeguarding (For age < 18)
  const [guardianName, setGuardianName] = useState("");
  const [guardianRelationship, setGuardianRelationship] = useState("Parent / Guardian");
  const [guardianContact, setGuardianContact] = useState("+91");
  const [parentalConsentClaimed, setParentalConsentClaimed] = useState(false);

  // 5. Credentials
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");

  // Step Validation Logic
  const validateCurrentStep = (): boolean => {
    const errors: Record<string, string> = {};

    if (currentStep === 1) {
      if (!firstName.trim()) errors.firstName = "First name is required.";
      if (!lastName.trim()) errors.lastName = "Last name is required.";
      if (!email.trim() || !email.includes("@")) errors.email = "Valid email address is required.";
      if (!mobileNumber.trim() || !mobileNumber.match(/^\+?[1-9]\d{6,14}$/)) {
        errors.mobileNumber = "Enter a valid international phone number (e.g. +919876543210).";
      }
      if (!age || age < 10 || age > 100) errors.age = "Please enter a valid age.";
    }

    if (currentStep === 2) {
      if (!category) errors.category = "Please select a volunteer category.";
    }

    if (currentStep === 3) {
      if (category === "STUDENT") {
        if (!studentCollege.trim()) errors.studentCollege = "College name is required.";
        if (!studentDegree.trim()) errors.studentDegree = "Degree is required (e.g. B.E, B.Sc).";
        if (!studentDepartment.trim()) errors.studentDepartment = "Department is required.";
        if (!studentRegNumber.trim()) errors.studentRegNumber = "Maatram Registration Number is required.";
      } else if (category === "ALUMNI") {
        if (!alumniOrg.trim()) errors.alumniOrg = "Current organisation is required.";
        if (!alumniRole.trim()) errors.alumniRole = "Job role is required.";
        if (!alumniCollege.trim()) errors.alumniCollege = "College name is required.";
        if (!alumniDegree.trim()) errors.alumniDegree = "Degree is required.";
      } else if (category === "CORPORATE") {
        if (!corporateOrg.trim()) errors.corporateOrg = "Current organisation is required.";
        if (!corporateDesignation.trim()) errors.corporateDesignation = "Designation is required.";
      }
    }

    if (currentStep === 4) {
      // If user is under 18, safeguarding fields are required
      if (age < 18) {
        if (!guardianName.trim()) errors.guardianName = "Guardian's full name is required for minors.";
        if (!guardianContact.trim() || !guardianContact.match(/^\+?[1-9]\d{6,14}$/)) {
          errors.guardianContact = "Valid guardian contact number is required.";
        }
        if (!parentalConsentClaimed) {
          errors.parentalConsentClaimed = "Parental consent acknowledgment is required for under-18 applicants.";
        }
      }
    }

    if (currentStep === 5) {
      if (!password || password.length < 8) {
        errors.password = "Password must be at least 8 characters long.";
      }
      if (password !== confirmPassword) {
        errors.confirmPassword = "Passwords do not match.";
      }
    }

    setStepErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleNext = () => {
    if (validateCurrentStep()) {
      setCurrentStep((prev) => Math.min(prev + 1, TOTAL_STEPS));
      window.scrollTo({ top: 0, behavior: "smooth" });
    }
  };

  const handleBack = () => {
    setStepErrors({});
    setCurrentStep((prev) => Math.max(prev - 1, 1));
    window.scrollTo({ top: 0, behavior: "smooth" });
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    setSubmissionError(null);

    // Build payload strictly adhering to RegisterRequest Pydantic schema
    const payload: RegisterInput = {
      email: email.trim().toLowerCase(),
      password,
      first_name: firstName.trim(),
      last_name: lastName.trim(),
      mobile_number: mobileNumber.trim(),
      age: Number(age),
      gender,
      category,
      parent_guardian_name: age < 18 ? guardianName.trim() : null,
      parent_guardian_relationship: age < 18 ? guardianRelationship.trim() : null,
      parent_guardian_contact: age < 18 ? guardianContact.trim() : null,
      parental_consent_claimed: age < 18 ? parentalConsentClaimed : false,
      parental_consent_submitted: age < 18 ? parentalConsentClaimed : false,
      consent: {
        leaderboard_visible: consentLeaderboard,
        name_visible: consentNameVisible,
        thank_you_emails: consentThankYou,
        linkedin_content: consentLinkedin,
        contact_available: consentContact,
        media_usage: consentMedia,
      },
    };

    if (category === "STUDENT") {
      payload.student_details = {
        college_name: studentCollege.trim(),
        degree: studentDegree.trim(),
        department: studentDepartment.trim(),
        batch_year: Number(studentBatchYear),
        current_year: Number(studentCurrentYear),
        maatram_reg_number: studentRegNumber.trim(),
      };
    } else if (category === "ALUMNI") {
      const skillsArr = alumniSkills
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);
      payload.alumni_details = {
        college_name: alumniCollege.trim(),
        degree: alumniDegree.trim(),
        department: alumniDepartment.trim(),
        batch_year: Number(alumniBatchYear),
        graduation_year: Number(alumniGradYear),
        organisation: alumniOrg.trim(),
        job_role: alumniRole.trim(),
        years_of_experience: Number(alumniExp),
        location: alumniLocation.trim(),
        skills: skillsArr,
      };
    } else if (category === "CORPORATE") {
      const skillsArr = corporateSkills
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);
      payload.corporate_details = {
        organisation: corporateOrg.trim(),
        designation: corporateDesignation.trim(),
        years_of_experience: Number(corporateExp),
        location: corporateLocation.trim(),
        skills: skillsArr,
      };
    }

    try {
      const response = await apiClient<RegisterResponse>("/auth/register", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      // Redirect to confirmation page with actual status
      router.push(
        `/register/confirmation?email=${encodeURIComponent(response.email)}&status=${encodeURIComponent(
          response.status
        )}&parental_consent_claimed=${response.parental_consent_claimed}`
      );
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Registration failed. Please review your details.";
      setSubmissionError(msg);
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      {/* STEPPER PROGRESS BAR */}
      <div className="mb-10">
        <div className="flex items-center justify-between mb-3 text-xs font-semibold text-[#6B7280]">
          <span>
            Step {currentStep} of {TOTAL_STEPS}
          </span>
          <span className="text-[#B45309] font-bold">{STEP_LABELS[currentStep - 1]}</span>
        </div>

        {/* Bar */}
        <div className="w-full h-2 rounded-full bg-[#E5E7EB] overflow-hidden">
          <div
            className="h-full bg-[#F5B817] transition-all duration-300 rounded-full"
            style={{ width: `${(currentStep / TOTAL_STEPS) * 100}%` }}
          />
        </div>

        {/* Step dots */}
        <div className="hidden sm:flex items-center justify-between mt-3">
          {STEP_LABELS.map((label, idx) => {
            const stepNum = idx + 1;
            const isCompleted = stepNum < currentStep;
            const isCurrent = stepNum === currentStep;
            return (
              <div key={label} className="flex flex-col items-center">
                <div
                  className={`w-6 h-6 rounded-full flex items-center justify-center text-[10px] font-bold transition-all ${
                    isCompleted
                      ? "bg-[#15803D] text-white"
                      : isCurrent
                      ? "bg-[#F5B817] text-[#1F2421] ring-4 ring-[#FFF8E7]"
                      : "bg-[#E5E7EB] text-[#6B7280]"
                  }`}
                >
                  {isCompleted ? "✓" : stepNum}
                </div>
                <span
                  className={`text-[10px] mt-1 text-center font-medium ${
                    isCurrent ? "text-[#1F2421] font-bold" : "text-[#9CA3AF]"
                  }`}
                >
                  {label}
                </span>
              </div>
            );
          })}
        </div>
      </div>

      {/* STEP CONTAINER CARD */}
      <Card className="p-6 sm:p-10 bg-white border-[#EBE6DD] shadow-lg rounded-3xl space-y-6">
        {/* Error Alert */}
        {submissionError && (
          <div className="p-4 rounded-xl bg-[#FEF2F2] border border-[#FCA5A5] text-[#991B1B] text-xs flex items-center gap-2">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{submissionError}</span>
          </div>
        )}

        {/* STEP 1: BASIC DETAILS */}
        {currentStep === 1 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">Personal & Contact Details</h2>
              <p className="text-xs text-[#6B7280]">
                Enter your identity details as per your educational or government ID records.
              </p>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="First Name"
                placeholder="Priya"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                error={stepErrors.firstName}
                required
              />
              <Input
                label="Last Name"
                placeholder="Sundaram"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                error={stepErrors.lastName}
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Email Address"
                type="email"
                placeholder="priya@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                error={stepErrors.email}
                helperText="We will send session invitations to this email."
                required
              />
              <Input
                label="Mobile Phone Number"
                placeholder="+919876543210"
                value={mobileNumber}
                onChange={(e) => setMobileNumber(e.target.value)}
                error={stepErrors.mobileNumber}
                helperText="International E.164 format (with country code)."
                required
              />
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <Input
                label="Age (Years)"
                type="number"
                min={10}
                max={100}
                value={age}
                onChange={(e) => setAge(parseInt(e.target.value) || 0)}
                error={stepErrors.age}
                helperText={age < 18 ? "Note: Under-18 volunteers will require parental consent in Step 4." : undefined}
                required
              />
              <Select
                label="Gender"
                value={gender}
                onChange={(e) =>
                  setGender(e.target.value as "MALE" | "FEMALE" | "OTHER" | "PREFER_NOT_TO_SAY")
                }
                options={[
                  { label: "Female", value: "FEMALE" },
                  { label: "Male", value: "MALE" },
                  { label: "Other", value: "OTHER" },
                  { label: "Prefer not to say", value: "PREFER_NOT_TO_SAY" },
                ]}
              />
            </div>
          </div>
        )}

        {/* STEP 2: CATEGORY SELECTION */}
        {currentStep === 2 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">Select Volunteer Category</h2>
              <p className="text-xs text-[#6B7280]">
                Choose your primary role. This determines the background verification fields and event tracks.
              </p>
            </div>

            <div className="grid grid-cols-1 gap-4">
              {/* Student */}
              <div
                onClick={() => setCategory("STUDENT")}
                className={`p-5 rounded-2xl border-2 cursor-pointer transition-all flex items-start gap-4 ${
                  category === "STUDENT"
                    ? "border-[#F5B817] bg-[#FFF8E7]/50 shadow-sm"
                    : "border-[#E5E7EB] hover:border-gray-300"
                }`}
              >
                <div className="w-12 h-12 rounded-xl bg-[#FFF8E7] text-[#946C00] flex items-center justify-center shrink-0 border border-[#F5B817]/30">
                  <GraduationCap className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-[#1F2421]">Student Volunteer</h3>
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        category === "STUDENT" ? "border-[#F5B817]" : "border-gray-300"
                      }`}
                    >
                      {category === "STUDENT" && <div className="w-2 h-2 rounded-full bg-[#F5B817]" />}
                    </div>
                  </div>
                  <p className="text-xs text-[#6B7280] mt-1 leading-relaxed">
                    Current college scholars studying at partner universities. Eligible for school awareness visits and peer mentorship.
                  </p>
                </div>
              </div>

              {/* Alumni */}
              <div
                onClick={() => setCategory("ALUMNI")}
                className={`p-5 rounded-2xl border-2 cursor-pointer transition-all flex items-start gap-4 ${
                  category === "ALUMNI"
                    ? "border-[#F5B817] bg-[#FFF8E7]/50 shadow-sm"
                    : "border-[#E5E7EB] hover:border-gray-300"
                }`}
              >
                <div className="w-12 h-12 rounded-xl bg-[#EFF6FF] text-[#1D4ED8] flex items-center justify-center shrink-0 border border-[#93C5FD]/40">
                  <Users className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-[#1F2421]">Alumni Volunteer</h3>
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        category === "ALUMNI" ? "border-[#F5B817]" : "border-gray-300"
                      }`}
                    >
                      {category === "ALUMNI" && <div className="w-2 h-2 rounded-full bg-[#F5B817]" />}
                    </div>
                  </div>
                  <p className="text-xs text-[#6B7280] mt-1 leading-relaxed">
                    Graduated Maatram scholars now working in the industry who want to give back through career mentorship and transition guidance.
                  </p>
                </div>
              </div>

              {/* Corporate */}
              <div
                onClick={() => setCategory("CORPORATE")}
                className={`p-5 rounded-2xl border-2 cursor-pointer transition-all flex items-start gap-4 ${
                  category === "CORPORATE"
                    ? "border-[#F5B817] bg-[#FFF8E7]/50 shadow-sm"
                    : "border-[#E5E7EB] hover:border-gray-300"
                }`}
              >
                <div className="w-12 h-12 rounded-xl bg-[#F0FDF4] text-[#15803D] flex items-center justify-center shrink-0 border border-[#86EFAC]/40">
                  <Briefcase className="w-6 h-6" />
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <h3 className="text-base font-bold text-[#1F2421]">Corporate Panelist</h3>
                    <div
                      className={`w-4 h-4 rounded-full border-2 flex items-center justify-center ${
                        category === "CORPORATE" ? "border-[#F5B817]" : "border-gray-300"
                      }`}
                    >
                      {category === "CORPORATE" && <div className="w-2 h-2 rounded-full bg-[#F5B817]" />}
                    </div>
                  </div>
                  <p className="text-xs text-[#6B7280] mt-1 leading-relaxed">
                    Industry leaders, managers, and software professionals conducting mock interview panels and skill workshops.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* STEP 3: CATEGORY-SPECIFIC DETAILS */}
        {currentStep === 3 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">
                {category === "STUDENT"
                  ? "Academic Details"
                  : category === "ALUMNI"
                  ? "Career & Graduation History"
                  : "Professional Profile"}
              </h2>
              <p className="text-xs text-[#6B7280]">
                These details allow our coordinators to verify your status and match you with appropriate student cohorts.
              </p>
            </div>

            {/* Student Fields */}
            {category === "STUDENT" && (
              <div className="space-y-4">
                <Input
                  label="College / Institution Name"
                  placeholder="Sathyabama Institute of Science and Technology"
                  value={studentCollege}
                  onChange={(e) => setStudentCollege(e.target.value)}
                  error={stepErrors.studentCollege}
                  required
                />
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Degree"
                    placeholder="B.E / B.Tech"
                    value={studentDegree}
                    onChange={(e) => setStudentDegree(e.target.value)}
                    error={stepErrors.studentDegree}
                    required
                  />
                  <Input
                    label="Department / Branch"
                    placeholder="Computer Science & Engineering"
                    value={studentDepartment}
                    onChange={(e) => setStudentDepartment(e.target.value)}
                    error={stepErrors.studentDepartment}
                    required
                  />
                </div>
                <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
                  <Input
                    label="Batch (Admission Year)"
                    type="number"
                    value={studentBatchYear}
                    onChange={(e) => setStudentBatchYear(parseInt(e.target.value) || 2024)}
                    required
                  />
                  <Select
                    label="Current Academic Year"
                    value={studentCurrentYear}
                    onChange={(e) => setStudentCurrentYear(parseInt(e.target.value) || 1)}
                    options={[
                      { label: "1st Year", value: 1 },
                      { label: "2nd Year", value: 2 },
                      { label: "3rd Year", value: 3 },
                      { label: "4th Year", value: 4 },
                      { label: "5th Year", value: 5 },
                    ]}
                  />
                  <Input
                    label="Maatram Reg. Number"
                    placeholder="MT-2024-042"
                    value={studentRegNumber}
                    onChange={(e) => setStudentRegNumber(e.target.value)}
                    error={stepErrors.studentRegNumber}
                    helperText="Official scholar ID."
                    required
                  />
                </div>
              </div>
            )}

            {/* Alumni Fields */}
            {category === "ALUMNI" && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Current Employer / Organisation"
                    placeholder="Tata Consultancy Services"
                    value={alumniOrg}
                    onChange={(e) => setAlumniOrg(e.target.value)}
                    error={stepErrors.alumniOrg}
                    required
                  />
                  <Input
                    label="Job Role"
                    placeholder="Software Engineer"
                    value={alumniRole}
                    onChange={(e) => setAlumniRole(e.target.value)}
                    error={stepErrors.alumniRole}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Years of Experience"
                    type="number"
                    step="0.5"
                    value={alumniExp}
                    onChange={(e) => setAlumniExp(parseFloat(e.target.value) || 0)}
                    required
                  />
                  <Input
                    label="Work Location / City"
                    placeholder="Chennai"
                    value={alumniLocation}
                    onChange={(e) => setAlumniLocation(e.target.value)}
                    required
                  />
                </div>

                <Input
                  label="Skills & Expertise (Comma separated)"
                  placeholder="Java, Python, System Design, Communication"
                  value={alumniSkills}
                  onChange={(e) => setAlumniSkills(e.target.value)}
                  helperText="These skills help match mock interview sessions."
                />

                <div className="pt-2 border-t border-[#EBE6DD]">
                  <h3 className="text-xs font-bold uppercase tracking-wider text-[#B45309] mb-3">
                    Graduation Background
                  </h3>
                  <div className="space-y-4">
                    <Input
                      label="Alma Mater College"
                      placeholder="Anna University"
                      value={alumniCollege}
                      onChange={(e) => setAlumniCollege(e.target.value)}
                      error={stepErrors.alumniCollege}
                      required
                    />
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <Input
                        label="Degree"
                        placeholder="B.E"
                        value={alumniDegree}
                        onChange={(e) => setAlumniDegree(e.target.value)}
                        error={stepErrors.alumniDegree}
                        required
                      />
                      <Input
                        label="Department / Specialization"
                        placeholder="Mechanical Engineering"
                        value={alumniDepartment}
                        onChange={(e) => setAlumniDepartment(e.target.value)}
                        required
                      />
                    </div>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                      <Input
                        label="Batch (Admission Year)"
                        type="number"
                        value={alumniBatchYear}
                        onChange={(e) => setAlumniBatchYear(parseInt(e.target.value) || 2020)}
                        required
                      />
                      <Input
                        label="Graduation Year"
                        type="number"
                        value={alumniGradYear}
                        onChange={(e) => setAlumniGradYear(parseInt(e.target.value) || 2024)}
                        required
                      />
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Corporate Fields */}
            {category === "CORPORATE" && (
              <div className="space-y-4">
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Current Employer / Organisation"
                    placeholder="Amazon / Google / Cognizant"
                    value={corporateOrg}
                    onChange={(e) => setCorporateOrg(e.target.value)}
                    error={stepErrors.corporateOrg}
                    required
                  />
                  <Input
                    label="Designation / Role"
                    placeholder="Senior Engineering Manager"
                    value={corporateDesignation}
                    onChange={(e) => setCorporateDesignation(e.target.value)}
                    error={stepErrors.corporateDesignation}
                    required
                  />
                </div>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <Input
                    label="Years of Industry Experience"
                    type="number"
                    step="0.5"
                    value={corporateExp}
                    onChange={(e) => setCorporateExp(parseFloat(e.target.value) || 0)}
                    required
                  />
                  <Input
                    label="Location / Base City"
                    placeholder="Chennai / Bangalore / Remote"
                    value={corporateLocation}
                    onChange={(e) => setCorporateLocation(e.target.value)}
                    required
                  />
                </div>

                <Input
                  label="Interview & Mentoring Specializations"
                  placeholder="Data Structures, Behavioral Interviews, Cloud, Leadership"
                  value={corporateSkills}
                  onChange={(e) => setCorporateSkills(e.target.value)}
                  helperText="List the domains where you can assess or coach students."
                />
              </div>
            )}
          </div>
        )}

        {/* STEP 4: PRIVACY & SAFEGUARDING */}
        {currentStep === 4 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">Affirmative Privacy & Consents</h2>
              <p className="text-xs text-[#6B7280]">
                Under India&apos;s DPDP regulations, every consent below is optional, independent, and defaults to disabled.
              </p>
            </div>

            {/* 6 Affirmative Consents */}
            <div className="bg-[#FAF8F3] p-5 rounded-2xl border border-[#EBE6DD] space-y-4">
              <ConsentSwitch
                label="Show my profile & score on Public Leaderboards"
                description="When disabled, your score is aggregated anonymously as 'Anonymous Scholar'."
                checked={consentLeaderboard}
                onChange={setConsentLeaderboard}
              />
              <ConsentSwitch
                label="Display my full name in volunteering event rosters"
                description="Allow selected event co-volunteers and coordinators to see your full name."
                checked={consentNameVisible}
                onChange={setConsentNameVisible}
              />
              <ConsentSwitch
                label="Receive thank-you & impact summaries by email"
                description="Quarterly celebration emails highlighting the student batches you guided."
                checked={consentThankYou}
                onChange={setConsentThankYou}
              />
              <ConsentSwitch
                label="Allow LinkedIn recognition posts by Maatram Foundation"
                description="Permission to tag your profile in public thank-you posts celebrating milestones."
                checked={consentLinkedin}
                onChange={setConsentLinkedin}
              />
              <ConsentSwitch
                label="Share my phone number with event coordinators"
                description="Facilitates WhatsApp coordination for travel logistics to school visits."
                checked={consentContact}
                onChange={setConsentContact}
              />
              <ConsentSwitch
                label="Allow session photographs to be featured in Annual Trust Reports"
                description="Media usage during volunteering workshops and annual conventions."
                checked={consentMedia}
                onChange={setConsentMedia}
              />
            </div>

            {/* Minor Safeguarding Notice if Age < 18 */}
            {age < 18 && (
              <div className="p-5 rounded-2xl bg-[#FFFBEB] border-2 border-[#FCD34D] space-y-4">
                <div className="flex items-center gap-2 text-xs font-bold uppercase tracking-wider text-[#92400E]">
                  <ShieldAlert className="w-5 h-5 text-[#D97706]" />
                  <span>Mandatory Minor Safeguarding Verification (Age {age})</span>
                </div>
                <p className="text-xs text-[#78350F] leading-relaxed">
                  Because you are under 18, Maatram Foundation requires guardian information. Please note: Entering guardian
                  details records a parental consent claim, which must be verified by administrators before event participation.
                </p>

                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
                  <Input
                    label="Parent / Guardian Full Name"
                    placeholder="R. Sundaram"
                    value={guardianName}
                    onChange={(e) => setGuardianName(e.target.value)}
                    error={stepErrors.guardianName}
                    required
                  />
                  <Input
                    label="Guardian Relationship"
                    placeholder="Father / Mother / Legal Guardian"
                    value={guardianRelationship}
                    onChange={(e) => setGuardianRelationship(e.target.value)}
                    required
                  />
                </div>

                <Input
                  label="Parent / Guardian Mobile Number"
                  placeholder="+919876543210"
                  value={guardianContact}
                  onChange={(e) => setGuardianContact(e.target.value)}
                  error={stepErrors.guardianContact}
                  required
                />

                <div className="pt-2">
                  <ConsentSwitch
                    label="I confirm that my parent/guardian has agreed to my volunteering application"
                    description="I understand that entering this claim does NOT equal verified consent, and Maatram coordinators will verify directly."
                    checked={parentalConsentClaimed}
                    onChange={setParentalConsentClaimed}
                  />
                  {stepErrors.parentalConsentClaimed && (
                    <p className="text-xs font-semibold text-[#DC2626] mt-1">
                      {stepErrors.parentalConsentClaimed}
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        )}

        {/* STEP 5: SECURITY & CREDENTIALS */}
        {currentStep === 5 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">Account Password</h2>
              <p className="text-xs text-[#6B7280]">
                Choose a strong password to protect your volunteer account and attendance logs.
              </p>
            </div>

            <div className="space-y-4">
              <Input
                label="Password"
                type="password"
                placeholder="At least 8 characters"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                error={stepErrors.password}
                required
              />
              <Input
                label="Confirm Password"
                type="password"
                placeholder="Re-enter password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                error={stepErrors.confirmPassword}
                required
              />
            </div>

            <div className="p-4 rounded-xl bg-[#F0FDF4] border border-[#BBF7D0] flex items-start gap-3 text-xs text-[#15803D]">
              <ShieldCheck className="w-5 h-5 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold block">Enterprise Password Protection</span>
                <span>
                  Passwords are salted and hashed using Argon2id. We never store plain text passwords.
                </span>
              </div>
            </div>
          </div>
        )}

        {/* STEP 6: REVIEW & SUBMIT */}
        {currentStep === 6 && (
          <div className="space-y-6">
            <div className="space-y-1">
              <h2 className="text-xl font-bold text-[#1F2421]">Review Your Application</h2>
              <p className="text-xs text-[#6B7280]">
                Please verify that your details are accurate before submitting to the Maatram team.
              </p>
            </div>

            <div className="bg-[#FAF8F3] rounded-2xl p-6 border border-[#EBE6DD] space-y-4 text-xs">
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pb-4 border-b border-[#EBE6DD]">
                <div>
                  <span className="text-[#6B7280] block">Applicant Name</span>
                  <span className="font-bold text-[#1F2421] text-sm">
                    {firstName} {lastName}
                  </span>
                </div>
                <div>
                  <span className="text-[#6B7280] block">Email & Mobile</span>
                  <span className="font-medium text-[#1F2421]">
                    {email} • {mobileNumber}
                  </span>
                </div>
                <div>
                  <span className="text-[#6B7280] block">Age & Gender</span>
                  <span className="font-medium text-[#1F2421]">
                    {age} Years • {gender}
                  </span>
                </div>
                <div>
                  <span className="text-[#6B7280] block">Volunteer Track</span>
                  <span className="font-bold text-[#B45309]">{category} VOLUNTEER</span>
                </div>
              </div>

              {/* Category-specific summary */}
              <div className="pb-4 border-b border-[#EBE6DD]">
                <span className="text-[#6B7280] block font-semibold mb-1">Background Details</span>
                {category === "STUDENT" && (
                  <p className="text-[#1F2421]">
                    {studentCollege} ({studentDegree}, {studentDepartment}) • Year {studentCurrentYear} • Reg: {studentRegNumber}
                  </p>
                )}
                {category === "ALUMNI" && (
                  <p className="text-[#1F2421]">
                    {alumniRole} at {alumniOrg} ({alumniExp} yrs exp) • {alumniCollege} ({alumniGradYear})
                  </p>
                )}
                {category === "CORPORATE" && (
                  <p className="text-[#1F2421]">
                    {corporateDesignation} at {corporateOrg} ({corporateExp} yrs exp, {corporateLocation})
                  </p>
                )}
              </div>

              {/* Safeguarding summary */}
              {age < 18 && (
                <div className="pb-4 border-b border-[#EBE6DD] text-[#92400E]">
                  <span className="font-bold block">Safeguarding Status</span>
                  <span>
                    Parent/Guardian: {guardianName} ({guardianRelationship}, {guardianContact}). Parental consent status: <span className="font-bold">PENDING VERIFICATION</span>.
                  </span>
                </div>
              )}

              {/* Consents granted count */}
              <div>
                <span className="text-[#6B7280] block font-semibold mb-1">Privacy Permissions</span>
                <span className="text-[#15803D] font-medium">
                  {[
                    consentLeaderboard,
                    consentNameVisible,
                    consentThankYou,
                    consentLinkedin,
                    consentContact,
                    consentMedia,
                  ].filter(Boolean).length} of 6 optional permissions enabled.
                </span>
              </div>
            </div>
          </div>
        )}

        {/* BOTTOM NAVIGATION BUTTONS */}
        <div className="pt-6 border-t border-[#EBE6DD] flex items-center justify-between">
          {currentStep > 1 ? (
            <Button variant="outline" size="sm" onClick={handleBack} disabled={isSubmitting}>
              <ChevronLeft className="w-4 h-4 mr-1" />
              <span>Previous</span>
            </Button>
          ) : (
            <div />
          )}

          {currentStep < TOTAL_STEPS ? (
            <Button variant="primary" size="sm" onClick={handleNext}>
              <span>Continue</span>
              <ChevronRight className="w-4 h-4 ml-1" />
            </Button>
          ) : (
            <Button
              variant="primary"
              size="md"
              onClick={handleSubmit}
              disabled={isSubmitting}
              className="px-8 shadow-md shadow-[#F5B817]/25 font-bold"
            >
              {isSubmitting ? "Submitting Application..." : "Submit Volunteer Application"}
            </Button>
          )}
        </div>
      </Card>
    </div>
  );
}

export default function RegisterPage() {
  return (
    <div className="min-h-screen flex flex-col bg-[#FAF8F3] text-[#1F2421]">
      <PublicHeader activeNav="volunteer" />

      <main className="flex-1">
        <Suspense
          fallback={
            <div className="max-w-3xl mx-auto px-4 py-16 text-center animate-pulse space-y-4">
              <div className="h-6 bg-gray-200 rounded w-1/3 mx-auto" />
              <div className="h-32 bg-white rounded-3xl border border-[#EBE6DD]" />
            </div>
          }
        >
          <RegisterWizard />
        </Suspense>
      </main>

      <PublicFooter />
    </div>
  );
}
