import { redirect } from "next/navigation";

export default function AdminApplicationsRedirect() {
  redirect("/admin/volunteers?tab=pending");
}
