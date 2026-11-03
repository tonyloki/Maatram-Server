"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function VolunteerIndexPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/volunteer/dashboard");
  }, [router]);

  return null;
}

