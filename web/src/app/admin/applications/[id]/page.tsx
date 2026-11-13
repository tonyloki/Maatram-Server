import { redirect } from "next/navigation";

interface PageProps {
  params: Promise<{ id: string }>;
}

export default async function AdminApplicationDetailRedirect({ params }: PageProps) {
  const { id } = await params;
  redirect(`/admin/volunteers/${id}`);
}
