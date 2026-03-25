export function ErrorMessage({ message }: { message: string }) {
  return (
    <div
      role="alert"
      className="rounded-md bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 p-3 text-sm text-red-700 dark:text-red-400"
    >
      {message}
    </div>
  );
}
