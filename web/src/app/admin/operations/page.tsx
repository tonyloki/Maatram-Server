import { redirect } from "next/navigation";

export default function AdminOperationsRedirect() {
  redirect("/admin/dashboard");
}
