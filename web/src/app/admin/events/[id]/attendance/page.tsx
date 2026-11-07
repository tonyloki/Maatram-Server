"use client";

import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function AttendanceRedirect({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();

  useEffect(() => {
    router.replace(`/admin/events/${id}?tab=attendance`);
  }, [id, router]);

  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="w-8 h-8 border-3 border-[#F5B817] border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

