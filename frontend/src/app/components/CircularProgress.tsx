interface CircularProgressProps {
    size: number;
    strokeWidth: number;
    percentage: number;
  }

export const CircularProgress: React.FC<CircularProgressProps> = ({ size, strokeWidth, percentage }) => {
    const radius = (size - strokeWidth) / 2;
    const circumference = radius * 2 * Math.PI;
    const offset = circumference - (percentage / 100) * circumference;
  
    return (
      <div className="flex items-center justify-center relative">
        <svg
          className="transform -rotate-90"
          width={size}
          height={size}
        >
          <circle
            stroke="gray"
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{ strokeDashoffset: 0 }}
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
          <circle
            stroke="blue-500" // Tailwind color
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={`${circumference} ${circumference}`}
            style={{ strokeDashoffset: offset }}
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
        </svg>
        <span className="absolute text-sm font-semibold">
          {percentage}%
        </span>
      </div>
    );
  };