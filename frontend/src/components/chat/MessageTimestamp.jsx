export default function MessageTimestamp({
  date,
}) {
  return (
    <span className="text-xs text-slate-500">
      {new Date(date).toLocaleTimeString(
        [],
        {
          hour: "2-digit",
          minute: "2-digit",
        }
      )}
    </span>
  );
}