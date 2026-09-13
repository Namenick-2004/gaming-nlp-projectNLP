export function VideoCardSkeleton() {
  return (
    <div className="glass-card overflow-hidden">
      <div className="skeleton aspect-video" />
      <div className="p-4 space-y-2">
        <div className="skeleton h-4 w-3/4" />
        <div className="skeleton h-3 w-1/2" />
        <div className="skeleton h-8 w-full mt-2" />
      </div>
    </div>
  );
}

export function ChartSkeleton() {
  return <div className="glass-card p-4"><div className="skeleton h-52 w-full" /></div>;
}

export function EmptyState({ icon: Icon, title, subtitle }) {
  return (
    <div className="glass-card p-10 flex flex-col items-center text-center text-slate-400">
      {Icon && <Icon size={32} className="mb-3 opacity-60" />}
      <p className="font-medium text-slate-300">{title}</p>
      {subtitle && <p className="text-sm mt-1">{subtitle}</p>}
    </div>
  );
}

export function ErrorState({ message, onRetry }) {
  return (
    <div className="glass-card p-10 flex flex-col items-center text-center">
      <p className="text-red-400 font-medium">เกิดข้อผิดพลาด</p>
      <p className="text-sm text-slate-400 mt-1">{message}</p>
      {onRetry && (
        <button onClick={onRetry} className="mt-4 px-4 py-2 rounded-lg bg-accent-blue/20 text-accent-blue text-sm hover:bg-accent-blue/30">
          ลองใหม่
        </button>
      )}
    </div>
  );
}
