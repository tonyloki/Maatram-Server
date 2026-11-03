"use client";

import { use, useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ParticipantsRedirect({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  const router = useRouter();

  useEffect(() => {
    router.replace(`/admin/events/${id}?tab=subscribed`);
  }, [id, router]);

  return (
    <div className="flex items-center justify-center min-h-[40vh]">
      <div className="w-8 h-8 border-3 border-amber-500 border-t-transparent rounded-full animate-spin" />
    </div>
  );
}

