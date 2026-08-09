export default function AuroraBackground({ children }) {
  return (
    <div className="relative min-h-screen overflow-hidden bg-[#050816]">
      <div className="absolute -left-32 -top-32 h-[500px] w-[500px] rounded-full bg-blue-600/20 blur-[180px]" />

      <div className="absolute bottom-0 right-0 h-[500px] w-[500px] rounded-full bg-indigo-600/20 blur-[180px]" />

      {children}
    </div>
  );
}