export function ErrorMessage({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="rounded-md bg-red-50 border border-red-200 p-3 text-sm text-red-700"
    >
      {message}
    </div>
  );
}
