// Converts a hyphenated string (like a URL segment) into a prettified, capitalized version
export function prettifyUrlProvidedName(str: string): string {
  // Replace hyphens with spaces and capitalize the first letter of each word
  return capitalizeFirstLetter(str.replace(/-+/g, ' '));
}

// Capitalizes the first letter of each word in the string
export function capitalizeFirstLetter(str: string): string {
  return str
    .trim() // Remove any leading or trailing whitespace
    .replace(/\s+/g, ' ') // Normalize spaces
    .split(' ') // Split the string by single space
    .map(word => word.charAt(0).toUpperCase() + word.slice(1).toLowerCase()) // Capitalize first letter of each word
    .join(' '); // Join the capitalized words back with spaces
}

// Converts a space-separated string into a hyphenated lowercase string (reverse of prettifyUrlProvidedName)
export function convertToHyphenatedLowercase(str: string): string {
  return str
    .trim() // Remove any leading or trailing whitespace
    .toLowerCase() // Convert everything to lowercase
    .replace(/\s+/g, '-') // Replace spaces with hyphens
    .replace(/[^a-z0-9-]/g, ''); // Remove any non-alphanumeric characters except hyphens
}
