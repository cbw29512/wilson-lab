import type { Notice } from "../types";

type Props = {
  notice: Notice | null;
};

export function NoticeBanner({ notice }: Props) {
  if (!notice) return null;
  return (
    <div className={`notice notice-${notice.tone}`} role={notice.tone === "error" ? "alert" : "status"}>
      {notice.message}
    </div>
  );
}
