interface LoadingSpinnerProps {
  size?: "sm" | "md" | "lg";
  text?: string;
  textColor?: "light" | "dark";
}

export default function LoadingSpinner({ size = "md", text, textColor = "light" }: LoadingSpinnerProps) {
  const sizeClasses = {
    sm: "w-4 h-4",
    md: "w-6 h-6", 
    lg: "w-8 h-8"
  };

  const textColorClass = textColor === "dark" ? "text-slate-400" : "text-slate-600 dark:text-slate-400";

  return (
    <div className="flex flex-col items-center justify-center space-y-2">
      <div className={`${sizeClasses[size]} animate-spin rounded-full border-2 border-slate-300 border-t-blue-600`}></div>
      {text && (
        <p className={`text-sm ${textColorClass}`}>{text}</p>
      )}
    </div>
  );
}
