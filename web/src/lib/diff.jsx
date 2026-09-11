/**
 * Renders two same-length-ish alphanumeric strings with differing
 * characters highlighted — used for the GSTIN/PAN mismatch reveal.
 */
export function DiffValue({ value, compareTo, highlightClass = 'text-danger-400 bg-danger-500/20' }) {
  if (!value) return <span className="text-mist-600">—</span>;
  if (!compareTo || value.length !== compareTo.length) {
    return <span className="font-mono">{value}</span>;
  }
  return (
    <span className="font-mono">
      {value.split('').map((ch, i) => {
        const diff = ch.toUpperCase() !== compareTo[i]?.toUpperCase();
        return (
          <span key={i} className={diff ? `rounded px-0.5 font-bold ${highlightClass}` : ''}>
            {ch}
          </span>
        );
      })}
    </span>
  );
}
